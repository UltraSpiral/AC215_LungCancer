# Detailed technical documentation — checkpoint 30

Added [docs/TECHNICAL_OVERVIEW.md](docs/TECHNICAL_OVERVIEW.md), explaining the
source/evidence-backed data audit, preprocessing, frozen features, baseline
selection/results, cached serving, containers, tests and recovery. Expanded
the MS1-to-MS2 scope comparison and clarified the separate repository submission
and presentation tasks using the supplied rubric. Internal draft presentation
and rehearsal materials are excluded from the public deliverables.
This is documentation only; source code, private inputs, model, splits and
running services are unchanged. No processing/tests or Canvas action occurred.

# MS2 replay and submission evidence prepared — checkpoint 29

`make ms2-demo` passed on the M1: build/start, prepared-input inventory, real
16-tile preprocessing smoke, actual HTTP upload/poll, new saved-classifier
prediction from the immutable 512-tile cache, overlay and image identities.
The original CPU/app reports, successful Docker screenshot, preprocessing
visuals, saved training metadata and original MS1 mock-up are packaged under
docs/evidence/ms2/2026-10-20/. TF approval of MS1 and permission to simplify MS2
are attributed to the user's report. See [docs/MS2_SUBMISSION.md](docs/MS2_SUBMISSION.md).
Remaining team tasks: actual deck, shared rehearsal/private-snapshot access,
and final full-SHA Canvas submission. No training/encoding, new acquisitions,
split changes or new test metrics occurred. Broader fresh-UNI2 container work
remains unverified. The full unchanged CPU/app test suites were not repeated.

# Historical feature-cache and MS2 scope clarification — checkpoint 28

The earlier audit overstated fresh UNI2 container execution as an unconditional
MS2 requirement. Caching real versioned embeddings is valid; the saved model
computes fresh predictions without retraining. Full encoder execution in
containers remains unverified, while the cached app remains verified. The
selected pipeline boundary and one-command evidence must be explicit. Read the
correction in [docs/MS2_READINESS.md](docs/MS2_READINESS.md) and checkpoint 28.
No scientific code/artifacts, authorization or running service changed.

# Historical MS2 readiness audit — checkpoint 27

The current rubric/evidence mapping is in [docs/MS2_READINESS.md](docs/MS2_READINESS.md).
The real baseline, native CPU verification and cached-feature UI/API demo are
complete. The entire scientific pipeline has not been verified inside containers.
Selected CPU/model evidence still needs GitHub packaging; original mock-up and
feedback/refinement records, the team presentation and Canvas submission need
confirmation. This assessment runs no new processing or experiments and does
not expand authorization. Checkpoint 27 records the documentation audit.

# Working native M1 cached-feature app — checkpoint 26

The bounded local app is implemented and executed: browser → nginx → real API →
verified cached UNI2 vectors → saved audit2 scaler/logistic head → real UI result.
`make app-up` is the tested single build/start command; http://127.0.0.1:8080/.
14 backend tests and all 10 browser/API scenarios passed. Renamed identical
slide bytes and misleading case metadata preserve exact probabilities; unknown
or modified bytes fail with no prediction. Frontend type/lint/build checks,
actual API outage recovery and full app stop/resume passed. Genuine screenshots,
responses, Docker identities and logs are saved; see
[LOCAL_APP.md](docs/LOCAL_APP.md) and
[checkpoint 26](docs/checkpoints/2026-10-20-26-cached-feature-app.md).
The app remains a one-slide preprocessed-feature demo; full fresh-UNI2 container
verification is pending. No weights/slides, training, split/encoder/preprocessing
changes, test-metric reruns or profiling occurred. Earlier pending-app entries
below are historical.

# Historical handoff — checkpoint 25

All context for the next local M1 UI/API task is saved in
docs/MAC_CODEX_HANDOFF.md. Real modeling and native ARM64 CPU checks are complete.
The new app is not yet implemented or run. The next local task uses content-
verified cached UNI2 features and the saved classifier, with explicit support
limits; no fresh encoding or real model fitting. Full slide-to-prediction
container verification remains separately pending. Source backup coverage now
includes the existing frontend while excluding inputs, dependencies and secrets.
Checkpoint 25 and the private persistent docs/GIT_PUBLICATION.md receipt record
handoff verification/publication; earlier instructions below are dated history.

# Colab confirmation — checkpoint 23

The published M1 checkpoint 598bcd79662a72af832db698b9761658bd943736 has been
fast-forwarded into Colab. The approved Drive archive and all 72 SHA256
inventory entries match; saved JUnit/JSON and images independently confirm the
native CPU checks. No processing rerun occurred. CPU container verification
is complete; full slide-to-prediction containers and UI/backend interaction
remain separately pending. See docs/checkpoints/2026-10-20-23-m1-evidence-confirmed.md.

