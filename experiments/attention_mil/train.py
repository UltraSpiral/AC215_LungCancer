"""Phase 3: train the gated attention head for every seed in frozen_config.json.

Reads only train and validation slides. Writes to a NEW output directory and
refuses to overwrite. Example, from the repository root:

    uv run --project experiments/attention_mil python -m experiments.attention_mil.train \
        --bundle local_data/cpu_bundle --config experiments/attention_mil/frozen_config.json \
        --out local_outputs/attention/native-<UTC>
"""
import argparse
import copy
import json
import os
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from scipy.stats import spearmanr

from lungcancer.common import CLASSES, checksum
from lungcancer.modeling import metric_report

from .data import Normalizer, bundle_identity, load_split, training_file_ids
from .model import build_model, count_parameters


def set_determinism(seed):
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)


def class_weights(slides):
    """n / (3 * n_class): rarer classes count a little more (squamous has 10, others 11)."""
    counts = np.bincount([s.label for s in slides], minlength=len(CLASSES))
    return torch.tensor(len(slides) / (len(CLASSES) * counts), dtype=torch.float32)


@torch.no_grad()
def evaluate(model, slides, inputs):
    """Full tiles, dropout off. Returns unweighted mean loss, metrics, probabilities, attention."""
    model.eval()
    losses, probabilities, attention = [], [], {}
    for slide, x in zip(slides, inputs):
        logits, alpha = model(x)
        losses.append(F.cross_entropy(logits[None], torch.tensor([slide.label])).item())
        probabilities.append(torch.softmax(logits, 0).numpy().astype(np.float64))
        attention[slide.file_id] = alpha.numpy()
    probabilities = np.array(probabilities)
    truth = np.array([s.label_name for s in slides])
    return {'loss': float(np.mean(losses)), 'metrics': metric_report(truth, probabilities),
            'probabilities': probabilities, 'attention': attention}


def train_one_seed(config, seed, train, validation, normalizer, max_epochs=None, log=print):
    set_determinism(seed)
    model = build_model(config['model'], seed)
    optimiser = torch.optim.AdamW(model.parameters(), lr=config['optimiser']['lr'],
                                  weight_decay=config['optimiser']['weight_decay'])
    weights = class_weights(train)
    generator = torch.Generator().manual_seed(seed)       # slide order + tile subsampling
    low, high = config['regularisation']['tile_subsampling']['keep_fraction_uniform']
    train_x = [torch.from_numpy(normalizer.transform(s.features)) for s in train]
    val_x = [torch.from_numpy(normalizer.transform(s.features)) for s in validation]
    patience = config['early_stopping']['patience']
    history, best, waited = [], None, 0

    for epoch in range(1, (max_epochs or config['max_epochs']) + 1):
        model.train()
        epoch_loss = 0.0
        for i in torch.randperm(len(train), generator=generator).tolist():
            x, label = train_x[i], train[i].label
            fraction = low + (high - low) * torch.rand(1, generator=generator).item()
            keep = torch.randperm(len(x), generator=generator)[:max(1, round(len(x) * fraction))]
            logits, _ = model(x[keep])
            # Weight applied by hand: with one slide per step, F.cross_entropy(weight=...)
            # divides by that same weight under 'mean' reduction and cancels it out.
            loss = F.cross_entropy(logits[None], torch.tensor([label])) * weights[label]
            optimiser.zero_grad()
            loss.backward()
            optimiser.step()
            epoch_loss += loss.item()
        val = evaluate(model, validation, val_x)
        history.append({'epoch': epoch, 'train_loss': epoch_loss / len(train),
                        'validation_loss': val['loss'],
                        'validation_macro_f1': val['metrics']['macro_f1']})
        if best is None or val['loss'] < best['loss']:
            best = {**val, 'epoch': epoch, 'state': copy.deepcopy(model.state_dict())}
            waited = 0
        else:
            waited += 1
            if waited >= patience:
                break
    log(f'seed {seed}: stopped after epoch {epoch}, best epoch {best["epoch"]}, '
        f'val loss {best["loss"]:.4f}, val macro-F1 {best["metrics"]["macro_f1"]:.3f}')
    return {'seed': seed, 'best': best, 'history': history, 'epochs_run': epoch}


