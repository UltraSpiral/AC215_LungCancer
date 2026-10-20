# Current commands — checkpoint 22, documentation publication

**Needed now:** no manual user command. Codex is handling the authorized commit,
push and live SHA verification. [Checkpoint 22](checkpoints/2026-10-20-22-cpu-publication.md)
describes the scope; the observed final results are recorded in the ignored
local `artifacts/publication/2026-10-20-22-cpu/` receipts after the push.

Publication commands executed by Codex for this checkpoint:

```bash
git config --local user.name UltraSpiral
git config --local user.email UltraSpiral@users.noreply.github.com
git fetch origin milestone2
git rev-list --left-right --count HEAD...origin/milestone2
git diff --check
python3 scripts/persist_records.py
git add -- AGENTS.md STATUS.md docs/CHECKPOINTS.md docs/COMMANDS.md \
  docs/CPU_CONTAINER_VERIFICATION.md docs/INDEX.md docs/LATEST_BACKUP.md \
  docs/RESUME.md docs/VERIFICATION_MATRIX.md \
  docs/checkpoints/2026-10-20-21-native-arm64.md \
  docs/checkpoints/2026-10-20-22-cpu-publication.md
git diff --cached --check
git diff --cached --stat
git commit -m "Document successful native M1 CPU verification"
git push origin milestone2
git rev-parse HEAD
git ls-remote origin refs/heads/milestone2
git show -s --format=fuller HEAD
git status --short --branch
```

The standard persistence helper's genuine mounted-Drive check refuses Colab
copying on this Mac. Its newly created source archive and all Markdown receive
local SHA256-verified publication copies. No Drive mount is fabricated. The
checkpoint-21 Drive package is preserved; new Git publication receipts remain
local. No new cloud receipt upload or CPU/model execution is part of this step.

# Previous commands — checkpoint 21, native M1 CPU checks passed

**Needed now:** no user processing commands. Codex executed and inspected the
complete native ARM64 Docker check. Results, exact image identity and remaining
screenshot/cloud persistence status are in
[checkpoint 21](checkpoints/2026-10-20-21-native-arm64.md).

**Already executed by Codex on the Mac:**

```bash
git status --short --branch
git remote -v
git branch --show-current
git rev-parse HEAD
git ls-remote origin refs/heads/milestone2
uname -m
docker info --format 'server={{.ServerVersion}} os={{.OSType}} arch={{.Architecture}} cpus={{.NCPU}} memory={{.MemTotal}}'

mkdir -p local_outputs/cpu
python3 scripts/unpack_cpu_bundle.py \
  --archive '/Users/shlokdholakia/Downloads/CPU Verification Audit Oct 20 2026.tar.gz' \
  --sha256 c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988 \
  --destination local_data/cpu_bundle --apply

set -o pipefail
make cpu-build 2>&1 | tee local_outputs/cpu/build-initial.log
```

The restore output was also saved to `local_outputs/cpu/restore.log`. A separate
stdlib verification checked every manifest entry and the real SVS MD5, saving
`input_receipt.json` and `restored_inventory.json`. Restore refuses to overwrite
the now-existing destination; do not rerun it against that directory.

Codex then created a dedicated Terminal window and executed the local runner:

```bash
/bin/zsh local_outputs/cpu/run_cpu_checks.zsh
```

Its actual processing commands, including the exit-code preservation, were:

```zsh
set -o pipefail
make cpu-check 2>&1 | tee local_outputs/cpu/console.log
lc_check_status=$?
print -r -- "$lc_check_status" > local_outputs/cpu/make_exit_code.txt
if (( lc_check_status != 0 )); then exit "$lc_check_status"; fi
docker image inspect lungcancer-cpu:milestone2 \
  --format '{{.Id}} {{.Os}}/{{.Architecture}}' \
  > local_outputs/cpu/image_identity.txt
python3 local_outputs/cpu/show_evidence.py | tee local_outputs/cpu/ms2_summary.txt
```

The exit-code file contains `0`; all three stages report success. The local
evidence viewer validates JSON/JUnit and the exit code before printing a summary.
It is saved with the local evidence, outside Git. To display saved evidence
without rerunning processing:

```bash
python3 local_outputs/cpu/show_evidence.py
```