# CPU verification documentation publication — checkpoint 22

The user authorized committing and pushing the completed native M1 verification
records to milestone2. See [checkpoint 22](docs/checkpoints/2026-10-20-22-cpu-publication.md)
for publication scope and the local post-push verification receipt location.
The existing CPU results below are unchanged; this is documentation publication.
Raw/derived evidence remains outside Git. No model or preprocessing run is repeated.

# Native Apple Silicon CPU checks passed — checkpoint 21

Actual `make cpu-check` exited 0 on Apple M1 / Linux ARM64 Docker on 2026-10-20.
29 unit tests passed; all 44 real embedding caches (22,483 vectors), 12 saved
reference predictions, patient separation and training-only scaling verified.
The real-SVS preprocessing smoke selected 16 in-bounds tiles; overlays inspected.
No pipeline/lock/model/split changes were needed. Source HEAD and GitHub matched
`95fff6baab9e6942992356d70ee56e6c848da2c3` before these documentation edits.
Logs, JSON/JUnit, Docker identity and visual evidence are in `local_outputs/cpu/`.
See [checkpoint 21](docs/checkpoints/2026-10-20-21-native-arm64.md) and
[verification matrix](docs/VERIFICATION_MATRIX.md). This supersedes historical
pending-Mac statements below. Full slide-to-prediction container verification
and UI/backend interaction remain pending. No manual processing command is
needed; no weights/extra slides, retraining or split changes were performed.
The user subsequently approved Drive backup. The evidence package was uploaded
and SHA256-verified by readback; current Markdown mirroring is tracked by
`local_outputs/cpu/cloud_persistence_receipt.json`. Local copies are indexed in
docs/LATEST_BACKUP.md.

# GitHub publication verified — checkpoint 20

GitHub authentication is verified as UltraSpiral. The modeling/CPU workflow
and saved return instructions were pushed to origin/milestone2; local and live
remote SHAs matched at c6627377194d21711b6814be771de70da96cb9b1. This current
checkpoint receives a final documentation commit; its verified full SHA and
refreshed recovery bundle are in the private persistent docs/GIT_PUBLICATION.md
receipt. Earlier missing-auth notes below are historical. No manual Colab login
or modeling command is needed now. M1 Docker verification is the next task;
read docs/CPU_CONTAINER_VERIFICATION.md and docs/VERIFICATION_MATRIX.md.

# Historical Git publication identity — checkpoint 18

User selected UltraSpiral <UltraSpiral@users.noreply.github.com>; repository-local
author settings now match. No Codex-author commit was created. GitHub CLI login
is absent in this fresh runtime. The new commit/push and recovery-bundle result
must be read from the private persistent docs/GIT_PUBLICATION.md receipt. Do not
infer publication success from the older synchronized branch status below.
Browser-login command and Mac fallback: docs/COMMANDS.md and
docs/CPU_CONTAINER_VERIFICATION.md. Modeling results are unchanged.

# Current verified modeling state — 2026-10-20, checkpoints 16–17

Real baseline complete: 45 slides processed; one ambiguous portion-link slide
excluded, leaving 44 independent patients (15 normal / 15 adenocarcinoma /
14 squamous), split 32 train / 6 validation / 6 test. All nine pilot patients
stay in training and every other patient retains the original assignment.
Frozen UNI2-h mean pooling plus training-only scaling and logistic regression
C=0.01. Validation macro F1 0.667; test macro F1 1.000 on only six patients.
The provisional test had already been seen before the metadata-only correction;
no test-based tuning occurred. This is engineering evidence with strong limits.
Current model ID: 42af9fb3f51e1539d994af4f20e2980e4118eac6a8cd665aeb372c1440b2fed5.

Current artifact root:
/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z-audit2/
Use this corrected model. The older 45-slide directory is provisional history.
All eligible vectors are finite (22,483); real arbitrary-name inference passed.
Raw download total remains 5,453,285,795 bytes within 10 GB. Prep is inferred,
not explicitly confirmed Frozen. Detailed results: checkpoint 16 and RESULTS.md.