def select_seed(summaries):
    """Frozen rule: highest val macro-F1, then lowest val loss, then lowest seed."""
    return min(summaries, key=lambda s: (-s['validation_macro_f1'], s['validation_loss'], s['seed']))['seed']


def attention_stability(results, validation):
    """Mean / min pairwise Spearman correlation of alpha across seeds, per validation slide."""
    out = {}
    for slide in validation:
        alphas = [r['best']['attention'][slide.file_id] for r in results]
        rhos = [spearmanr(alphas[i], alphas[j]).statistic
                for i in range(len(alphas)) for j in range(i + 1, len(alphas))]
        out[slide.file_id] = {'mean_spearman': float(np.mean(rhos)), 'min_spearman': float(np.min(rhos)),
                              'pairs': len(rhos)}
    return out


def logistic_baseline(bundle, validation):
    """Existing saved model on the same validation slides, read-only, for a continuous comparison."""
    import joblib
    from lungcancer.modeling import named_probabilities
    meta = json.loads((bundle / 'run/model/model.json').read_text())
    path = bundle / 'run/model/classifier.joblib'
    if checksum(path) != meta['classifier_sha256']:
        raise ValueError('saved classifier checksum mismatch')
    pooled = np.array([s.features.mean(axis=0, dtype=np.float64) for s in validation])
    # numpy 2.1 on macOS (Apple Accelerate) raises spurious divide/overflow flags in
    # matmul. The output is checked below against the predictions saved on 20 Oct.
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):
        probabilities = named_probabilities(joblib.load(path), pooled)
    saved = {r['file_id']: r['class_probabilities'] for r in
             json.loads((bundle / 'run/evaluation_validation/predictions.json').read_text())}
    expected = np.array([[saved[s.file_id][c] for c in CLASSES] for s in validation])
    if not np.isfinite(probabilities).all() or np.abs(probabilities - expected).max() > 1e-9:
        raise ValueError('logistic baseline does not reproduce the saved validation predictions')
    truth = np.array([s.label_name for s in validation])
    loss = -np.mean(np.log([probabilities[i, s.label] for i, s in enumerate(validation)]))
    report = metric_report(truth, probabilities)
    return {'validation_loss': float(loss), 'validation_macro_f1': report['macro_f1'],
            'validation_balanced_accuracy': report['balanced_accuracy'],
            'saved_model_json_validation_macro_f1': meta['validation']['macro_f1']}


