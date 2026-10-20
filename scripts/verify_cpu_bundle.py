"""Offline CPU verification; does not load UNI2 or perform full-slide inference."""
from pathlib import Path
import argparse
import importlib.metadata
import importlib.util
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from lungcancer.common import CLASSES,atomic_json,checksum,read_json,utcnow


def verify_inventory(bundle):
    manifest=read_json(bundle/'manifest.json')
    for entry in manifest['files']:
        path=(bundle/entry['path']).resolve()
        if not path.is_relative_to(bundle.resolve()) or not path.is_file():
            raise ValueError('missing_or_unsafe_bundle_path')
        if path.stat().st_size!=entry['bytes'] or checksum(path)!=entry['sha256']:
            raise ValueError('bundle_checksum_mismatch: '+entry['path'])
    return manifest


def check_cache(bundle,output):
    import joblib
    from lungcancer.features import load_features
    from lungcancer.modeling import check_patient_separation,named_probabilities
    from lungcancer.modeling_run import verify_cache
    from lungcancer.preprocess import TileConfig
    metadata=read_json(bundle/'run/model/model.json')
    split=read_json(bundle/'run/splits.json')
    check_patient_separation(split['slides'])
    if checksum(bundle/'run/splits.json')!=metadata['split_file_sha256']:
        raise ValueError('split_assignments_changed')
    if checksum(bundle/'run/model/classifier.joblib')!=metadata['classifier_sha256']:
        raise ValueError('classifier_changed')
    model=joblib.load(bundle/'run/model/classifier.joblib')
    vectors={};total=0;train=[]
    for row in split['slides']:
        directory=bundle/'slides'/row['file_id']
        embeddings,coords,meta=load_features(directory/'embeddings.npz')
        # Identity-string verification only: no encoder object, weights or generated features.
        verify_cache(row,directory,TileConfig(**metadata['preprocessing_config']),metadata['encoder_identifier'])
        with np.load(directory/'coordinates.npz',allow_pickle=False) as data:
            if not np.array_equal(data['coordinates'],coords):
                raise ValueError('embedding_coordinate_order_mismatch')
        if (meta['file_id']!=row['file_id'] or meta['source_md5']!=row['md5sum'] or
                meta['encoder_identifier']!=metadata['encoder_identifier'] or
                meta['preprocessing_config']!=metadata['preprocessing_config']):
            raise ValueError('feature_provenance_mismatch')
        vectors[row['file_id']]=embeddings.mean(axis=0,dtype=np.float64)
        if row['split']=='train':train.append(vectors[row['file_id']])
        total+=len(embeddings)
    scaler=model.named_steps['scaler'];train=np.asarray(train)
    if (int(scaler.n_samples_seen_)!=len(train) or
            not np.allclose(scaler.mean_,train.mean(0),rtol=1e-12,atol=1e-12) or
            not np.allclose(scaler.var_,train.var(0),rtol=1e-12,atol=1e-12)):
        raise ValueError('scaler_training_only_statistics_mismatch')
    maximum_delta=0.0;checked=0
    for name in ('validation','test'):
        # Verify frozen reference predictions; no hyperparameter choice or new evaluation.
        for reference in read_json(bundle/f'run/evaluation_{name}/predictions.json'):
            p=named_probabilities(model,vectors[reference['file_id']][None,:])[0]
            expected=np.asarray([reference['class_probabilities'][c] for c in CLASSES])
            if not np.isfinite(p).all() or not np.isclose(p.sum(),1):
                raise ValueError('invalid_probabilities')
            maximum_delta=max(maximum_delta,float(np.max(np.abs(p-expected))))
            if not np.allclose(p,expected,rtol=0,atol=1e-8):
                raise ValueError('cached_cpu_prediction_disagrees_with_frozen_reference')
            checked+=1
    report={'status':'success','scope':'real cached UNI2 embeddings and saved logistic head only',
            'slides':len(vectors),'real_tile_embeddings':total,'all_finite':True,
            'patient_separation_verified':True,'training_only_scaler_verified':True,
            'class_order':list(CLASSES),'frozen_reference_predictions_checked':checked,
            'maximum_probability_difference':maximum_delta,'probability_tolerance':1e-8,
            'model_identifier':metadata['model_identifier'],'split_identifier':split['split_identifier'],
            'new_model_training_performed':False,'new_test_metric_evaluation_performed':False,
            'uni2_encoding_performed':False,'full_slide_prediction_performed':False}
    atomic_json(output/'cached_embeddings.json',report)
    return report


