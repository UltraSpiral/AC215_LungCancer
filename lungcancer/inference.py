"""Filename-independent inference from an SVS path and a trusted model bundle."""
from pathlib import Path
import shutil
import numpy as np
from .common import read_json,atomic_json,checksum,CLASSES
from .preprocess import TileConfig
from .safety import prepare_checked as prepare_slide
from .encoder import UNI2Encoder
from .features import extract_features,load_features
from .modeling import named_probabilities


def predict(slide_path,model_root,output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    try:
        import joblib
        model_root=Path(model_root); metadata=read_json(model_root/'model.json')
        if checksum(model_root/'classifier.joblib')!=metadata['classifier_sha256']:
            raise ValueError('classifier_checksum_mismatch')
        if metadata['pooling']!='mean_of_tile_embeddings' or set(metadata['classes'])!=set(CLASSES):
            raise ValueError('unsupported_model_bundle')
        from . import preprocess
        import openslide
        if (metadata['preprocessing_implementation_sha256']!=checksum(preprocess.__file__) or
                metadata['openslide_library_version']!=openslide.__library_version__):
            raise ValueError('preprocessing_implementation_or_openslide_version_mismatch')
        config=TileConfig(**metadata['preprocessing_config'])
        # No filename parsing, diagnosis access, or TCGA metadata is used here.
        prep=prepare_slide(slide_path,output/'processing',config)
        encoder=UNI2Encoder(revision=metadata['encoder']['revision'])
        if encoder.identifier!=metadata['encoder_identifier']:
            raise ValueError('encoder_or_transform_configuration_mismatch')
        extract_features(slide_path,output/'processing',encoder)
        embeddings,_,_=load_features(output/'processing'/'embeddings.npz')
        model=joblib.load(model_root/'classifier.joblib')
        pooled=embeddings.mean(axis=0,dtype=np.float64)[None,:]
        probabilities=named_probabilities(model,pooled)[0]
        result={'status':'success','predicted_class':CLASSES[int(np.argmax(probabilities))],
                'class_probabilities':dict(zip(CLASSES,map(float,probabilities))),
                'probabilities_calibrated':False,'tiles_analyzed':len(embeddings),
                'quality_warnings':prep['warnings'],'model_identifier':metadata['model_identifier'],
                'encoder_identifier':encoder.identifier,'configuration_identifier':prep['fingerprint'],
                'source_md5':prep['source_md5'],
                'analyzed_tile_locations_overlay':str(output/'analyzed_tiles_overlay.jpg')}
        shutil.copyfile(output/'processing'/'selected_tiles_overlay.jpg',output/'analyzed_tiles_overlay.jpg')
    except Exception as exc:
        result={'status':'error','reason':str(exc)}
    atomic_json(output/'prediction.json',result)
    return result
