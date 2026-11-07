"""Phase 5: how closely does the Docker (Linux) run reproduce the native (macOS) run?

    uv run --project experiments/attention_mil python -m experiments.attention_mil.compare_runs \
        --native local_outputs/attention/native-<UTC> --docker local_outputs/attention/docker
"""
import argparse
import json
from pathlib import Path

import numpy as np


def compare(native, docker):
    n = json.loads((native / 'seed_search.json').read_text())
    d = json.loads((docker / 'seed_search.json').read_text())
    native_seeds = {s['seed']: s for s in n['seeds']}
    per_seed = {}
    for ds in d['seeds']:
        ns, seed = native_seeds[ds['seed']], ds['seed']
        with np.load(native / f'seed_{seed}/validation_attention.npz') as a, \
                np.load(docker / f'seed_{seed}/validation_attention.npz') as b:
            alpha_diff = max(float(np.abs(a[k] - b[k]).max()) for k in a.files)
        per_seed[seed] = {
            'same_best_epoch': ns['best_epoch'] == ds['best_epoch'],
            'same_validation_predictions': [p['predicted'] for p in ns['validation_predictions']] ==
                                           [p['predicted'] for p in ds['validation_predictions']],
            'validation_macro_f1_native_docker': [ns['validation_macro_f1'], ds['validation_macro_f1']],
            'validation_loss_abs_diff': abs(ns['validation_loss'] - ds['validation_loss']),
            'max_abs_alpha_diff': alpha_diff,
        }
    with np.load(native / 'normalization.npz') as a, np.load(docker / 'normalization.npz') as b:
        norm_diff = max(float(np.abs(a[k] - b[k]).max()) for k in a.files)
    return {
        'native_run': str(native), 'docker_run': str(docker),
        'native_preferred_seed': n.get('native_preferred_seed'), 'docker_chosen_seed': d.get('chosen_seed'),
        'same_seed_selected': n.get('native_preferred_seed') == d.get('chosen_seed'),
        'normalization_max_abs_diff': norm_diff,
        'per_seed': per_seed,
        'max_abs_alpha_diff_all_seeds': max(v['max_abs_alpha_diff'] for v in per_seed.values()),
        'max_validation_loss_abs_diff': max(v['validation_loss_abs_diff'] for v in per_seed.values()),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--docker', type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.docker / 'native_vs_docker.json'
    if out.exists():
        raise SystemExit(f'{out} exists; refusing to overwrite')
    result = compare(args.native, args.docker)
    out.write_text(json.dumps(result, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k != 'per_seed'}, indent=1))
    return result


if __name__ == '__main__':
    main()
