# Apple Silicon CPU container verification

The GPU modeling stage has completed in Colab. The final model uses **44 eligible
patients**, with 32 train / 6 validation / 6 test. One multiply linked slide was
excluded conservatively; the other patients kept their original assignments.
Read checkpoint 16 and the final RESULTS.md for the tiny-test and audit limitations.

This guide is for Codex on the user's M1 MacBook. The CPU image supports three
checks: synthetic unit tests, real cached UNI2 embeddings with the saved logistic
head, and a small real-SVS preprocessing smoke. Full slide → UNI2 → prediction
container verification is tracked separately and remains pending.

## What is already verified

- Python Docker base metadata includes linux/arm64. The multi-platform digest is
  pinned in containers/cpu/Dockerfile and base-image.json.
- containers/cpu/pyproject.toml and uv.lock pin an isolated CPU environment.
  The recipe uses native ARM64, compiles the binding if necessary, and uses the
  maintained openslide-bin 4.0.1.2 ARM64 library.
- The same verification scripts passed in a Torch-free **x86_64 Colab virtual
  environment**: 29 unit tests; all 44 real embedding caches; training-only
  scaler statistics; 12 frozen validation/test probability references; and a
  real-SVS 16-tile preprocessing smoke. This is script-level evidence.
- Dockerfile builds, Docker Compose execution and ARM64 runtime behavior have
  **not** been executed here. Colab has no Docker daemon. Record them only after
  actually running on the Mac.

