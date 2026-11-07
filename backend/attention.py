"""Torch-free gated attention head for the app (exported from experiments/attention_mil).

Same math as experiments/attention_mil/model.py, in numpy float64:
    h = relu(W_in x + b);  a = w . (tanh(V h) * sigmoid(U h));  alpha = softmax(a)
    z = sum_i alpha_i h_i;  logits = W_out z + b_out
The existing logistic model remains the app's prediction; this adds a second
opinion and the per-tile attention used for the heatmap.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from scipy.stats import rankdata

WEIGHT_SHAPES = {
    'embed_weight': (256, 1536), 'embed_bias': (256,),
    'v_weight': (128, 256), 'v_bias': (128,), 'u_weight': (128, 256), 'u_bias': (128,),
    'w_weight': (1, 128), 'cls_weight': (3, 256), 'cls_bias': (3,),
    'norm_mean': (1536,), 'norm_std': (1536,),
}
# Frontend design tokens --color-heatmap-low/mid/high (frontend/src/styles/tokens.css).
HEATMAP_LOW, HEATMAP_MID, HEATMAP_HIGH = '#1e46ff', '#0090ff', '#00f0ff'
DISCLAIMER = 'Attention over a 512-tile sample of tissue; not a tumor segmentation.'


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _softmax(values):
    shifted = np.exp(values - values.max())
    return shifted / shifted.sum()


class AttentionHead:
    def __init__(self, weights, manifest):
        for key, shape in WEIGHT_SHAPES.items():
            if weights[key].shape != shape or not np.isfinite(weights[key]).all():
                raise ValueError(f'invalid_attention_weight_{key}')
        self.weights = {k: v.astype(np.float64) for k, v in weights.items()}
        self.manifest = manifest
        self.model_identifier = manifest['model_identifier']

    @classmethod
    def load(cls, directory):
        """Verify the export's checksum before reading any weights."""
        directory = Path(directory)
        manifest = json.loads((directory / 'manifest.json').read_text())
        weights_path = directory / 'attention_head.npz'
        if _sha256(weights_path) != manifest['npz_sha256'] or manifest['npz_sha256'] != manifest['model_identifier']:
            raise ValueError('attention_export_checksum_mismatch')
        with np.load(weights_path, allow_pickle=False) as data:
            weights = {k: data[k] for k in WEIGHT_SHAPES}
        return cls(weights, manifest)

    def forward(self, features):
        """features [n, 1536] raw UNI2-h vectors -> (class probabilities [3], alpha [n])."""
        w = self.weights
        x = (np.asarray(features, dtype=np.float64) - w['norm_mean']) / w['norm_std']
        h = np.maximum(x @ w['embed_weight'].T + w['embed_bias'], 0)
        gate = np.tanh(h @ w['v_weight'].T + w['v_bias']) / (1 + np.exp(-(h @ w['u_weight'].T + w['u_bias'])))
        alpha = _softmax((gate @ w['w_weight'].T)[:, 0])
        logits = (alpha @ h) @ w['cls_weight'].T + w['cls_bias']
        return _softmax(logits), alpha


def rank_normalise(alpha):
    """Within-slide percentile in (0, 1]: colours compare tiles of THIS slide only."""
    return rankdata(alpha, method='average') / len(alpha)


def _rgb(colour):
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


def _ramp(value):
    stops = [np.array(_rgb(c), float) for c in (HEATMAP_LOW, HEATMAP_MID, HEATMAP_HIGH)]
    position = float(np.clip(value, 0, 1)) * 2
    i = min(int(position), 1)
    return tuple(int(round(v)) for v in stops[i] + (position - i) * (stops[i + 1] - stops[i]))


def render_heatmap(thumbnail, coordinates, footprint, dimensions, alpha, destination, top_fraction=0.10):
    """Colour each analysed tile by attention rank; outline the top 10% in white.
    Tissue that was never sampled is left uncoloured (it was not analysed)."""
    from PIL import Image, ImageDraw
    ranks = rank_normalise(alpha)
    cutoff = np.quantile(ranks, 1 - top_fraction)
    sx, sy = thumbnail.width / dimensions[0], thumbnail.height / dimensions[1]
    layer = Image.new('RGBA', thumbnail.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for (x, y), rank in zip(coordinates, ranks):
        box = (x * sx, y * sy, (x + footprint[0]) * sx, (y + footprint[1]) * sy)
        top = rank >= cutoff
        draw.rectangle(box, fill=(*_ramp(rank), 230 if top else 150),
                       outline=(255, 255, 255, 255) if top else None, width=2 if top else 1)
    image = Image.alpha_composite(thumbnail.convert('RGBA'), layer).convert('RGB')
    image.save(destination, quality=92)
    return {'top_fraction': top_fraction, 'top_tiles': int((ranks >= cutoff).sum())}