Codex also recorded the engine/host, final image/layer identity and live
container network/root-filesystem/mount inspection. Screenshot capture uses
the dedicated Terminal window; see checkpoint 21 for its final result.

**Persistence command executed; expected Mac failure preserved:**

```bash
python3 scripts/persist_records.py
```

It created a local source archive, then refused cloud copying because
`/content/drive` is not a genuine mounted Drive on this Mac. The exception is in
`local_outputs/cpu/colab-persistence-attempt.log`; no mount was fabricated.
Actual local backup/copy hashes are in `docs/LATEST_BACKUP.md`. The connected
Drive upload was initially rejected by automatic review; the user subsequently
approved the exact package/Markdown backup. The connected Drive upload succeeded
and the package's downloaded bytes matched SHA256
`70493e8e5086ad83fc339bc649d13d52f2411b39dbe6e365a4202ffff5c4effa`.
Temporary authenticated readback references were passed through hidden stdin;
no such reference was saved in commands, logs, documents or backups.

**Local persistence executed by Codex:**

```bash
python3 local_outputs/cpu/persist_local_evidence.py
```

This saved a new local source archive, copies of all Markdown and all CPU
evidence under `artifacts/checkpoints/2026-10-20-21-native-arm64/`, verified every
copied SHA256, and packaged the snapshot as
`artifacts/checkpoints/cpu-evidence-2026-10-20-21-native-arm64.tar.gz`.
The helper refuses existing snapshot destinations. The source archive follows
the existing helper's allowlist; no credentials, input SVS, cached embedding
inputs or UNI2 weights are included in this new evidence package.
To recheck the saved snapshot without processing data:

```bash
cd artifacts/checkpoints/2026-10-20-21-native-arm64
shasum -a 256 -c SHA256SUMS
```

The genuine screenshot is
`local_outputs/cpu/ms2-docker-success-2026-10-20.png`. Codex restored the dedicated
Terminal window onscreen and immediately ran `/usr/sbin/screencapture -x -l`
with its actual window ID; capture succeeded and was visually inspected.

**Connected Drive backup:** performed by Codex tools after explicit approval;
no shell command or login is needed. The immutable package is the pre-upload
snapshot, so its internal Markdown accurately says cloud backup was pending
when it was created. Current Markdown in Drive is updated separately. The
package link and final mirror verification receipt are in checkpoint 21 and
LATEST_BACKUP.md. Drive Desktop remains unavailable; this uses the connected
Drive service, without creating a fake Colab mount.

**Future stages awaiting a new request:** full containerized UNI2 feature
extraction/prediction and actual UI/backend interaction. New weights/slides,
real-model training, split changes and optional profiling are outside the
completed CPU check. No current need to run `cpu-unit`, `cpu-cache` or `cpu-real`
again: the complete target already passed all three stages.

# Historical commands — checkpoint 20, publication verified

GitHub authentication and push succeeded. No manual Colab command is needed
now. Current source is on origin/milestone2; the private Drive
docs/GIT_PUBLICATION.md receipt records the final verified full SHA and bundle.
Read-only synchronization checks, already executed during publication:

```bash
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/milestone2
```

The next authorized stage is the user's M1 CPU container verification. Its
archive restore, build/run commands and Codex prompt are in
[CPU_CONTAINER_VERIFICATION.md](CPU_CONTAINER_VERIFICATION.md). Actual Docker
execution remains pending there; full slide-to-prediction container verification
is separately pending. New real training/downloads remain outside this step.

# Historical return instructions — checkpoint 19

Keep the current Colab runtime running. Type `/quit` in Codex, then run the
following at the terminal shell prompt. Complete the browser login before
running the resume command:

```bash
gh auth login --hostname github.com --git-protocol https --web
CODEX_HOME=/root/.codex-lung-recovery codex resume 01a1513c-c07c-7100-8c49-70f63dff2251 -C /content/LungCancer
```

Then tell Codex: `GitHub login is complete. Push milestone2 and verify the remote SHA.`
These are needed now and have not been executed by the agent. For another
terminal or a lost-runtime fallback, read [RETURN_TO_CHAT.md](RETURN_TO_CHAT.md).

# Current Git identity and authentication — checkpoint 18

