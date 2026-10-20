# Checkpoint 13 — 45-slide modeling readiness after setup

2026-10-20 UTC. The user ran the notebook setup and asked whether the 45-slide
cohort is enough for MS2 modeling. For the supplied requirement to train/adapt
an initial baseline and document early experiments, this is a reasonable small
engineering experiment. It is not evidence of statistical adequacy or a
completed modeling deliverable before an actual real-data run.

## Verified now

- A100 80 GB and CUDA remain available; Drive is mounted.
- Terminal-supported HF cached authentication is now present. Both HF credential
  files have private 0600 permissions. No credential value was printed or saved.
- OpenSlide remains absent and pinned UNI2-h weights are not cached; these are
  remaining routine setup steps for an authorized processing run. The encoder
  was not downloaded or loaded by this check. No real model bundle exists yet.
- The draft contains 45 slides from 45 distinct patients, 15 per class, with
  shared frozen preparation according to the saved specimen audit. Frozen
  classification remains an inference where explicit preservation is unknown.
- A temporary metadata-only split feasibility check yields **33 training,
  6 validation, 6 test**: 11/2/2 independent patients per class, respectively.
  All nine inspected pilot patients are in training; patient groups do not cross
  partitions. Normal coverage is LUAD 6 / LUSC 9. No persistent split assignment
  was created or adopted; the temporary check fits no model.
- Nine slides already have verified real embeddings. The additional 36 slides
  still need acquisition, scale/QC checks and extraction; usable final counts
  must be reported if any processing failure occurs.

## What completes the modeling deliverable

An actual fitted/saved scaler+multinomial logistic model on frozen UNI2 slide
features; a training-majority baseline; separate validation and held-out test
metrics/counts and predictions; a real renamed held-out SVS inference result;
configuration/encoder/data identities and concise experiment/limitation logs.
Hyperparameter selection stays on validation, and test patients stay untouched.
Only the classification head is trained. Do not claim UNI2-h was fine-tuned.

Six test patients in total (two/class) are too few for stable performance claims.
One additional test error changes overall accuracy by 16.7 percentage points;
one error in a class changes its recall by 50 points. The test run can demonstrate
held-out engineering execution, with explicit small-sample limitations and a
larger future cohort. No clinical/generalization claim is supported by size alone.

The full MS2 still separately needs the infrastructure/app evidence in
MS2_GAP_ANALYSIS.md. No container/model/data work was started by this assessment.
The user's conditional cohort question is recorded as an assessment, not a
fabricated completed run or a saved/final split. No repeated notebook setup is
needed. Current evidence files: environment_after_setup.json and
split_feasibility.json under artifacts/time_budget/2026-10-20/.

## Commands already executed

```bash
cd /content/LungCancer
python scripts/preflight.py --output artifacts/time_budget/2026-10-20/environment_after_setup.json
```

Preflight reports credential/CUDA/persistence readiness; a separate offline
probe established that OpenSlide/checkpoint setup remains incomplete. No new
command needs to be copied for this readiness answer.
