# Checkpoint 05 — one-slide profiling prerequisite

Requested: profile one representative slide using existing downloads, splitting
reading/tiling, synchronized UNI2 inference, and artifact saving; report batch
size and peak GPU memory, then assess A100 benefit. Do not rerun the full pilot.

## Verified inputs and current boundary

No raw SVS or partial SVS remains in the local workspace, configured raw storage,
or dedicated persistent project directory. These temporary slides were removed
after verified persistence as recorded in the pilot checkpoint. Derived
embeddings and visual audits remain. The genuine UNI2-h checkpoint is cached.

Raw transfer remains **1,020,202,701 bytes**, nine download attempts. No new slide
download, real-slide profiling, or training has been run during this request.

## Implemented, not yet executed

`lungcancer/profiling.py` and the `profile` CLI process exactly one existing pilot
file. They never download a slide or change original pilot caches. Source syntax
and CLI help were checked. Planned fixed batch size is 16, float32, cached weights.

The profiler separately measures reading/masking/sampling/tile construction,
CPU transforms, host/device transfers, synchronized model-forward wall time,
CUDA-event forward time, local encoding/saving, and Drive copy/hash verification.
Model loading and real-tile warm-up are separate. Peak allocated/reserved GPU
statistics reset after warm-up. There are **no measured timing or peak-memory
results yet**; the earlier total slide times cannot provide this decomposition.

## Pending user decision

The user was asked whether to reacquire only existing pilot file
`ee261db5-3576-4c52-90b4-4c8e16f7937e` (TCGA-33-4547), **95,344,817 bytes**.
It is the median raw file size among the nine slides and has 512 selected tiles.
Reacquisition would bring cumulative raw transfer to **1,115,547,518 bytes**,
within the original 10 GB budget, without adding a patient or cohort slide.

Permission remains pending because the request specified existing downloads.
OpenSlide reading/tiling requires a raw SVS; cached feature arrays cannot replace
that measurement. A100 projections will use measured GPU-forward fractions and
will be labeled hypothetical, not A100 benchmarks. No hardware switch is planned.

The copyable command is in [COMMANDS.md](../COMMANDS.md). Any subsequent measured
result must be saved as another completed checkpoint alongside this record.
