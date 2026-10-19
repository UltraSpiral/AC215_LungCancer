# Checkpoint 01 — authenticated environment and UNI2-h readiness

Date: 2026-10-18 UTC. Synthetic encoder smoke timestamp: 2026-10-18T23:25:12.950791+00:00.

Implemented and actually run:

- Verified NVIDIA L4, 23,034 MiB GPU memory, approximately 53 GiB system RAM.
- Verified Python 3.13.15, torch 2.11.0+cu130 and torchvision 0.26.0+cu130.
- GPU access worked in the approved process outside the terminal sandbox.
- Verified Google Drive mount and supported Hugging Face cached authentication.
  Cached credential permissions were 0600; no token values were printed or backed up.
- Installed only project-local OpenSlide Python 1.4.6 and openslide-bin 4.0.1.2;
  the working Colab PyTorch/CUDA installation was retained.
- Loaded the genuine `MahmoodLab/UNI2-h` checkpoint on the L4 with frozen
  parameters, evaluation mode, and no-gradient inference.
- The deliberately synthetic smoke test returned finite **[2,1536]** embeddings.
  This test checked tensor plumbing; the later pilot used real slides.

Encoder revision: `d517a8dd47902dd7c308b3c36f63bce47e7b9a43`.

Checkpoint SHA256: `6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e`.

Evidence:

- `/content/drive/MyDrive/LungCancer_AC215/artifacts/encoder_smoke.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/encoder_source.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/environment.json`

The environment file was refreshed later at 2026-10-18T23:39:34.866818+00:00; it is a
current environment record rather than the untouched initial inspection.

Next authorized work at this historical checkpoint was discovery, label audit,
and the small preparation-matched pilot under the 10 GB cumulative raw budget.
Authentication and display commands are preserved in [COMMANDS.md](../COMMANDS.md).
