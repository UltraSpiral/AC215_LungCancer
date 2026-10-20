# Latest Git identity and publication check — checkpoint 18

For the current short GitHub-login interruption, use
[RETURN_TO_CHAT.md](RETURN_TO_CHAT.md), added at checkpoint 19. It includes
the exact CODEX_HOME and session UUID; keep this Colab runtime running.

The user selected UltraSpiral <UltraSpiral@users.noreply.github.com>, configured
locally. No Codex-author commit was made. Authentication is separate: this
runtime's gh login is missing. Read the private persistent docs/GIT_PUBLICATION.md
receipt for the actual new commit, push result and verified Git-bundle fallback.
Do not assume the remote contains the modeling/CPU work without comparing SHAs.
The secure browser-login command is saved in docs/COMMANDS.md; M1 restoration
and offline verification are in docs/CPU_CONTAINER_VERIFICATION.md. Completed
modeling and current scope are recorded below; no new training is needed.

# Current verified state — 2026-10-20, checkpoints 16–17

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

# Resume this project

Current Git state (checkpoint 09, 2026-10-20): repository synchronization is
complete. milestone2 tracks origin/milestone2 at `99c52a33ca4f097f27c369af16622740044295ca`; the 95 missing
tracked frontend files are restored. Local notes/helpers remain uncommitted and
are backed up. No slide/model/package downloads or training ran. Earlier
missing-metadata descriptions below refer to the pre-sync state. Follow
[checkpoint 09](checkpoints/2026-10-20-09-git-sync.md) for the current Git state.
Full source including existing frontend and Git history are preserved in
`/content/drive/MyDrive/LungCancer_AC215/sync_checkpoints/20261020T014239Z`; older source archives remain intact.

Latest verification: 2026-10-20, checkpoint 08. All saved artifacts are intact.
Saved-pilot review is ready; new processing still needs OpenSlide, HF login and
pinned UNI2 weights. No downloads or training were authorized or performed.
This fresh archive restore currently has no local Git metadata; the published
milestone2 branch is verified, but the prior runtime's local Git/frontend linkage
was not restored in this check. Use [checkpoint 08](checkpoints/2026-10-20-08-readiness.md)
for the current state. Earlier runtime-specific instructions/results below
remain historical and must not be treated as current local Git verification.

Read `STATUS.md` first. Latest recovery check: 2026-10-19 on A100-SXM4-80GB.
GitHub push succeeded after the old checkpoint; verified `milestone2` HEAD is
`99c52a33ca4f097f27c369af16622740044295ca`. All 126 restored artifact files and
155 saved checksum entries pass. PyTorch/CUDA work unchanged. Missing prerequisites
for future extraction: OpenSlide, HF login and pinned UNI2 weights. Nothing was
installed or reprocessed. Full current evidence: checkpoint 07.

Read `STATUS.md` first. Preserve `/content/LungCancer`. The current gate is pilot
review: **no new SVS downloads, cohort expansion, training or experiments**.
Profiling is optional deferred work, not permission to reacquire a slide.

## A. Runtime still exists

Reconnect to Colab's terminal. If Codex is still open, continue that session.
Otherwise run:

```bash
cd /content/LungCancer
codex resume 01a1513c-c07c-7100-8c49-70f63dff2251
```

To display the three saved class panels in one Colab cell:

```python
%run /content/LungCancer/scripts/show_pilot.py
```

No re-encoding is needed. If Drive disconnected, mount it with the fresh-runtime
cell below; avoid reinstalling dependencies in this working runtime.

## B. Fresh runtime

Select a GPU runtime if later processing is needed. Mount Drive and restore the
checksummed private project snapshot in a notebook cell. This uses only Python
stdlib and refuses to overwrite different existing files:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Then run this **single notebook command** (the helper is copied alongside the archive):

```python
%run /content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z/restore_checkpoint.py project /content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z --apply
```

Dry-run by omitting `--apply`. Different existing files stop the entire restore;
have Codex reconcile them. Artifacts are restored from the timestamped snapshot,
including the cumulative download ledger. No raw SVS, weights or credentials are
restored. The private source archive also contains the original proposal PDF.

The source archive restores code but not `.git`. To restore Git history without
network, use this fresh-workspace-only terminal sequence AFTER the source restore:

```bash
cd /content/LungCancer
git init -b recovery-workspace
git remote add origin https://github.com/UltraSpiral/LungCancer.git
git fetch /content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z/LungCancer.bundle refs/heads/milestone2:refs/heads/milestone2
git symbolic-ref HEAD refs/heads/milestone2
git read-tree HEAD
```

