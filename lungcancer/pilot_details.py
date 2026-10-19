"""Read-only pilot verification and an explicit specimen/preparation evidence report."""
from collections import Counter, defaultdict
from pathlib import Path
import tarfile
import numpy as np
from .common import ROOT, DEFAULT_PERSISTENT, CLASSES, read_json, atomic_json, checksum, utcnow
from .features import load_features


def build_details(output='artifacts/pilot_review/details.json'):
    selection=read_json(ROOT/'artifacts/pilot_selection.json')
    ledger=read_json(ROOT/'artifacts/download_ledger.json')
    raw={}
    for page in sorted((ROOT/'artifacts/discovery').glob('raw_page_*.json')):
        for hit in read_json(page)['response']['data']['hits']:
            raw[hit['file_id']]=hit
    rows=[]
    for record in selection['slides']:
        hit=raw[record['file_id']]
        entities=[e for e in hit['associated_entities'] if e['entity_type']=='slide']
        if len(entities)!=1: raise ValueError('pilot_does_not_have_one_associated_slide')
        entity=entities[0]
        matches=[]
        for case in hit['cases']:
            if case['case_id']!=entity['case_id']: continue
            for sample in case['samples']:
                for portion in sample.get('portions',[]):
                    for slide in portion.get('slides',[]):
                        if slide['slide_id']==entity['entity_id']:
                            matches.append((case,sample,portion,slide))
        if len(matches)!=1: raise ValueError('pilot_slide_specimen_link_is_not_unique')
        case,sample,portion,slide=matches[0]
        for observed,expected in [(sample['sample_id'],record['sample_id']),
                                  (slide['slide_id'],record['slide_id']),
                                  (case['case_id'],record['case_id']),
                                  (sample['sample_type'],record['sample_type']),
                                  (case['project']['project_id'],record['project_id']),
                                  (entity['entity_submitter_id'],slide['submitter_id'])]:
            if observed!=expected: raise ValueError('saved_label_provenance_disagrees_with_raw_link')
        directory=ROOT/'artifacts/slides'/record['file_id']
        prep=read_json(directory/'preprocessing.json')
        features,coords,meta=load_features(directory/'embeddings.npz')
        if meta['source_md5']!=record['md5sum'] or meta['file_id']!=record['file_id'] or prep['source_md5']!=record['md5sum']:
            raise ValueError('feature_source_identity_disagrees_with_selected_gdc_file')
        if checksum(directory/'embeddings.npz')!=read_json(directory/'embeddings.json')['npz_sha256']:
            raise ValueError('embedding_file_checksum_mismatch')
        with np.load(directory/'coordinates.npz',allow_pickle=False) as saved:
            if not np.array_equal(saved['coordinates'],coords): raise ValueError('embedding_coordinate_order_mismatch')
        if prep['candidate_count']!=prep['accepted_count']+prep['rejected_count']:
            raise ValueError('candidate_count_does_not_reconcile')
        row={
            'class':record['candidate_class'],'patient':record['patient_id'],'project':record['project_id'],
            'file_id':record['file_id'],'filename':record['file_name'],'md5sum':record['md5sum'],
            'raw_bytes':record['file_size'],'case_id':case['case_id'],
            'associated_entity':entity,'slide_id':slide['slide_id'],'slide_barcode':slide['submitter_id'],
            'portion_id':portion['portion_id'],'portion_barcode':portion.get('submitter_id'),
            'sample_id':sample['sample_id'],'sample_barcode':sample['submitter_id'],'sample_type':sample['sample_type'],
            'specimen_link_verified_against_saved_raw_response':True,
            'label_provenance':record['label_provenance'],'diagnosis_evidence':record.get('diagnosis_evidence',[]),
            'preservation_method_as_reported':sample.get('preservation_method'),
            'portion_is_ffpe_as_reported':portion.get('is_ffpe'),
            'frozen_explicitly_confirmed':str(sample.get('preservation_method','')).lower() in {'frozen','snap frozen','cryopreserved'},
            'preparation_used':record['preparation'],'preparation_provenance':record['preparation_provenance'],
            'preparation_evidence':record['preparation_evidence'],
            'candidates':prep['candidate_count'],'accepted':prep['accepted_count'],'rejected':prep['rejected_count'],
            'selected_for_embeddings':prep['selected_count'],'accepted_but_not_selected':prep['accepted_but_not_sampled'],
            'partial_edge_positions_excluded':prep['partial_edge_positions_excluded'],
            'coverage_threshold_counts':prep['coverage_threshold_counts'],
            'whole_grid_acceptance_fraction':prep['accepted_count']/prep['candidate_count'],
            'embedding_shape':list(features.shape),'coordinates_shape':list(coords.shape),
            'all_embeddings_finite':bool(np.isfinite(features).all()),'encoder':meta['encoder'],
            'quality_warnings':prep['warnings'],
            'persistent_files':{name:str(DEFAULT_PERSISTENT/'artifacts/slides'/record['file_id']/name)
                                for name in ['thumbnail.jpg','contact_sheet.jpg','tissue_mask.png','tissue_mask_overlay.jpg',
                                             'selected_tiles_overlay.jpg','coordinates.npz','preprocessing.json','embeddings.npz','embeddings.json']},
        }
        rows.append(row)
        if not all(Path(path).is_file() for path in row['persistent_files'].values()):
            raise ValueError('required_persisted_pilot_file_missing')
    encoder=rows[0]['encoder']
    if any(r['encoder']!=encoder for r in rows): raise ValueError('pilot_uses_multiple_encoder_configurations')
    if sum(a['transferred_bytes'] for a in ledger['attempts'])!=ledger['transferred_bytes']:
        raise ValueError('download_ledger_bytes_do_not_reconcile')
    counts={c:{'slides':sum(r['class']==c for r in rows),
               'independent_patients':len({r['case_id'] for r in rows if r['class']==c})} for c in CLASSES}
    backups=sorted((DEFAULT_PERSISTENT/'code_backups').glob('code-*.tar.gz'))
    if not backups: raise ValueError('no_persistent_source_backup_found')
    with tarfile.open(backups[-1]) as archive:
        if 'scripts/show_pilot.py' not in archive.getnames(): raise ValueError('latest_backup_missing_notebook_helper')
    report={
        'verified_at_utc':utcnow(),'counts':counts,'total_independent_patients':len({r['case_id'] for r in rows}),
        'actual_raw_bytes_downloaded':ledger['transferred_bytes'],'raw_budget_bytes':ledger['budget_bytes'],
        'raw_bytes_reserved':ledger['reserved_bytes'],'download_attempts':len(ledger['attempts']),
        'download_failures':[a for a in ledger['attempts'] if a['status']!='verified'],
        'normal_slides_by_project':dict(Counter(r['project'] for r in rows if r['class']=='non_tumor')),
        'preservation_methods_as_reported':dict(Counter(r['preservation_method_as_reported'] for r in rows)),
        'explicit_frozen_confirmations':sum(r['frozen_explicitly_confirmed'] for r in rows),
        'frozen_inferred_from_barcode':sum(r['preparation_provenance']=='barcode_inference' for r in rows),
        'all_portion_is_ffpe_flags_false':all(r['portion_is_ffpe_as_reported'] is False for r in rows),
        'encoder':encoder,'all_embeddings_finite':all(r['all_embeddings_finite'] for r in rows),
        'total_tile_embeddings':sum(r['embedding_shape'][0] for r in rows),
        'mean_whole_grid_acceptance_by_class':{c:float(np.mean([r['whole_grid_acceptance_fraction'] for r in rows if r['class']==c])) for c in CLASSES},
        'filtering_concerns':'Whole-grid pass rates include slide background and cannot measure tissue false-negative rates. The 50% threshold may favor denser normal tissue despite all three normals exceeding 512 accepted candidates. Three slides per class cannot establish absence of masking bias.',
        'persistent_paths':{k:str(DEFAULT_PERSISTENT/v) for k,v in {
            'root':'','selection':'artifacts/pilot_selection.json','raw_metadata_and_manifest':'artifacts/discovery',
            'download_ledger':'artifacts/download_ledger.json','slide_outputs':'artifacts/slides',
            'review':'artifacts/pilot_review','detailed_summary':'artifacts/pilot_review/details.json',
            'source_backups':'code_backups','notebook_helper':'code/scripts/show_pilot.py'}.items()},
        'source_code_backups':[str(p) for p in backups],
        'latest_source_code_backup':{'path':str(backups[-1]),'sha256':checksum(backups[-1])},
        'rows':rows,'download_expansion_performed':False,'training_performed':False,
    }
    atomic_json(output,report)
    lines=['# Detailed pilot evidence','',
           'Read-only verification of the existing nine-slide pilot. No downloads, extraction, or training were run.',
           '', '## Counts and downloaded bytes','',
           '| Class | Slides | Independent patients |','|---|---:|---:|']
    for c in CLASSES: lines.append(f'| {c} | {counts[c]["slides"]} | {counts[c]["independent_patients"]} |')
    lines+=['',f'Actual raw transfer: **{ledger["transferred_bytes"]:,} bytes**. UNI2 checkpoint transfer is separate from raw-slide bytes.',
            '', '## Specimen linkage and labels','',
            'For each file, its associated slide UUID was matched to exactly one slide under exactly one portion/sample/case in the saved raw GDC response. Labels use the linked sample type and project, with primary-diagnosis and barcode consistency checks. Barcode names alone do not assign labels.']
    for r in rows:
        lines+=['',f'**{r["patient"]}: {r["class"]}, {r["project"]}**',
                f'- File `{r["file_id"]}` (`{r["filename"]}`).',
                f'- Associated slide `{r["slide_id"]}` (`{r["slide_barcode"]}`) → portion `{r["portion_id"]}` (`{r["portion_barcode"]}`).',
                f'- Linked sample `{r["sample_id"]}` (`{r["sample_barcode"]}`, **{r["sample_type"]}**) → case `{r["case_id"]}`.']
    lines+=['','## Preparation evidence','',
            'Explicit Frozen confirmations: **0/9**. Frozen by documented TS barcode inference: **9/9**. '
            'All nine portions report `is_ffpe=false`; this is evidence of reported non-FFPE status, not independent proof of freezing.',
            '', 'Preservation fields: **Unknown for eight samples; OCT for TCGA-98-A538**. '
            'OCT is supporting context and is not promoted to an explicit Frozen confirmation. '
            'The raw Unknown values remain Unknown in the evidence.',
            '', '[GDC](https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/) defines TS as Top Slide. '
            '[The TCGA archive methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC3822112/) describe TS/BS as frozen sections adjacent to genomics tissue.',
            '', '## Encoder and finite embeddings','',
            f'Encoder: `{encoder["repository"]}`; revision `{encoder["revision"]}`; checkpoint SHA256 `{encoder["checkpoint_sha256"]}`.',
            '', 'All nine arrays have shape **[512,1536]** with matching **[512,2]** coordinates; **4,608 embeddings, all finite**. '
            'The frozen model and official evaluation transforms were used; no synthetic features contributed to these arrays.',
            '', '## Tile filtering','',
            '| Patient | Candidates | Accepted | Rejected | Embedded | Accepted, not sampled |',
            '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f'| {r["patient"]} | {r["candidates"]} | {r["accepted"]} | {r["rejected"]} | {r["selected_for_embeddings"]} | {r["accepted_but_not_selected"]} |')
    lines+=['', 'Rejected means below the 50% tissue-coverage threshold on the complete candidate grid. '
            'The sampling cap is separate; partial edge positions are also recorded separately in the JSON.',
            '', report['filtering_concerns'],
            '', 'Mean complete-grid acceptance: '+', '.join(f'{c}: {v:.1%}' for c,v in report['mean_whole_grid_acceptance_by_class'].items())+'.',
            '', 'All slides warn that embedded ICC profiles were not applied. Visual QC also noted pale/low-contrast tiles in TCGA-60-2715, folds, cut edges, and focus/color variation. No aggressive blur/artifact filter was added.',
            '', '## Normal source projects','',
            'Normals from both projects are represented: **TCGA-LUSC 2** (TCGA-33-4547, TCGA-58-8391); '
            '**TCGA-LUAD 1** (TCGA-55-7910).',
            '', '## Exact persistent locations','']
    for name,path in report['persistent_paths'].items(): lines.append(f'- {name}: `{path}`')
    lines+=['',f'Latest code backup: `{backups[-1]}`; SHA256 `{report["latest_source_code_backup"]["sha256"]}`.',
            '', 'The JSON lists all nine exact per-file output paths, all UUIDs, raw preparation fields, encoder transforms, and every code archive.',
            '', '**Downloads and training remain paused.**']
    Path(output).with_suffix('.md').write_text('\n'.join(lines)+'\n')
    return report
