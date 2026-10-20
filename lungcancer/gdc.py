"""Live GDC discovery and conservative specimen-to-file label auditing."""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .common import atomic_json, read_json, fingerprint, utcnow, CLASSES

API = 'https://api.gdc.cancer.gov'
BARCODE_DOC = 'https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/'
PREPARATION_DOC = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3822112/'
SAMPLE_DOC = 'https://gdc.cancer.gov/resources-tcga-users/tcga-code-tables/sample-type-codes'
BARCODE = re.compile(r'^(TCGA-[A-Z0-9]{2}-[A-Z0-9]{4})-(\d{2})([A-Z])(?:-(\d{2})-([A-Z]{2}[A-Z0-9]+))?$', re.I)


def session():
    s = requests.Session()
    s.mount('https://', HTTPAdapter(max_retries=Retry(total=4, backoff_factor=1,
        status_forcelist=[429,500,502,503,504], allowed_methods=['GET','POST'])))
    return s


def barcode_parts(barcode):
    match = BARCODE.match(barcode or '')
    if not match:
        return None
    patient, code, vial, portion, slide = match.groups()
    return {'patient':patient.upper(), 'sample_code':code, 'vial':vial.upper(),
            'portion':portion, 'slide_category':slide[:2].upper() if slide else None}


def identity_match(entity, node, id_field):
    """UUID determines identity; supplied barcode must agree when available."""
    eid = entity.get('entity_id')
    barcode = entity.get('entity_submitter_id')
    if eid:
        return eid == node.get(id_field) and (not barcode or not node.get('submitter_id') or barcode == node['submitter_id'])
    return bool(barcode and barcode == node.get('submitter_id'))


def unique_specimen_links(links):
    """Keep full UUID hierarchy; do not silently collapse distinct portions.

    Actual UUID relationships determine the specimen. Display-barcode portion
    numbers may differ in legacy metadata and cannot resolve ambiguous UUIDs.
    """
    unique={}
    for link in links:
        case,sample,portion,slide,entity=link
        key=(case.get('case_id'),sample.get('sample_id'),
             portion.get('portion_id') if portion else None,slide.get('slide_id') if slide else None)
        unique[key]=link
    return list(unique.values()),[]


def diagnosis_audit(case, project):
    diagnoses = case.get('diagnoses', [])
    relevant = [d for d in diagnoses if d.get('diagnosis_is_primary_disease') is True]
    if not relevant:
        relevant = [d for d in diagnoses if d.get('diagnosis_is_primary_disease') is not False
                    and str(d.get('classification_of_tumor','')).lower() == 'primary']
    if not relevant:
        return [], ['primary_diagnosis_missing_or_unidentified'], []
    expected = 'adenocarcinoma' if project == 'TCGA-LUAD' else 'squamous'
    evidence, conflicts, warnings = [], [], []
    for d in relevant:
        name = str(d.get('primary_diagnosis') or '')
        morphology = str(d.get('morphology') or '')
        origin = str(d.get('tissue_or_organ_of_origin') or '')
        evidence.append({k:d.get(k) for k in ('diagnosis_id','primary_diagnosis','morphology',
                         'tissue_or_organ_of_origin','diagnosis_is_primary_disease','classification_of_tumor')})
        text = name.lower()
        try:
            code = int(morphology.split('/')[0])
        except ValueError:
            code = None
        adeno_codes = {8140,8211,8230,8260,8310,8480,8481,8490,8550,*range(8250,8258),*range(8570,8577)}
        squamous_codes = {8050,8051,8052,8083,8084,*range(8070,8077)}
        compatible = ('adenocarcinoma' in text or code in adeno_codes) if expected == 'adenocarcinoma' else ('squamous' in text or code in squamous_codes)
        unknown = text in {'', 'not reported', 'unknown', 'not available'} and code is None
        if unknown:
            warnings.append('primary_histology_unreported')
        elif not compatible or 'adenosquamous' in text:
            conflicts.append('primary_diagnosis_conflicts_with_project_or_is_ambiguous')
        if code in squamous_codes and expected=='adenocarcinoma' or code in adeno_codes and expected=='squamous':
            conflicts.append('primary_diagnosis_conflicts_with_project_or_is_ambiguous')
        if expected=='adenocarcinoma' and 'squamous' in text or expected=='squamous' and 'adenocarcinoma' in text:
            conflicts.append('primary_diagnosis_conflicts_with_project_or_is_ambiguous')
        if origin.lower() not in {'', 'not reported', 'unknown'} and not any(t in origin.lower() for t in ['lung','bronch','lobe']):
            conflicts.append('primary_diagnosis_not_lung')
    return sorted(set(conflicts)), sorted(set(warnings)), evidence