`git fetch` recreates milestone2 while the temporary unborn branch is selected.
The final commands select its HEAD and populate the new index without changing
the restored working files. If `.git` already exists, inspect its branches/remotes first and skip the
initialization/remote-add commands. Alternatively clone `--branch milestone2` from
GitHub into `/content/LungCancer` when the workspace does not yet exist.
The subsequent push has now been verified; the old report's push failure is
historical. Prefer the current GitHub branch for code, including its existing
frontend, and recover saved artifacts separately. For offline recovery, the old
bundle still preserves the Python checkpoint. Never force a branch over work.

Inspection on the A100 found the two OpenSlide wheels still absent. The user
requested no downloads yet; the install below is deferred, not a command to run
now. No PyTorch/CUDA replacement is needed.

Install only dependencies absent from the new Colab image. In the captured image,
only these two local wheels were missing:

```bash
cd /content/LungCancer
python -m pip install --no-deps --target .vendor -r requirements.txt
python scripts/preflight.py
python scripts/show_pilot.py --check
```

Expected core versions: torch 2.11.0+cu130, torchvision 0.26.0+cu130,
timm 1.0.30, huggingface-hub 1.33.0,
numpy 2.1.3, scipy 1.16.3,
scikit-learn 1.6.1, Pillow 11.3.0.
Actual full inventory is in `artifacts/recovery_environment/`. Preserve Colab's
working torch/CUDA; have Codex resolve missing non-torch packages deliberately.
Do not use the full machine inventory as a blanket requirements file.

Authenticate Hugging Face from a notebook cell using the supported cached login:

```python
%run /content/LungCancer/scripts/colab_setup.py
```

Grant access to Colab Secret `HF_HARV` when prompted. Never print its value.
The helper sets private 0600 credential files. Access to gated UNI2-h must still
be approved for this account. Encoder reload command, **reference for a later
authorized processing session only** (downloads gated weights, not slide data):

```bash
python -m lungcancer encoder-smoke --revision d517a8dd47902dd7c308b3c36f63bce47e7b9a43
```

This smoke uses synthetic images, not new tissue. Pinning the revision is required;
weights are intentionally excluded from all backups. Original checkpoint SHA256:
`6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e`.

### GitHub authentication — only if future authenticated operations need it