def check_preprocess(bundle,output,manifest):
    from lungcancer.preprocess import TileConfig
    from lungcancer.safety import prepare_checked
    sample=manifest['real_slide'];path=bundle/sample['path']
    if checksum(path,'md5')!=sample['md5sum']:
        raise ValueError('real_slide_md5_mismatch')
    config=TileConfig(max_tiles=16,thumbnail_max=1024)
    prep=prepare_checked(path,output/'preprocessing',config,sample['file_id'],sample['md5sum'])
    if prep['selected_count']<1 or prep['candidate_count']!=prep['accepted_count']+prep['rejected_count']:
        raise ValueError('invalid_preprocessing_counts')
    with np.load(output/'preprocessing/coordinates.npz',allow_pickle=False) as data:
        coords=data['coordinates']; w,h=prep['dimensions_level0'];tw,th=prep['geometry']['footprint_level0']
        if np.any(coords<0) or np.any(coords[:,0]+tw>w) or np.any(coords[:,1]+th>h):
            raise ValueError('preprocessing_coordinates_out_of_bounds')
    report={'status':'success','scope':'small real-SVS CPU preprocessing smoke only',
            'source_file_id':sample['file_id'],'source_md5':sample['md5sum'],
            'selected_tiles':prep['selected_count'],'actual_output_mpp':prep['geometry']['actual_output_mpp'],
            'quality_warnings':prep['warnings'],'config':prep['config'],
            'smoke_config_differs_from_frozen_model_config':True,
            'uni2_encoding_performed':False,'class_prediction_performed':False}
    atomic_json(output/'real_preprocessing.json',report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['all','unit','cache','preprocess'])
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--require-arm64',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    report={'started_at':utcnow(),'architecture':platform.machine(),'python':platform.python_version(),
            'status':'running','stages':{},'full_slide_to_prediction_container_verification':'pending'}
    try:
        if args.require_arm64 and platform.machine().lower() not in {'aarch64','arm64'}:
            raise ValueError('expected_native_arm64; no_silent_x86_emulation')
        if importlib.util.find_spec('torch') is not None:
            raise ValueError('use_the_isolated_torch_free_cpu_environment')
        import openslide
        report['openslide_library_version']=openslide.__library_version__
        report['dependencies']={p:importlib.metadata.version(p) for p in
                                ['numpy','scipy','scikit-learn','Pillow','joblib','openslide-python','openslide-bin','pytest']}
        if args.stage in {'all','unit'}:
            subprocess.run([sys.executable,'-m','pytest','-q','-p','no:cacheprovider',
                            '--junitxml='+str((args.output/'unit-tests.xml').resolve())],cwd=ROOT,check=True)
            report['stages']['unit']={'status':'success','data':'synthetic unit fixtures only'}
        if args.stage in {'all','cache','preprocess'}:
            manifest=verify_inventory(args.bundle)
            report['data_snapshot_identifier']=manifest['data_snapshot_identifier']
            if args.stage in {'all','cache'}:
                report['stages']['cache']=check_cache(args.bundle,args.output)
            if args.stage in {'all','preprocess'}:
                report['stages']['preprocess']=check_preprocess(args.bundle,args.output,manifest)
        report['status']='success'
    except Exception as exc:
        report.update(status='error',reason=str(exc))
    report['finished_at']=utcnow();report['elapsed_seconds']=time.monotonic()-start
    atomic_json(args.output/f'verification_{args.stage}.json',report)
    print(report)
    if report['status']!='success':raise SystemExit(2)


if __name__=='__main__':main()
