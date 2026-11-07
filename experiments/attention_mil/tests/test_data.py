import json
import shutil
from collections import Counter

import numpy as np
import pytest

from experiments.attention_mil.data import (
    Normalizer, LockedTestSplit, bundle_identity, load_split, training_file_ids)

SAMPLE_ID = 'a2e48dce-1874-468d-a302-fd30b3107f4a'


@pytest.fixture(scope='module')
def train(bundle):
    return load_split(bundle, 'train')


@pytest.fixture(scope='module')
def validation(bundle):
    return load_split(bundle, 'validation')


def test_development_splits_match_saved_model(train, validation):
    assert len(train) == 32 and len(validation) == 6
    assert Counter(s.label_name for s in train) == {'non_tumor': 11, 'adenocarcinoma': 11, 'squamous': 10}
    assert Counter(s.label_name for s in validation) == {'non_tumor': 2, 'adenocarcinoma': 2, 'squamous': 2}
    for s in train + validation:
        assert s.features.dtype == np.float32 and s.features.shape[1] == 1536
        assert len(s.features) == len(s.coords) > 0
        assert len(s.footprint) == 2 and min(s.footprint) > 0


def test_no_patient_or_slide_shared_between_train_and_validation(train, validation):
    assert not {s.case_id for s in train} & {s.case_id for s in validation}
    assert not {s.file_id for s in train} & {s.file_id for s in validation}


def test_test_split_is_locked_unless_explicitly_allowed(bundle):
    with pytest.raises(LockedTestSplit):
        load_split(bundle, 'test')
    test = load_split(bundle, 'test', allow_test=True)
    assert len(test) == 6 and SAMPLE_ID in {s.file_id for s in test}


def test_modified_split_file_is_rejected(bundle, tmp_path):
    (tmp_path / 'run/model').mkdir(parents=True)
    shutil.copy(bundle / 'run/model/model.json', tmp_path / 'run/model/model.json')
    split = json.loads((bundle / 'run/splits.json').read_text())
    split['slides'][0]['split'] = 'validation'   # move one training slide
    (tmp_path / 'run/splits.json').write_text(json.dumps(split))
    with pytest.raises(ValueError, match='splits.json differs'):
        bundle_identity(tmp_path)


def test_normalizer_uses_training_slides_only(bundle, train, validation):
    with pytest.raises(ValueError, match='exactly the training slides'):
        Normalizer.fit(validation, training_file_ids(bundle))
    norm = Normalizer.fit(train, training_file_ids(bundle))
    tiles = norm.transform(np.concatenate([s.features for s in train]))
    assert np.allclose(tiles.mean(axis=0), 0, atol=1e-3)
    assert np.allclose(tiles.std(axis=0), 1, atol=1e-3)


def test_normalizer_round_trip_and_constant_dimension(tmp_path):
    from experiments.attention_mil.data import Slide
    features = np.random.default_rng(0).normal(size=(10, 1536)).astype(np.float32)
    features[:, 0] = 3.0   # constant dimension: std floored, no division by zero
    slide = Slide('a', 'p', 0, features, np.zeros((10, 2), int), (223, 223), (1000, 1000))
    norm = Normalizer.fit([slide], ['a'])
    assert np.isfinite(norm.transform(features)).all()
    norm.save(tmp_path / 'norm.npz')
    loaded = Normalizer.load(tmp_path / 'norm.npz')
    assert np.array_equal(loaded.mean, norm.mean) and np.array_equal(loaded.std, norm.std)