Correction: push succeeded after the original checkpoint. The current public
remote branch and local tracking HEAD were verified at checkpoint 07. The old
Drive report's failure remains a historical record. Public fetch worked without
an interactive login; no push was attempted during current readiness checks.
If later authenticated writes require login, do this interactively in the terminal.
Do not paste a token into chat or URLs:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
cd /content/LungCancer
git push -u origin milestone2
git rev-parse HEAD
git ls-remote origin refs/heads/milestone2
```

Complete the browser/device flow, then compare both full SHAs. Before retrying,
inspect/fetch any remote changes and merge them without force. The checkpoint
uses repository-local author `UltraSpiral <UltraSpiral@users.noreply.github.com>`
when no Git author identity was configured; no authentication identity is invented.

### Optional native Codex session restoration

Captured version: `codex-cli 0.163.0`. Install that same version first if absent:

```bash
npm install -g @openai/codex@0.163.0
```

Close any Codex app-server using the destination home before restoring its state.
For a **fresh, empty** Codex home, before login/startup, run:

```bash
python /content/LungCancer/scripts/restore_checkpoint.py session /content/drive/MyDrive/LungCancer_AC215/private_codex_recovery/20261019T002107Z/01a1513c-c07c-7100-8c49-70f63dff2251 --codex-home /root/.codex --include-state --apply
codex login
cd /content/LungCancer
codex resume 01a1513c-c07c-7100-8c49-70f63dff2251
```

Default mode is a dry-run. For a nonempty Codex home, the helper refuses to
overwrite different rollouts/indexes/databases. Restore to a new home instead,
authenticate it separately, and explicitly select it:

```bash
python /content/LungCancer/scripts/restore_checkpoint.py session /content/drive/MyDrive/LungCancer_AC215/private_codex_recovery/20261019T002107Z/01a1513c-c07c-7100-8c49-70f63dff2251 --codex-home /root/.codex-lung-recovery --include-state --apply
CODEX_HOME=/root/.codex-lung-recovery codex login
CODEX_HOME=/root/.codex-lung-recovery codex resume 01a1513c-c07c-7100-8c49-70f63dff2251 -C /content/LungCancer
```

The snapshot contains only this session's rollout, filtered history/index,
consistent filtered state/history SQLite databases and a readable export. No
auth.json, HF/GitHub credentials, shell environment snapshots, logs or caches.
SQLite backups use the online backup API, then filter and VACUUM; no live DB file
is blindly copied. Individual databases are consistent; the whole multi-file
snapshot is not transactionally atomic. A complete trailing JSONL record is the
snapshot boundary. Preserve the rollout path and original workspace path.

See `/content/drive/MyDrive/LungCancer_AC215/private_codex_recovery/20261019T002107Z/01a1513c-c07c-7100-8c49-70f63dff2251/restore_verification.json` for the actual read-only restore check.
Even a successful native `thread/read` is not proof of authenticated interactive
continuation on a new runtime. CLI/server/account changes can prevent exact chat
restoration; use section C. The readable Markdown alone is never resumable.
Opaque server-encrypted reasoning cannot be secret-inspected; plaintext fields
are scanned, credentials are excluded. The final checkpoint response is later
than the session snapshot and is not included; the Drive report records results.

Official behavior references, checked 2026-10-19:
[resume CLI](https://learn.chatgpt.com/docs/developer-commands?surface=cli),
[Codex home/state](https://learn.chatgpt.com/docs/config-file/config-advanced).
Installed CLI help and generated app-server schemas were also checked.

## C. Exact chat recovery fails

Start `codex -C /content/LungCancer` after authenticating, and paste:

```text
Read /content/LungCancer/AGENTS.md, STATUS.md, and docs/RESUME.md first.
This is the AC215 TCGA lung WSI project. The nine-slide UNI2-h pilot is complete,
but no real classifier, held-out evaluation or real inference exists yet.
Do not download slides, expand the cohort, train, or start experiments.
Profiling is optional and deferred; no raw SVS remains and none may be
reacquired without new permission. Verify the saved recovery report and
artifact inventory, display the existing pilot with scripts/show_pilot.py,
then wait for my review. Keep every checkpoint and copyable command in
persistent Markdown. Preserve all existing work and patient-level separation.
```

## Scientific handoff and exact artifacts

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



Pilot specimen table (actual slide barcodes are each sample + `-01-TS1`):

| Class | Patient | Project | File UUID | Linked sample | Sample type | Accepted | Rejected | Preservation as reported |
|---|---|---|---|---|---|---:|---:|---|
| non_tumor | TCGA-33-4547 | TCGA-LUSC | ee261db5-3576-4c52-90b4-4c8e16f7937e | TCGA-33-4547-11A | Solid Tissue Normal | 2865 | 4760 | Unknown |
| adenocarcinoma | TCGA-05-4403 | TCGA-LUAD | f6c36a27-f310-4c96-b5bf-1b6adc5f86f9 | TCGA-05-4403-01A | Primary Tumor | 1192 | 3396 | Unknown |
| squamous | TCGA-66-2794 | TCGA-LUSC | bc589465-32ab-406a-94b1-ed48f412f2d9 | TCGA-66-2794-01A | Primary Tumor | 2940 | 5337 | Unknown |
| non_tumor | TCGA-58-8391 | TCGA-LUSC | 2908ac70-541d-4521-9cf5-83e1178263ea | TCGA-58-8391-11A | Solid Tissue Normal | 1167 | 1112 | Unknown |
| adenocarcinoma | TCGA-55-A493 | TCGA-LUAD | 179c64eb-e8ae-46fa-ba37-a2180dcd4ad2 | TCGA-55-A493-01A | Primary Tumor | 1265 | 14213 | Unknown |
| squamous | TCGA-98-A538 | TCGA-LUSC | 660c880b-d78b-4b8b-aceb-5dc7c8e4a3f1 | TCGA-98-A538-01A | Primary Tumor | 1994 | 8991 | OCT |
| non_tumor | TCGA-55-7910 | TCGA-LUAD | 615609e8-fb52-41f7-8abe-d0e9d4d14742 | TCGA-55-7910-11A | Solid Tissue Normal | 2486 | 2200 | Unknown |
| adenocarcinoma | TCGA-69-7761 | TCGA-LUAD | 8cc3b5f7-1f74-4bb9-a046-9870d8cdf912 | TCGA-69-7761-01A | Primary Tumor | 1251 | 1134 | Unknown |
| squamous | TCGA-60-2715 | TCGA-LUSC | 90c06ba4-30bf-49d5-a84b-ddc213de048d | TCGA-60-2715-01A | Primary Tumor | 1317 | 3395 | Unknown |

Every slide selected 512 accepted tiles. Full slide/sample/portion/case UUID chains,
MD5, label evidence and preparation references are in
`docs/checkpoints/2026-10-18-03-pilot-evidence.md` and
`artifacts/pilot_review/details.json`. This table does not flatten samples across
a patient's slides. No ambiguous/conflicting slide was included.

Local active artifacts: `/content/LungCancer/artifacts`.
Persistent working mirror: `/content/drive/MyDrive/LungCancer_AC215/artifacts`.
Immutable checkpoint copies: `/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z/artifacts`.
Source archives + Git bundle: `/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z`.
Markdown mirror: `/content/drive/MyDrive/LungCancer_AC215/docs`.
Historical code archives: `/content/drive/MyDrive/LungCancer_AC215/code_backups`.
Each slide has coordinates, embeddings, preprocessing metadata, thumbnail,
contact sheet, tissue mask/overlay and selected-tile overlay under
`artifacts/slides/<file UUID>`. These are analyzed locations, not tumor heatmaps.
No real splits/models/predictions exist; none should be fabricated during recovery.

## Optional pending profiling

When the user returns, ask whether profiling is still wanted and whether an
existing local raw slide is available. Otherwise seek explicit permission to
reacquire one representative pilot file within the cumulative budget. The
previous candidate is UUID `ee261db5-3576-4c52-90b4-4c8e16f7937e`, 95,344,817 bytes;
a new transfer would raise the ledger to at least 1,115,547,518 bytes. Do not run
that download now. The `profile` CLI measures one slide only, separates
reading/tiling, UNI2 inference and artifact saving, uses CUDA synchronization,
and records batch size/peak memory. It has not been executed. No A100 benefit
claim can be made from a measurement that has not happened.

## Verification and finish record

Final exact Git SHA/push result, archive checks, inventories, raw-file policy and
session restore limits are recorded in `/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z/VERIFICATION.md` and machine-readable
reports alongside it. Verify SHA256SUMS from that directory:

```bash
cd /content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z
sha256sum -c SHA256SUMS
```

Private conversation has its own SHA256SUMS and inventory. Keep it out of GitHub.
The runtime was not disconnected or shut down by the agent.

## Current A100 verification and next modeling step

See [checkpoint 07](checkpoints/2026-10-19-07-a100-recovery.md) for current evidence
and missing prerequisites. The original L4 environment above is historical.
The current runtime has 167.1 GiB RAM and an A100 80 GB with working CUDA; no
UNI2 model load or processing has been repeated. Existing artifact validation:

```bash
cd /content/LungCancer
python scripts/verify_restored_artifacts.py --output artifacts/recovery_checks/manual/artifacts.json
python scripts/show_pilot.py --check
```

Before further acquisition/training: review the pilot, propose 30–50 independent
patients/class with matched preparation, cost it against the remaining budget,
and fix grouped splits with paired classes together and pilot patients in training.
No new cohort acquisition or training is authorized yet.


## Training plan after the frontend commit

See [TRAINING_PLAN.md](TRAINING_PLAN.md) and checkpoint 10. The scientific model,
cohort safeguards and patient-level evaluation are unchanged. A later real-model
HTTP integration is proposed separately and is not authorized or implemented by
this plan review. Current frontend mock/stub outputs remain UI fixtures only.

## Newly supplied MS2 rubric — checkpoint 12

Read MS2_GAP_ANALYSIS.md before resuming execution. The classifier remains an
appropriate baseline, but container/uv/one-command execution evidence and
validated UI/backend interaction are required by the course and remain missing.
Docker was previously excluded by the brief and is absent from this runtime.
No Docker build/run or new training/data work was authorized or executed by
the assessment. The one-hour forecast was modeling-only.

## Authentication now restored — checkpoint 13

HF cached login is verified with 0600 permissions. Do not request repeated
setup. OpenSlide/checkpoint setup remains incomplete. The 45-slide draft
supports an initial baseline experiment with 33/6/6 patient assignments in
a temporary feasibility check; no actual final split or model fit exists yet.

## Latest work order / approval boundary — checkpoint 14

Modeling first, MLOps afterward. The user explicitly said not to start training
without their approval; the sequencing message is not approval. No model run
is authorized or active. Existing acquisition pauses remain. HF login is
already verified. See AGENTS.md and checkpoint 14 before doing processing.


## Authorized modeling run — 2026-10-20 checkpoint 15

User explicitly approved: go ahead and start. This authorizes the proposed 45-slide, 45-patient cohort (15/class), necessary OpenSlide/pinned-UNI2 setup, 36 additional downloads within the unchanged cumulative 10,000,000,000-byte raw budget, real baseline fitting, fixed patient-level validation/test evaluation, and renamed held-out inference. All nine pilot patients remain in training. Modeling precedes MLOps; profiling remains deferred. Prior pause/pending-auth statements above are historical.

Run directory: `artifacts/modeling/20261020T0220Z/`; persistent counterpart: `/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z/`. A100 80GB and HF cached login verified; pinned OpenSlide wheels installed without replacing PyTorch/CUDA. Frozen UNI2 float32, 512 tiles, physical-scale config and pilot cache identities are preserved. No performance result is claimed at launch.