def preparation_audit(sample, portion, slide_barcode, strategy):
    evidence = []
    known = []
    preservation = sample.get('preservation_method')
    if preservation:
        evidence.append({'field':'cases.samples.preservation_method','value':preservation})
        text = str(preservation).lower()
        if 'frozen' in text:
            known.append('frozen')
        elif 'ffpe' in text or 'paraffin' in text:
            known.append('ffpe')
    ffpe = portion.get('is_ffpe') if portion else None
    if ffpe is not None:
        evidence.append({'field':'cases.samples.portions.is_ffpe','value':ffpe})
        if ffpe is True:
            known.append('ffpe')
    parts = barcode_parts(slide_barcode)
    inferred = None
    if parts and parts['slide_category'] in {'TS','BS','MS'}:
        inferred = 'frozen'
    elif parts and parts['slide_category'] == 'DX':
        inferred = 'ffpe'
    if inferred:
        evidence.append({'field':'linked_slide_barcode_category','value':parts['slide_category'],
                         'inference':inferred,'references':[BARCODE_DOC,PREPARATION_DOC]})
    if (known and (len(set(known)) > 1 or inferred and inferred not in known)) or (ffpe is False and (inferred=='ffpe' or 'ffpe' in known)):
        return 'unknown', 'conflicting', evidence, ['preparation_metadata_conflict']
    if known:
        return known[0], 'explicit_metadata', evidence, []
    if inferred:
        return inferred, 'barcode_inference', evidence, []
    return 'unknown', 'unknown', evidence, []


