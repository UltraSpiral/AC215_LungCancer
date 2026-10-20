# Apple Silicon CPU handoff — checkpoint 17

Implemented containers/cpu/Dockerfile, its uv pyproject and lock, Compose services,
Make targets, an offline CPU verifier, a checksum-checked portable bundle builder
and a non-overwriting restore helper. Docker base registry metadata confirms ARM64
and its index digest is pinned. Compose YAML parses and Make command expansion
was inspected. Docker build/run has not been executed in Colab.

Actually executed in a separate Torch-free x86_64 environment: 29 unit tests,
verification of 44 real caches / 22,483 finite vectors and matching coordinates,
32-slide training-only scaler statistics, 12 frozen probability references
(max difference 2.22e-16), and a 16-tile preprocessing smoke on a real 71 MB SVS
(actual scale 0.499261 microns/pixel). The full offline sequence passed in 9.91 s.
The input archive was read fully and restored into a fresh directory; all 187
members were verified. This is script/transport evidence, not ARM64 container proof.

Private portable archive (186,505,459 bytes):
`/content/drive/MyDrive/LungCancer_AC215/portable/cpu-verification-20261020T0220Z-audit2.tar.gz`

SHA256: `c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988`.
Data snapshot: `f9491fe4d35f30267df95d26c61d6bb325908694e6df7d746a6acb9826eddb24`.
No gated encoder weights, credentials, or session records are included.

Read docs/CPU_CONTAINER_VERIFICATION.md for all exact Mac commands and the
Codex handoff prompt. After restoring the archive into local_data/cpu_bundle,
`make cpu-check` builds and runs the CPU sequence on the M1. Generated reports,
JUnit XML and overlays belong in ignored local_outputs/cpu/. User's Mac Codex
will execute, debug and document the actual Docker/native ARM64 run.

Full slide-to-prediction container verification is separately pending. The CPU
smoke uses max 16 tiles / 1024 thumbnail and never supplies model embeddings or
predictions. It cannot replace frozen 512-tile model processing. No HF login
or GPU is required for CPU checks. UI/backend interaction remains unverified.

Source/code and all records are backed up by scripts/persist_records.py to
Drive. Git publication is attempted after source review; its exact result and
commit/bundle identifiers are saved separately in Drive/docs/GIT_PUBLICATION.md.
