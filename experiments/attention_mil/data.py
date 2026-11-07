"""Phase 1 data module: verified cached slides in, model-ready arrays out.

Every slide passes the repository's own read-only checks (the same ones the
saved logistic-regression model and the app use), so the attention model sees
exactly the data the existing model saw. Nothing here writes to the bundle.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from lungcancer.common import CLASSES, checksum, read_json
from lungcancer.features import load_features
from lungcancer.modeling import check_patient_separation
from lungcancer.modeling_run import verify_cache
from lungcancer.preprocess import TileConfig

DEVELOPMENT_SPLITS = ('train', 'validation')


class LockedTestSplit(PermissionError):
    """Raised when code outside the single test evaluation asks for test slides."""


@dataclass(frozen=True)
class Slide:
    file_id: str
    case_id: str
    label: int                 # index into CLASSES
    features: np.ndarray       # [n_tiles, 1536] float32, raw (not normalised)
    coords: np.ndarray         # [n_tiles, 2] level-0 upper-left x, y in pixels
    footprint: tuple           # level-0 tile width, height in pixels (223, 223)
    dimensions: tuple          # level-0 slide width, height in pixels

    @property
    def label_name(self):
        return CLASSES[self.label]


def bundle_identity(bundle):
    """Identities every slide must share with the saved model (read from model.json)."""
    bundle = Path(bundle)
    model = read_json(bundle / 'run/model/model.json')
    split_path = bundle / 'run/splits.json'
    # Same split file the existing model was trained on, byte for byte.
    if checksum(split_path) != model['split_file_sha256']:
        raise ValueError('splits.json differs from the one the saved model used')
    split = read_json(split_path)
    if split['split_identifier'] != model['split_identifier']:
        raise ValueError('split identifier differs from the saved model')
    check_patient_separation(split['slides'])
    return {
        'split_rows': split['slides'],
        'split_identifier': split['split_identifier'],
        'split_file_sha256': model['split_file_sha256'],
        'encoder_identifier': model['encoder_identifier'],
        'preprocessing_config': model['preprocessing_config'],
    }


def load_split(bundle, split_name, *, allow_test=False):
    """Return the verified slides of one split, in splits.json order.

    Test slides are locked: only the single test-evaluation command passes
    allow_test=True. Training and model selection can therefore never read them.
    """
    if split_name not in (*DEVELOPMENT_SPLITS, 'test'):
        raise ValueError(f'unknown split {split_name!r}')
    if split_name == 'test' and not allow_test:
        raise LockedTestSplit('test slides are reserved for the single test evaluation')
    bundle = Path(bundle)
    identity = bundle_identity(bundle)
    config = TileConfig(**identity['preprocessing_config'])
    slides = []
    for row in identity['split_rows']:
        if row['split'] != split_name:
            continue
        directory = bundle / 'slides' / row['file_id']
        # verify_cache: file hashes, md5/file_id identity, preprocessing + encoder fingerprint.
        prep, meta = verify_cache(row, directory, config, identity['encoder_identifier'])
        features, coords, embedded = load_features(directory / 'embeddings.npz')
        if (embedded['encoder_identifier'] != identity['encoder_identifier'] or
                embedded['preprocessing_config'] != identity['preprocessing_config']):
            raise ValueError(f'feature provenance mismatch for {row["file_id"]}')
        slides.append(Slide(
            file_id=row['file_id'], case_id=row['case_id'],
            label=CLASSES.index(row['candidate_class']),
            features=features, coords=coords,
            footprint=tuple(prep['geometry']['footprint_level0']),
            dimensions=tuple(prep['dimensions_level0'])))
    if not slides:
        raise ValueError(f'no slides in split {split_name!r}')
    return slides


class Normalizer:
    """Per-dimension standardisation fitted on TRAINING tiles only.

    Fitting on validation or test tiles would leak their statistics into the
    model, so fit() refuses anything that is not the training split.
    """
    EPS = 1e-6

    def __init__(self, mean, std):
        self.mean = np.asarray(mean, dtype=np.float32)
        self.std = np.asarray(std, dtype=np.float32)

    @classmethod
    def fit(cls, train_slides, train_file_ids):
        if {s.file_id for s in train_slides} != set(train_file_ids):
            raise ValueError('Normalizer must be fitted on exactly the training slides')
        tiles = np.concatenate([s.features for s in train_slides]).astype(np.float64)
        return cls(tiles.mean(axis=0), np.maximum(tiles.std(axis=0), cls.EPS))

    def transform(self, features):
        return ((features - self.mean) / self.std).astype(np.float32)

    def save(self, path):
        np.savez(path, mean=self.mean, std=self.std)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as data:
            return cls(data['mean'], data['std'])


def training_file_ids(bundle):
    return [r['file_id'] for r in bundle_identity(bundle)['split_rows'] if r['split'] == 'train']
