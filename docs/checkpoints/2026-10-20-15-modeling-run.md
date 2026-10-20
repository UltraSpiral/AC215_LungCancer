# Approved real modeling run

Recorded: 2026-10-20T02:20:36.776525+00:00

## Authorized modeling run — 2026-10-20 checkpoint 15

User explicitly approved: go ahead and start. This authorizes the proposed 45-slide, 45-patient cohort (15/class), necessary OpenSlide/pinned-UNI2 setup, 36 additional downloads within the unchanged cumulative 10,000,000,000-byte raw budget, real baseline fitting, fixed patient-level validation/test evaluation, and renamed held-out inference. All nine pilot patients remain in training. Modeling precedes MLOps; profiling remains deferred. Prior pause/pending-auth statements above are historical.

Run directory: `artifacts/modeling/20261020T0220Z/`; persistent counterpart: `/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z/`. A100 80GB and HF cached login verified; pinned OpenSlide wheels installed without replacing PyTorch/CUDA. Frozen UNI2 float32, 512 tiles, physical-scale config and pilot cache identities are preserved. No performance result is claimed at launch.

## Execution status

Setup executed: pinned OpenSlide installation, environment verification and pinned UNI2 cache acquisition. Fixed cohort/splits and tests are being verified before slide processing. No completed real classifier or held-out result is claimed yet. The run progress/log will be persisted incrementally. Final results will be appended here.

## Scientific limits

Preparation is inferred from linked TS barcodes with non-FFPE evidence; no fabricated explicit Frozen confirmation. Small resource-capped cohort, site/tissue-size selection bias, sparse-normal masking concerns and only two held-out patients/class limit performance interpretation. Model choices use validation only; test patients are processed after model configuration is fixed.

## Launch verification

The 24-test suite passed (1.78 s; one expected sklearn warning from a synthetic single-class metric fixture). UNI2-h loaded on the A100 with matching pilot encoder identifier `debc5e8769258a2e970772801d440debc2500868f5a6cf93b7b5c0c8c1e41324` and pinned checkpoint SHA256 `6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e`. All parameters are frozen and evaluation mode is verified. All nine pilot caches passed exact compatibility/coordinate/SHA checks without raw acquisition. New slide processing started. Live progress and incremental verified Drive receipts are in the run directory. No classifier/evaluation success is claimed at launch. Normal project representation: LUAD 6, LUSC 9; all 45 preparations have barcode_inference provenance.

## Routine processing recovery

Slide db65ae8d-2429-4fa7-a35e-d07f06df20a0 has level dimensions 14000×13897, 3500×3474 and 1750×1737. Default OpenSlide thumbnail selection would decode level 0 (~194.6 million pixels); the 64-million-pixel guard correctly stopped it. The bounded fallback now reads the existing 3500×3474 pyramid level, records the actual thumbnail dimensions and warning, and versions only this previously unsupported preprocessing branch. Legacy safe-slide processing, preprocessing.py, features.py, their cache identities and all 12 completed embedding files remain unchanged. No patient/split replacement or additional raw acquisition is needed. The wrapper implementation is pinned in the final model bundle for inference. Unit coverage includes bounded reads, fallback fingerprinting and stale-implementation rejection. Full suite: 25 passed, one expected fixture warning, 4.65 seconds. Resuming the same run; original raw file remains verified locally.

## Network/compute overlap

GDC transfer averaged about 2 MB/s, below the historical pilot rate. After 19 slides were fully persisted, the identified modeling process was gracefully interrupted during the next slide feature transforms, with its raw download already verified and no active partial transfer. Only 32 uncommitted tile computations need repeating; all 19 completed caches, raw byte accounting and fixed splits are intact. One download worker now prefetches exactly the next approved slide while extraction remains serial. Ledger writes remain serialized, and log copying uses a lock to prevent checksum races. Prefetch phases stop before test processing, which still begins only after model selection. No new patient, file, budget, tile, precision or model change. Full test suite: 27 passed, one expected fixture warning.

Timing interpretation after prefetch: per-slide processing timers exclude waits for prefetched downloads, unlike the original serial pilot timers. Compare total pipeline wall time, not those unequal per-slide timings. No synchronized UNI2 stage profile or measured hardware-only A100 speedup is claimed.

## Final correction and completion

The portion-barcode resolver described in interim messages was rejected after
checking the full metadata. GDC UUID relationships are authoritative; differing
portion display numbers are warnings, not grounds to invent a link. Distinct
portion UUID chains are ambiguous and excluded. Exactly one selected slide was
affected; the final model uses 44 patients with all remaining assignments inherited.
The earlier 45-slide fit is provisional and preserved. Read checkpoints 16–17,
which record corrected model/results, timing limitations and the M1 CPU handoff.
