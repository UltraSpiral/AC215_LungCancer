"""Patient-grouped splits and training-only scaled slide-level logistic regression.

These commands are provided for the post-pilot stage. They do not expand data
downloads or execute automatically as part of the pilot.
"""
from collections import Counter, defaultdict
from pathlib import Path
import importlib.metadata
import json
import os
import tempfile
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (f1_score,balanced_accuracy_score,precision_recall_fscore_support,
                             confusion_matrix,roc_auc_score)
from .common import CLASSES,atomic_json,read_json,fingerprint,checksum,utcnow
from .features import load_features


def check_patient_separation(records):
    assignments={}
    for record in records:
        patient=record['case_id']; split=record['split']
        if split not in {'train','validation','test'}: raise ValueError('invalid_split_name')
        if patient in assignments and assignments[patient]!=split:
            raise ValueError('patient_leakage_across_splits')
        assignments[patient]=split
    return assignments


def split_counts(records):
    return {split:{c:{'slides':sum(r['split']==split and r['candidate_class']==c for r in records),
                      'patients':len({r['case_id'] for r in records if r['split']==split and r['candidate_class']==c})}
                   for c in CLASSES} for split in ['train','validation','test']}


def create_splits(cohort_path,output,seed=215,pilot_selection=None):
    output=Path(output)
    if output.exists(): raise ValueError('split_file_already_exists; refusing_to_regenerate')
    records=read_json(cohort_path)
    if isinstance(records,dict): records=records['slides']
    if any(r.get('decision')!='include' for r in records): raise ValueError('cohort_contains_excluded_specimens')
    if len({r['file_id'] for r in records})!=len(records): raise ValueError('duplicate_cohort_file_ids')
    if len({r['md5sum'] for r in records})!=len(records): raise ValueError('duplicate_slide_checksums')
    if len({r['preparation'] for r in records})!=1 or records[0]['preparation']=='unknown':
        raise ValueError('cohort_preparation_is_not_matched')
    # At most one selected slide per patient per class.
    if len({(r['case_id'],r['candidate_class']) for r in records})!=len(records):
        raise ValueError('multiple_slides_per_patient_per_class; select_one_before_splitting')
    patients=defaultdict(list)
    for record in records: patients[record['case_id']].append(record)
    vectors={p:np.array([1]+[int(any(r['candidate_class']==c for r in rows)) for c in CLASSES],dtype=float)
             for p,rows in patients.items()}
    totals=sum(vectors.values())
    if np.min(totals[1:])<10: raise ValueError('too_few_independent_patients_per_class_for_three_way_split')
    pilot=set(read_json(pilot_selection)['pilot_patients_development_only']) if pilot_selection else set()
    names=['train','validation','test']; targets=np.array([0.70,0.15,0.15])[:,None]*totals[None,:]
    counts=np.zeros_like(targets); assignments={}
    for patient in sorted(pilot & patients.keys()):
        assignments[patient]='train'; counts[0]+=vectors[patient]
    # Balance the multi-label patient vectors jointly; paired samples never split.
    remaining=[p for p in patients if p not in assignments]
    remaining.sort(key=lambda p:(-float(np.sum(vectors[p][1:]/totals[1:])),fingerprint([seed,p])))
    for patient in remaining:
        vector=vectors[patient]
        scores=[]
        for i in range(3):
            proposed=counts.copy(); proposed[i]+=vector
            score=np.sum(((proposed-targets)/np.maximum(targets,1))**2)
            scores.append(score)
        index=int(np.argmin(scores)); assignments[patient]=names[index]; counts[index]+=vector
    records=[{**r,'split':assignments[r['case_id']]} for r in records]
    check_patient_separation(records)
    summary=split_counts(records)
    if any(summary[s][c]['patients']==0 for s in names for c in CLASSES):
        raise ValueError('grouped_split_has_missing_class; cohort_design_requires_review')
    result={'created_at':utcnow(),'seed':seed,'target_fractions':dict(zip(names,[0.70,0.15,0.15])),
            'method':'deterministic greedy joint balance of patient and multi-label class counts',
            'cohort_sha256':checksum(cohort_path),'pilot_patients_forced_train':sorted(pilot & patients.keys()),
            'rules':'one slide per patient per class; one preparation; fixed assignments; paired classes remain together',
            'counts':summary,'slides':records}
    result['split_identifier']=fingerprint(result)
    atomic_json(output,result)
    return result


