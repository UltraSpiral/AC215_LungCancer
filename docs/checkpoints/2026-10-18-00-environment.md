# Checkpoint 00 — initial environment/authentication gate

Historical record from 2026-10-18, before notebook setup. This describes the
initial inspection; the current runtime is authenticated and the pilot is complete.

The original summary below was preserved in
`code-20261018T232430Z.tar.gz`; it described the earlier inspection even though
that archive was created after setup. Current state: [checkpoint history](../CHECKPOINTS.md).

---

# Phase 0 checkpoint

Inspected 2026-10-18 UTC. No repository instructions were present. The repository
had no commits or code; the existing proposal PDF was preserved. No SVS slides
were found under `/content`.

Verified with approved access outside the terminal sandbox:

- NVIDIA L4, 23,034 MiB device memory; PyTorch CUDA sees one device.
- Python 3.13.15; torch 2.11.0+cu130; torchvision 0.26.0+cu130; timm 1.0.30.
- About 53 GiB system RAM and 192 GiB available disk.
- Most scientific dependencies are installed; OpenSlide Python is absent.

Implemented: reusable environment preflight command, initial pilot configuration,
and Git exclusions for local data, outputs, checkpoints, and credentials.

Blocked: Google Drive is not mounted and no supported Hugging Face cached
credential is available to terminal processes. Await the single notebook setup
cell before creating persistent backups or starting slide processing. No package
installation, slide download, UNI2-h checkpoint download, synthetic encoder smoke
test, or real-tissue feature extraction has run. No classifier has been trained.

Next: verify mounted persistence and private credential permissions; verify gated
UNI2-h access, download the official checkpoint, load it on the L4, and run an
explicitly synthetic finite 1536-dimensional embedding smoke test. Then discover
and audit specimen-linked labels and preparation, choose a deterministic matched
pilot within 10 GB cumulative raw downloads, and process real slides through
frozen features with persistent audit artifacts. Pause for pilot review before
cohort expansion and modeling.
