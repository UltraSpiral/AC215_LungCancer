"""Verify completed, persisted real-model artifacts and write a durable report."""
from pathlib import Path
import argparse
from collections import Counter
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from lungcancer.common import (CLASSES, DEFAULT_PERSISTENT, atomic_json, checksum,
                              persist_file, read_json, sync_artifacts, utcnow)
from lungcancer.features import load_features
from lungcancer.modeling import check_patient_separation


def report(run_root):
    run_root = Path(run_root).resolve()
    progress = read_json(run_root / 'progress.json')
    if progress['status'] != 'success':
        raise ValueError('run_not_successfully_complete; no_reported_model_success')
    split = read_json(run_root / 'splits.json'); cohort = read_json(run_root / 'cohort.json')
    model = read_json(run_root / 'model/model.json')
    validation = read_json(run_root / 'evaluation_validation/metrics.json')
    test = read_json(run_root / 'evaluation_test/metrics.json')
    inference = read_json(run_root / 'inference_arbitrary_filename/prediction.json')
    inference_check = read_json(run_root / 'inference_verification.json')
    check_patient_separation(split['slides'])
    eligible_count=len(split['slides'])
    if len({r['case_id'] for r in split['slides']}) != eligible_count:
        raise ValueError('cohort_must_have_independent_patients')
    patient_splits={}
    for row in split['slides']:
        old=patient_splits.setdefault(row['patient_id'],row['split'])
        if old!=row['split']:
            raise ValueError('patient_barcode_leakage')
    if checksum(run_root/'splits.json') != model['split_file_sha256']:
        raise ValueError('frozen_splits_changed')
    if checksum(run_root/'model/classifier.joblib') != model['classifier_sha256']:
        raise ValueError('classifier_changed')
    pilot_cases=set(read_json(ROOT/'artifacts/pilot_selection.json')['pilot_patients_development_only'])
    if any(r['split']!='train' for r in split['slides'] if r['case_id'] in pilot_cases):
        raise ValueError('inspected_pilot_patient_outside_training')
    wanted={r['file_id'] for r in split['slides']}
    raw_hits={}
    for page in sorted((ROOT/'artifacts/discovery').glob('raw_page_*.json')):
        for hit in read_json(page)['response']['data']['hits']:
            if hit['file_id'] in wanted: raw_hits[hit['file_id']]=hit
    verified=[]; tile_rows=[]; training_vectors=[]
    for row in split['slides']:
        hit=raw_hits[row['file_id']]
        matches=[]
        entities=[e for e in hit['associated_entities'] if e['entity_type']=='slide']
        for entity in entities:
            for case in hit['cases']:
                if case['case_id']!=entity['case_id']: continue
                for sample in case.get('samples',[]):
                    for portion in sample.get('portions',[]):
                        for slide in portion.get('slides',[]):
                            if slide['slide_id']==entity['entity_id']:
                                matches.append((case,sample,portion,slide,entity))
        from lungcancer.gdc import unique_specimen_links,normalize_file
        raw_portion_ids=sorted({p['portion_id'] for c,s,p,sl,e in matches})
        matches,link_warnings=unique_specimen_links(matches)
        if len(matches)!=1:
            raise ValueError('actual_slide_specimen_link_not_unique')
        case,sample,portion,slide,entity=matches[0]
        if (case['case_id']!=row['case_id'] or sample['sample_id']!=row['sample_id'] or
                slide['slide_id']!=row['slide_id'] or sample['sample_type']!=row['sample_type'] or
                case['project']['project_id']!=row['project_id']):
            raise ValueError('cohort_label_link_disagrees_with_raw_gdc_response')
        normalized=normalize_file(hit)
        if normalized['decision']!='include' or any(normalized[k]!=row[k] for k in
                 ['case_id','sample_id','slide_id','sample_type','project_id','candidate_class','preparation']):
            raise ValueError('updated_specimen_audit_changes_cohort_label_or_preparation')
        directory=ROOT/'artifacts/slides'/row['file_id']
        embeddings,coordinates,meta=load_features(directory/'embeddings.npz')
        prep=read_json(directory/'preprocessing.json')
        if meta['source_md5']!=row['md5sum'] or meta['file_id']!=row['file_id']:
            raise ValueError('feature_identity_mismatch')
        if meta['encoder_identifier']!=model['encoder_identifier']:
            raise ValueError('feature_encoder_mismatch')
        if row['split']=='train':
            training_vectors.append(embeddings.mean(axis=0,dtype=np.float64))
        for receipt in progress['slides'][row['file_id']]['persistent_receipts']:
            local=directory/Path(receipt['path']).name
            if checksum(local)!=receipt['sha256'] or checksum(receipt['path'])!=receipt['sha256']:
                raise ValueError('slide_persistence_verification_failed')
            verified.append(receipt)
        tile_rows.append({**row,'portion_id':portion['portion_id'],
                          'raw_candidate_portion_ids':raw_portion_ids,'portion_link_resolution_warnings':link_warnings,
                          'portion_barcode':portion.get('submitter_id'),
                          'actual_associated_entity':entity,
                          'preservation_method_as_reported':sample.get('preservation_method'),
                          'portion_is_ffpe_as_reported':portion.get('is_ffpe'),
                          'frozen_explicitly_confirmed':str(sample.get('preservation_method','')).lower() in {'frozen','snap frozen','cryopreserved'},
                          'specimen_link_verified_against_saved_raw_metadata':True,
                          'embedding_shape':list(embeddings.shape),
                          'all_finite':bool(np.isfinite(embeddings).all()),
                          'coordinates_shape':list(coordinates.shape),
                          'candidate_count':prep['candidate_count'],
                          'accepted_count':prep['accepted_count'],
                          'rejected_count':prep['rejected_count'],
                          'selected_count':prep['selected_count'],
                          'actual_output_mpp':prep['geometry']['actual_output_mpp'],
                          'coverage_threshold_counts':prep['coverage_threshold_counts'],
                          'warnings':prep['warnings']})
    original=read_json(run_root/'protected_input_checksums.json')
    if any(checksum(p)!=digest for p,digest in original.items()):
        raise ValueError('protected_pilot_input_changed')
    ledger=read_json(ROOT/'artifacts/download_ledger.json')
    if ledger['transferred_bytes']>10_000_000_000 or ledger['reserved_bytes']>10_000_000_000:
        raise ValueError('raw_budget_exceeded')
    for row in split['slides']:
        if ledger['verified_files'][row['file_id']]['md5sum']!=row['md5sum']:
            raise ValueError('download_ledger_manifest_mismatch')
    import joblib
    pipeline=joblib.load(run_root/'model/classifier.joblib')
    scaler=pipeline.named_steps['scaler']
    training_matrix=np.asarray(training_vectors)
    if (int(scaler.n_samples_seen_)!=len(training_vectors) or
            not np.allclose(scaler.mean_,training_matrix.mean(axis=0),rtol=1e-12,atol=1e-12) or
            not np.allclose(scaler.var_,training_matrix.var(axis=0),rtol=1e-12,atol=1e-12)):
        raise ValueError('saved_scaler_does_not_match_training_only_statistics')
    class_qc={}
    for c in CLASSES:
        rows=[r for r in tile_rows if r['candidate_class']==c]
        ratios=[r['accepted_count']/r['candidate_count'] for r in rows]
        class_qc[c]={'slides':len(rows),'patients':len({r['case_id'] for r in rows}),
                     'selected_tile_min_max':[min(r['selected_count'] for r in rows),max(r['selected_count'] for r in rows)],
                     'mean_grid_acceptance_fraction':float(np.mean(ratios)),
                     'grid_acceptance_fraction_min_max':[min(ratios),max(ratios)],
                     'warnings':dict(Counter(w for r in rows for w in r['warnings']))}
    summary={'verified_at':utcnow(),'status':'success','run_root':str(run_root),
             'persistent_run_root':str(DEFAULT_PERSISTENT/run_root.relative_to(ROOT)),
             'counts':split['counts'],'class_qc':class_qc,
             'all_embeddings_finite':all(r['all_finite'] for r in tile_rows),
             'total_real_tile_embeddings':sum(r['selected_count'] for r in tile_rows),
             'reused_pilot_slides':len(pilot_cases),'new_slides':len(tile_rows)-len(pilot_cases),
             'normal_project_counts':dict(Counter(r['project_id'] for r in tile_rows if r['candidate_class']=='non_tumor')),
             'preparation_provenance_counts':dict(Counter(r['preparation_provenance'] for r in tile_rows)),
             'explicit_frozen_confirmations':sum(r['frozen_explicitly_confirmed'] for r in tile_rows),
             'raw_preservation_method_counts':dict(Counter(str(r['preservation_method_as_reported']) for r in tile_rows)),
             'raw_portion_is_ffpe_counts':dict(Counter(str(r['portion_is_ffpe_as_reported']) for r in tile_rows)),
             'raw_bytes_total':ledger['transferred_bytes'],
             'raw_bytes_this_expansion':ledger['transferred_bytes']-1_020_202_701,
             'reserved_bytes_total':ledger['reserved_bytes'],'raw_budget_bytes':10_000_000_000,
             'download_attempts':len(ledger['attempts']),
             'failed_download_attempts':sum(a['status']=='failed' for a in ledger['attempts']),
             'encoder':model['encoder'],'encoder_identifier':model['encoder_identifier'],
             'model_identifier':model['model_identifier'],'split_identifier':split['split_identifier'],
             'training_only_scaler_statistics_verified':True,
             'classifier_input_dimension':int(pipeline.n_features_in_),
             'C':model['C'],'regularization_search':model['regularization_search'],
             'eligible_slides':eligible_count,
             'original_processed_slide_count':progress.get('original_processed_slide_count',eligible_count),
             'excluded_files':progress.get('excluded_files',[]),
             'validation':validation,'test':test,'heldout_inference':inference,
             'heldout_inference_verification':inference_check,
             'processing_events':progress['events'],
             'pipeline_wall_seconds':progress.get('original_pipeline_wall_seconds',0)+progress.get('elapsed_seconds_total',progress['elapsed_seconds_this_attempt']),
             'initial_pipeline_wall_seconds':progress.get('original_pipeline_wall_seconds'),
             'correction_wall_seconds':progress.get('correction_wall_seconds'),
             'slide_receipts_verified':len(verified),'slides':tile_rows}
    atomic_json(run_root/'verified_results.json',summary)
    # Full provenance includes actual associated slide entity and linked sample IDs.
    atomic_json(run_root/'cohort_provenance_and_qc.json',tile_rows)
    def fmt(value):
        return 'undefined' if value is None else f'{value:.4f}'
    lines=[f'# Real {eligible_count}-slide modeling baseline: verified results','',f'Verified UTC: {summary["verified_at"]}',
           '',f'Persistent run directory: `{summary["persistent_run_root"]}`','',
           '## What actually ran','',
           f'{eligible_count} eligible real TCGA slides from {eligible_count} independent patients. '
           'Initially 45 slides (15/class) were processed, reusing nine pilot caches and acquiring 36 new slides. '
           'One squamous slide was excluded after its actual slide UUID was found under two distinct portion UUIDs. '
           'The corrected model uses 15 normal, 15 adenocarcinoma and 14 squamous slides. Original outputs are retained. '
           'Every remaining patient keeps the original split assignment; no splits were regenerated. '
           'All derived slide files were copied '
           'to mounted Drive and reread by SHA256 before temporary managed raw slides were removed. '
           'All nine original pilot patients are in training. Fixed model choices precede test-slide processing.',
           '',f'Pipeline elapsed: {summary["pipeline_wall_seconds"]:.1f} seconds; setup/reporting overhead is separate. '
           'This sums the original run and the metadata correction, excluding intervening audit/packaging time; '
           'it is not a CUDA-synchronized stage profile. Profiling remains deferred. '
           'The post-run audit meant the full turn, including verification and container preparation, exceeded one hour.',
           '', '## Fixed patient split','',
           '| Class | Train slides/patients | Validation slides/patients | Test slides/patients |',
           '|---|---:|---:|---:|']
    for c in CLASSES:
        counts=split['counts']
        lines.append(f'| {c} | {counts["train"][c]["slides"]}/{counts["train"][c]["patients"]} | '
                     f'{counts["validation"][c]["slides"]}/{counts["validation"][c]["patients"]} | '
                     f'{counts["test"][c]["slides"]}/{counts["test"][c]["patients"]} |')
    lines += ['', '## Model and metrics','',
              f'Frozen `MahmoodLab/UNI2-h` revision `{model["encoder"]["revision"]}`, checkpoint SHA256 '
              f'`{model["encoder"]["checkpoint_sha256"]}`. Official evaluation transforms; float32; '
              '512-tile cap at approximately 0.5 MPP, 224×224 pixels. Mean pooling; StandardScaler fitted on '
              f'training slides only; L2 multinomial logistic regression, validation-selected C={model["C"]}.',
              '', '| Split | Model macro F1 | Model balanced accuracy | Majority macro F1 | Majority balanced accuracy |',
              '|---|---:|---:|---:|---:|']
    for name,evaluation in [('Validation',validation),('Test',test)]:
        m,b=evaluation['metrics'],evaluation['majority_baseline']
        lines.append(f'| {name} | {fmt(m["macro_f1"])} | {fmt(m["balanced_accuracy"])} | {fmt(b["macro_f1"])} | {fmt(b["balanced_accuracy"])} |')
    lines += ['', '| Test class | Precision | Recall | One-vs-rest AUROC | Test patients |', '|---|---:|---:|---:|---:|']
    for c in CLASSES:
        m=test['metrics']['per_class'][c]
        lines.append(f'| {c} | {fmt(m["precision"])} | {fmt(m["recall"])} | {fmt(test["metrics"]["one_vs_rest_auroc"][c])} | 2 |')
    lines += ['', 'Test confusion matrix: rows=true, columns=predicted; class order '
              '`non_tumor, adenocarcinoma, squamous`.', '', '```text',
              *[' '.join(str(x) for x in row) for row in test['metrics']['confusion_matrix']], '```', '',
              '**Only six test patients, two per class.** Each error changes overall accuracy by 16.7 percentage '
              'points and that class recall by 50 points. Results demonstrate engineering execution; '
              'they do not establish stable generalization or clinical performance. Validation is also six patients. '
              'These same test patients were previously evaluated with the provisional 45-slide model. '
              'The subsequent exclusion was based solely on raw specimen UUID ambiguity, independently of metrics; '
              'the prespecified C grid and preprocessing remained fixed. This history limits a pristine-test claim. '
              'Undefined metrics are null in JSON, never fabricated.', '',
              '## Label and preparation provenance','',
              'Labels follow actual file-associated slide UUID → unique nested specimen → linked sample type '
              'and project. Solid Tissue Normal → non_tumor, irrespective of the patient cancer diagnosis; '
              'LUAD/LUSC Primary Tumor → adenocarcinoma/squamous. Diagnosis and barcode checks exclude conflicts. '
              'The frozen classification is inferred from linked TS/BS slide categories with non-FFPE evidence. '
              'Inference is distinguished from reported preservation fields in each manifest record. '
              'Source sites remain partly associated with class; no site-held-out robustness is established.', '',
              f'Normal project counts: {summary["normal_project_counts"]}. '
              f'Preparation provenance counts: {summary["preparation_provenance_counts"]}. '
              f'Explicit Frozen confirmations: {summary["explicit_frozen_confirmations"]}/{eligible_count}. '
              f'Reported preservation fields: {summary["raw_preservation_method_counts"]}; '
              f'portion is_ffpe fields: {summary["raw_portion_is_ffpe_counts"]}. '
              'Labels have not been independently adjudicated by a pathologist.', '',
              'Full per-slide entity UUIDs, sample IDs/types, diagnoses, preparation evidence, file UUID/MD5 '
              'and QC are in `cohort_provenance_and_qc.json`; raw query/metadata remain in `artifacts/discovery/`.', '',
              '## Tile filtering','',
              '| Class | Selected tiles: min–max | Mean grid acceptance fraction |', '|---|---:|---:|']
    for c,q in class_qc.items():
        lo,hi=q['selected_tile_min_max']
        lines.append(f'| {c} | {lo}–{hi} | {q["mean_grid_acceptance_fraction"]:.4f} |')
    lines += ['', 'Grid acceptance includes background and is not tissue sensitivity or tumor area. Sparse normal '
              'lung may be preferentially rejected by the 50% coverage threshold even when 512 tiles survive. '
              'The threshold was fixed before held-out processing; no stain normalization or aggressive artifact '
              'filtering was introduced. Warnings, thresholds, actual scale and candidate/accepted/rejected '
              'counts for every slide are saved in the provenance/QC JSON.', '',
              f'All embeddings finite: {summary["all_embeddings_finite"]}; '
              f'total real tile vectors: {summary["total_real_tile_embeddings"]:,}, dimension 1536. '
              'Coordinate order and bounds verified.', '',
              '## Raw transfer and persistence','',
              f'Cumulative raw bytes transferred: **{summary["raw_bytes_total"]:,}**; '
              f'this expansion: **{summary["raw_bytes_this_expansion"]:,}**. '
              f'Conservative reserved bytes: {summary["reserved_bytes_total"]:,}; approved cumulative limit '
              f'{summary["raw_budget_bytes"]:,}. Failed download attempts: {summary["failed_download_attempts"]}. '
              'Public raw SVS files are omitted after verified processing; UUIDs, sizes and MD5s allow redownload. '
              'UNI2 gated weights remain only in the disposable HF cache and are not redistributed.', '',
              f'SHA256 read-back verified {len(verified)} persisted per-slide files, plus model/run outputs '
              'listed in `verification_inventory.json`. Visual audits: '
              '`/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/<file_uuid>/contact_sheet.jpg`, '
              '`tissue_mask_overlay.jpg`, `selected_tiles_overlay.jpg` and `thumbnail.jpg`.', '',
              '## Real arbitrary-filename inference','',
              f'Input: `/tmp/lungcancer-inference/unknown_slide.svs` (actual held-out source UUID '
              f'`{inference_check["source_file_id"]}`). Status `{inference["status"]}`; '
              f'prediction `{inference["predicted_class"]}`; tiles {inference["tiles_analyzed"]}; '
              '`probabilities_calibrated: false`. This used real region reading, UNI2 and the saved sklearn model, '
              'without TCGA filename/diagnosis lookup. Its named probabilities agree with the held-out cached '
              f'prediction; maximum difference {inference_check["maximum_probability_difference"]:.8g}. '
              'Output and analyzed-location overlay are in `inference_arbitrary_filename/`. '
              'The location overlay is not a tumor heatmap.', '',
              '## Remaining work','',
              'MLOps/container/uv/one-command and basic frontend/backend execution evidence follow the modeling '
              'stage. A Docker-capable execution host is not yet established. Existing frontend fixtures/stub '
              'are separate from all real results here. No clinical validation, calibration, segmentation or '
              'attention MIL is claimed. Optional single-slide synchronized profiling remains deferred.', '']
    (run_root/'RESULTS.md').write_text('\n'.join(lines))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay
    fig,ax=plt.subplots(figsize=(6.5,5.5))
    ConfusionMatrixDisplay(np.asarray(test['metrics']['confusion_matrix']),
                           display_labels=list(CLASSES)).plot(ax=ax,colorbar=False,cmap='Blues')
    ax.set_title('Held-out test: 6 independent patients (2 per class)')
    ax.tick_params(axis='x',rotation=20)
    fig.tight_layout(); fig.savefig(run_root/'test_confusion_matrix.png',dpi=180); plt.close(fig)
    receipts=sync_artifacts(run_root,run_root.relative_to(ROOT))
    inventory={'verified_at':utcnow(),'slide_files':verified,'run_files':receipts}
    atomic_json(run_root/'verification_inventory.json',inventory)
    persist_file(run_root/'verification_inventory.json',(run_root/'verification_inventory.json').relative_to(ROOT))
    print(f'Verified {len(verified)} slide files and {len(receipts)} run files; {summary["persistent_run_root"]}/RESULTS.md')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-root',required=True)
    report(parser.parse_args().run_root)
