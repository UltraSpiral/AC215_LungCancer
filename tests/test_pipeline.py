"""Synthetic fixtures are used exclusively for unit tests, never pilot results."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
from lungcancer.common import CLASSES,atomic_json,checksum,fingerprint,read_json
from lungcancer.gdc import normalize_file,barcode_parts,preparation_audit
from lungcancer.preprocess import (TileConfig,scale_metadata,extraction_geometry,
    mask_coverage,distributed_indices,rgb_white,prepare_slide,atomic_npz)
from lungcancer.features import validate_alignment,extract_features,load_features
from lungcancer.modeling import (check_patient_separation,create_splits,fit_classifier,named_probabilities,metric_report)


@pytest.fixture
def paired_case():
    def sample(code,kind):
        barcode=f'TCGA-AA-0001-{code}A'
        return {'sample_id':f'sample-{code}','submitter_id':barcode,'sample_type':kind,
                'preservation_method':'Unknown','portions':[{'portion_id':f'portion-{code}',
                 'is_ffpe':False,'slides':[{'slide_id':f'slide-{code}','submitter_id':barcode+'-01-TS1'}]}]}
    return {'file_id':'file-11','file_name':'TCGA-AA-0001-11A-01-TS1.uuid.svs',
            'file_size':123,'md5sum':'a'*32,'access':'open','experimental_strategy':'Tissue Slide',
            'associated_entities':[{'entity_id':'slide-11','entity_type':'slide',
                                    'entity_submitter_id':'TCGA-AA-0001-11A-01-TS1','case_id':'case-1'}],
            'cases':[{'case_id':'case-1','submitter_id':'TCGA-AA-0001','project':{'project_id':'TCGA-LUAD'},
                      'diagnoses':[{'primary_diagnosis':'Adenocarcinoma, NOS','morphology':'8140/3',
                                    'tissue_or_organ_of_origin':'Lung, NOS','diagnosis_is_primary_disease':True}],
                      'samples':[sample('01','Primary Tumor'),sample('11','Solid Tissue Normal')]}]}


def test_paired_normal_is_labeled_from_actual_link_not_case_diagnosis(paired_case):
    row=normalize_file(paired_case)
    assert row['decision']=='include'
    assert row['candidate_class']=='non_tumor'
    assert row['sample_id']=='sample-11'
    assert row['slide_id']=='slide-11'


def test_paired_tumor_link(paired_case):
    case=copy.deepcopy(paired_case)
    case['associated_entities'][0].update(entity_id='slide-01',entity_submitter_id='TCGA-AA-0001-01A-01-TS1')
    case['file_name']='TCGA-AA-0001-01A-01-TS1.uuid.svs'
    row=normalize_file(case)
    assert row['candidate_class']=='adenocarcinoma' and row['decision']=='include'
    case['cases'][0]['project']['project_id']='TCGA-LUSC'
    case['cases'][0]['diagnoses'][0].update(primary_diagnosis='Squamous cell carcinoma, NOS',morphology='8070/3')
    assert normalize_file(case)['candidate_class']=='squamous'


def test_ambiguous_specimen_links_excluded(paired_case):
    paired_case['associated_entities'].append({'entity_id':'slide-01','entity_type':'slide','case_id':'case-1'})
    assert 'ambiguous_specimen_links' in normalize_file(paired_case)['reasons']


def test_duplicate_slide_uuid_under_distinct_portions_is_ambiguous(paired_case):
    sample=paired_case['cases'][0]['samples'][1]
    correct=sample['portions'][0]
    correct['submitter_id']='TCGA-AA-0001-11A-01'
    wrong=copy.deepcopy(correct)
    wrong.update(portion_id='wrong-portion',submitter_id='TCGA-AA-0001-11A-02',is_ffpe=True)
    sample['portions']=[correct,wrong]
    a=normalize_file(paired_case)
    sample['portions'].reverse()
    b=normalize_file(paired_case)
    assert a==b and a['decision']=='exclude'
    assert 'ambiguous_specimen_links' in a['reasons']
    wrong['submitter_id']=correct['submitter_id']
    assert 'ambiguous_specimen_links' in normalize_file(paired_case)['reasons']


def test_unique_uuid_link_with_different_portion_display_barcode_is_flagged(paired_case):
    paired_case['cases'][0]['samples'][1]['portions'][0]['submitter_id']='TCGA-AA-0001-11A-02'
    row=normalize_file(paired_case)
    assert row['decision']=='include' and row['candidate_class']=='non_tumor'
    assert 'linked_slide_portion_display_barcodes_differ; UUID_link_is_authoritative' in row['warnings']


def test_uuid_barcode_disagreement_and_missing_link_fail_closed(paired_case):
    paired_case['associated_entities'][0]['entity_submitter_id']='TCGA-AA-0001-01A-01-TS1'
    assert normalize_file(paired_case)['decision']=='exclude'
    paired_case['associated_entities']=[]
    assert normalize_file(paired_case)['reasons']==['unresolved_associated_specimen']


def test_partially_resolved_association_is_excluded(paired_case):
    paired_case['associated_entities'].append({'entity_type':'slide','entity_id':'missing-slide','case_id':'case-1'})
    assert normalize_file(paired_case)['decision']=='exclude'


def test_barcode_consistency_and_sample_level_link(paired_case):
    assert barcode_parts('TCGA-AA-0001-11A-01-TS1')['sample_code']=='11'
    assert barcode_parts('arbitrary.svs') is None
    paired_case['associated_entities']=[{'entity_type':'sample','entity_id':'sample-11','case_id':'case-1'}]
    row=normalize_file(paired_case)
    assert row['sample_id']=='sample-11' and row['candidate_class']=='non_tumor'
    paired_case['cases'][0]['samples'][1]['sample_type']='Primary Tumor'
    assert any('sample_type_conflict' in s for s in normalize_file(paired_case)['reasons'])


def test_prior_unrelated_diagnosis_is_not_primary_conflict(paired_case):
    paired_case['cases'][0]['diagnoses'].append({'primary_diagnosis':'Melanoma','diagnosis_is_primary_disease':False})
    assert normalize_file(paired_case)['decision']=='include'
    paired_case['cases'][0]['diagnoses'][0]['primary_diagnosis']='Small cell carcinoma'
    paired_case['cases'][0]['diagnoses'][0]['morphology']='8041/3'
    assert normalize_file(paired_case)['decision']=='exclude'


def test_preparation_inferences_and_unknowns_are_explicit():
    assert preparation_audit({'preservation_method':'Unknown'},{'is_ffpe':False},'opaque','Tissue Slide')[0]=='unknown'
    value=preparation_audit({}, {}, 'TCGA-AA-0001-11A-01-TS1','Tissue Slide')
    assert value[0:2]==('frozen','barcode_inference')
    assert value[2][0]['references']
    assert preparation_audit({}, {'is_ffpe':True},'TCGA-AA-0001-11A-01-TS1','Tissue Slide')[3]
    assert preparation_audit({}, {'is_ffpe':False},'TCGA-AA-0001-01Z-00-DX1','Diagnostic Slide')[3]


def test_patient_separation_includes_paired_classes():
    check_patient_separation([{'case_id':'p','split':'train','class':'non_tumor'}, {'case_id':'p','split':'train','class':'squamous'}])
    with pytest.raises(ValueError,match='leakage'):
        check_patient_separation([{'case_id':'p','split':'train'},{'case_id':'p','split':'test'}])


def test_grouped_multilabel_split_is_fixed_and_pilots_train(tmp_path):
    records=[]
    for i in range(60):
        for cls in ([CLASSES[i%3],CLASSES[(i+1)%3]] if i%5==0 else [CLASSES[i%3]]):
            records.append({'file_id':f'{i}-{cls}','md5sum':f'{i}-{cls}','case_id':f'p{i}',
                            'candidate_class':cls,'preparation':'frozen','decision':'include'})
    atomic_json(tmp_path/'cohort.json',records)
    atomic_json(tmp_path/'pilot.json',{'pilot_patients_development_only':['p0','p1','p2']})
    result=create_splits(tmp_path/'cohort.json',tmp_path/'split.json',pilot_selection=tmp_path/'pilot.json')
    check_patient_separation(result['slides'])
    assert all(r['split']=='train' for r in result['slides'] if r['case_id'] in ['p0','p1','p2'])
    assert all(result['counts'][s][c]['patients']>0 for s in ['train','validation','test'] for c in CLASSES)
    with pytest.raises(ValueError,match='refusing_to_regenerate'):
        create_splits(tmp_path/'cohort.json',tmp_path/'split.json')


def test_coordinate_conversion_uses_actual_axis_ratios_and_bounds():
    mask=np.zeros((10,20),dtype=bool); mask[5:,10:]=True
    coords=np.array([[0,0],[1000,500]])
    assert np.array_equal(mask_coverage(mask,coords,(1000,500),(2000,1000)),[0,1])
    for bad in [[-1,0],[1001,500]]:
        with pytest.raises(ValueError,match='bounds'):
            mask_coverage(mask,np.array([bad]),(1000,500),(2000,1000))


def test_physical_scale_and_pyramid_geometry():
    assert scale_metadata({'openslide.mpp-x':'0.25','openslide.mpp-y':'0.25'})==(.25,.25)
    for props in [{},{'openslide.mpp-x':'0.5'},{'openslide.mpp-x':'nan','openslide.mpp-y':'0.5'}]:
        with pytest.raises(ValueError): scale_metadata(props)
    geometry=extraction_geometry((5000,4000),(.25,.5),TileConfig(),[1.,4.,16.])
    assert geometry['footprint_level0']==[448,224]
    assert geometry['level']==0 and geometry['actual_output_mpp']==[.5,.5]


def test_selection_is_deterministic_bounded_and_spread():
    coords=np.array([[x,y] for y in range(10) for x in range(10)])
    a=distributed_indices(coords,8,215)
    assert np.array_equal(a,distributed_indices(coords,8,215))
    assert len(set(a))==8 and np.ptp(coords[a],axis=0).min()>=8
    assert rgb_white(Image.new('RGBA',(2,2),(255,0,0,0))).getpixel((0,0))==(255,255,255)


@pytest.fixture
def fake_slide(monkeypatch):
    import openslide
    class FakeSlide:
        dimensions=(1024,768)
        level_downsamples=(1.,4.)
        level_dimensions=((1024,768),(256,192))
        properties={'openslide.mpp-x':'0.5','openslide.mpp-y':'0.5'}
        color_profile=None
        color=(180,100,160)
        def __init__(self,*args): pass
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def get_thumbnail(self,size): return Image.new('RGB',(256,192),self.color)
        def read_region(self,location,level,size): return Image.new('RGBA',size,(location[0]%255,100,160,255))
    monkeypatch.setattr(openslide,'OpenSlide',FakeSlide)
    return FakeSlide


def test_empty_tissue_and_missing_scale_produce_explicit_failure(tmp_path,fake_slide):
    slide=tmp_path/'fixture.svs'; slide.write_bytes(b'synthetic unit fixture')
    fake_slide.color='white'
    with pytest.raises(ValueError,match='no_usable_tiles'):
        prepare_slide(slide,tmp_path/'empty')
    assert read_json(tmp_path/'empty'/'processing_failure.json')['status']=='error'
    fake_slide.properties={}
    with pytest.raises(ValueError,match='physical_scale'):
        prepare_slide(slide,tmp_path/'scale')


def test_no_large_full_resolution_thumbnail_decode(tmp_path,fake_slide):
    from lungcancer.safety import prepare_checked
    fake_slide.dimensions=(100000,100000)
    fake_slide.level_dimensions=((100000,100000),)
    fake_slide.level_downsamples=(1.,)
    slide=tmp_path/'fixture.svs'; slide.write_bytes(b'synthetic unit fixture')
    with pytest.raises(ValueError,match='no_memory_safe_thumbnail'):
        prepare_checked(slide,tmp_path/'out')
    assert read_json(tmp_path/'out'/'processing_failure.json')['status']=='error'


def test_bounded_thumbnail_fallback_versions_only_affected_slides(tmp_path,fake_slide,monkeypatch):
    from lungcancer.safety import prepare_checked,preprocessing_fingerprint
    fake_slide.dimensions=(14000,13897)
    fake_slide.level_dimensions=((14000,13897),(3500,3474),(1750,1737))
    fake_slide.level_downsamples=(1.,4.,8.)
    monkeypatch.setattr(fake_slide,'close',lambda self:None,raising=False)
    reads=[]
    original=fake_slide.read_region
    def guarded_read(self,location,level,size):
        assert size[0]*size[1]<=64_000_000
        reads.append((level,size))
        return original(self,location,level,size)
    monkeypatch.setattr(fake_slide,'read_region',guarded_read)
    slide=tmp_path/'fixture.svs';slide.write_bytes(b'synthetic pyramid unit fixture')
    config=TileConfig(max_tiles=8)
    meta=prepare_checked(slide,tmp_path/'out',config,'fixture',checksum(slide,'md5'))
    assert meta['status']=='success' and meta['thumbnail_policy']['pyramid_level']==1
    assert reads[0]==(1,(3500,3474))
    assert meta['thumbnail_size']==[3500,3474]
    legacy=preprocessing_fingerprint(meta['source_md5'],meta['config'])
    assert meta['fingerprint']!=legacy
    assert meta['fingerprint']==preprocessing_fingerprint(meta['source_md5'],meta['config'],meta)
    changed=copy.deepcopy(meta);changed['thumbnail_policy']['implementation_sha256']='wrong'
    with pytest.raises(ValueError,match='thumbnail_policy'):
        preprocessing_fingerprint(meta['source_md5'],meta['config'],changed)


def test_cache_invalidates_config_and_inputs_and_preserves_coordinate_order(tmp_path,fake_slide):
    slide=tmp_path/'fixture.svs'; slide.write_bytes(b'synthetic unit fixture')
    directory=tmp_path/'processing'
    first=prepare_slide(slide,directory,TileConfig(max_tiles=8))
    second=prepare_slide(slide,directory,TileConfig(max_tiles=12))
    assert first['fingerprint']!=second['fingerprint']
    class FakeEncoder:
        identifier='unit-test-only'
        metadata={'unit_test_fixture':True}
        def encode(self,images):
            output=np.zeros((len(images),1536),dtype=np.float32)
            output[:,0]=[im.getpixel((0,0))[0] for im in images]
            return output
    encoder=FakeEncoder()
    meta=extract_features(slide,directory,encoder)
    array,coords,_=load_features(directory/'embeddings.npz')
    assert np.array_equal(array[:,0],coords[:,0]%255)
    old=meta['fingerprint']; encoder.identifier='changed-unit-test-encoder'
    assert extract_features(slide,directory,encoder)['fingerprint']!=old
    slide.write_bytes(b'different synthetic unit fixture')
    assert prepare_slide(slide,directory,TileConfig(max_tiles=12))['fingerprint']!=second['fingerprint']


def test_embedding_alignment_and_cache_coordinate_integrity(tmp_path):
    with pytest.raises(ValueError,match='misaligned'):
        validate_alignment(np.zeros((2,1536)),np.zeros((3,2)))
    with pytest.raises(ValueError): validate_alignment(np.empty((0,1536)),np.empty((0,2)))
    data=np.zeros((2,1536)); data[0,0]=np.nan
    with pytest.raises(ValueError,match='nonfinite'): validate_alignment(data,np.zeros((2,2)))
    atomic_npz(tmp_path/'bad.npz',embeddings=np.zeros((2,1536)),coordinates=np.zeros((2,2)),
               metadata_json=np.array(json.dumps({'coordinates_fingerprint':'wrong'})))
    with pytest.raises(ValueError,match='fingerprint'): load_features(tmp_path/'bad.npz')


def test_modeling_run_reuses_only_verified_cache_bytes(tmp_path,fake_slide):
    from lungcancer.modeling_run import verify_cache
    slide=tmp_path/'fixture.svs'; slide.write_bytes(b'synthetic cache verification fixture')
    directory=tmp_path/'processing'; config=TileConfig(max_tiles=8)
    record={'file_id':'unit-fixture','md5sum':checksum(slide,'md5')}
    prepare_slide(slide,directory,config,record['file_id'],record['md5sum'])
    class FixtureEncoder:
        identifier='synthetic-unit-test-only'
        metadata={'unit_test_fixture':True}
        def encode(self,images): return np.ones((len(images),1536),dtype=np.float32)
    encoder=FixtureEncoder()
    extract_features(slide,directory,encoder)
    prep,meta=verify_cache(record,directory,config,encoder)
    assert prep['selected_count']==meta['shape'][0]==8
    with pytest.raises(ValueError,match='incompatible_cache'):
        verify_cache({**record,'md5sum':'0'*32},directory,config,encoder)
    with np.load(directory/'embeddings.npz',allow_pickle=False) as cache:
        arrays={k:cache[k] for k in cache.files}
    arrays['embeddings']=arrays['embeddings']+1
    atomic_npz(directory/'embeddings.npz',**arrays)
    with pytest.raises(ValueError,match='embedding_file_checksum'):
        verify_cache(record,directory,config,encoder)


def test_prefetch_verifies_current_raw_and_preserves_serial_extraction():
    from lungcancer.modeling_run import process_with_prefetch
    import threading
    records=[{'file_id':str(i)} for i in range(4)]
    available={'0'};order=[];active=0;max_active=0;lock=threading.Lock()
    next_download_started=threading.Event();allow_next_download=threading.Event()
    def download(record):
        nonlocal active,max_active
        with lock:
            active+=1;max_active=max(max_active,active)
        if record['file_id']=='1':
            next_download_started.set()
            assert allow_next_download.wait(3)
        available.add(record['file_id'])
        with lock: active-=1
    def process(record):
        assert record['file_id'] in available
        order.append(record['file_id'])
        if record['file_id']=='0':
            assert next_download_started.wait(3)
            allow_next_download.set()
    process_with_prefetch(records,process,download,lambda r:r['file_id']=='0')
    assert order==['0','1','2','3'] and max_active==1


def test_prefetch_download_failure_does_not_process_unverified_slide():
    from lungcancer.modeling_run import process_with_prefetch
    seen=[]
    def download(record):
        if record['file_id']=='bad': raise ValueError('download_failed_fixture')
    with pytest.raises(ValueError,match='download_failed_fixture'):
        process_with_prefetch([{'file_id':'ok'},{'file_id':'bad'}],
                              lambda r:seen.append(r['file_id']),download,lambda r:False)
    assert seen==['ok']


def test_scaler_is_fit_on_training_only_and_probability_class_order():
    rng=np.random.default_rng(215)
    X=rng.normal(size=(30,4)); y=np.array(CLASSES*10)
    validation=np.full((3,4),1000.)
    model=fit_classifier(X,y)
    expected=X.mean(axis=0)
    assert np.allclose(model.named_steps['scaler'].mean_,expected)
    probability=named_probabilities(model,validation)
    assert np.allclose(model.named_steps['scaler'].mean_,expected)
    assert probability.shape==(3,3) and np.allclose(probability.sum(1),1)
    class Scrambled:
        classes_=np.array(['squamous','non_tumor','adenocarcinoma'])
        def predict_proba(self,X): return np.tile([.7,.2,.1],(len(X),1))
    assert np.allclose(named_probabilities(Scrambled(),np.zeros((1,4))),[[.2,.1,.7]])


def test_undefined_metrics_are_explicit():
    report=metric_report(np.array(['non_tumor','non_tumor']),np.array([[1.,0.,0.],[1.,0.,0.]]))
    assert report['one_vs_rest_auroc']['non_tumor'] is None
    assert report['per_class']['adenocarcinoma']['precision'] is None


def test_inference_failure_returns_no_fabricated_prediction(tmp_path):
    from lungcancer.inference import predict
    result=predict(tmp_path/'anything.svs',tmp_path/'absent-model',tmp_path/'out')
    assert result['status']=='error'
    assert 'predicted_class' not in result and 'class_probabilities' not in result


def test_prediction_is_independent_of_arbitrary_renaming(tmp_path,fake_slide,monkeypatch):
    # End-to-end control-flow unit test: synthetic slide fixture and unit-test encoder.
    # This is never used as evidence of real-slide inference or model performance.
    import joblib
    from dataclasses import asdict
    from lungcancer import inference
    from lungcancer import preprocess
    import openslide
    class UnitTestEncoder:
        identifier='synthetic-unit-test-only'
        metadata={'unit_test_fixture':True}
        def __init__(self,revision): pass
        def encode(self,images):
            features=np.zeros((len(images),1536),dtype=np.float32)
            features[:,0]=[im.getpixel((0,0))[0] for im in images]
            return features
    monkeypatch.setattr(inference,'UNI2Encoder',UnitTestEncoder)
    bundle=tmp_path/'bundle'; bundle.mkdir()
    rng=np.random.default_rng(215)
    model=fit_classifier(rng.normal(size=(30,1536)),np.array(CLASSES*10))
    joblib.dump(model,bundle/'classifier.joblib')
    atomic_json(bundle/'model.json',{'classifier_sha256':checksum(bundle/'classifier.joblib'),
        'pooling':'mean_of_tile_embeddings','classes':list(CLASSES),
        'encoder':{'revision':'unit-test-only'},'encoder_identifier':UnitTestEncoder.identifier,
        'preprocessing_config':asdict(TileConfig(max_tiles=8)),'model_identifier':'unit-test-only'})
    metadata=read_json(bundle/'model.json')
    metadata['preprocessing_implementation_sha256']=checksum(preprocess.__file__)
    metadata['openslide_library_version']=openslide.__library_version__
    atomic_json(bundle/'model.json',metadata)
    original=tmp_path/'TCGA-AA-0001-01A-01-TS1.svs'; renamed=tmp_path/'anything.svs'
    original.write_bytes(b'synthetic unit fixture'); renamed.write_bytes(original.read_bytes())
    a=inference.predict(original,bundle,tmp_path/'first')
    b=inference.predict(renamed,bundle,tmp_path/'second')
    assert a['status']==b['status']=='success'
    assert a['class_probabilities']==b['class_probabilities']
    assert a['configuration_identifier']==b['configuration_identifier']
    assert set(a['class_probabilities'])==set(CLASSES)


def test_download_resume_checksum_skip_and_cumulative_accounting(tmp_path,monkeypatch):
    import hashlib
    from lungcancer import download
    data=b'synthetic download unit fixture'
    record={'file_id':'00000000-0000-4000-8000-000000000001','file_size':len(data),
            'md5sum':hashlib.md5(data).hexdigest(),'access':'open'}
    calls=[]
    class Response:
        def __init__(self,offset):
            self.status_code=206 if offset else 200
            self.headers={'Content-Range':f'bytes {offset}-{len(data)-1}/{len(data)}'}
            self.offset=offset
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def raise_for_status(self): pass
        def iter_content(self,chunk_size): yield data[self.offset:]
    class Client:
        def mount(self,*args): pass
        def get(self,url,headers,**kwargs):
            calls.append(headers)
            offset=int(headers.get('Range','bytes=0-').split('=')[1].split('-')[0])
            return Response(offset)
    monkeypatch.setattr(download,'session',Client)
    raw=tmp_path/'raw'; raw.mkdir()
    (raw/(record['file_id']+'.svs.partial')).write_bytes(data[:5])
    path=download.download_slide(record,raw,tmp_path/'ledger.json',budget=len(data)*3,persist=False)
    assert path.read_bytes()==data and calls==[{'Range':'bytes=5-'}]
    ledger=read_json(tmp_path/'ledger.json')
    assert ledger['transferred_bytes']==len(data)-5 and ledger['reserved_bytes']==len(data)
    download.download_slide(record,raw,tmp_path/'ledger.json',budget=len(data)*3,persist=False)
    assert len(calls)==1


def test_download_budget_blocks_network_request(tmp_path,monkeypatch):
    from lungcancer import download
    class Client:
        def mount(self,*args): pass
        def get(self,*args,**kwargs): pytest.fail('network request exceeded byte budget')
    monkeypatch.setattr(download,'session',Client)
    record={'file_id':'00000000-0000-4000-8000-000000000002','file_size':100,'md5sum':'a'*32,'access':'open'}
    with pytest.raises(RuntimeError,match='budget_exhausted'):
        download.download_slide(record,tmp_path/'raw',tmp_path/'ledger.json',budget=99,persist=False)