def plot_curves(results, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for r in results:
        epochs = [h['epoch'] for h in r['history']]
        axes[0].plot(epochs, [h['train_loss'] for h in r['history']], alpha=0.8, label=f'seed {r["seed"]}')
        axes[1].plot(epochs, [h['validation_loss'] for h in r['history']], alpha=0.8, label=f'seed {r["seed"]}')
        axes[1].axvline(r['best']['epoch'], color=axes[1].lines[-1].get_color(), ls=':', lw=1)
    for ax, title in zip(axes, ['Training loss (weighted, subsampled tiles)', 'Validation loss (6 slides, all tiles)']):
        ax.set_title(title); ax.set_xlabel('epoch'); ax.grid(alpha=0.3)
    axes[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig)


SOURCES = ('data.py', 'model.py', 'train.py', 'heatmap.py', 'evaluate.py', 'compare_runs.py')


def git_commit():
    """Docker has no git: `make` passes the host commit in LC_ATTN_GIT_COMMIT."""
    if os.environ.get('LC_ATTN_GIT_COMMIT'):
        return os.environ['LC_ATTN_GIT_COMMIT']
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def source_hashes():
    here = Path(__file__).resolve().parent
    return {name: checksum(here / name) for name in SOURCES if (here / name).is_file()}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Train gated attention MIL for every frozen seed.')
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--max-epochs', type=int, help='testing only; overrides the frozen value')
    parser.add_argument('--authoritative', action='store_true',
                        help='official (Docker) run: record the rule-selected seed as chosen_seed')
    parser.add_argument('--require-arm64', action='store_true')
    args = parser.parse_args(argv)
    if args.require_arm64 and platform.machine().lower() not in {'aarch64', 'arm64'}:
        raise SystemExit(f'expected an arm64 machine, got {platform.machine()}')
    if args.out.exists():
        raise SystemExit(f'{args.out} already exists; refusing to overwrite a run')
    config = json.loads(args.config.read_text())

    started = time.time()
    identity = bundle_identity(args.bundle)
    train = load_split(args.bundle, 'train')
    validation = load_split(args.bundle, 'validation')
    normalizer = Normalizer.fit(train, training_file_ids(args.bundle))

    results = [train_one_seed(config, seed, train, validation, normalizer, args.max_epochs)
               for seed in config['seeds']]

    args.out.mkdir(parents=True)
    normalizer.save(args.out / 'normalization.npz')
    summaries = []
    for r in results:
        seed_dir = args.out / f'seed_{r["seed"]}'
        seed_dir.mkdir()
        torch.save(r['best']['state'], seed_dir / 'model.pt')
        np.savez(seed_dir / 'validation_attention.npz', **r['best']['attention'])
        (seed_dir / 'history.json').write_text(json.dumps(r['history'], indent=1))
        m = r['best']['metrics']
        summaries.append({
            'seed': r['seed'], 'best_epoch': r['best']['epoch'], 'epochs_run': r['epochs_run'],
            'validation_loss': r['best']['loss'], 'validation_macro_f1': m['macro_f1'],
            'validation_balanced_accuracy': m['balanced_accuracy'],
            'validation_confusion_matrix': m['confusion_matrix'],
            'validation_predictions': [
                {'file_id': s.file_id, 'true': s.label_name,
                 'predicted': CLASSES[int(np.argmax(p))],
                 'probabilities': dict(zip(CLASSES, map(float, p)))}
                for s, p in zip(validation, r['best']['probabilities'])],
            'model_pt_sha256': checksum(seed_dir / 'model.pt')})

    f1 = np.array([s['validation_macro_f1'] for s in summaries])
    loss = np.array([s['validation_loss'] for s in summaries])
    selected = select_seed(summaries)
    report = {
        'stage': ('authoritative Docker run (Phase 5)' if args.authoritative
                  else 'native exploratory run (Phase 3); Docker (Phase 5) is authoritative'),
        'seed_selection_rule': config['seed_selection_rule'],
        ('chosen_seed' if args.authoritative else 'native_preferred_seed'): selected,
        'seeds': summaries,
        'across_seeds': {'validation_macro_f1_mean': float(f1.mean()), 'validation_macro_f1_sd': float(f1.std(ddof=1)),
                         'validation_loss_mean': float(loss.mean()), 'validation_loss_sd': float(loss.std(ddof=1))},
        'attention_stability_validation': attention_stability(results, validation),
        'logistic_regression_baseline': logistic_baseline(args.bundle, validation),
    }
    (args.out / 'seed_search.json').write_text(json.dumps(report, indent=1))
    plot_curves(results, args.out / 'training_curves.png')
    run = {
        'config_path': str(args.config), 'config_sha256': checksum(args.config), 'config': config,
        'git_commit': git_commit(), 'source_sha256': source_hashes(), 'split_identifier': identity['split_identifier'],
        'split_file_sha256': identity['split_file_sha256'],
        'encoder_identifier': identity['encoder_identifier'],
        'preprocessing_config': identity['preprocessing_config'],
        'parameters': count_parameters(build_model(config['model'], 0)),
        'max_epochs_override': args.max_epochs, 'authoritative': args.authoritative,
        'versions': {'python': platform.python_version(), 'torch': torch.__version__, 'numpy': np.__version__},
        'platform': f'{platform.system()} {platform.machine()}',
        'elapsed_seconds': round(time.time() - started, 1),
        'test_split_accessed': False,
    }
    (args.out / 'run.json').write_text(json.dumps(run, indent=1))
    print(f'wrote {args.out} in {run["elapsed_seconds"]} s; '
          f'{"chosen" if args.authoritative else "native preferred"} seed {selected}')
    return report


if __name__ == '__main__':
    main()
