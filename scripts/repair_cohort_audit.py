"""Conservatively exclude ambiguous UUID chains; preserve patient assignments."""
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lungcancer.common import atomic_json,checksum,fingerprint,read_json,sync_artifacts,utcnow
from lungcancer.gdc import normalize_file,audit
from lungcancer.modeling import train,evaluate,split_counts


def main():
    original=ROOT/'artifacts/modeling/20261020T0220Z'
    output=ROOT/'artifacts/modeling/20261020T0220Z-audit2'
    output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    raw={h['file_id']:h for p in (ROOT/'artifacts/discovery').glob('raw_page_*.json')
         for h in read_json(p)['response']['data']['hits']}
    old_split=read_json(original/'splits.json')
    excluded=[];rows=[]
    for record in old_split['slides']:
        new=normalize_file(raw[record['file_id']])
        if new['decision']!='include':
            excluded.append({'original_record':record,'updated_audit':new})
        else:
            if any(new[k]!=record[k] for k in ['case_id','sample_id','slide_id','candidate_class','preparation']):
                raise ValueError('unexpected_label_or_preparation_change')
            rows.append({**new,'split':record['split']})
    if len(rows)!=44 or len(excluded)!=1 or excluded[0]['original_record']['file_id']!='6125ea6f-c49e-4809-9502-f121e6d35d8c':
        raise ValueError('unexpected_audit_exclusions; scientific_review_required')
    atomic_json(output/'exclusions.json',excluded)
    cohort={**read_json(original/'cohort.json'),'slides':[{k:v for k,v in r.items() if k!='split'} for r in rows],
            'created_at':utcnow(),'complete_target':False,'eligible_slides':44,
            'correction':'One slide UUID attached to two distinct portion UUIDs excluded; all other patient assignments preserved.',
            'source_cohort_sha256':checksum(original/'cohort.json')}
    cohort['counts']={c:sum(r['candidate_class']==c for r in rows) for c in ('non_tumor','adenocarcinoma','squamous')}
    cohort['selected_bytes']=sum(r['file_size'] for r in rows)
    atomic_json(output/'cohort.json',cohort)
    split={**old_split,'slides':rows,'counts':split_counts(rows),'cohort_sha256':checksum(output/'cohort.json'),
           'created_at':utcnow(),'assignment_source_sha256':checksum(original/'splits.json'),
           'assignment_source_identifier':old_split['split_identifier'],
           'assignments_regenerated':False,'excluded_file_ids':[excluded[0]['original_record']['file_id']]}
    split.pop('split_identifier',None);split['split_identifier']=fingerprint(split)
    atomic_json(output/'splits.json',split)
    prior={r['case_id']:r['split'] for r in old_split['slides']}
    assert all(prior[r['case_id']]==r['split'] for r in rows)
    progress=read_json(original/'progress.json')
    progress['slides']={k:v for k,v in progress['slides'].items() if k in {r['file_id'] for r in rows}}
    progress.update(status='running',stage='metadata_audit_correction',excluded_files=excluded,
                    original_processed_slide_count=45,original_pipeline_wall_seconds=progress['elapsed_seconds_total'])
    progress['events'].append({'event':'conservative_metadata_exclusion_before_corrected_fit','at':utcnow(),
                               'assignments_regenerated':False,'prior_test_results_already_observed':True,
                               'decision_basis':'raw specimen UUID hierarchy, independent of predictions or metrics'})
    for name in ['protected_input_checksums.json','encoder.json','environment.json','cpu_real_input.json','unit_tests.md']:
        import shutil
        shutil.copyfile(original/name,output/name)
    atomic_json(output/'progress.json',progress);sync_artifacts(output,output.relative_to(ROOT))
    model=train(output/'splits.json',ROOT/'artifacts/slides',output/'model')
    for name in ['validation','test']:
        evaluate(output/'splits.json',ROOT/'artifacts/slides',output/'model',name,output/f'evaluation_{name}')
    from lungcancer.inference import predict
    sample=read_json(output/'cpu_real_input.json')
    result=predict(sample['local_path'],output/'model',output/'inference_arbitrary_filename')
    if result['status']!='success':raise ValueError(result)
    fid=sample['record']['file_id']
    expected=next(p for p in read_json(output/'evaluation_test/predictions.json') if p['file_id']==fid)
    delta=max(abs(result['class_probabilities'][c]-expected['class_probabilities'][c]) for c in model['classes'])
    if delta>1e-4 or result['predicted_class']!=expected['predicted_class']:
        raise ValueError('corrected_renamed_inference_disagrees')
    atomic_json(output/'inference_verification.json',{'status':'success','source_file_id':fid,'split':'test',
        'actual_input_path':sample['local_path'],'source_md5':result['source_md5'],
        'maximum_probability_difference':delta,'agrees_with_test_prediction':True,
        'float32_comparison_tolerance':1e-4,'no_filename_or_diagnosis_inputs':True})
    progress.update(status='success',stage='complete',finished_at=utcnow(),
                    elapsed_seconds_this_attempt=time.monotonic()-started,
                    elapsed_seconds_total=time.monotonic()-started,
                    correction_wall_seconds=time.monotonic()-started)
    atomic_json(output/'progress.json',progress)
    sync_artifacts(output,output.relative_to(ROOT))
    print({'status':'success','eligible_patients':44,'counts':split['counts'],
           'validation_macro_f1':model['validation']['macro_f1'],'correction_seconds':progress['correction_wall_seconds']})


if __name__=='__main__':main()
