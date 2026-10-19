"""Generate the pilot review artifact; no downloads, fitting, or predictions."""
from collections import Counter,defaultdict
import importlib.metadata
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from .common import CLASSES,read_json,atomic_json,checksum,utcnow
from .features import load_features


def make_review(output='artifacts/pilot_review'):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    results=read_json('artifacts/pilot_results.json')
    selection=read_json('artifacts/pilot_selection.json')
    preservation_values=Counter(
        next((e['value'] for e in r['preparation_evidence']
              if e.get('field')=='cases.samples.preservation_method'), 'Missing')
        for r in selection['slides'])
    audit=read_json('artifacts/discovery/audit.json')
    manifest=read_json('artifacts/discovery/manifest.json')
    ledger=read_json('artifacts/download_ledger.json')
    summaries=[]; by_class=defaultdict(list)
    for result in results['slides']:
        record=next(x for x in selection['slides'] if x['file_id']==result['file_id'])
        if result['status']!='success':
            summaries.append(result); continue
        directory=Path('artifacts/slides')/result['file_id']
        prep=read_json(directory/'preprocessing.json')
        features,coordinates,meta=load_features(directory/'embeddings.npz')
        features_meta=read_json(directory/'embeddings.json')
        if checksum(directory/'embeddings.npz')!=features_meta['npz_sha256']:
            raise ValueError('review_embedding_checksum_failed')
        if not np.array_equal(coordinates,np.load(directory/'coordinates.npz',allow_pickle=False)['coordinates']):
            raise ValueError('review_coordinate_alignment_failed')
        for receipt in result['persistent_receipts']:
            if checksum(receipt['path'])!=receipt['sha256']: raise ValueError('review_persistence_receipt_failed')
        summary={'file_id':record['file_id'],'patient_id':record['patient_id'],'class':record['candidate_class'],
                 'source_site':record['source_site'],'raw_bytes':record['file_size'],'source_md5':record['md5sum'],
                 'preparation':record['preparation'],'preparation_provenance':record['preparation_provenance'],
                 'status':'success','shape':list(features.shape),'all_finite':bool(np.isfinite(features).all()),
                 'candidates':prep['candidate_count'],'accepted':prep['accepted_count'],'selected':prep['selected_count'],
                 'grid_acceptance_fraction':prep['accepted_count']/prep['candidate_count'],
                 'coverage_threshold_counts':prep['coverage_threshold_counts'],
                 'actual_mpp':prep['geometry']['actual_output_mpp'],'quality_warnings':prep['warnings'],
                 'elapsed_seconds':result['elapsed_seconds'],'audit_directory':str(directory)}
        summaries.append(summary); by_class[summary['class']].append(summary)
    for cls,group in by_class.items():
        width=1920; rowheight=410
        canvas=Image.new('RGB',(width,rowheight*len(group)),'white'); draw=ImageDraw.Draw(canvas)
        for index,s in enumerate(group):
            y=index*rowheight
            draw.text((8,y+4),f'{cls} | {s["patient_id"]} | {s["file_id"]} | tiles={s["selected"]}',fill='black')
            for j,(filename,label) in enumerate([('thumbnail.jpg','thumbnail'),('tissue_mask_overlay.jpg','tissue mask'),
                                                ('selected_tiles_overlay.jpg','analyzed tile locations'),('contact_sheet.jpg','representative tiles')]):
                im=Image.open(Path(s['audit_directory'])/filename).convert('RGB'); im.thumbnail((472,360))
                x=j*480; draw.text((x+8,y+24),label,fill='black'); canvas.paste(im,(x+4,y+45))
        canvas.save(output/f'{cls}_audit.jpg',quality=92)
    success=[s for s in summaries if s['status']=='success']
    elapsed=[s['elapsed_seconds'] for s in success]
    resource_estimates={}
    for n in [30,50]:
        raw=sum(float(np.median([r['file_size'] for r in manifest if r['decision']=='include' and r['preparation']=='frozen' and r['candidate_class']==c]))*n for c in CLASSES)
        local_derived=sum(p.stat().st_size for s in success for p in Path(s['audit_directory']).iterdir() if p.is_file())
        resource_estimates[str(n)+'_patients_per_class']={
            'slides_if_one_per_patient_per_class':n*3,
            'raw_GB_using_class_median_sizes':raw/1e9,
            'serial_processing_hours_at_observed_median':float(np.median(elapsed))*n*3/3600,
            'derived_GB_at_observed_mean':local_derived/max(1,len(success))*n*3/1e9,
            'notes':'Estimates, not a new cohort selection or download authorization. Patient classes can overlap.'}
    report={'created_at':utcnow(),'status':results['status'],'slides':summaries,
            'raw_transferred_bytes':ledger['transferred_bytes'],'raw_reserved_bytes':ledger['reserved_bytes'],
            'download_failures':[x for x in ledger['attempts'] if x['status']=='failed'],
            'successful_slides':len(success),'real_tissue_tile_embeddings':sum(s['selected'] for s in success),
            'counts':{c:{'slides':len(by_class[c]),'patients':len({r['patient_id'] for r in by_class[c]})} for c in CLASSES},
            'mean_grid_acceptance_by_class':{c:float(np.mean([s['grid_acceptance_fraction'] for s in by_class[c]])) for c in CLASSES},
            'resources':resource_estimates,
            'versions':{p:importlib.metadata.version(p) for p in ['torch','torchvision','timm','huggingface-hub','openslide-python','openslide-bin','numpy','scipy','scikit-learn','Pillow','requests','pytest']},
            'remaining_stages':'Pilot review; approved preparation-matched modeling cohort; fixed grouped splits; real-data training, validation, test evaluation, and renamed held-out slide inference.'}
    notes={'scope':'Visual engineering QC only; no independent histology relabeling.',
           'all_slides':'Masks follow major tissue fragments; no threshold change made after inspection.',
           'non_tumor':'Visible airspaces are retained. All three slides have over 512 accepted candidates.',
           '90c06ba4-30bf-49d5-a84b-ddc213de048d':'Several representative tiles are pale or low contrast; inspect the full contact sheet before finalizing quality handling.',
           'caution':'Folds, cut edges, and variation in focus/color are present. No automatic blur/artifact exclusion introduced.'}
    atomic_json(output/'visual_audit_notes.json',notes)
    report['visual_audit_notes']=notes
    import xml.etree.ElementTree as ET
    suite=ET.parse('artifacts/unit_tests.xml').getroot().find('testsuite')
    report['unit_tests']={k:suite.attrib[k] for k in ['tests','errors','failures','skipped','time']}
    atomic_json(output/'summary.json',report)
    rows=['# Pilot review checkpoint','',f'Generated {report["created_at"]}.',
          '',f'Executed: {len(success)}/{len(selection["slides"])} real slides; {report["real_tissue_tile_embeddings"]:,} real tile embeddings. '
          f'Raw transfer: {ledger["transferred_bytes"]/1e9:.3f} GB of the 10 GB budget.',
          '', '## Label and preparation audit','',
          'All labels follow the specimen actually linked to the file. Patient diagnosis alone does not label a normal specimen as tumor. '
          'Primary diagnosis conflicts and preparation conflicts are excluded. Barcode sample codes are consistency checks.',
          '', '| Class | Eligible slides | Independent patients | Frozen slides | FFPE slides |',
          '|---|---:|---:|---:|---:|']
    for c in CLASSES:
        a=audit['class_counts'][c]; prep=audit['by_preparation'][c]
        rows.append(f'| {c} | {a["slides"]} | {a["patients"]} | {prep.get("frozen",0)} | {prep.get("ffpe",0)} |')
    rows+=['',f'{audit["excluded"]} exclusions: '+', '.join(f'{k}: {v}' for k,v in audit['exclusion_reasons'].items())+'.',
           '', 'Normal slides are exclusively frozen in this eligible discovery cohort. The pilot uses frozen slides for every class. '
           'For all pilot slides, frozen preparation is inferred from TS/BS slide barcodes and documented TCGA acquisition; '
           'preservation_method values are '+', '.join(f'{k}: {v}' for k,v in preservation_values.items())+'. '
           'False is_ffpe flags support non-FFPE status, not proof of freezing. No pilot sample has an explicit Frozen value; '
           'all nine remain classified as inferred, including the OCT sample TCGA-98-A538.',
           '', 'References: [GDC barcode documentation](https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/) and '
           '[the original TCGA slide archive methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC3822112/).',
           '', 'The full source-site, missing-metadata, repeated-ID, and checksum audit is in '
           '[audit.json](../discovery/audit.json). Source-site differences remain and need reporting in the larger cohort.',
           '', '## Real slide outputs','',
           '| Class | Patient | File UUID | Grid / accepted / selected | Actual MPP X/Y | Images |',
           '|---|---|---|---:|---|---|']
    for s in success:
        base=f'../slides/{s["file_id"]}'
        images=f'[tiles]({base}/contact_sheet.jpg), [mask]({base}/tissue_mask_overlay.jpg), [locations]({base}/selected_tiles_overlay.jpg)'
        rows.append(f'| {s["class"]} | {s["patient_id"]} | {s["file_id"]} | {s["candidates"]} / {s["accepted"]} / {s["selected"]} | '
                    f'{s["actual_mpp"][0]:.4f}/{s["actual_mpp"][1]:.4f} | {images} |')
    rows+=['','Coordinate arrays are level-0 upper-left X,Y pixels. Each NPZ contains finite embeddings and coordinates in identical order. '
           'The location overlay only shows analyzed tile positions.',
           '', '## Masking and quality','',
           'HSV color thresholding, one small morphological closing, and removal of tiny components retain airspaces. '
           'The initial 50% tissue threshold was kept for this pilot. No stain normalization, blur rejection, or artifact classifier was applied.',
           '', 'Mean grid acceptance fractions: '+', '.join(f'{c}: {v:.1%}' for c,v in report['mean_grid_acceptance_by_class'].items())+'. '
           'These three-slide groups cannot establish absence of masking bias; threshold counts at 0.10/0.25/0.50/0.75 are saved for every slide.',
           '', 'Quality warnings: embedded ICC profiles were present and not applied. RGB conversion and white alpha compositing were consistent. '
           'Inspect the full contact sheets for focus, folds, ink, and sparse tissue before approving preprocessing.',
           '', 'Visual inspection found pale/low-contrast tiles in TCGA-60-2715, plus folds, cut edges, and focus/color variation. '
           'See [visual audit notes](visual_audit_notes.json). No independent histology relabeling or automatic exclusion was performed.',
           '', '## Estimated next-cohort resources','',
           '| Patients per class | Slides | Raw GB, class-median estimate | Hours, observed median | Derived GB |',
           '|---:|---:|---:|---:|---:|']
    for n,e in resource_estimates.items():
        rows.append(f'| {n.split("_")[0]} | {e["slides_if_one_per_patient_per_class"]} | {e["raw_GB_using_class_median_sizes"]:.1f} | '
                    f'{e["serial_processing_hours_at_observed_median"]:.1f} | {e["derived_GB_at_observed_mean"]:.2f} |')
    rows+=['','UNI2-h uses a pinned 2.73 GB checkpoint cached locally. Raw slides can be processed serially and deleted after verified persistence, '
           'so local raw storage need not equal cumulative transfer. Estimates exclude network stalls and retries.',
           '', '## Execution boundary','',
           'Implemented and unit-tested: grouped splitting, mean pooling, training-only scaling, small validation search, '
           'multinomial logistic regression, baseline comparison, metrics, and filename-independent prediction.',
           '', 'Not executed on real data: training, validation/test evaluation, or held-out slide inference. '
           'The synthetic inference unit test is not evidence of real-data performance. No accuracy is reported for this pilot. '
           'Pilot patients must remain in training/development because their images were inspected.',
           '', 'Downloads and modeling remain paused for pilot review.']
    (output/'README.md').write_text('\n'.join(rows)+'\n')
    return report
