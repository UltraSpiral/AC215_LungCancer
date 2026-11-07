"""Attention heatmap integration: numpy head behaviour, fail-soft app, real export when mounted."""
import json
import os
from pathlib import Path

import numpy as np
import pytest

from backend.app import AttentionView
from backend.attention import WEIGHT_SHAPES, AttentionHead, _sha256, rank_normalise

EXPORT = Path(os.environ.get('LC_APP_ATTENTION', '/attention'))


def synthetic_head(tmp_path, zero_attention=False):
    rng = np.random.default_rng(0)
    weights = {k: rng.normal(scale=0.05, size=s).astype(np.float32) for k, s in WEIGHT_SHAPES.items()}
    weights['norm_std'] = np.ones(1536, np.float32)
    if zero_attention:
        weights['w_weight'][:] = 0
    np.savez(tmp_path / 'attention_head.npz', **weights)
    digest = _sha256(tmp_path / 'attention_head.npz')
    (tmp_path / 'manifest.json').write_text(json.dumps({'model_identifier': digest, 'npz_sha256': digest}))
    return AttentionHead.load(tmp_path)


def test_outputs_are_distributions_and_tile_order_does_not_matter(tmp_path):
    head = synthetic_head(tmp_path)
    x = np.random.default_rng(1).normal(size=(40, 1536))
    probs, alpha = head.forward(x)
    assert np.isclose(probs.sum(), 1) and np.isclose(alpha.sum(), 1) and (alpha >= 0).all()
    order = np.random.default_rng(2).permutation(40)
    probs2, alpha2 = head.forward(x[order])
    assert np.allclose(probs, probs2) and np.allclose(alpha[order], alpha2)


def test_equal_scores_give_uniform_attention(tmp_path):
    _, alpha = synthetic_head(tmp_path, zero_attention=True).forward(np.ones((8, 1536)))
    assert np.allclose(alpha, 1 / 8)


def test_tampered_export_is_rejected_before_use(tmp_path):
    synthetic_head(tmp_path)
    with open(tmp_path / 'attention_head.npz', 'ab') as f:
        f.write(b'x')
    with pytest.raises(ValueError, match='checksum_mismatch'):
        AttentionHead.load(tmp_path)


def test_rank_normalise_orders_tiles():
    assert list(np.argsort(rank_normalise(np.array([0.1, 0.5, 0.2])))) == [0, 2, 1]


def test_missing_export_leaves_attention_off(tmp_path):
    view = AttentionView(model=None, directory=tmp_path / 'absent', output=tmp_path)
    assert view.head is None and view.result('job', 'non_tumor') is None
    assert view.reason == 'no attention export mounted'


@pytest.mark.skipif(not (EXPORT / 'manifest.json').is_file(), reason='attention export not mounted')
def test_real_export_reproduces_its_manifest_on_the_supplied_slide(tmp_path):
    from backend.model import CachedClassifier
    model = CachedClassifier(Path('/inputs'))
    view = AttentionView(model, EXPORT, tmp_path)
    assert view.head is not None, view.reason
    manifest = json.loads((EXPORT / 'manifest.json').read_text())
    for c, p in manifest['sample_slide_probabilities'].items():
        assert abs(view.summary['class_probabilities'][c] - p) < 1e-9
    result = view.result('abc', 'non_tumor')
    assert result['predicted_class'] == 'non_tumor' and result['agrees_with_default_model']
    assert result['heatmap'] == '/api/jobs/abc/heatmap' and result['top_tiles_outlined'] == 52
    assert (tmp_path / 'attention_heatmap.jpg').stat().st_size > 10_000
