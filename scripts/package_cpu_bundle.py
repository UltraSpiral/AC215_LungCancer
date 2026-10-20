"""Package verified real caches and one public SVS; exclude UNI2 weights/auth."""
from pathlib import Path
import argparse
import shutil
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lungcancer.common import atomic_json,checksum,fingerprint,persist_file,read_json,utcnow


def package(run_root):
    run_root=Path(run_root).resolve()
    verified=read_json(run_root/'verified_results.json')
    if verified['status']!='success':raise ValueError('verified_modeling_results_required')
    sample=read_json(run_root/'cpu_real_input.json');record=sample['record']
    if checksum(sample['local_path'],'md5')!=record['md5sum']:
        raise ValueError('retained_real_slide_checksum_mismatch')
    stage=ROOT/'artifacts/portable/cpu_bundle'
    if stage.exists():raise ValueError('portable_bundle_exists; preserve_existing_bundle')
    stage.mkdir(parents=True)
    sources={}
    for name in ['cohort.json','splits.json','model/model.json','model/classifier.joblib',
                 'evaluation_validation/predictions.json','evaluation_test/predictions.json',
                 'cohort_provenance_and_qc.json','RESULTS.md','exclusions.json']:
        sources['run/'+name]=run_root/name
    for row in read_json(run_root/'splits.json')['slides']:
        for name in ['embeddings.npz','embeddings.json','coordinates.npz','preprocessing.json']:
            relative=Path('slides')/row['file_id']/name
            sources[str(relative)]=ROOT/'artifacts'/relative
    sources['sample/sample.svs']=Path(sample['local_path'])
    entries=[]
    for relative,source in sources.items():
        destination=stage/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination)
        digest=checksum(source)
        if checksum(destination)!=digest:raise ValueError('portable_copy_checksum_mismatch')
        entries.append({'path':relative,'sha256':digest,'bytes':destination.stat().st_size})
    manifest={'created_at':utcnow(),'files':entries,
              'data_snapshot_identifier':fingerprint({'files':entries,'split':verified['split_identifier']}),
              'model_identifier':verified['model_identifier'],'split_identifier':verified['split_identifier'],
              'real_slide':{'path':'sample/sample.svs','file_id':record['file_id'],
                            'md5sum':record['md5sum'],'bytes':record['file_size']},
              'includes_uni2_weights':False,'includes_credentials':False,
              'additional_raw_download_bytes':0,
              'scope':'cached real UNI2 vectors + saved logistic head + real-SVS preprocessing; full UNI2 inference container pending'}
    atomic_json(stage/'manifest.json',manifest)
    archive=ROOT/'artifacts/portable'/f'cpu-verification-{run_root.name}.tar.gz'
    with tarfile.open(archive,'w:gz',dereference=True) as tf:
        for path in sorted(stage.rglob('*')):
            if path.is_file():tf.add(path,arcname=str(path.relative_to(stage)))
    expected={e['path']:e['sha256'] for e in entries}
    expected['manifest.json']=checksum(stage/'manifest.json')
    with tarfile.open(archive,'r:gz') as tf:
        for member in tf:
            import hashlib
            digest=hashlib.sha256()
            stream=tf.extractfile(member)
            for chunk in iter(lambda:stream.read(8*1024*1024),b''):digest.update(chunk)
            if digest.hexdigest()!=expected.pop(member.name):raise ValueError('archive_member_checksum_mismatch')
    if expected:raise ValueError('archive_members_missing')
    receipt=persist_file(archive,Path('portable')/archive.name)
    result={**receipt,'created_at':utcnow(),'data_snapshot_identifier':manifest['data_snapshot_identifier'],
            'members_verified':len(entries)+1,'real_slide':manifest['real_slide'],
            'includes_uni2_weights':False,'includes_credentials':False,'additional_raw_download_bytes':0}
    atomic_json(archive.with_suffix('.json'),result)
    persist_file(archive.with_suffix('.json'),Path('portable')/archive.with_suffix('.json').name)
    print(result)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-root',required=True)
    package(parser.parse_args().run_root)
