# One-hour engineering-MVP proposal

**Subsequent rubric correction (checkpoint 12):** This forecast covers only
modeling. Full MS2 also requires containerization, one-command execution,
uv/container environment work and tested app interaction. Docker is absent
here. Do not interpret the forecast below as a complete MS2 deadline guarantee.
See MS2_GAP_ANALYSIS.md before deciding execution priorities.

Prepared 2026-10-20. User wants completion in under one hour. This is a concrete
resource/time proposal, not a runtime guarantee or a completed model run.
The user has been asked to approve a reduction from the original 30–50 patients
per class to 15 per class; that scope choice is pending. HF login is also missing.
No new slide/model/package downloads or training have started.

## Where time goes

UNI2-h stays frozen; fitting the slide-level logistic classifier should be a
small part of runtime. A seconds-to-few-minutes fitting estimate is unbenchmarked
on the future cohort. Acquisition, physical-scale tiling and UNI2 inference are
the large stages. Actual saved L4 pilot observations:

- Nine serial slides: 484.69 seconds summed per-slide wall time.
- Median per slide: 57.32 seconds, including acquisition, preprocessing,
  embedding extraction and persistence.
- Download-attempt wall times: 131.46 seconds for 1,020,202,701 bytes,
  roughly 7.76 MB/s. This is historical and not the current network rate.
- The remaining 353.23 seconds includes ALL reading/tiling/inference/saving,
  averaging 39.25 seconds per slide. It is not a CUDA-synchronized inference
  profile. No actual A100 throughput or stage-speedup measurement exists.

A uniform median-times-slide-count extrapolation is optimistic when new files
are larger than pilot files. The illustrative forecast below separately scales
historical download time by new bytes and other work by new slide count.

## Concrete faster cohort — pending user approval

45 slides from 45 distinct patients, 15 per class. It reuses all nine compatible
pilot embeddings; 36 slides need new acquisition/extraction. Saved draft:
artifacts/time_budget/2026-10-20/draft_resource_capped_15.json.

Original specimen/diagnosis/barcode audits and shared frozen preparation are
retained. A 300,000,000-byte per-file resource bound is applied AFTER requiring
included labels; remaining selection uses the existing deterministic preparation,
source-site diversity and hash ordering. All original pilot slides fit the bound.
This is an engineering sampling constraint and may favor particular sites/tissue
extents; document that selection bias rather than claiming a representative cohort.
Normal coverage from both projects remains through the included pilot normals.

Exact additional raw transfer: **4,433,083,094 bytes**.
Cumulative if downloaded once: **5,453,285,795 bytes**, within the unchanged
10,000,000,000-byte budget with room for retries. Encoder/dependency transfers
are separate from raw-slide bytes; no increase in the raw budget is requested.

Historical-rate forecast for the 36 new slides: **33.07 minutes**, including
estimated acquisition and the old average combined non-download slide work.
It excludes one-time setup, encoder acquisition/loading, fitting, evaluation,
final real-slide inference and final backup. Budget roughly 10–20 additional
minutes for those tasks and contingency; this is a planning allowance, not a
measured stage forecast. Aim below 60 minutes AFTER required authentication and
cohort approval, with progress/ETA checks during processing. GDC stalls, corrupt
or missing-scale slides, GPU behavior and runtime errors can overrun that target.
Never claim a guaranteed deadline or complete stages that did not run.

The original unbounded-size deterministic 30/class selection needs about
19.27 GB cumulative raw, beyond the current budget. Even with the same 300 MB
per-file cap, that selector reaches only 27/26/27 examples under 10 GB, with an
illustrative 65.73 minutes of new data work before setup/fitting. These are draft
selection outcomes, not proof that no alternative balanced cohort can fit.
The 90–150-slide original target cannot honestly be promised within one hour
from the measured evidence and current setup. No budget expansion is authorized.

## Acceleration choices that preserve the scientific plan

- Reuse the nine compatible caches without raw redownload or re-embedding.
- Load the pinned UNI2 encoder once for acquisition/extraction. Keep float32,
  official eval transforms, ~0.5 MPP and 512-tile cap so pilot caches remain
  compatible. Keep parameters frozen and inference_mode; these are already used.
- Try batch 32 after checking it fits the A100, with existing OOM fallback. The
  current extractor hands the encoder at most 32 tiles at a time, so merely
  setting a larger batch than 32 would not increase its effective batch size.
  Any actual speed benefit must be measured; no batch change was executed here.
- CPU prefetch/pinned transfers are possible later optimizations, but require
  preserving coordinate order, safe OpenSlide handles and timing verification.
  Do not spend the one-hour target on a broad performance experiment or library
  migration. [Official PyTorch tuning guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html).