The user selected UltraSpiral <UltraSpiral@users.noreply.github.com>. This
repository's local Git author settings have been applied; no manual identity
command is needed. Authentication is separate. If the publication receipt says
login is missing, run this in the Colab terminal, complete GitHub's browser
flow, and tell Codex when it finishes:

```bash
gh auth login --hostname github.com --git-protocol https --web
```

Do not paste tokens into chat or documents. Exact publication state, commit SHA
and verified backup identifiers are in the private Drive record
`/content/drive/MyDrive/LungCancer_AC215/docs/GIT_PUBLICATION.md`.

Codex's post-authentication commands, pending successful login:

```bash
gh auth setup-git --hostname github.com
git fetch origin milestone2
git push origin milestone2
git rev-parse HEAD
git ls-remote origin refs/heads/milestone2
```

Inspect any remote changes before pushing. Matching full SHAs are required to
claim successful publication. The Mac guide includes a Git-bundle fallback.

# Current modeling commands — checkpoints 16–17

Real modeling is complete. Do not rerun the historical provisional 45-slide
acquisition/training commands. No manual processing command is needed in Colab.

Display current saved results only:

```python
%run /content/LungCancer/scripts/show_modeling.py
```

Read-only re-verification of the current model outputs (no refitting or test
metric recomputation):

```bash
python scripts/report_modeling.py --run-root artifacts/modeling/20261020T0220Z-audit2
```

Apple Silicon setup, archive checksum/restore, one-command `make cpu-check`,
individual debug targets and the exact Mac Codex prompt are all in
[CPU_CONTAINER_VERIFICATION.md](CPU_CONTAINER_VERIFICATION.md).
No HF login is needed for CPU checks. New real training/downloads are not part of
that scope. The earlier repair_cohort_audit.py command was executed once to create
the corrected model; it refuses to overwrite an existing model and is not a
routine resume command.

## Earlier commands and historical authorization boundaries

# Current repository state — checkpoint 09

Git synchronization is complete. milestone2 tracks origin/milestone2; local
notes/helpers remain uncommitted and preserved. Earlier absent-.git notes below
are historical. No new data/model/package downloads or training now.

Read-only terminal verification:

```bash
cd /content/LungCancer
git status --short --branch
git rev-parse HEAD
git rev-parse origin/milestone2
git rev-list --left-right --count HEAD...origin/milestone2
git ls-remote origin refs/heads/milestone2
```

Details and commands already executed:
[checkpoint 09](checkpoints/2026-10-20-09-git-sync.md).

# Current readiness — checkpoint 08, 2026-10-20

No setup command needs to be run for saved-pilot review. OpenSlide/HF/UNI2 setup
and Git metadata recovery remain deferred. No downloads or training now.
The checkpoint-07 local Git repair below describes the previous runtime.
Current local metadata is absent; remote milestone2 exists and is verified.

Display in one Colab cell:

```python
%run /content/LungCancer/scripts/show_pilot.py
```

All current verification commands and results are saved in
[checkpoint 08](checkpoints/2026-10-20-08-readiness.md). Existing setup and older
commands below are preserved as references.

# Current A100 runtime — checkpoint 07

Runtime recovery is verified. No commands need to be copied now.
For evidence and missing prerequisites, see [checkpoint 07](checkpoints/2026-10-19-07-a100-recovery.md).
GitHub push-failure notes below are historical; current milestone2 is verified
at `99c52a33ca4f097f27c369af16622740044295ca`. Do not repeat completed preprocessing.

Display existing pilot, notebook:

```python
%run /content/LungCancer/scripts/show_pilot.py
```

Read-only verification, terminal (already run):

```bash
cd /content/LungCancer
python scripts/verify_restored_artifacts.py --output /content/LungCancer/artifacts/recovery_checks/20261019T204309Z/artifacts.json
python scripts/show_pilot.py --check
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/milestone2
```

Git metadata repair used an empty Git directory, fetched milestone2, selected
HEAD and populated only the index; it never checked out over working files.
The following is reference for a future archive restore with NO Git metadata;
do not rerun initialization in this now-linked workspace:

