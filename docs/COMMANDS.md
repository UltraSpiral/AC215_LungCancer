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