def pooled_dataset(records,artifact_root):
    X=[]; y=[]; encoders=set(); preprocessing=set(); metas=[]
    for r in records:
        features,coords,meta=load_features(Path(artifact_root)/r['file_id']/'embeddings.npz')
        if meta['source_md5']!=r['md5sum'] or meta['file_id']!=r['file_id']:
            raise ValueError('feature_manifest_identity_mismatch')
        X.append(features.mean(axis=0,dtype=np.float64)); y.append(r['candidate_class'])
        encoders.add(meta['encoder_identifier']); preprocessing.add(fingerprint(meta['preprocessing_config']))
        metas.append(meta)
    if len(encoders)!=1 or len(preprocessing)!=1: raise ValueError('incompatible_feature_configurations')
    return np.asarray(X),np.asarray(y),metas


def fit_classifier(X_train,y_train,C=1.0):
    pipeline=Pipeline([('scaler',StandardScaler()),
                       ('classifier',LogisticRegression(C=C,penalty='l2',solver='lbfgs',max_iter=3000,random_state=215))])
    # With three classes lbfgs optimizes the multinomial loss in sklearn >=1.6.
    pipeline.fit(X_train,y_train)
    return pipeline


def named_probabilities(classifier,features):
    raw=classifier.predict_proba(features)
    order=list(classifier.classes_)
    if set(order)!=set(CLASSES): raise ValueError('classifier_classes_do_not_match_task')
    return raw[:,[order.index(c) for c in CLASSES]]


def metric_report(y,probabilities,predictions=None):
    predictions=np.asarray(predictions) if predictions is not None else np.asarray(CLASSES)[np.argmax(probabilities,axis=1)]
    precision,recall,fscore,support=precision_recall_fscore_support(y,predictions,labels=list(CLASSES),zero_division=0)
    per_class={}
    auc={}
    for index,c in enumerate(CLASSES):
        predicted_n=int(np.sum(predictions==c)); actual_n=int(np.sum(y==c))
        per_class[c]={'precision':float(precision[index]) if predicted_n else None,
                      'recall':float(recall[index]) if actual_n else None,
                      'f1':float(fscore[index]) if actual_n or predicted_n else None,
                      'support':int(support[index]),'predicted_count':predicted_n}
        binary=np.asarray(y)==c
        auc[c]=float(roc_auc_score(binary,probabilities[:,index])) if len(set(binary))==2 else None
    return {'macro_f1':float(f1_score(y,predictions,labels=list(CLASSES),average='macro',zero_division=0)),
            'balanced_accuracy':float(balanced_accuracy_score(y,predictions)),
            'per_class':per_class,'one_vs_rest_auroc':auc,
            'confusion_matrix':confusion_matrix(y,predictions,labels=list(CLASSES)).tolist(),
            'confusion_matrix_class_order':list(CLASSES),
            'undefined_metrics':'null: no predicted examples (precision), no true examples (recall), or no binary class contrast (AUROC)'}