def normalize_file(hit):
    row = {k:hit.get(k) for k in ('file_id','file_name','file_size','md5sum','access','experimental_strategy','state')}
    row['file_id'] = row['file_id'] or hit.get('id')
    row.update(case_id=None, patient_id=None, project_id=None, slide_id=None, slide_barcode=None,
               sample_id=None, sample_barcode=None, sample_type=None, source_site=None,
               preparation='unknown', preparation_provenance='unknown', preparation_evidence=[],
               candidate_class=None, label_provenance=None, decision='exclude', reasons=[], warnings=[])
    row['associated_entities'] = hit.get('associated_entities', [])
    links = []
    unresolved=[]
    for entity in row['associated_entities']:
        before=len(links)
        for case in hit.get('cases', []):
            if entity.get('case_id') and entity['case_id'] != case.get('case_id'):
                continue
            for sample in case.get('samples', []):
                kind = entity.get('entity_type')
                if kind == 'sample' and identity_match(entity,sample,'sample_id'):
                    links.append((case,sample,None,None,entity))
                for portion in sample.get('portions', []):
                    if kind == 'portion' and identity_match(entity,portion,'portion_id'):
                        links.append((case,sample,portion,None,entity))
                    for slide in portion.get('slides', []):
                        if kind == 'slide' and identity_match(entity,slide,'slide_id'):
                            links.append((case,sample,portion,slide,entity))
        if len(links)==before and entity.get('entity_type') in {'slide','sample','portion'}:
            unresolved.append(entity)
    if unresolved:
        row['reasons'].append('unresolved_or_conflicting_associated_specimen')
        return row
    candidates,link_warnings=unique_specimen_links(links)
    row['warnings'].extend(link_warnings)
    if len(candidates) != 1:
        row['reasons'].append('ambiguous_specimen_links' if len(candidates)>1 else 'unresolved_associated_specimen')
        return row
    case,sample,portion,slide,entity = candidates[0]
    slide_barcode = slide.get('submitter_id') if slide else hit.get('file_name','').split('.')[0]
    if (slide and portion and slide.get('submitter_id') and portion.get('submitter_id') and
            slide['submitter_id'].rsplit('-',1)[0]!=portion['submitter_id']):
        row['warnings'].append('linked_slide_portion_display_barcodes_differ; UUID_link_is_authoritative')
    row.update(case_id=case.get('case_id'),patient_id=case.get('submitter_id'),
               project_id=case.get('project',{}).get('project_id'),
               slide_id=slide.get('slide_id') if slide else None, slide_barcode=slide_barcode,
               slide_id_provenance='linked_slide_entity' if slide else 'no_slide_entity_in_gdc_sample_or_portion_link',
               sample_id=sample.get('sample_id'),sample_barcode=sample.get('submitter_id'),
               sample_type=sample.get('sample_type'),source_site=case.get('tissue_source_site',{}).get('code'))
    row['source_site_name'] = case.get('tissue_source_site',{}).get('name')
    if not row['patient_id'] or not row['case_id'] or not row['sample_id']:
        row['reasons'].append('required_patient_or_specimen_id_missing')
    if row['sample_type'] == 'Solid Tissue Normal':
        row['candidate_class'] = 'non_tumor'
    elif row['sample_type'] == 'Primary Tumor' and row['project_id'] in {'TCGA-LUAD','TCGA-LUSC'}:
        row['candidate_class'] = {'TCGA-LUAD':'adenocarcinoma','TCGA-LUSC':'squamous'}[row['project_id']]
    else:
        row['reasons'].append('sample_type_or_project_outside_task')
    row['label_provenance'] = {'mapping':'associated_entities -> unique nested specimen -> sample_type + project',
                               'associated_entity':entity, 'sample_type':row['sample_type'],
                               'project_id':row['project_id'], 'sample_type_codes_reference':SAMPLE_DOC}
    expected_code = {'Solid Tissue Normal':'11','Primary Tumor':'01'}.get(row['sample_type'])
    for name,value in [('slide',slide_barcode),('sample',row['sample_barcode']),('filename',hit.get('file_name','').split('.')[0])]:
        parsed = barcode_parts(value)
        if not parsed:
            row['warnings'].append(f'{name}_barcode_unparseable')
        elif parsed['patient'] != row['patient_id'] or expected_code and parsed['sample_code'] != expected_code:
            row['reasons'].append(f'{name}_barcode_patient_or_sample_type_conflict')
    if slide and entity.get('entity_submitter_id') and entity['entity_submitter_id'] != slide_barcode:
        row['reasons'].append('slide_uuid_barcode_conflict')
    conflicts,warnings,evidence = diagnosis_audit(case,row['project_id'])
    row['reasons'].extend(conflicts); row['warnings'].extend(warnings); row['diagnosis_evidence'] = evidence
    prep,provenance,evidence,conflicts = preparation_audit(sample,portion,slide_barcode,hit.get('experimental_strategy'))
    row.update(preparation=prep,preparation_provenance=provenance,preparation_evidence=evidence)
    row['reasons'].extend(conflicts)
    if prep == 'unknown':
        row['warnings'].append('preparation_unknown')
    annotations = [*hit.get('annotations',[]),*case.get('annotations',[]),*sample.get('annotations',[])]
    if portion:
        annotations += portion.get('annotations',[])
    if slide:
        annotations += slide.get('annotations',[])
    row['annotations'] = annotations
    if any(str(a.get('classification','')).lower() == 'redaction' for a in annotations):
        row['reasons'].append('gdc_redaction_annotation')
    if hit.get('access') != 'open':
        row['reasons'].append('not_open_access')
    if not row['md5sum'] or not row['file_size']:
        row['reasons'].append('checksum_or_size_missing')
    row['reasons'] = sorted(set(row['reasons']))
    row['warnings'] = sorted(set(row['warnings']))
    if not row['reasons'] and row['candidate_class']:
        row['decision'] = 'include'
    return row


