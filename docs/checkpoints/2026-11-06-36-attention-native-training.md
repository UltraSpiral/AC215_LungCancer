# Checkpoint 36 — Attention experiment Phase 3: native training

Date: 2026-11-06, America/New_York (run at 2026-11-07T00:37Z). Branch: `attention-mil`.
Plan: [ATTENTION_PLAN.md](../ATTENTION_PLAN.md), Phase 3. Native results are
exploratory; the Docker run in Phase 5 is authoritative.

## Implemented

- `experiments/attention_mil/frozen_config.json`, committed in `04582f0` **before**
  any training: hidden 256, attention 128, dropout 0.25; AdamW lr 2e-4, weight
  decay 1e-4; class-weighted cross-entropy; ≤100 epochs; early stopping on
  validation loss, patience 15, keep the lowest-loss epoch; tile subsampling
  50–100% per slide per step; seeds 215–219; deterministic single-thread torch;
  seed rule (highest validation macro-F1, then lowest validation loss, then lowest seed).
  Deviation from the plan: Gaussian feature noise is fixed **off** a priori rather
  than "decided natively", because choosing it on 6 validation slides would be
  tuning on noise. The plan's small hyperparameter grid was already removed.
- `experiments/attention_mil/train.py`: trains every seed, refuses an existing
  output directory, reads only train and validation slides. Class weights are
  applied by multiplying the per-slide loss, because `F.cross_entropy(weight=...)`
  with mean reduction cancels the weight when each step has one slide.
  The read-only logistic-regression baseline must reproduce the saved 20 Oct
  validation predictions within 1e-9 or the run fails.
- `experiments/attention_mil/tests/test_train.py`: 5 tests (class weights, the
  weight-cancellation trap, seed rule tie-breaks, identical training for the same
  seed, a full run that requests only train/validation and refuses overwrite).

## Actually executed and verified

```bash
uv run --project experiments/attention_mil pytest experiments/attention_mil -q   # 25 passed
uv run --project experiments/attention_mil python -m experiments.attention_mil.train \
  --bundle local_data/cpu_bundle --config experiments/attention_mil/frozen_config.json \
  --out local_outputs/attention/native-20261107T0037Z
```

macOS arm64, Python 3.13.16, torch 2.15.0, numpy 2.1.3. 13.9 s for all five seeds.
`run.json` records git commit `04582f0`, which did not yet contain `train.py`; the
executed sources are byte-identical to those committed with this checkpoint:

| File | SHA256 |
|---|---|
| train.py | `ed686bda22e1a055c7ff3cae49bd109c84abbab60f9593c0b6c996ad6bcef02e` |
| model.py | `683588bb5c267bf76de27c3368e2e8b1d6994f6acaf5742341894390ed785a12` |
| data.py | `f347cbe50981c03889e7bbede3c7195a9b4441015b3c7fad06a2440fd28cfd06` |
| frozen_config.json | `84f71a610f7d8ca9c8570908d8fcd6b87c10ef50061ccf4978140305c208ddf7` |
| seed_search.json (output) | `dd61831095ce5f6b932ae6c266903291a02d65a3c30e30e3e599042540e0ec70` |

### Validation results (6 slides, 2 per class)

| Model | Macro-F1 | Balanced accuracy | Validation loss |
|---|---:|---:|---:|
| Existing mean-pool logistic regression | 0.667 | 0.667 | 0.510 |
| Attention, each of seeds 215–219 | 0.822 | 0.833 | 0.222 / 0.273 / 0.338 / 0.387 / 0.317 |

Every seed misclassifies the same squamous slide (`374c3296…`) as adenocarcinoma
(adenocarcinoma probability 0.64–0.84); the logistic model makes the same error.
The only difference from the logistic model is adenocarcinoma slide `c90322c7…`:
logistic regression predicted squamous (0.59), attention predicts adenocarcinoma
(0.82 for seed 215). The improvement is therefore **one slide**.

Best epochs 9–17; runs stopped at epochs 24–32. Training loss approaches zero
by epoch ~10 while validation loss plateaus: the model memorises 32 slides, and
early stopping is doing real work.

Attention stability across seeds (mean pairwise Spearman of alpha, 10 pairs):
0.97, 0.99, 0.93, 0.92, 0.99 and 0.76 (minimum 0.65) on the normal slide `07fc3708…`.

Native preferred seed: **215** (all F1 tied; lowest validation loss 0.222 vs 0.273 next).
Not frozen here; Docker applies the rule in Phase 5.

### Caveats

- The same 6 validation slides choose the early-stopping epoch and the seed, so
  validation scores are optimistic. Only the single Phase 5 test evaluation is unbiased.
- One slide of difference is within the noise of a 6-slide set.
- Native macOS warnings from numpy's Accelerate BLAS during the logistic baseline were
  spurious: probabilities matched the saved predictions to 3.3e-16.

## Outputs (git-ignored)

`local_outputs/attention/native-20261107T0037Z/`: `normalization.npz`,
`seed_<n>/model.pt`, `history.json`, `validation_attention.npz`, `seed_search.json`,
`training_curves.png`, `run.json`. 9.1 MB.

## Not changed

Test slides not read. Bundle, splits, caches, saved model, `lungcancer/`,
`backend/`, `frontend/` untouched.