```bash
git init -b recovery-workspace
git remote add origin https://github.com/UltraSpiral/LungCancer.git
git fetch origin refs/heads/milestone2:refs/remotes/origin/milestone2
git branch milestone2 origin/milestone2
git symbolic-ref HEAD refs/heads/milestone2
git read-tree HEAD
git branch --set-upstream-to=origin/milestone2 milestone2
```

Future setup only after authorization (not executed in this check): install
just the missing local OpenSlide wheels using requirements.txt, authenticate
with scripts/colab_setup.py in a notebook, and later reload the pinned encoder.
Keep all package/model/slide downloads and training deferred now.

# Recovery commands — latest instructions

See [docs/RESUME.md](RESUME.md) for the complete A/B/C recovery procedure, exact
Drive paths, secure login and fallback prompt. No new downloads or training now.

Existing runtime terminal:

```bash
cd /content/LungCancer
codex resume 01a1513c-c07c-7100-8c49-70f63dff2251
```

Existing runtime notebook display:

```python
%run /content/LungCancer/scripts/show_pilot.py
```

Fresh-runtime notebook setup (mount first, then restore):

```python
from google.colab import drive
drive.mount('/content/drive')
```

```python
%run /content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z/restore_checkpoint.py project /content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z --apply
```

The remaining commands below are historical or future references; prefer the
current RESUME.md instructions if a historical recovery snippet differs.

# Copyable commands

Notebook commands below run in a **Colab code cell**. Shell commands run in the
**runtime terminal**, from `/content/LungCancer`. Codex handles processing and
debugging; these records preserve the commands without relying on scrollback.

Current boundary: pilot review only. Additional slide downloads and real-data
training have not been authorized. Reference commands for those stages are
clearly marked below and were not executed by the documentation update.

## Display the existing pilot in Colab — use now

```python
%run /content/LungCancer/scripts/show_pilot.py
```

Displays three class panels covering all nine slides. Each row shows a thumbnail,
tissue-mask overlay, analyzed-tile overlay, and representative contact sheet.
The helper only reads saved files. It uses local artifacts, then mounted Drive
as a fallback.

To display using the persistent artifact directory explicitly:

```python
%run /content/LungCancer/scripts/show_pilot.py --root /content/drive/MyDrive/LungCancer_AC215/artifacts
```

## Notebook authentication — already completed in this runtime

```python
%run /content/LungCancer/scripts/colab_setup.py
```

Follow Drive authorization prompts and allow notebook access to the Colab Secret
named `HF_HARV` if requested. The script uses supported Hugging Face cached login
and private credential-file permissions. No token value belongs in a command,
Markdown file, notebook output, Git, or Drive backup.

## Inspect the current environment and saved display files

```bash
cd /content/LungCancer
python scripts/preflight.py
python scripts/show_pilot.py --check
```

In this session, GPU, network, and mounted-Drive operations through Codex need
approved terminal execution. Keep the security controls enabled. A sandboxed
process may report no CUDA device even though the approved process sees the L4.

## Persist checkpoint records and source code

```bash
cd /content/LungCancer
python scripts/persist_records.py
```

This creates a code archive, refreshes `docs/LATEST_BACKUP.md`, and copies all
checkpoint Markdown files to the persistent `docs/` directory. Every copy is
reread and SHA256 verified. Copy receipts are saved in
`artifacts/documentation_persistence.json`. It performs no slide downloads,
feature extraction, or model training.

For the general artifact backup command:

```bash
python -m lungcancer backup
```

Use `persist_records.py` when updating checkpoint Markdown; the general backup
command does not refresh the dedicated persistent Markdown directory or its
latest-backup pointer.

## Recover after a complete Colab runtime reset

Run the following in a notebook code cell **only for a fresh workspace**. It
mounts Drive, selects the newest source archive, and refuses to overwrite
existing files. The archive's exact SHA256 is recorded in persistent
`docs/LATEST_BACKUP.md`.

```python
from google.colab import drive
from pathlib import Path
import tarfile

drive.mount('/content/drive')
project = Path('/content/drive/MyDrive/LungCancer_AC215')
archives = sorted((project / 'code_backups').glob('code-*.tar.gz'))
if not archives:
    raise RuntimeError('No persistent source archive found.')
workspace = Path('/content/LungCancer')
workspace.mkdir(parents=True, exist_ok=True)
with tarfile.open(archives[-1]) as archive:
    members = archive.getmembers()
    if any((workspace / item.name).exists() for item in members):
        raise RuntimeError('Existing files found; have Codex restore while preserving them.')
    archive.extractall(workspace, filter='data')
print('Source restored to /content/LungCancer')
```

