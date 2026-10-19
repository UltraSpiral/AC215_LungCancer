from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from .common import canonical, fingerprint, checksum, read_json, atomic_json
from .preprocess import atomic_npz, read_tile
from .encoder import DIMENSION


def validate_alignment(embeddings,coordinates):
    if embeddings.ndim!=2 or embeddings.shape[1]!=DIMENSION or coordinates.ndim!=2 or coordinates.shape[1]!=2:
        raise ValueError('invalid_embedding_or_coordinate_shape')
    if len(embeddings)!=len(coordinates) or len(embeddings)==0:
        raise ValueError('empty_or_misaligned_embeddings_and_coordinates')
    if not np.isfinite(embeddings).all() or not np.isfinite(coordinates).all():
        raise ValueError('nonfinite_embeddings_or_coordinates')


def load_features(path):
    with np.load(path,allow_pickle=False) as cache:
        features=cache['embeddings']; coordinates=cache['coordinates']
        metadata=json.loads(str(cache['metadata_json']))
    validate_alignment(features,coordinates)
    if fingerprint(coordinates.tolist())!=metadata['coordinates_fingerprint']:
        raise ValueError('coordinates_fingerprint_mismatch')
    return features,coordinates,metadata


def extract_features(path,preprocess_dir,encoder,output=None):
    import openslide
    preprocess_dir=Path(preprocess_dir)
    output=Path(output or preprocess_dir/'embeddings.npz')
    prep=read_json(preprocess_dir/'preprocessing.json')
    if prep['status']!='success': raise ValueError('preprocessing_not_successful')
    if checksum(path,'md5')!=prep['source_md5']: raise ValueError('source_does_not_match_preprocessing')
    if checksum(preprocess_dir/'coordinates.npz')!=prep['coordinates_file_sha256']:
        raise ValueError('coordinates_file_checksum_mismatch')
    with np.load(preprocess_dir/'coordinates.npz',allow_pickle=False) as cache:
        coords=cache['coordinates']
    coords_hash=fingerprint(coords.tolist())
    key=fingerprint({'preprocessing':prep['fingerprint'],'encoder':encoder.identifier,
                     'coordinates':coords_hash,'implementation':checksum(__file__)})
    if output.exists():
        features,oldcoords,meta=load_features(output)
        if meta.get('fingerprint')==key and np.array_equal(oldcoords,coords):
            print(f'Embedding cache verified: {output}',flush=True); return meta
    blocks=[]
    with openslide.OpenSlide(str(path)) as slide:
        for offset in range(0,len(coords),32):
            tiles=[read_tile(slide,c,prep['geometry'],prep['config']['tile_size']) for c in coords[offset:offset+32]]
            blocks.append(encoder.encode(tiles))
            print(f'Embedded {min(offset+32,len(coords))}/{len(coords)} tiles',flush=True)
    features=np.concatenate(blocks).astype(np.float32)
    validate_alignment(features,coords)
    meta={'status':'success','fingerprint':key,'source_md5':prep['source_md5'],'file_id':prep['file_id'],
          'preprocessing_fingerprint':prep['fingerprint'],'preprocessing_config':prep['config'],
          'encoder':encoder.metadata,'encoder_identifier':encoder.identifier,
          'coordinates_fingerprint':coords_hash,'coordinate_system':prep['coordinate_system'],
          'shape':list(features.shape),'quality_warnings':prep['warnings'],'pooling':'mean_of_tile_embeddings'}
    atomic_npz(output,embeddings=features,coordinates=coords,metadata_json=np.array(canonical(meta)))
    atomic_json(output.with_suffix('.json'),{**meta,'npz_sha256':checksum(output)})
    return meta
