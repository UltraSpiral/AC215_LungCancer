"""Phase 0 smoke test: torch works, and every cached slide passes the repo's own checks.

Run from the repository root so `lungcancer` is importable:
    uv run --project experiments/attention_mil python -m experiments.attention_mil.smoke \
        --bundle local_data/cpu_bundle
"""
import argparse
from collections import Counter
from pathlib import Path

import torch
import openslide

from lungcancer.common import read_json
from lungcancer.features import load_features
from lungcancer.modeling import check_patient_separation
from lungcancer.modeling_run import verify_cache
from lungcancer.preprocess import TileConfig


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--bundle', type=Path, required=True)
    args = parser.parse_args()

    # 1. torch: version, CPU-only, and the determinism settings the plan relies on.
    torch.manual_seed(215)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)
    x = torch.randn(512, 1536)
    print(f'torch {torch.__version__}; cuda={torch.cuda.is_available()}; '
          f'threads={torch.get_num_threads()}; test matmul shape {tuple((x @ x.T).shape)}')

    # 2. The same identities the saved model was trained with.
    model = read_json(args.bundle / 'run/model/model.json')
    split = read_json(args.bundle / 'run/splits.json')
    config = TileConfig(**model['preprocessing_config'])
    encoder_id = model['encoder_identifier']
    check_patient_separation(split['slides'])
    print(f'openslide library {openslide.__library_version__} '
          f'(saved model expects {model["openslide_library_version"]})')

    # 3. Every cached slide must pass verify_cache + load_features unchanged.
    tiles = Counter()
    for row in split['slides']:
        directory = args.bundle / 'slides' / row['file_id']
        prep, meta = verify_cache(row, directory, config, encoder_id)
        features, coords, _ = load_features(directory / 'embeddings.npz')
        assert meta['encoder_identifier'] == encoder_id
        assert features.shape == (prep['selected_count'], 1536) and features.dtype.name == 'float32'
        tiles[row['split']] += len(features)
    slides = Counter(r['split'] for r in split['slides'])
    print(f'verified {sum(slides.values())} slides: {dict(slides)}; tiles per split {dict(tiles)}')
    print('SMOKE OK')


if __name__ == '__main__':
    main()
