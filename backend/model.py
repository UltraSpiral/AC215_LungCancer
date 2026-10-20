"""Verify immutable inputs, resolve content identity and classify real cached vectors."""
from pathlib import Path
import importlib.util

import joblib
import numpy as np

from lungcancer.common import CLASSES, checksum, read_json
from lungcancer.features import load_features
from lungcancer.modeling import check_patient_separation, named_probabilities
from lungcancer.modeling_run import verify_cache
from lungcancer.preprocess import TileConfig
from scripts.verify_cpu_bundle import verify_inventory

MODEL_ID = '42af9fb3f51e1539d994af4f20e2980e4118eac6a8cd665aeb372c1440b2fed5'
CLASSIFIER_SHA = 'c4bf98706e52febb1fe80ac5baeec75748511c6e1d835b272d19c3570647a71d'
SNAPSHOT_ID = 'f9491fe4d35f30267df95d26c61d6bb325908694e6df7d746a6acb9826eddb24'
SPLIT_ID = '964f3b6c073863efbe38b560cfe93b2783cff5d822c64bde12f71241a7a4f2c4'
ENCODER_ID = 'debc5e8769258a2e970772801d440debc2500868f5a6cf93b7b5c0c8c1e41324'
SOURCE_SHA = '544fc4ab2cf62ebc99e01e734907ec4194c71baba8b61bb4cbca92ae739c9a9d'


class UnsupportedSlide(ValueError):
    pass


class CachedClassifier:
    def __init__(self, bundle: Path):
        if importlib.util.find_spec('torch') is not None:
            raise ValueError('The cached demo requires its isolated Torch-free environment.')
        self.bundle = Path(bundle).resolve()
        manifest = verify_inventory(self.bundle)
        if manifest['data_snapshot_identifier'] != SNAPSHOT_ID:
            raise ValueError('incompatible_input_snapshot')
        self.entries = {e['path']: e for e in manifest['files']}
        self.metadata = read_json(self.bundle / 'run/model/model.json')
        self.split = read_json(self.bundle / 'run/splits.json')
        if (self.metadata['model_identifier'] != MODEL_ID or
                self.metadata['encoder_identifier'] != ENCODER_ID or
                self.split['split_identifier'] != SPLIT_ID or
                checksum(self.bundle / 'run/splits.json') != self.metadata['split_file_sha256']):
            raise ValueError('incompatible_model_or_split')
        check_patient_separation(self.split['slides'])
        self.sample = manifest['real_slide']
        self.source = self.bundle / self.sample['path']
        if checksum(self.source) != SOURCE_SHA or checksum(self.source, 'md5') != self.sample['md5sum']:
            raise ValueError('supported_source_checksum_mismatch')
        self.row = next(r for r in self.split['slides'] if r['file_id'] == self.sample['file_id'])
        self.directory = self.bundle / 'slides' / self.row['file_id']
        self._features()  # Validate the matching cache before trusted deserialization.
        classifier = self.bundle / 'run/model/classifier.joblib'
        if (checksum(classifier) != CLASSIFIER_SHA or
                self.metadata['classifier_sha256'] != CLASSIFIER_SHA):
            raise ValueError('classifier_checksum_mismatch')
        self.classifier = joblib.load(classifier)
        if (set(self.classifier.classes_) != set(CLASSES) or
                int(self.classifier.named_steps['scaler'].n_samples_seen_) != 32 or
                self.classifier.named_steps['classifier'].C != 0.01):
            raise ValueError('incompatible_saved_classifier')

    def _features(self):
        for name in ('embeddings.npz', 'embeddings.json', 'coordinates.npz', 'preprocessing.json'):
            path = self.directory / name
            entry = self.entries[str(path.relative_to(self.bundle))]
            if path.stat().st_size != entry['bytes'] or checksum(path) != entry['sha256']:
                raise ValueError('cached_features_checksum_mismatch')
        prep, meta = verify_cache(self.row, self.directory,
                                  TileConfig(**self.metadata['preprocessing_config']), ENCODER_ID)
        vectors, coords, embedded_meta = load_features(self.directory / 'embeddings.npz')
        if (embedded_meta['encoder_identifier'] != ENCODER_ID or
                embedded_meta['preprocessing_config'] != self.metadata['preprocessing_config'] or
                len(vectors) != prep['selected_count']):
            raise ValueError('cached_feature_provenance_mismatch')
        return vectors, coords, meta, prep

    def predict(self, sha256: str, size: int, md5: str):
        if (sha256 != SOURCE_SHA or size != self.sample['bytes'] or md5 != self.sample['md5sum']):
            raise UnsupportedSlide('Unsupported slide: no verified preprocessed features match these file bytes. '
                                   'Use the supplied previously processed slide; this demo cannot process new slides.')
        vectors, _, meta, _ = self._features()
        pooled = vectors.mean(axis=0, dtype=np.float64)[None, :]
        probabilities = named_probabilities(self.classifier, pooled)[0]
        if (not np.isfinite(probabilities).all() or np.any(probabilities < 0) or
                np.any(probabilities > 1) or not np.isclose(probabilities.sum(), 1, atol=1e-12)):
            raise ValueError('invalid_saved_model_probabilities')
        return {
            'status': 'success', 'predicted_class': CLASSES[int(np.argmax(probabilities))],
            'class_probabilities': {c: float(p) for c, p in zip(CLASSES, probabilities)},
            'probabilities_calibrated': False, 'tiles_analyzed': len(vectors),
            'quality_warnings': meta['quality_warnings'], 'model_identifier': MODEL_ID,
            'encoder_identifier': ENCODER_ID, 'data_snapshot_identifier': SNAPSHOT_ID,
            'source_sha256': sha256, 'source_md5': md5,
            'feature_fingerprint': meta['fingerprint'],
            'processing_mode': 'preprocessed_slide_demo', 'uni2_encoding_performed': False,
        }

    def create_overlay(self, destination: Path):
        import openslide
        from PIL import ImageDraw
        _, coordinates, _, prep = self._features()
        with openslide.OpenSlide(str(self.source)) as slide:
            image = slide.get_thumbnail((1024, 1024)).convert('RGB')
        width, height = prep['dimensions_level0']
        tile_w, tile_h = prep['geometry']['footprint_level0']
        sx, sy = image.width / width, image.height / height
        draw = ImageDraw.Draw(image)
        for x, y in coordinates:
            draw.rectangle((x*sx, y*sy, (x+tile_w)*sx, (y+tile_h)*sy), outline='#c32342', width=1)
        image.save(destination, quality=92)