References: [uv Docker integration](https://docs.astral.sh/uv/guides/integration/docker/),
[OpenSlide Python](https://openslide.org/api/python/),
[maintainer ARM64 binary wheels](https://pypi.org/project/openslide-bin/4.0.1.2/).

## Obtain the private input bundle

The source code belongs on GitHub milestone2. Inspect the local repository,
synchronize it without overwriting existing work, then obtain this private file
from the user's Google Drive. Do not place the archive or extracted data in Git.

Check the private Drive `LungCancer_AC215/docs/GIT_PUBLICATION.md` receipt for
the exact source commit and publication status. If GitHub authentication blocked
the Colab push, download `LungCancer_AC215/portable/LungCancer-modeling-audit2.bundle`
as well. After verifying its SHA256 against that receipt, restore the code into
a **new** directory, preserving any existing checkout:

```bash
git clone --branch milestone2 "$HOME/Downloads/LungCancer-modeling-audit2.bundle" LungCancer-from-checkpoint
cd LungCancer-from-checkpoint
git remote rename origin checkpoint-bundle
git remote add origin https://github.com/UltraSpiral/LungCancer.git
git rev-parse HEAD
```

Compare HEAD with the receipt. Do not reset an existing checkout or push over
remote work. Codex can inspect and synchronize it after authentication.

Drive file:
`/content/drive/MyDrive/LungCancer_AC215/portable/cpu-verification-20261020T0220Z-audit2.tar.gz`

Archive size: **186,505,459 bytes**. SHA256:
`c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988`.

Data snapshot:
`f9491fe4d35f30267df95d26c61d6bb325908694e6df7d746a6acb9826eddb24`.
The bundle has 187 verified files: genuine cached vectors/coordinates,
preprocessing provenance, the trained logistic pipeline, frozen references and
one **71,138,367-byte public SVS**. No UNI2 checkpoint, credentials or Codex state
is included. The raw sample was retained from the approved download; no extra
GDC transfer was needed. Its UUID is a2e48dce-1874-468d-a302-fd30b3107f4a and MD5 is
a86f358f5325b6229035d19ed23440aa.

From the repository root, after downloading the archive into Downloads:

```bash
python3 scripts/unpack_cpu_bundle.py \
  --archive "$HOME/Downloads/cpu-verification-20261020T0220Z-audit2.tar.gz" \
  --sha256 c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988 \
  --destination local_data/cpu_bundle --apply
```

The restore script verifies the archive and refuses an existing destination.
Use a new directory if needed, and set LC_CPU_BUNDLE to its absolute path.
It never restores credentials. Docker inputs are mounted read-only; generated
outputs go into ignored local_outputs/cpu/.

## Build and run on the M1

Docker Desktop must be running with Linux containers. No GPU, HF login or HF
token is needed for these CPU checks. Build-time network access fetches public
dependencies; the verification containers run offline.

```bash
uname -m
docker version --format '{{.Server.Version}}'
mkdir -p local_outputs/cpu
set -o pipefail
make cpu-check 2>&1 | tee local_outputs/cpu/console.log
```

`make cpu-check` builds and runs the complete CPU verification sequence.
Individual commands for debugging are `make cpu-unit`, `make cpu-cache`, and
`make cpu-real`. Each uses the same locked image. The default target platform is
linux/arm64, and the verifier requires arm64/aarch64. Host UID/GID are propagated
for output-file ownership. Keep the original input bundle unchanged.

Capture the actual built image identity without dumping environment/config:

```bash
docker image inspect lungcancer-cpu:milestone2 \
  --format '{{.Id}} {{.Os}}/{{.Architecture}}' \
  > local_outputs/cpu/image_identity.txt
```

Expected outputs are verification_all.json, cached_embeddings.json,
real_preprocessing.json, unit-tests.xml, and preprocessing/ contact sheet,
mask/selection overlays, coordinates and scale metadata. Inspect every stage's
status. Preserve nonzero exits; do not treat a successful tee command as a pass.
The verifier compares cached probabilities within 1e-8 and checks all file hashes,
coordinate ordering, source identities, patient separation and scaler statistics.

The preprocessing smoke uses ~0.5 MPP, 224 pixels, max 16 tiles and a 1024-pixel
thumbnail. This is deliberately isolated from the frozen model's 512-tile/4096
configuration. Its output is a preprocessing check and contains no prediction.
Do not feed those 16 tiles into the trained model or replace Colab caches.

## Evidence and remaining verification

After the Mac run, save a dated Markdown checkpoint with the commands, image ID,
platform, dependency versions, input snapshot ID, outputs and actual failures/fixes.
Update docs/INDEX.md, docs/CHECKPOINTS.md and docs/COMMANDS.md. Commit only source,
locks, sanitized docs and tests. Keep bundles, raw images, joblib/NPZ files and
local outputs outside Git. Save a screenshot of the running local Docker
environment for MS2. Retain the console log and JUnit/JSON evidence.

The Colab persistence helper expects its real mounted Drive. On the Mac, use the
user's actual Drive Desktop project directory or connected Drive tools if
available, verify copied hashes, and report persistence gaps explicitly. Do not
fabricate /content/drive or copy authentication stores to make the helper pass.

Track full containerized slide-to-prediction separately: the CPU checks do not
instantiate UNI2. The Colab GPU CLI already demonstrated real single-slide
inference, but that does not prove a GPU container works. Containerized encoder
loading/feature extraction, matching full preprocessing, real inference, and the
UI/backend interaction still need their own execution evidence.

## Prompt for Codex on the Mac

> Work in this LungCancer repository. Read AGENTS.md, STATUS.md,
> docs/RESUME.md, this guide and docs/VERIFICATION_MATRIX.md. Inspect Git and
> preserve existing work. Synchronize milestone2 without reset or force-push.
> Restore the checksum-verified private CPU bundle into ignored local_data/.
> Build and run make cpu-check natively on Apple Silicon. Execute, inspect,
> debug and rerun necessary checks yourself. Preserve nonzero failures and
> record actual image/platform/log evidence. Do not install or load UNI2/Torch,
> download additional slides, train another real model, change frozen splits,
> or claim full slide-to-prediction container verification. Keep generated data
> and credentials out of Git. Save a dated checkpoint and persistent commands.
