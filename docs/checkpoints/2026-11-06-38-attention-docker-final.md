# Checkpoint 38 — Attention experiment Phase 5: Docker run, single test evaluation, final heatmap

Date: 2026-11-06, America/New_York (Docker runs 2026-11-07T01:0xZ). Branch: `attention-mil`.
Plan: [ATTENTION_PLAN.md](../ATTENTION_PLAN.md), Phase 5. **These are the
authoritative results of the experiment.**

## Implemented (commit `d6a8fe0`, made before any Docker run)

- `containers/attention/Dockerfile`: same pinned `python:3.13.15-slim-bookworm`
  digest as `containers/cpu`; uv 0.13.0 (the version that wrote the lock);
  `uv sync --frozen`; two stages, build tools only in the first; runtime adds
  `libgomp1`/`libstdc++6`; non-root; `HOME`/`MPLCONFIGDIR` on `/tmp`.
- `compose.attention.yml`: `attention-unit`, `attention-train`, `attention-test`,
  `attention-heatmap`; linux/arm64, `network_mode: none`, read-only root, tmpfs
  `/tmp`, bundle mounted read-only at `/inputs`, `local_outputs/attention` at
  `/outputs`, host UID/GID, host git commit passed as `LC_ATTN_GIT_COMMIT`.
  `compose.cpu.yml` and `compose.app.yml` are unchanged.
- `Makefile`: additive targets `attention-build`, `attention-unit`,
  `attention-train`, `attention-test`, `attention-heatmap`, `attention-compare`
  (`LC_ATTN_RUN` defaults to `docker`).
- `train.py`: `--authoritative` records `chosen_seed`; `run.json` stores source
  SHA256s and `--require-arm64` is enforced.
- `evaluate.py` (renamed from `evaluate_test.py`, which pytest collected as a test
  file): single test evaluation of the chosen seed. Refuses runs without
  `chosen_seed`, a model file whose SHA256 changed since training, and an existing
  `test.json`. Reproduces the existing model's saved test predictions within 1e-9.
- `compare_runs.py`: native vs Docker agreement.
- `heatmap.py`: extra top-10% view (`top10_<id>.png`).
- `tests/test_phase5.py`: 5 guard tests that never open the test split. 36 tests total.

## Actually executed and verified

```bash
make attention-unit      # image build + 36 passed inside the container
make attention-train     # 5 seeds, authoritative
make attention-compare   # native-20261107T0037Z vs docker
make attention-test      # the single test evaluation
make attention-heatmap
```

Image `lungcancer-attention:milestone2`: linux/arm64, 1.5 GB, Python 3.13.15,
torch `2.15.0+cpu`, numpy 2.1.3 with OpenBLAS, 32 packages, none from NVIDIA,
no CUDA. Content-layer identity (SHA256 of the 9 RootFS layer digests):
`e96003cff84f03fe57d0128e6d232e078cb8798b0be0d4458747894720da4d3f`.
**Image IDs change on every rebuild** (`6cb845…`, `120bac…`, `967621…` observed)
because Docker Desktop's containerd image store includes build metadata in the ID;
a no-change rebuild was verified to keep all 9 content layers identical. Each
`make` target rebuilds from cache first.

`run.json` and `test.json` record git commit `d6a8fe06319ee0e751c932bc0e427c6c89f743d5`
and source hashes identical to that commit (data, model, train, heatmap, evaluate,
compare_runs).

### Training and seed selection (Docker)

Docker reproduced the native run: same best epochs, same validation predictions,
same seed chosen (**215**). 61.7 s in Docker vs 13.9 s native (Apple Accelerate
uses M1 matrix hardware that the Linux container cannot).

| Native vs Docker | Value |
|---|---|
| Same chosen seed | yes (215) |
| Normalisation max abs difference | 0.0 |
| Max abs difference in any alpha (all seeds, validation) | 1.23e-06 |
| Max validation loss difference | 5.9e-07 |

### Single test evaluation (6 slides, 2 per class)

| Model | Macro-F1 | Balanced accuracy | Test loss |
|---|---:|---:|---:|
| Attention, seed 215 | 1.000 | 1.000 | 0.005 |
| Existing mean-pool logistic regression | 1.000 | 1.000 | 0.110 |
| Majority class | 0.167 | 0.333 | — |

Both models classify all six test slides correctly; the test set cannot separate
them on accuracy. The attention model is more confident on every slide (lowest
correct-class probability 0.981 vs 0.735). Higher confidence is not established
as better calibration: on validation it was wrong at 0.64–0.84 confidence.
These test slides were already evaluated with the mean-pool model on 2026-10-20;
not a pristine test set. Evaluated once at 2026-11-07T01:10:29Z.

### Final heatmap (`sample.svs`, chosen seed 215)

Identical to the native preview: same top-5 tiles (408, 409, 489, 435, 391),
alpha max 0.0107, top-10 share 0.073, Spearman with the existing model's tile
scores 0.70. Top-10% view: the two models share 21 of their 52 top tiles
(40%; about 5 expected by chance). Known flaw: the faint grey outlines of
non-top tiles in `top10_a2e48dce.png` are not visible at figure scale although
the caption mentions them; not re-rendered, to keep the official output unchanged.

| Output | SHA256 |
|---|---|
| test.json | `51c23e4acf4207db5a2c0751ccacb9f3e2c04a0fc9333f1f35d611b7368b47cf` |
| seed_search.json | `04fa87c2265caa20c469c715e24552ac4f1dad424a166e4d677ae5ffd4454b52` |
| native_vs_docker.json | `b1ab3c798206487675ff295d825cf4cdf2cb15c7d2fa7ec17f3153493e85583b` |
| seed_215/model.pt | `b9e8b2df5e024ecca416786954aba457e1899437b4829f6dc6e2d7f228f2ee8b` |

Outputs: `local_outputs/attention/docker/` (git-ignored, 19 MB).

## Not changed

Bundle, splits, caches, saved model, `lungcancer/`, `backend/`, `frontend/`,
`compose.cpu.yml`, `compose.app.yml`, existing images. No downloads at run time
(containers ran with no network).
