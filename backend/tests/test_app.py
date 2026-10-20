"""Trust-boundary/error fixtures; the one real prediction is explicitly identified."""
from pathlib import Path
import copy
import hashlib
import json
import threading
import time

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app import MAX_REQUEST_BYTES, create_app
from backend.model import CachedClassifier, MODEL_ID, SOURCE_SHA, UnsupportedSlide
from lungcancer.common import CLASSES, read_json

BUNDLE = Path('/inputs')


@pytest.fixture(scope='session')
def real_model():
    return CachedClassifier(BUNDLE)


def test_real_saved_classifier_matches_the_one_frozen_reference(real_model):
    result = real_model.predict(SOURCE_SHA, real_model.sample['bytes'], real_model.sample['md5sum'])
    references = read_json(BUNDLE / 'run/evaluation_test/predictions.json')
    reference = next(r for r in references if r['file_id'] == real_model.sample['file_id'])
    np.testing.assert_allclose([result['class_probabilities'][c] for c in CLASSES],
                               [reference['class_probabilities'][c] for c in CLASSES], rtol=0, atol=1e-8)
    assert result['model_identifier'] == MODEL_ID
    assert result['tiles_analyzed'] == 512
    assert result['uni2_encoding_performed'] is False
    assert result['probabilities_calibrated'] is False


def test_unknown_content_cannot_select_a_real_cache(real_model):
    with pytest.raises(UnsupportedSlide):
        real_model.predict('0' * 64, real_model.sample['bytes'], real_model.sample['md5sum'])


def test_corrupt_bundle_fails_before_joblib_deserialization(tmp_path, monkeypatch):
    target = tmp_path / 'run/model/classifier.joblib'
    target.parent.mkdir(parents=True)
    target.write_bytes(b'not a trusted classifier')
    manifest = read_json(BUNDLE / 'manifest.json')
    entry = next(e for e in manifest['files'] if e['path'] == 'run/model/classifier.joblib')
    (tmp_path / 'manifest.json').write_text(json.dumps({'files': [entry]}))
    def forbidden(*args, **kwargs):
        pytest.fail('Corrupt data reached joblib.load')
    monkeypatch.setattr('backend.model.joblib.load', forbidden)
    with pytest.raises(ValueError, match='bundle_checksum_mismatch'):
        CachedClassifier(tmp_path)


def test_incompatible_model_identity_fails_before_deserialization(monkeypatch):
    from backend import model
    original = model.read_json
    def modified(path):
        data = original(path)
        if str(path).endswith('run/model/model.json'):
            data = {**data, 'model_identifier': 'incompatible'}
        return data
    monkeypatch.setattr(model, 'read_json', modified)
    monkeypatch.setattr(model.joblib, 'load', lambda *a: pytest.fail('Incompatible model was loaded'))
    with pytest.raises(ValueError, match='incompatible_model_or_split'):
        CachedClassifier(BUNDLE)


def test_corrupt_cached_vectors_produce_no_prediction(real_model, tmp_path):
    import shutil
    bad = copy.copy(real_model)
    bad.bundle = tmp_path
    bad.directory = tmp_path / 'slides' / real_model.row['file_id']
    shutil.copytree(real_model.directory, bad.directory)
    path = bad.directory / 'embeddings.npz'
    raw = bytearray(path.read_bytes()); raw[-20] ^= 1; path.write_bytes(raw)
    with pytest.raises(ValueError, match='cached_features_checksum_mismatch'):
        bad.predict(SOURCE_SHA, bad.sample['bytes'], bad.sample['md5sum'])


class ErrorFixture:
    """Synthetic failure fixture only; it never returns a predicted class."""
    def __init__(self, *, fail=False, entered=None, release=None):
        self.fail, self.entered, self.release = fail, entered, release
    def create_overlay(self, destination):
        destination.write_bytes(b'unit-test placeholder; never presented as real-slide evidence')
    def predict(self, *identity):
        if self.entered:
            self.entered.set()
            assert self.release.wait(5)
        if self.fail:
            raise ValueError('corrupt cache fixture')
        raise UnsupportedSlide('Unsupported slide: no verified preprocessed features match these file bytes.')


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(output=tmp_path, model_factory=lambda _: ErrorFixture())) as c:
        yield c


def wait_job(client, key):
    for _ in range(100):
        job = client.get('/jobs/' + key).json()
        if job['status'] in {'failed', 'done'}:
            return job
        time.sleep(0.01)
    pytest.fail('job did not complete')


@pytest.mark.parametrize('files', [None, {'slide': ('empty.svs', b'')}, {'slide': ('wrong.txt', b'bytes')}])
def test_bad_upload_has_an_explicit_error_and_no_prediction(client, files):
    response = client.post('/jobs', files=files)
    assert response.status_code in {400, 415}
    assert response.json()['status'] == 'error'
    assert response.json()['reason']
    assert 'predicted_class' not in response.text


def test_declared_oversized_upload_is_rejected_before_reading(client):
    response = client.post('/jobs', content=b'', headers={
        'content-type': 'multipart/form-data; boundary=x', 'content-length': str(MAX_REQUEST_BYTES + 1)})
    assert response.status_code == 413
    assert response.json()['status'] == 'error'
    assert 'predicted_class' not in response.text


def test_stream_without_content_length_cannot_bypass_limit(client, monkeypatch):
    monkeypatch.setattr('backend.app.MAX_REQUEST_BYTES', 16)
    response = client.post('/jobs', content=iter([b'a' * 10, b'b' * 10]),
                           headers={'content-type': 'multipart/form-data; boundary=x'})
    assert response.status_code == 413


def test_unknown_input_and_path_like_filename_fail_without_result(client):
    response = client.post('/jobs', files={'slide': ('../../TCGA-LUAD-tumor.svs', b'unprocessed bytes')},
                           data={'case_id': 'squamous'})
    assert response.status_code == 202
    key = response.json()['job_id']
    assert len(key) == 32 and all(c in '0123456789abcdef' for c in key)
    job = wait_job(client, key)
    assert job['status'] == 'failed'
    assert 'Unsupported slide' in job['error']
    assert 'result' not in job and 'predicted_class' not in job
    assert client.get('/jobs/' + key + '/overlay').status_code == 404


def test_runtime_cache_failure_has_no_result(tmp_path):
    with TestClient(create_app(output=tmp_path, model_factory=lambda _: ErrorFixture(fail=True))) as c:
        key = c.post('/jobs', files={'slide': ('sample.svs', b'fixture')}).json()['job_id']
        job = wait_job(c, key)
        assert job['status'] == 'failed' and job['reason'] == 'cached_input_verification_failed'
        assert 'result' not in job


def test_cancelled_job_cannot_be_overwritten_by_worker(tmp_path):
    entered, release = threading.Event(), threading.Event()
    with TestClient(create_app(output=tmp_path,
                              model_factory=lambda _: ErrorFixture(entered=entered, release=release))) as c:
        key = c.post('/jobs', files={'slide': ('sample.svs', b'fixture')}).json()['job_id']
        assert entered.wait(5)
        cancelled = c.delete('/jobs/' + key).json()
        release.set()
        assert cancelled['status'] == 'failed' and cancelled['reason'] == 'cancelled'
        assert wait_job(c, key)['reason'] == 'cancelled'


def test_missing_job_never_exposes_an_arbitrary_file(client):
    response = client.get('/jobs/not-a-real-job')
    assert response.status_code == 404
    assert response.json()['status'] == 'error'