def train(split_path,artifact_root,output):
    import joblib
    output=Path(output)
    if output.exists(): raise ValueError('model_bundle_already_exists; use_a_new_experiment_directory')
    split=read_json(split_path); records=split['slides']; check_patient_separation(records)
    train_rows=[r for r in records if r['split']=='train']
    validation_rows=[r for r in records if r['split']=='validation']
    # Test files and embeddings are never opened during model selection.
    X,y,metas=pooled_dataset(train_rows,artifact_root)
    Xv,yv,validation_metas=pooled_dataset(validation_rows,artifact_root)
    if any(m['encoder_identifier']!=metas[0]['encoder_identifier'] or m['preprocessing_config']!=metas[0]['preprocessing_config'] for m in validation_metas):
        raise ValueError('training_validation_feature_configuration_mismatch')
    from . import preprocess
    import openslide
    from . import safety
    for meta in [*metas,*validation_metas]:
        prep=read_json(Path(artifact_root)/meta['file_id']/'preprocessing.json')
        expected=safety.preprocessing_fingerprint(meta['source_md5'],meta['preprocessing_config'],prep)
        if meta['preprocessing_fingerprint']!=expected:
            raise ValueError('features_not_generated_with_current_preprocessing_implementation')
    if set(y)!=set(CLASSES) or set(yv)!=set(CLASSES): raise ValueError('training_or_validation_missing_class')
    search=[]; best=None
    for C in [0.01,0.1,1.0]:
        pipeline=fit_classifier(X,y,C)
        probability=named_probabilities(pipeline,Xv)
        metrics=metric_report(yv,probability)
        search.append({'C':C,'validation_macro_f1':metrics['macro_f1']})
        if best is None or metrics['macro_f1']>best[0]: best=(metrics['macro_f1'],C,pipeline,metrics)
    baseline=DummyClassifier(strategy='most_frequent').fit(X,y)
    baseline_metrics=metric_report(yv,named_probabilities(baseline,Xv))
    output.mkdir(parents=True)
    with tempfile.NamedTemporaryFile('wb',dir=output,prefix='.model-',delete=False) as f:
        temporary=f.name
    joblib.dump(best[2],temporary); os.replace(temporary,output/'classifier.joblib')
    metadata={'created_at':utcnow(),'classes':list(CLASSES),'pooling':'mean_of_tile_embeddings',
              'probabilities_calibrated':False,'C':best[1],'regularization_search':search,
              'validation':best[3],'majority_baseline_validation':baseline_metrics,
              'training_majority_class':str(baseline.classes_[np.argmax(baseline.class_prior_)]),
              'split_identifier':split['split_identifier'],'split_file_sha256':checksum(split_path),
              'counts':split['counts'],'training_file_ids':[r['file_id'] for r in train_rows],
              'validation_file_ids':[r['file_id'] for r in validation_rows],
              'encoder':metas[0]['encoder'],'encoder_identifier':metas[0]['encoder_identifier'],
              'preprocessing_config':metas[0]['preprocessing_config'],
              'preprocessing_implementation_sha256':checksum(preprocess.__file__),
              'thumbnail_safety_implementation_sha256':checksum(safety.__file__),
              'openslide_library_version':openslide.__library_version__,
              'dependency_versions':{p:importlib.metadata.version(p) for p in ['torch','torchvision','timm','scikit-learn','numpy','joblib']},
              'classifier_sha256':checksum(output/'classifier.joblib'),
              'limitations':['Engineering prototype; not clinically validated.','Uncalibrated probabilities.','TCGA frozen specimens and source-site confounding limit generalization.']}
    metadata['model_identifier']=fingerprint(metadata)
    atomic_json(output/'model.json',metadata)
    return metadata


def evaluate(split_path,artifact_root,model_root,split_name,output):
    import joblib
    output=Path(output); model_root=Path(model_root)
    if output.exists(): raise ValueError('evaluation_output_exists; refusing_repeat_test_evaluation')
    metadata=read_json(model_root/'model.json'); split=read_json(split_path)
    check_patient_separation(split['slides'])
    if checksum(split_path)!=metadata['split_file_sha256']: raise ValueError('split_assignments_changed')
    if checksum(model_root/'classifier.joblib')!=metadata['classifier_sha256']: raise ValueError('classifier_checksum_mismatch')
    rows=[r for r in split['slides'] if r['split']==split_name]
    X,y,metas=pooled_dataset(rows,artifact_root)
    if any(m['encoder_identifier']!=metadata['encoder_identifier'] or m['preprocessing_config']!=metadata['preprocessing_config'] for m in metas):
        raise ValueError('evaluation_feature_configuration_mismatch')
    model=joblib.load(model_root/'classifier.joblib')
    probability=named_probabilities(model,X); predicted=np.asarray(CLASSES)[probability.argmax(1)]
    baseline_prediction=np.repeat(metadata['training_majority_class'],len(y))
    baseline_probability=np.zeros_like(probability); baseline_probability[:,CLASSES.index(metadata['training_majority_class'])]=1
    report={'split':split_name,'metrics':metric_report(y,probability),
            'majority_baseline':metric_report(y,baseline_probability,baseline_prediction),
            'counts':split['counts'][split_name], 'model_identifier':metadata['model_identifier'],
            'split_identifier':split['split_identifier'],'error_analysis':{}}
    predictions=[]
    for r,pred,probs,meta in zip(rows,predicted,probability,metas):
        predictions.append({'file_id':r['file_id'],'case_id':r['case_id'],'true_class':r['candidate_class'],
                            'predicted_class':str(pred),'class_probabilities':dict(zip(CLASSES,map(float,probs))),
                            'preparation':r['preparation'],'site':r.get('source_site'),'tiles':meta['shape'][0]})
    for field in ['preparation','site','tiles']:
        groups=defaultdict(list)
        for r in predictions:
            value=str(r[field]) if field!='tiles' else ('<128' if r['tiles']<128 else '128-511' if r['tiles']<512 else '512')
            groups[value].append(r)
        report['error_analysis'][field]={k:{'slides':len(v),'errors':sum(r['true_class']!=r['predicted_class'] for r in v)} for k,v in groups.items()}
    output.mkdir(parents=True)
    atomic_json(output/'metrics.json',report); atomic_json(output/'predictions.json',predictions)
    return report