def write_manifest(path, rows):
    atomic_json(path, rows)
    with Path(path).with_suffix('.csv').open('w',newline='') as stream:
        columns = list(dict.fromkeys(k for row in rows for k in row))
        writer = csv.DictWriter(stream,fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in row.items()})


def audit(rows):
    included = [r for r in rows if r['decision'] == 'include']
    summary = {'total_files':len(rows),'included':len(included),'excluded':len(rows)-len(included),
               'class_counts':{},'by_preparation':{},'by_site':{},'missing_metadata':{},
               'exclusion_reasons':dict(Counter(x for r in rows for x in r['reasons'])),
               'warnings':dict(Counter(x for r in rows for x in r['warnings']))}
    for cls in CLASSES:
        group = [r for r in included if r['candidate_class']==cls]
        summary['class_counts'][cls] = {'slides':len(group),'patients':len({r['case_id'] for r in group})}
        summary['by_preparation'][cls] = dict(Counter(r['preparation'] for r in group))
        summary['by_site'][cls] = dict(Counter(r['source_site'] or 'unknown' for r in group))
    for key in ['case_id','patient_id','sample_id','sample_type','slide_id','source_site']:
        summary['missing_metadata'][key] = sum(not r.get(key) for r in rows)
    summary['missing_metadata']['preparation'] = sum(r['preparation']=='unknown' for r in rows)
    for key in ['file_id','md5sum','file_name','slide_id']:
        groups = defaultdict(list)
        for r in rows:
            if r.get(key): groups[r[key]].append(r['file_id'])
        summary['duplicates_'+key] = {k:v for k,v in groups.items() if len(v)>1}
    summary['preparation_warning'] = 'Only a single known preparation is permitted for pilot selection; unknown is not treated as matched.'
    return summary


def refresh_audit(directory='artifacts/discovery'):
    """Re-normalize the saved exact API responses; never silently re-query data."""
    directory=Path(directory)
    raw=[]
    for page in sorted(directory.glob('raw_page_*.json')):
        raw.extend(read_json(page)['response']['data']['hits'])
    if not raw: raise ValueError('no_saved_raw_metadata_pages')
    rows=[normalize_file(h) for h in raw]
    write_manifest(directory/'manifest.json',rows)
    report=audit(rows)
    report['normalizer_sha256']=__import__('lungcancer.common',fromlist=['checksum']).checksum(__file__)
    atomic_json(directory/'audit.json',report)
    return report