The user now requests Apple Silicon CPU containers and a local verification
guide, to be executed/debugged by Codex on their M1. CPU script logic passed in
an isolated Torch-free Colab environment. Actual Docker/ARM64 execution is pending;
full slide-to-prediction container verification is tracked separately.
Read docs/CPU_CONTAINER_VERIFICATION.md and docs/VERIFICATION_MATRIX.md.
No more real training, cohort expansion or profiling is currently needed/authorized.
Current commands supersede the historical provisional-run commands below.
Code backups are indexed by docs/LATEST_BACKUP.md. Git publication result is
recorded separately in the persistent docs/GIT_PUBLICATION.md receipt.

## Historical status entries — superseded where different from the current state

# Synced A100 workspace — 2026-10-20 UTC

## Latest state — Git synchronization complete

Local milestone2 now tracks origin/milestone2; both resolve to `99c52a33ca4f097f27c369af16622740044295ca`,
with zero commits ahead/behind and a matching live GitHub branch reference.
Restored 95 absent tracked frontend files. Existing Python source already matched
GitHub. Newer local documentation and verification helpers were preserved and
remain uncommitted. All 52 preexisting source files and 135 artifact hashes were
verified unchanged during synchronization. No frontend install/build/run occurred.
Full pre/post source archives, inventories and the Git bundle are saved under
`/content/drive/MyDrive/LungCancer_AC215/sync_checkpoints/20261020T014239Z`. See `docs/checkpoints/2026-10-20-09-git-sync.md`.
The prior missing-.git notes below describe the pre-sync state and are superseded.
No slide/model/package download, encoder loading, profiling or training ran.
OpenSlide/HF login/pinned weights remain missing; saved-pilot review is ready.

## Artifact readiness check before Git synchronization — 2026-10-20

All 155 saved checksum entries and 126 restored artifact files pass. All nine
real embedding arrays are finite and aligned; specimen labels were re-audited
from saved raw metadata. A100 80 GB / 167.1 GiB RAM / ~191.9 GiB free disk verified.
Core imports pass; OpenSlide, HF login and pinned UNI2 weights remain absent.
Ready for saved-pilot review; new processing awaits setup and authorization.
Local `.git` is absent, while remote milestone2 is verified. No downloads,
installation, encoder load, profiling, training or synthetic fitting ran.
Recovered newer checkpoint-07 handoff records from verified Drive persistence
without overwriting user edits. Current evidence and every command:
`docs/checkpoints/2026-10-20-08-readiness.md` and
`artifacts/readiness/2026-10-20/`. Prior environment notes below are dated history.

## Training plan after the frontend addition

Static review at checkpoint 10 confirms the scientific pipeline is unchanged.
Keep frozen UNI2-h → mean pooling → training-only scaling and multinomial L2
logistic regression, with preparation-matched cohorts and fixed patient groups.
The existing frontend defaults to fixtures and its reference server is a stub;
no real-model integration or held-out performance is established. Proposed later
HTTP integration needs output-schema alignment and filename-independent real
inference, without using viewer JPEG tiles or changing the 512-tile cap to match
mock values. See docs/TRAINING_PLAN.md. This is planning only and does not
expand the current authorization. No model/data/package downloads or training ran.

## Latest deadline request — scope choice pending

The user wants the modeling MVP completed under one hour. A concrete offline
45-slide / 15-patients-per-class engineering proposal reuses all nine cached
slides and needs 36 new files, 4.433 GB additional raw (5.453 GB cumulative).
A historical-rate forecast gives ~33 minutes for new data work plus setup,
fitting/evaluation/inference and backup; no A100 speedup or deadline is guaranteed.
The original target was 30–50 patients/class, so the material cohort reduction
is pending the user's choice. HF notebook login is missing; the one-cell setup
and every assumption are in docs/ONE_HOUR_PLAN.md. No training, model/data
acquisition, dependency installation or performance experiment has started.
The draft alone does not authorize expansion or change the raw budget.

## MS2 rubric assessment — infrastructure work remains

The user supplied the full MS2 rubric. Frozen UNI2-h plus a trained logistic
head fits its baseline adaptation requirement, but no real classifier is fitted
and the project is not yet a complete MS2 submission. Dockerfiles, Compose/
one-command execution, uv locks, container run evidence, a runtime screenshot
and exercised UI/backend interaction are still missing or unverified. Docker
client/daemon access is absent here. Original Docker/frontend exclusions must
be reconciled with the new rubric when authorizing submission work. No resources
were provisioned and no infrastructure/model implementation was launched by
this assessment. See docs/MS2_GAP_ANALYSIS.md and checkpoint 12. The prior
one-hour forecast covered the modeling run only, not all MS2 deliverables.

## Latest setup/modeling assessment — checkpoint 13