Then authenticate from a notebook cell using the restored script:

```python
%run /content/LungCancer/scripts/colab_setup.py
```

Codex can then run these terminal commands to recover outputs and dependencies:

```bash
cd /content/LungCancer
python -m pip install --no-deps --target .vendor -r requirements.txt
python -m lungcancer restore
python scripts/preflight.py
python scripts/show_pilot.py --check
```

The install adds only the two OpenSlide wheels missing from the inspected
runtime. Preserve a working Colab PyTorch/CUDA installation. Raw slides and
credentials are not restored from source archives. The cumulative download
ledger and completed embeddings are restored from persistent artifacts.

## Review regeneration — no new slide downloads or training

```bash
cd /content/LungCancer
python -m lungcancer review
python -m lungcancer pilot-details --persist
python scripts/persist_records.py
```

The review commands verify existing outputs and regenerate reports. The detailed
audit validates actual file/slide/portion/sample/case links from saved raw GDC
responses. It records the archive current at its own verification timestamp.

## Focused tests

```bash
python -m pytest -q --junitxml=artifacts/unit_tests.xml
```

The last recorded suite passed 23 tests. Synthetic fixtures are confined to unit
tests and do not establish real-data classification performance.

## Previously executed acquisition and extraction stages — reference only

These are preserved for reproducibility. They are not needed to inspect the
completed pilot. Discovery and encoder loading use the network; the pilot or
download command may redownload raw slides. Keep them paused until authorized.

```bash
python -m lungcancer encoder-smoke \
  --revision d517a8dd47902dd7c308b3c36f63bce47e7b9a43
python -m lungcancer discover
python -m lungcancer audit --refresh-from-raw
python -m lungcancer select-pilot --per-class 3 --budget 10000000000
python -m lungcancer pilot --tile-config configs/preprocessing.json
```

The smoke test uses synthetic images only to check tensor plumbing. Every pilot
embedding was extracted from real tissue. Auditing from saved raw responses is
offline. Pilot selection is deterministic and uses one preparation across classes.

Individual-stage examples use the first pilot file. Its raw SVS was deleted after
verified persistence; download would therefore transfer it again.

```bash
python -m lungcancer download \
  --file-id ee261db5-3576-4c52-90b4-4c8e16f7937e
python -m lungcancer preprocess \
  --slide /tmp/lungcancer-raw/ee261db5-3576-4c52-90b4-4c8e16f7937e.svs \
  --output artifacts/manual_slide \
  --tile-config configs/preprocessing.json
python -m lungcancer embed \
  --slide /tmp/lungcancer-raw/ee261db5-3576-4c52-90b4-4c8e16f7937e.svs \
  --preprocessing artifacts/manual_slide \
  --revision d517a8dd47902dd7c308b3c36f63bce47e7b9a43
```

## Future modeling stages — not authorized or executed on real data

These are templates for the post-review stage. A compatible larger cohort,
an agreed expanded download budget, completed features, and fixed grouped splits
are prerequisites. `cohort.json`, the real model bundle, and a held-out inference
slide do not exist yet.

```bash
python -m lungcancer split \
  --cohort cohort.json --output artifacts/splits.json
python -m lungcancer train \
  --splits artifacts/splits.json \
  --output artifacts/models/experiment_01
python -m lungcancer evaluate \
  --splits artifacts/splits.json \
  --model artifacts/models/experiment_01 \
  --split validation --output artifacts/evaluation/validation
python -m lungcancer evaluate \
  --splits artifacts/splits.json \
  --model artifacts/models/experiment_01 \
  --split test --output artifacts/evaluation/test
python -m lungcancer predict \
  --slide /path/arbitrary_filename.svs \
  --model artifacts/models/experiment_01 \
  --output artifacts/prediction
```

Keep all slides and paired classes from each patient in one split. Inspected
pilot patients belong in development/training. Fix model choices before opening
test results. The nine-slide pilot is not a meaningful held-out study.

## One-slide profiling — raw input currently unavailable

