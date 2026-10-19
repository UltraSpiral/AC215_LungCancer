# Recovery checkpoint — 2026-10-19 UTC

## Current boundary and next action

Work is paused at pilot review. **Do not download slides, expand the cohort, train,
or start experiments without the user's return and explicit authorization.**
One-slide profiling is optional, deferred work; do not reacquire its missing SVS now.
The next action is to reconnect/recover, read this file and `docs/RESUME.md`, and
inspect the saved pilot using `%run /content/LungCancer/scripts/show_pilot.py`.
Then wait for the user's review. The requested final scientific MVP is incomplete.

## Objective and architecture

AC215 engineering prototype for three-class lung tissue classification:
`non_tumor`, `adenocarcinoma`, `squamous`. Public TCGA-LUAD/LUSC SVS files and
actual linked biospecimens provide traceable labels. Pipeline: OpenSlide tissue
tiles → frozen UNI2-h → mean pooling → training-only scaling and L2 multinomial
logistic regression. Later evaluation uses fixed patient groups with all paired
classes together. This is not clinical validation or comprehensive disease detection.
No deployment, frontend, segmentation, tumor-area estimation, calibration or
attention MIL is in scope.

## Implemented versus executed

Executed and verified before this checkpoint: environment/authentication, official
UNI2-h GPU smoke (synthetic [2,1536]), GDC discovery and specimen audit, deterministic
preparation-matched nine-slide pilot, downloads with MD5 checks, OpenSlide physical
scale tiling, real frozen embeddings, visual audit outputs and verified Drive copies.
All 23 focused unit tests passed; their synthetic fixtures are not classification
performance evidence. The checkpoint reads/verifies existing artifacts, records
dependencies and backs up code/conversation; it runs no ML workload.

Implemented but **not run on a real modeling cohort**: grouped fixed splits,
mean pooling, training-only sklearn pipeline, validation C search, majority
baseline, evaluation and arbitrary-filename single-slide inference. No real split,
classifier, held-out evaluation, predictions or renamed held-out inference exists.
Profiling code is implemented and syntax checked but has never run. No measured
inference timing, batch-memory profile or A100 speedup is available.

## Discovery, pilot and scientific decisions

Discovery: 3,220 open SVS files. Eligible 3,175; excluded 45 (12 histology conflicts
or ambiguity, 28 preparation conflicts, 5 out-of-scope sample types). No duplicate
UUID, filename, slide ID or MD5. Eligible counts: normal 588 slides/429 patients;
adenocarcinoma 1,323/519; squamous 1,264/503. Normals are exclusively frozen-classified;
tumors include frozen and FFPE, so this pilot selects frozen-classified slides only.

Pilot: **3 slides and 3 independent patients per class, 9 distinct patients total**.
Exactly **1,020,202,701 raw bytes** downloaded in 9 verified attempts, zero failures.
All nine output embedding arrays are [512,1536], all coordinates [512,2], all finite
(4,608 real tile embeddings). Normal projects: LUAD 1 and LUSC 2. Actual specimen
linking is file associated slide UUID → nested portion UUID → sample UUID → case;
never all case samples flattened onto a slide. Solid Tissue Normal → non_tumor;
Primary Tumor plus LUAD → adenocarcinoma; Primary Tumor plus LUSC → squamous.
Diagnosis is a conflict check, never grounds for calling a normal specimen tumor.

All nine preparations are **inferred** from linked TS barcodes, supported by
`portion.is_ffpe=false`. Explicit Frozen confirmations: **0/9**. Preservation is
Unknown for 8; OCT for TCGA-98-A538. Unknown was not replaced by a fabricated
explicit value. Full UUID chains, diagnosis checks, barcode checks and references
are in `docs/checkpoints/2026-10-18-03-pilot-evidence.md` and persistent
`artifacts/pilot_review/details.json`. Histology is metadata-derived, not relabeled
by a pathologist. Preparation inference and source-site confounding remain limits.

All slides have >512 accepted candidates; the 50% threshold may still favor dense
normal tissue and reject sparse lung. Grid acceptance includes background and
cannot measure tissue false negatives. Pale TCGA-60-2715, folds/cut edges/focus
variation and unapplied embedded ICC profiles are documented. Do not claim masking
bias absent or add aggressive filtering without further review.

## Exact encoder and preprocessing

