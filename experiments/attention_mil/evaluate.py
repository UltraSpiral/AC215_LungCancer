"""Phase 5: the single test evaluation of the rule-chosen attention model.

Runs once per official run: refuses non-authoritative runs, a changed model file,
or an existing test.json. Example (inside the attention container):

    python -m experiments.attention_mil.evaluate --bundle /inputs --run /outputs/docker
"""
import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from lungcancer.common import CLASSES, checksum
from lungcancer.modeling import metric_report, named_probabilities

from .data import Normalizer, load_split
from .model import build_model
from .train import source_hashes


def logistic_test_report(bundle, slides):
    """Existing model on the same test slides, verified against its saved predictions."""
    import joblib
    meta = json.loads((bundle / 'run/model/model.json').read_text())
    path = bundle / 'run/model/classifier.joblib'
    if checksum(path) != meta['classifier_sha256']:
        raise ValueError('saved classifier checksum mismatch')
    pooled = np.array([s.features.mean(axis=0, dtype=np.float64) for s in slides])
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):   # macOS Accelerate false flags
        probabilities = named_probabilities(joblib.load(path), pooled)
    saved = {r['file_id']: r['class_probabilities'] for r in
             json.loads((bundle / 'run/evaluation_test/predictions.json').read_text())}
    expected = np.array([[saved[s.file_id][c] for c in CLASSES] for s in slides])
    if not np.isfinite(probabilities).all() or np.abs(probabilities - expected).max() > 1e-9:
        raise ValueError('logistic baseline does not reproduce the saved test predictions')
    truth = np.array([s.label_name for s in slides])
    loss = -np.mean(np.log([probabilities[i, s.label] for i, s in enumerate(slides)]))
    return {'metrics': metric_report(truth, probabilities), 'test_loss': float(loss),
            'training_majority_class': meta['training_majority_class']}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Single test evaluation of the chosen attention model.')
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--require-arm64', action='store_true')
    args = parser.parse_args(argv)
    if args.require_arm64 and platform.machine().lower() not in {'aarch64', 'arm64'}:
        raise SystemExit(f'expected an arm64 machine, got {platform.machine()}')
    out = args.run / 'test.json'
    if out.exists():
        raise SystemExit(f'{out} exists; refusing to repeat the test evaluation')
    search = json.loads((args.run / 'seed_search.json').read_text())
    if 'chosen_seed' not in search:
        raise SystemExit('run has no chosen_seed: only an authoritative (Docker) run may be tested')
    seed = search['chosen_seed']
    summary = next(s for s in search['seeds'] if s['seed'] == seed)
    model_path = args.run / f'seed_{seed}' / 'model.pt'
    if checksum(model_path) != summary['model_pt_sha256']:
        raise SystemExit('chosen model file changed since training')
    config = json.loads((args.run / 'run.json').read_text())['config']

    model = build_model(config['model'], seed)
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    normalizer = Normalizer.load(args.run / 'normalization.npz')

    # The one place in the experiment that opens the test split.
    slides = load_split(args.bundle, 'test', allow_test=True)
    probabilities, losses = [], []
    with torch.no_grad():
        for s in slides:
            logits, _ = model(torch.from_numpy(normalizer.transform(s.features)))
            losses.append(torch.nn.functional.cross_entropy(logits[None], torch.tensor([s.label])).item())
            probabilities.append(torch.softmax(logits, 0).numpy().astype(np.float64))
    probabilities = np.array(probabilities)
    truth = np.array([s.label_name for s in slides])
    logistic = logistic_test_report(args.bundle, slides)
    majority = np.zeros_like(probabilities)
    majority[:, CLASSES.index(logistic['training_majority_class'])] = 1

    report = {
        'evaluated_at': datetime.now(timezone.utc).isoformat(), 'chosen_seed': seed,
        'model_pt_sha256': summary['model_pt_sha256'],
        'attention': {'metrics': metric_report(truth, probabilities), 'test_loss': float(np.mean(losses))},
        'logistic_regression_existing': logistic,
        'majority_baseline': {'metrics': metric_report(truth, majority)},
        'predictions': [{'file_id': s.file_id, 'case_id': s.case_id, 'true': s.label_name,
                         'predicted': CLASSES[int(np.argmax(p))],
                         'probabilities': dict(zip(CLASSES, map(float, p)))}
                        for s, p in zip(slides, probabilities)],
        'caveats': ['6 test slides, 2 per class: one error moves accuracy by 16.7 points.',
                    'The same test slides were evaluated earlier with the mean-pool model; not a pristine test set.'],
        'platform': f'{platform.system()} {platform.machine()}', 'torch': torch.__version__,
        'source_sha256': source_hashes(),
    }
    out.write_text(json.dumps(report, indent=1))
    a, l = report['attention']['metrics'], logistic['metrics']
    print(f'test macro-F1: attention {a["macro_f1"]:.3f} vs existing {l["macro_f1"]:.3f}; '
          f'test loss {report["attention"]["test_loss"]:.3f} vs {logistic["test_loss"]:.3f}; wrote {out}')
    return report


if __name__ == '__main__':
    main()