The new command profiles exactly one existing pilot SVS, never downloads a file,
uses cached UNI2-h weights in offline mode, and leaves original caches unchanged.
Default batch size is 16 in float32. It measures CUDA-synchronized inference,
CUDA-event forward time, peak allocated/reserved memory, CPU preprocessing,
local saving, and verified Drive copy times. Loading and warm-up are separate.

No raw SVS remains. **Profiling is deferred and optional as of checkpoint 06.**
The prior reacquisition question is superseded. Do not download or run this now.
This reference command would require an authorized available local input:

```bash
cd /content/LungCancer
python -u -m lungcancer profile \
  --slide /tmp/lungcancer-raw/ee261db5-3576-4c52-90b4-4c8e16f7937e.svs \
  --file-id ee261db5-3576-4c52-90b4-4c8e16f7937e \
  --batch-size 16
```

The results use a new directory under local and persistent `artifacts/profiles/`.
Report bookkeeping and raw acquisition are excluded from stage times. GPU-only
speedup scenarios are not A100 benchmarks. Do not re-run the full pilot.

## Training-plan review — checkpoint 10

No new processing command is needed or authorized. Read docs/TRAINING_PLAN.md.
The static Git comparison commands already executed are saved in
[checkpoint 10](checkpoints/2026-10-20-10-training-plan.md).

## One-hour goal — checkpoint 11

Full scope choice, forecasts, prerequisites and setup command are saved in
[ONE_HOUR_PLAN.md](ONE_HOUR_PLAN.md). HF login is required in this fresh runtime:

```python
%run /content/LungCancer/scripts/colab_setup.py
```

Do not print credentials. Reducing to 15 patients/class is awaiting the user's
choice; no training/download command is authorized by this draft alone.

## MS2 rubric assessment — checkpoint 12

Saved assessment: docs/MS2_GAP_ANALYSIS.md. Environment availability checks
already executed:

```bash
docker --version
uv --version
```

Docker is not installed; uv reports 0.12.21. No container build or end-to-end
command exists yet, so no untested run command is presented as working.
The provided course template and official UNI sources are linked in the audit.

## Setup confirmation — checkpoint 13

HF authentication is now restored; no repeated notebook setup is needed.
The environment check already executed was:

```bash
python scripts/preflight.py --output artifacts/time_budget/2026-10-20/environment_after_setup.json
```

OpenSlide and pinned UNI2 weights still need routine setup for an authorized
run. No data/model download or training command was executed in this check.

## Current action — checkpoint 14

No command needs to be run or copied. Modeling is first in the proposed work
order, followed by MLOps, but explicit training approval has not been given.
Do not run the historical acquisition/training commands above. No repeat HF
setup is needed. See checkpoint 14 for the current authorization boundary.

## Current authorized modeling run — checkpoint 15

No manual command is needed while Codex is running it. The command below starts/resumes the same run and never regenerates existing splits. Run only when no other modeling process is active.

```bash
cd /content/LungCancer
python -u -m lungcancer.modeling_run --draft artifacts/time_budget/2026-10-20/draft_resource_capped_15.json --run-root artifacts/modeling/20261020T0220Z --batch-size 32
```

Setup executed (preserves Colab PyTorch):

```bash
python -m pip install --target /content/LungCancer/.vendor --no-deps openslide-python==1.4.6 openslide-bin==4.0.1.2
python scripts/preflight.py --output artifacts/modeling_preflight.json
python -m pytest -q
```

Official references rechecked: [UNI2-h](https://huggingface.co/MahmoodLab/UNI2-h), [GDC download API](https://docs.gdc.cancer.gov/API/Users_Guide/Downloading_Files/), [OpenSlide Python](https://openslide.org/api/python/). Existing supported HF login is reused; no secret needs copying.

After the run reports success, verify all saved results without refitting or repeating test evaluation:

```bash
python scripts/report_modeling.py --run-root artifacts/modeling/20261020T0220Z
```

Colab display helper (after verified completion; reads existing artifacts only):

```python
%run /content/LungCancer/scripts/show_modeling.py
```

Data version and immutable file/patient/split identities are recorded in `configs/modeling_snapshot_45.json`. Full specimen audit metadata stays in the persistent artifact manifests.