`MahmoodLab/UNI2-h` revision `d517a8dd47902dd7c308b3c36f63bce47e7b9a43`;
checkpoint SHA256 `6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e`.
Official timm ViT-H/14 loading configuration; 1,536 features; frozen parameters,
eval mode, inference_mode, float32, pilot batch 16 with OOM batch reduction.
Official eval transforms: 224 bilinear resize, center crop, mean
[0.485,0.456,0.406], std [0.229,0.224,0.225]. No stain normalization.

`configs/preprocessing.json`: target 0.5 MPP, 224×224 pixels, non-overlap grid,
max 512, seed 215, spatially distributed deterministic selection, 50% tissue
coverage. Thumbnail max 4096; HSV saturation ≥0.08, value 0.15–0.98; light closing
one iteration and 16-pixel component cleanup. OpenSlide level-0 XY coordinates;
validated MPP, no silent objective-power or missing-scale fallback. Actual pilot
extraction scale ~0.4993–0.5002 MPP. Cache keys cover source checksum, encoder,
transforms, preprocessing and coordinates; writes are atomic. No usable tiles or
missing scale returns explicit failure.

## Environment and budgets

Python 3.13.15, torch 2.11.0+cu130, compiled CUDA 13.0, NVIDIA L4 23,034 MiB,
driver 580.82.07, ~53 GiB RAM. Kept working PyTorch/CUDA. Installed only local
OpenSlide wheels: openslide-python 1.4.6 and openslide-bin 4.0.1.2 (native 4.0.1).
Codex CLI 0.163.0. Full actual package/system/CUDA inventory:
`artifacts/recovery_environment/installed_environment.json` and installed_packages.txt.
Do not reinstall that entire inventory over Colab. See setup in docs/RESUME.md.

Initial cumulative raw budget remains 10,000,000,000 bytes; reserved and actual
transfer both 1,020,202,701. No expansion approved. Public SVS originals were only
temporary pipeline downloads and are all omitted/deleted after verified persistence;
file UUID/MD5/size remain available. User-provided proposal PDF is retained locally
and in the private recovery source archive, excluded from public Git.
UNI2 weights (~2.73 GB) remain only in the disposable HF cache and are NOT backed
up or redistributed. Fresh-runtime encoder reload requires HF authentication and
network; do not run it merely to inspect saved pilot outputs.

Larger cohort estimate (not approval): 30–50 independent patients per class,
90–150 slides, roughly 11–18 GB raw transfer at class-median sizes, 1.2–2.0 GB
outputs; prior serial wall-time estimate 1.4–2.4 hours is not a profiler measurement.
Patients can contribute multiple classes. Prefer one slide/patient/class and
keep inspected pilot patients in training; never tune against held-out test images.

## Persistence and code recovery

Mounted Drive root: `/content/drive/MyDrive/LungCancer_AC215`.
Timestamped recovery directory: `/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z`.
Private session directory: `/content/drive/MyDrive/LungCancer_AC215/private_codex_recovery/20261019T002107Z/01a1513c-c07c-7100-8c49-70f63dff2251`.
Current Codex home: `/root/.codex`; session ID `01a1513c-c07c-7100-8c49-70f63dff2251`.
Keep original workspace path `/content/LungCancer`.

The recovery directory contains verified artifact copies, source archive(s),
source member hashes, SHA256 inventory, Git bundle, restore helper and final
verification report. Existing `artifacts/`, `docs/`, `code_backups/` backups are
preserved. Full location index: `docs/ARTIFACTS.md`. The final report records exact
Git commit/push outcome; a push is not established merely by a local commit.
The authorized Git push was attempted and failed: Git cannot read a GitHub
username without credentials. Remote milestone2 was checked and is absent.
The local commits and verified Drive Git bundle preserve the code; no push
success is claimed. Secure browser authentication steps are saved in
`docs/RESUME.md`. No credentials, chat/session records or large artifacts belong
in Git. Authorized public remote: https://github.com/UltraSpiral/LungCancer.git,
branch `milestone2`; preserve any remote work and never force push.

Private session snapshot uses consistent SQLite online backups, current-thread
filtering and a complete JSONL prefix; credentials/config/logs/caches are excluded.
Plaintext fields are scanned for token patterns before copying; opaque encrypted
reasoning cannot be inspected. Native recovery verification, if successful, is a
read-only thread read in an isolated credential-free home, not an authenticated
interactive continuation. Exact interactive chat restoration on a new runtime
remains unverified. Readable Markdown is not resumable session data. The final
assistant response and later events are outside the late snapshot. A new-session
recovery prompt is saved in `docs/RESUME.md`.