- Fit the existing three-value regularization search and majority baseline;
  keep training-only scaling. There is no long neural-network training schedule.
- Preserve fixed patient-level splits, all pilot patients in training, and
  untouched test patients. With 15/class, validation/test class counts will be
  tiny; report actual counts and metrics as exploratory engineering evidence.
- Retain one selected held-out raw SVS locally until renamed-file inference
  finishes, avoiding an unnecessary second acquisition. Keep normal verified
  incremental artifact persistence and managed-download cleanup for other files.
- Finish the real CLI/model/evaluation/inference MVP first. Frontend integration
  remains a separate proposed milestone and is outside this hour's model target.

Do not meet the clock by using synthetic embeddings, filename-selected mock
predictions, leaking patients across splits or evaluating only the nine pilot
slides. Do not silently reduce tiles or change precision: either would change
cache/configuration compatibility and could require reprocessing pilot slides.

## Immediate user action

The earlier 30–50 patients/class target makes reducing the cohort a material
scope change. The pending choice asks whether 15/class is acceptable for a first
engineering MVP. No answer or elapsed time is treated as approval.

HF credentials are missing in this fresh terminal runtime. Run this one Colab
notebook cell using the existing supported setup helper:

```python
%run /content/LungCancer/scripts/colab_setup.py
```

Allow access to Colab Secret HF_HARV when prompted. Never print or paste its
value into chat, commands or persistent files. This helper mounts Drive and
uses supported cached HF login; it does not download slides or UNI2 weights.
After scope approval/authentication, dependency installation and gated model
acquisition are necessary setup for the chosen modeling run. Preserve Colab's
working PyTorch/CUDA. The current preflight confirms A100 80 GB / CUDA available,
with OpenSlide absent and no cached HF token. No stage was run by this proposal.

## Saved evidence and commands

All draft selections, resource-filtered manifest, feasibility.json and current
environment.json are under artifacts/time_budget/2026-10-20. Draft files are
explicitly marked unapproved; no fixed split has been generated or model fit.
All executable budget fields remain at the approved 10 GB even when a report
shows a hypothetical larger requirement. Only the original nine pilot patients
are marked development/training-only in the modeling draft; a draft must never
force all newly selected patients into training.

Read the saved plan or view the pilot; no processing command is needed now:

```python
%run /content/LungCancer/scripts/show_pilot.py
```

Terminal environment check already executed:

```bash
cd /content/LungCancer
python scripts/preflight.py --output artifacts/time_budget/2026-10-20/environment.json
```

This records prerequisites only and exits 2 while cached HF authentication is
missing. No package installation, encoder load or data/model acquisition occurs.

## Setup and split feasibility update — checkpoint 13

The user ran the notebook helper. HF cached login now works with 0600 files;
no repeat login is needed. OpenSlide and pinned model weights remain absent.
A temporary metadata-only draft split check gives 33 train / 6 validation /
6 test patients (11/2/2 per class), with all nine pilot patients in training.
The six-patient test demonstrates engineering execution only; performance
estimates will be unstable. No final split or real model fit was performed.


## Authorized modeling run — 2026-10-20 checkpoint 15

User explicitly approved: go ahead and start. This authorizes the proposed 45-slide, 45-patient cohort (15/class), necessary OpenSlide/pinned-UNI2 setup, 36 additional downloads within the unchanged cumulative 10,000,000,000-byte raw budget, real baseline fitting, fixed patient-level validation/test evaluation, and renamed held-out inference. All nine pilot patients remain in training. Modeling precedes MLOps; profiling remains deferred. Prior pause/pending-auth statements above are historical.

Run directory: `artifacts/modeling/20261020T0220Z/`; persistent counterpart: `/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z/`. A100 80GB and HF cached login verified; pinned OpenSlide wheels installed without replacing PyTorch/CUDA. Frozen UNI2 float32, 512 tiles, physical-scale config and pilot cache identities are preserved. No performance result is claimed at launch.

## Current outcome — checkpoints 16–17

The model was actually fitted/evaluated and real arbitrary-name inference passed.
Initial 45-slide processing took 49.32 minutes; a later conservative UUID-hierarchy
audit excluded one slide, and a corrected head/inference rebuild took 48.60 seconds.
The full audit/verification/CPU preparation exceeded a strict one-hour clock.
Final eligible cohort 44 (32 train / 6 validation / 6 test), validation macro F1
.667, test 1.000 on six previously observed provisional-test patients. No test-based
choice was made; small-sample/reused-test limits are explicit. Current model is
audit2. The user now requested M1 CPU containers and a guide; script logic passed
without Torch. Actual Docker/ARM64 execution and full slide-to-prediction container
proof remain pending. See the verification matrix and CPU container guide.