HF cached login now works and credential files are 0600. A100/CUDA/Drive remain
available. OpenSlide and pinned UNI2 weights are still absent. The 45-slide,
45-patient draft supports 33 train / 6 validation / 6 test, with all nine pilot
patients in training. This is an initial MS2 engineering baseline with very small
held-out counts; model fitting/results/inference have not run. No persistent
split was created by the temporary metadata-only check. See checkpoint 13.
Prior missing-HF notes are historical; do not repeat setup unnecessarily.

## Latest execution order — waiting for explicit training approval

The user prefers modeling first, then MLOps work. Their sequencing message
explicitly withheld training approval; no training is authorized or running.
After unambiguous approval, execute the chosen real modeling baseline and save
all artifacts/configurations/results, then complete and verify the required
container/uv/one-command/UI-backend deliverables. Existing acquisition pauses
remain until authorized. Do not ask for HF setup again; it is already verified.
See docs/checkpoints/2026-10-20-14-execution-order.md. This update ran no model,
download, experiment or infrastructure build.

## Current boundary and next action

Work is paused at pilot review. **Do not download slides, expand the cohort, train,
or start experiments without the user's return and explicit authorization.**
One-slide profiling is optional, deferred work; do not reacquire its missing SVS now.
Recovery is verified. The next action is pilot review, then a costed proposal
for a larger preparation-matched modeling cohort and fixed patient-level splits.
No further downloads or training are authorized. The requested final scientific
MVP remains incomplete. See docs/checkpoints/2026-10-19-07-a100-recovery.md.

## Current runtime readiness (verified 2026-10-19)

A100-SXM4-80GB, 167.1 GiB RAM, ~192 GiB free disk; Python 3.13.15,
torch 2.11.0+cu130 / torchvision 0.26.0+cu130, CUDA 13.0 available.
Working PyTorch/CUDA and all installed packages were preserved. Required core
imports passed. OpenSlide, cached Hugging Face authentication and pinned UNI2-h
weights are missing; no installation, data/model download or encoder load ran.
Ready for saved-pilot review and offline planning; feature extraction awaits
those prerequisites. The prior encoder load was on L4, not this A100.

Verified all 155 recovery checksum entries and all 126 restored artifact files;
all nine finite [512,1536] embedding arrays have aligned, in-bounds coordinates.
Original pilot source identities, encoder metadata and visual audits are intact.
The offline verification helper is scripts/verify_restored_artifacts.py.

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

## Original pilot environment and current budgets

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
UNI2 weights (~2.73 GB) were present only in the original disposable HF cache;
they are absent on this A100 and are NOT backed up or redistributed. Fresh-runtime encoder reload requires HF authentication and
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
Original snapshot Codex home: `/root/.codex`; session ID `01a1513c-c07c-7100-8c49-70f63dff2251`.
Keep original workspace path `/content/LungCancer`.

The recovery directory contains verified artifact copies, source archive(s),
source member hashes, SHA256 inventory, Git bundle, restore helper and final
verification report. Existing `artifacts/`, `docs/`, `code_backups/` backups are
preserved. Full location index: `docs/ARTIFACTS.md`. The final report records exact
Git commit/push outcome; a push is not established merely by a local commit.
Correction after the original checkpoint: the user subsequently completed the
GitHub push. The remote milestone2 branch is verified at `99c52a33ca4f097f27c369af16622740044295ca` on 2026-10-20.
The initial readiness recheck found local Git metadata absent. Checkpoint 09
subsequently restored Git linkage and 95 missing frontend files on the user's
explicit synchronization request. Local and remote HEAD now match. Checkpoint 07
describes a prior runtime's earlier recovery. The original Drive verification report retains its
historical push-failure result and is not current remote status.
The latest readiness documentation/helper are local changes saved to Drive;
no new commit/push was performed during this recovery. Secure login guidance is in
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


## Authorized modeling run — 2026-10-20 checkpoint 15

User explicitly approved: go ahead and start. This authorizes the proposed 45-slide, 45-patient cohort (15/class), necessary OpenSlide/pinned-UNI2 setup, 36 additional downloads within the unchanged cumulative 10,000,000,000-byte raw budget, real baseline fitting, fixed patient-level validation/test evaluation, and renamed held-out inference. All nine pilot patients remain in training. Modeling precedes MLOps; profiling remains deferred. Prior pause/pending-auth statements above are historical.

Run directory: `artifacts/modeling/20261020T0220Z/`; persistent counterpart: `/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z/`. A100 80GB and HF cached login verified; pinned OpenSlide wheels installed without replacing PyTorch/CUDA. Frozen UNI2 float32, 512 tiles, physical-scale config and pilot cache identities are preserved. No performance result is claimed at launch.
