"""Export the authoritative attention model to torch-free numpy weights for the app.

    uv run --project experiments/attention_mil python -m experiments.attention_mil.export_for_app \
        --bundle local_data/cpu_bundle --run local_outputs/attention/docker --out local_outputs/attention_app

Writes <out>/{attention_head.npz, manifest.json} and refuses to overwrite. The app mounts
<out> read-only; it is kept outside run directories so a mount can never create one.
Parity: the numpy head (backend/attention.py) must reproduce the torch model on the
train + validation slides and on sample.svs, or nothing is written.
"""
import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from backend.attention import WEIGHT_SHAPES, AttentionHead, _sha256
from lungcancer.common import CLASSES, checksum

from .data import Normalizer, load_slide, load_split
from .model import build_model

SAMPLE_ID = 'a2e48dce-1874-468d-a302-fd30b3107f4a'
STATE_KEYS = {'embed_weight': 'embed.0.weight', 'embed_bias': 'embed.0.bias',
              'v_weight': 'attention_v.weight', 'v_bias': 'attention_v.bias',
              'u_weight': 'attention_u.weight', 'u_bias': 'attention_u.bias',
              'w_weight': 'attention_w.weight', 'cls_weight': 'classifier.1.weight',
              'cls_bias': 'classifier.1.bias'}
TOLERANCE = 1e-5


def main(argv=None):
    parser = argparse.ArgumentParser(description='Export the chosen attention model for the app.')
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out
    if out.exists():
        raise SystemExit(f'{out} exists; refusing to overwrite')
    search = json.loads((args.run / 'seed_search.json').read_text())
    if 'chosen_seed' not in search:
        raise SystemExit('only an authoritative run (with chosen_seed) can be exported')
    seed = search['chosen_seed']
    entry = next(s for s in search['seeds'] if s['seed'] == seed)
    model_path = args.run / f'seed_{seed}' / 'model.pt'
    if checksum(model_path) != entry['model_pt_sha256']:
        raise SystemExit('chosen model file changed since training')
    run = json.loads((args.run / 'run.json').read_text())

    state = torch.load(model_path, weights_only=True)
    normalizer = Normalizer.load(args.run / 'normalization.npz')
    weights = {k: state[v].numpy().astype(np.float32) for k, v in STATE_KEYS.items()}
    weights['norm_mean'], weights['norm_std'] = normalizer.mean, normalizer.std
    assert {k: v.shape for k, v in weights.items()} == WEIGHT_SHAPES

    torch_model = build_model(run['config']['model'], seed)
    torch_model.load_state_dict(state)
    torch_model.eval()
    slides = load_split(args.bundle, 'train') + load_split(args.bundle, 'validation')
    slides.append(load_slide(args.bundle, SAMPLE_ID, allow_test=True)[0])   # what the app will show

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        np.savez(tmp / 'attention_head.npz', **weights)
        digest = _sha256(tmp / 'attention_head.npz')
        manifest = {'model_identifier': digest, 'npz_sha256': digest}
        (tmp / 'manifest.json').write_text(json.dumps(manifest))
        head = AttentionHead.load(tmp)
        prob_diff = alpha_diff = 0.0
        with torch.no_grad():
            for s in slides:
                logits, alpha = torch_model(torch.from_numpy(normalizer.transform(s.features)))
                probs_np, alpha_np = head.forward(s.features)
                prob_diff = max(prob_diff, float(np.abs(torch.softmax(logits, 0).numpy() - probs_np).max()))
                alpha_diff = max(alpha_diff, float(np.abs(alpha.numpy() - alpha_np).max()))
        sample_probs, _ = head.forward(slides[-1].features)
    if prob_diff > TOLERANCE or alpha_diff > TOLERANCE:
        raise SystemExit(f'numpy head does not reproduce torch: probs {prob_diff:.2e}, alpha {alpha_diff:.2e}')

    test = json.loads((args.run / 'test.json').read_text()) if (args.run / 'test.json').exists() else None
    out.mkdir()
    np.savez(out / 'attention_head.npz', **weights)
    digest = _sha256(out / 'attention_head.npz')
    manifest = {
        'format_version': 1, 'model_identifier': digest, 'npz_sha256': digest,
        'architecture': 'gated attention MIL (Ilse et al. 2018), hidden 256, attention 128',
        'classes': list(CLASSES), 'chosen_seed': seed, 'model_pt_sha256': entry['model_pt_sha256'],
        'source_run': str(args.run), 'source_git_commit': run.get('git_commit'),
        'encoder_identifier': run['encoder_identifier'], 'split_identifier': run['split_identifier'],
        'validation_macro_f1': entry['validation_macro_f1'], 'validation_loss': entry['validation_loss'],
        'test_macro_f1': test['attention']['metrics']['macro_f1'] if test else None,
        'parity_vs_torch': {'slides': len(slides), 'max_abs_probability_diff': prob_diff,
                            'max_abs_alpha_diff': alpha_diff, 'tolerance': TOLERANCE},
        'sample_slide_probabilities': dict(zip(CLASSES, map(float, sample_probs))),
        'probabilities_calibrated': False,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    print(json.dumps(manifest, indent=1))
    return manifest


if __name__ == '__main__':
    main()