def discover(output='artifacts/discovery'):
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    client = session()
    mapping = client.get(API+'/files/_mapping',timeout=(15,90)); mapping.raise_for_status()
    mapping = mapping.json(); atomic_json(output/'api_mapping.json',mapping)
    status = client.get(API+'/status',timeout=(15,90)); status.raise_for_status()
    atomic_json(output/'gdc_status.json',status.json())
    fields = ['file_id','file_name','file_size','md5sum','access','state','data_format','experimental_strategy',
              'associated_entities.entity_id','associated_entities.entity_type','associated_entities.entity_submitter_id','associated_entities.case_id',
              'cases.case_id','cases.submitter_id','cases.project.project_id','cases.tissue_source_site.code','cases.tissue_source_site.name',
              'cases.samples.sample_id','cases.samples.submitter_id','cases.samples.sample_type','cases.samples.preservation_method',
              'cases.samples.portions.portion_id','cases.samples.portions.submitter_id','cases.samples.portions.is_ffpe',
              'cases.samples.portions.slides.slide_id','cases.samples.portions.slides.submitter_id']
    fields += ['cases.diagnoses.'+k for k in ['diagnosis_id','primary_diagnosis','morphology','tissue_or_organ_of_origin',
                                           'diagnosis_is_primary_disease','classification_of_tumor']]
    for prefix in ['annotations','cases.annotations','cases.samples.annotations','cases.samples.portions.annotations','cases.samples.portions.slides.annotations']:
        fields += [prefix+'.'+k for k in ['annotation_id','classification','category','notes']]
    available = set(mapping['fields'])
    missing = sorted(set(fields)-available)
    fields = [f for f in fields if f in available]
    filters = {'op':'and','content':[
        {'op':'in','content':{'field':'cases.project.project_id','value':['TCGA-LUAD','TCGA-LUSC']}},
        {'op':'=','content':{'field':'data_format','value':'SVS'}},
        {'op':'=','content':{'field':'data_type','value':'Slide Image'}},
        {'op':'=','content':{'field':'access','value':'open'}}]}
    query = {'filters':filters,'fields':','.join(fields),'size':400,'sort':'file_id:asc','format':'JSON'}
    atomic_json(output/'query.json',{'endpoint':API+'/files','method':'POST','retrieved_at':utcnow(),
                                  'request':query,'requested_fields_unavailable':missing})
    hits=[]; offset=0
    while True:
        request={**query,'from':offset}
        response=client.post(API+'/files',json=request,timeout=(15,180)); response.raise_for_status()
        raw=response.json(); atomic_json(output/f'raw_page_{offset:05d}.json',{'retrieved_at':utcnow(),'request':request,'response':raw})
        if raw.get('warnings'):
            print('GDC query warnings:',raw['warnings'],flush=True)
        batch=raw['data']['hits']; hits.extend(batch)
        total=raw['data']['pagination']['total']
        print(f'Discovery {len(hits)}/{total}',flush=True)
        offset += len(batch)
        if offset>=total: break
        if not batch: raise RuntimeError('gdc_pagination_incomplete')
    rows=[normalize_file(h) for h in hits]
    write_manifest(output/'manifest.json',rows)
    report=audit(rows); atomic_json(output/'audit.json',report)
    print(json.dumps({k:report[k] for k in ['total_files','included','excluded','class_counts','by_preparation','exclusion_reasons']},indent=2),flush=True)
    return rows


def select_pilot(manifest, output='artifacts/pilot_selection.json', per_class=3, budget=10_000_000_000, seed=215):
    rows=read_json(manifest)
    valid=[r for r in rows if r['decision']=='include' and r['preparation']!='unknown']
    options=[]
    for prep in sorted({r['preparation'] for r in valid}):
        counts=[len({r['case_id'] for r in valid if r['preparation']==prep and r['candidate_class']==c}) for c in CLASSES]
        options.append((min(counts),sum(counts),prep))
    if not options or max(options)[0]==0: raise RuntimeError('no_preparation_shared_by_all_three_classes')
    prep=max(options)[2]
    pool=[r for r in valid if r['preparation']==prep]
    sites=[{r['source_site'] for r in pool if r['candidate_class']==c and r['source_site']} for c in CLASSES]
    shared_sites=set.intersection(*sites)
    chosen=[]; used_patients=set(); used_md5=set(); total=0
    for cycle in range(per_class):
        for cls in CLASSES:
            eligible=[r for r in pool if r['candidate_class']==cls and r['case_id'] not in used_patients and r['md5sum'] not in used_md5]
            used_sites={r['source_site'] for r in chosen if r['candidate_class']==cls}
            eligible.sort(key=lambda r:(r['preparation_provenance']!='explicit_metadata',r['source_site'] not in shared_sites,
                                        r['source_site'] in used_sites,fingerprint([seed,r['case_id'],r['file_id']])))
            for r in eligible:
                if total+r['file_size']<=budget:
                    chosen.append(r); total+=r['file_size']; used_patients.add(r['case_id']); used_md5.add(r['md5sum']); break
    report={'created_at':utcnow(),'seed':seed,'preparation':prep,'target_per_class':per_class,
            'cumulative_raw_budget_bytes':budget,'selected_bytes':total,'slides':chosen,
            'counts':dict(Counter(r['candidate_class'] for r in chosen)),
            'rules':'One known shared preparation; explicit preparation first; common sites and site diversity; hash order; distinct patients and MD5s; size is a constraint, not the ranking criterion.',
            'pilot_patients_development_only':[r['case_id'] for r in chosen],
            'complete_target':len(chosen)==per_class*len(CLASSES)}
    atomic_json(output,report)
    print(json.dumps({k:v for k,v in report.items() if k!='slides'},indent=2),flush=True)
    return report
