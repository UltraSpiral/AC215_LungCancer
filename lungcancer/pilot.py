from __future__ import annotations
from pathlib import Path
import time
import json
import numpy as np
from .common import read_json, atomic_json, backup_code, sync_artifacts, persist_file, checksum, fingerprint, utcnow
from .preprocess import TileConfig
from .safety import prepare_checked as prepare_slide
from .features import extract_features, load_features
from .download import download_slide, remove_managed_raw
from .encoder import UNI2Encoder


def run_pilot(selection='artifacts/pilot_selection.json',config=None,cleanup=True):
    import openslide
    from . import preprocess,features
    selection=read_json(selection); config=config or TileConfig()
    encoder=UNI2Encoder(revision=read_json('artifacts/encoder_smoke.json')['encoder']['revision'])
    backup_code(); sync_artifacts('artifacts/discovery','artifacts/discovery')
    persist_file('artifacts/pilot_selection.json','artifacts/pilot_selection.json')
    persist_file('artifacts/encoder_smoke.json','artifacts/encoder_smoke.json')
    result_path=Path('artifacts/pilot_results.json')
    results={'started_at':utcnow(),'status':'running','selection':selection,'slides':[]}
    for index,record in enumerate(selection['slides']):
        start=time.monotonic(); file_id=record['file_id']; directory=Path('artifacts/slides')/file_id
        print(f'PILOT {index+1}/{len(selection["slides"])}: {record["candidate_class"]} {file_id}',flush=True)
        try:
            prep_key=fingerprint({'source_md5':record['md5sum'],'config':config.__dict__,
                                  'implementation_sha256':checksum(preprocess.__file__),'openslide_version':openslide.__library_version__})
            cached=False
            if (directory/'embeddings.npz').exists() and (directory/'preprocessing.json').exists():
                _,coords,meta=load_features(directory/'embeddings.npz')
                expected=fingerprint({'preprocessing':prep_key,'encoder':encoder.identifier,
                                      'coordinates':fingerprint(coords.tolist()),'implementation':checksum(features.__file__)})
                cached=meta['fingerprint']==expected and meta['source_md5']==record['md5sum']
            if cached:
                prep=read_json(directory/'preprocessing.json')
                path=None
                print('Compatible completed slide cache verified; skipping raw download',flush=True)
            else:
                path=download_slide(record,budget=selection['cumulative_raw_budget_bytes'])
                prep=prepare_slide(path,directory,config,file_id,record['md5sum'])
                meta=extract_features(path,directory,encoder)
            receipts=sync_artifacts(directory,Path('artifacts/slides')/file_id)
            if cleanup and path is not None:
                remove_managed_raw(path,record,receipts)
            result={'file_id':file_id,'patient_id':record['patient_id'],'case_id':record['case_id'],
                    'class':record['candidate_class'],'preparation':record['preparation'],
                    'status':'success','embedding_shape':meta['shape'],'warnings':prep['warnings'],
                    'tiles':prep['selected_count'],'candidate_count':prep['candidate_count'],
                    'accepted_count':prep['accepted_count'],'elapsed_seconds':time.monotonic()-start,
                    'cached':cached,'raw_deleted_after_persistence':bool(cleanup and path is not None),
                    'persistent_receipts':receipts}
        except Exception as exc:
            result={'file_id':file_id,'patient_id':record['patient_id'],'class':record['candidate_class'],
                    'status':'error','reason':str(exc),'elapsed_seconds':time.monotonic()-start}
            print(f'PILOT FAILURE {file_id}: {exc}',flush=True)
        results['slides'].append(result)
        atomic_json(result_path,results); persist_file(result_path,'artifacts/pilot_results.json')
    results['finished_at']=utcnow()
    results['status']='success' if all(x['status']=='success' for x in results['slides']) else 'partial_failure'
    results['successful_slides']=sum(x['status']=='success' for x in results['slides'])
    atomic_json(result_path,results); persist_file(result_path,'artifacts/pilot_results.json'); backup_code()
    print(json.dumps({k:v for k,v in results.items() if k not in ['selection','slides']},indent=2),flush=True)
    return results
