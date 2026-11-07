# Checkpoint 33 — Attention-pooling experiment approved; Phase 0 setup

Date: 2026-11-06, America/New_York. Branch: `attention-mil` (from `milestone2` at `5369a89`).

## Decision recorded

Awassada approved a CPU-only gated attention MIL experiment on the existing
cached UNI2-h embeddings, with a per-tile attention heatmap on `sample.svs`.
The plan, including every decision and its reason, is
[ATTENTION_PLAN.md](../ATTENTION_PLAN.md). The approval boundary is recorded at
the top of `AGENTS.md`.

Before this checkpoint, `git fetch` confirmed local `milestone2` equalled
`origin/milestone2` (`5369a89`), the only remote branch.

## Implemented

- `AGENTS.md`: approval section and boundary for this experiment.
- `docs/ATTENTION_PLAN.md`: the reviewed plan.
- This checkpoint, plus entries in `INDEX.md`, `CHECKPOINTS.md`, `COMMANDS.md`.

## Phase 0 — native environment (executed)

Added `experiments/attention_mil/`:

- `pyproject.toml`: Python 3.13; torch 2.15.0 from PyTorch's CPU-only index;
  numpy 2.1.3, scipy 1.16.3, scikit-learn 1.6.1, joblib 1.6.0, Pillow 11.3.0,
  openslide-python 1.4.6 and openslide-bin 4.0.1.2 (same pins as the CPU image);
  matplotlib 3.11.2; pytest 8.4.2. Lock limited to macOS arm64 and Linux arm64.
- `uv.lock`: written by host uv 0.13.0. It resolves torch `2.15.0` on macOS and
  `2.15.0+cpu` on Linux arm64, with no NVIDIA packages. The Phase 5 image must
  install uv 0.13.0 to read it with `--frozen`.
- `smoke.py`: torch determinism settings plus `verify_cache` and `load_features`
  on every cached slide.
- `README.md`: purpose and run convention.

## Actually executed and verified

```bash
uv lock --project experiments/attention_mil --python 3.13
uv sync --project experiments/attention_mil --python 3.13
uv run --project experiments/attention_mil python -m experiments.attention_mil.smoke --bundle local_data/cpu_bundle
```

Smoke output on the M1:

```text
torch 2.15.0; cuda=False; threads=1; test matmul shape (512, 512)
openslide library 4.0.1 (saved model expects 4.0.1)
verified 44 slides: {'train': 32, 'validation': 6, 'test': 6}; tiles per split {'train': 16384, 'validation': 3072, 'test': 3027}
SMOKE OK
```

The 22,483 total vectors match checkpoint 21. Test-slide caches were opened only
for file integrity; no labels were used and nothing was fitted. Nothing has been
trained or evaluated.

## Not changed

Splits, preprocessing, cached features, the saved logistic-regression bundle,
`lungcancer/`, `backend/`, `frontend/`, `local_data/` and `local_outputs/app/`.
No downloads of slides or weights.

## Persistence

`scripts/persist_records.py` targets a mounted Colab Drive, which does not exist
on this Mac; it was not run. Records are in Git on branch `attention-mil`.
