# Current baseline and M1 verification

The real UNI2-h baseline is trained and has held-out predictions/inference.
The corrected eligible cohort has 44 patients (32/6/6); one multiply linked
slide was excluded. Validation macro F1 is 0.667; test macro F1 is 1.000 on only
six patients, with the audit/reused-test caveats in checkpoint 16.

Start with [STATUS.md](STATUS.md), [modeling results](docs/checkpoints/2026-10-20-16-modeling-results.md),
[Apple Silicon CPU guide](docs/CPU_CONTAINER_VERIFICATION.md) and
[verification matrix](docs/VERIFICATION_MATRIX.md). CPU Docker/ARM64 execution
and full slide-to-prediction container verification remain separate pending work.

# Lung histopathology classification MVP

AC215 engineering prototype: whole slide → tissue tiles → frozen UNI2-h → slide mean pooling → multinomial logistic regression.

**Pilot executed:** nine genuine GDC slides from nine patients, three per class; 4,608 finite real-tissue tile embeddings. Raw downloads totaled 1.020 GB. Artifacts and code backups are verified in Drive. **Real-data training, held-out evaluation, and held-out inference have not run.** Pilot review is required before expanding the cohort.

- [Complete pilot report and all slide images](artifacts/pilot_review/README.md)
- [Machine-readable results](artifacts/pilot_review/summary.json)
- [Label/preparation audit](artifacts/discovery/audit.json)
- [Current checkpoint](STATUS.md)
- [Persistent checkpoint and command index](docs/INDEX.md)

The existing proposal PDF was preserved. Raw slides, outputs, credentials, and checkpoints are excluded from Git.

Display the three saved class panels, including every pilot contact sheet and overlay, in one Colab code cell:

```python
%run /content/LungCancer/scripts/show_pilot.py
```

## Runtime and installation

Verified L4 with 23,034 MiB memory, approximately 53 GiB system RAM, Python 3.13.15, torch 2.11.0+cu130 and torchvision 0.26.0+cu130. PyTorch/CUDA was retained. GPU/network/Drive operations require approved command execution outside this session's terminal sandbox; keep security controls enabled.

Only OpenSlide was missing. Colab could not bootstrap ensurepip, so the two missing wheels were installed in a project-local directory without replacing system packages:

```bash
python -m pip install --no-deps --target .vendor -r requirements.txt
python scripts/preflight.py
```

Mount Drive and authenticate once from a notebook cell:

```python
%run /content/LungCancer/scripts/colab_setup.py
```

The script uses Colab Secrets HF_HARV and supported Hugging Face cached login, disables Git credential storage, and sets credential-file permissions to 0600. Never save token values in code, notebooks, outputs, or backups.

## Storage and restart

- Workspace: /content/LungCancer.
- Temporary pipeline-owned raw slides: /tmp/lungcancer-raw.
- Persistent project: /content/drive/MyDrive/LungCancer_AC215.
- Persistent subdirectories: code_backups/ and artifacts/.
- Local model checkpoint: supported Hugging Face cache, outside Git.

```bash
python -m lungcancer backup
python -m lungcancer restore
```

Copies are reread and SHA256 verified. Restore recovers missing local artifacts, including the cumulative download ledger. After a complete reset, mount Drive, recover the latest code archive from code_backups/ into the workspace, restore artifacts, install the two OpenSlide wheels if absent, and rerun preflight. Local paths alone do not survive a reset. Credentials and checkpoint weights are excluded from backups.

## Executed pipeline commands

Run from the repository root. These reusable commands have already been executed; you do not need to rerun them to inspect the pilot.

```bash
python -m lungcancer encoder-smoke
python -m lungcancer discover
python -m lungcancer audit --refresh-from-raw
python -m lungcancer select-pilot --per-class 3 --budget 10000000000
python -m lungcancer pilot --tile-config configs/preprocessing.json
python -m lungcancer review
```

Discovery saves the live field mapping, GDC release, exact query, timestamps, raw paginated responses, JSON/CSV manifests, and audit. Re-auditing saved raw responses makes no new query. The synthetic encoder smoke test only validates finite [2,1536] outputs; reported pilot features come from real tissue.

Individual stage commands:

```bash
python -m lungcancer download --file-id FILE_UUID --selection artifacts/pilot_selection.json
python -m lungcancer preprocess --slide /path/slide.svs --output artifacts/one_slide --tile-config configs/preprocessing.json
python -m lungcancer embed --slide /path/slide.svs --preprocessing artifacts/one_slide --revision ENCODER_COMMIT_SHA
```

Downloads reserve bytes durably before HTTP requests and conservatively charge a full slide for each attempt. They skip MD5-verified files, resume partial files where ranges are supported, and log failures. The pilot processes one slide at a time and deletes only its own temporary downloads after verified persistent copies. Use --keep-raw to retain pilot downloads.

## Labels and preparation

Files resolve through associated_entities into their actual nested sample and slide; case expansion is never flattened into slide labels.

| Actual linked sample | Project | Candidate class |
|---|---|---|
| Solid Tissue Normal | LUAD or LUSC | non_tumor |
| Primary Tumor | TCGA-LUAD | adenocarcinoma |
| Primary Tumor | TCGA-LUSC | squamous |

Primary diagnoses, UUID/barcode agreement, sample-type codes, preparation metadata, and redactions are checked. Ambiguous/conflicting links are excluded. Prior non-lung malignancies explicitly marked as prior diagnoses do not replace the current primary diagnosis. Labels describe submitted specimens, not independent expert annotations of every tile.

Discovery includes Tissue Slide and Diagnostic Slide. All eligible normals were frozen, while tumors included frozen and FFPE sections. The pilot uses frozen slides for all classes by inference. Pilot preservation_method fields are Unknown for eight samples and OCT for TCGA-98-A538; none explicitly says Frozen. Frozen preparation is inferred from TS barcodes using documented TCGA acquisition methods. Raw metadata values are preserved, and unresolved/conflicting preparation is never silently matched. Source-site differences remain a limitation.

## Preprocessing and frozen features

[configs/preprocessing.json](configs/preprocessing.json) controls approximately 0.5 MPP, 224×224 output, a non-overlapping physical grid, at most 512 spatially distributed deterministic tiles, and the initial 50% tissue threshold. Both MPP axes must be valid; objective power is recorded but never substituted. The CLI refuses slides without a memory-safe thumbnail pyramid.

The mask uses HSV thresholds, one small binary closing, and removal of tiny components; airspaces remain open. No stain normalization or blur/artifact filtering is applied. Coordinate conversion uses actual per-axis thumbnail dimensions. OpenSlide region locations are level-0 X,Y; read sizes refer to the chosen pyramid level. RGBA tiles are composited onto white. Unapplied embedded ICC profiles are recorded as warnings.

Every slide saves a thumbnail, tissue mask/overlay, analyzed-tile overlay, representative contact sheet, coordinates, coverage counts/histograms, physical scale, warnings, and embeddings. Thousands of individual tiles are not saved.

UNI2-h uses the official custom ViT architecture and evaluation transforms, frozen parameters, eval mode, and inference_mode. Batch size begins at 16 and decreases on GPU memory pressure. Pilot revision: d517a8dd47902dd7c308b3c36f63bce47e7b9a43. Checkpoint SHA256, architecture, transforms, and versions are recorded. Feature NPZs contain [N,1536] embeddings and aligned [N,2] coordinates. Fingerprints and atomic writes prevent incompatible reuse.

## Post-review modeling commands

Implemented and covered by focused tests; **not executed on real data**. Do not present evaluation on the nine pilot slides as meaningful. After review, select a frozen cohort initially around 30–50 independent patients per class, with at most one slide per patient per class. Save audited selected manifest records in cohort.json.

```bash
python -m lungcancer split --cohort cohort.json --output artifacts/splits.json
python -m lungcancer train --splits artifacts/splits.json --output artifacts/models/experiment_01
python -m lungcancer evaluate --splits artifacts/splits.json --model artifacts/models/experiment_01 --split validation --output artifacts/evaluation/validation
python -m lungcancer evaluate --splits artifacts/splits.json --model artifacts/models/experiment_01 --split test --output artifacts/evaluation/test
python -m lungcancer predict --slide /path/arbitrary_filename.svs --model artifacts/models/experiment_01 --output artifacts/prediction
```

Fixed splits balance multi-label patient groups at approximately 70/15/15; paired normal/tumor specimens remain together, and inspected pilot patients go to training. Existing splits cannot be regenerated in place. Scaling fits training slide means only. Training searches three L2 regularization values on validation macro F1, compares a training-majority baseline, and never opens test embeddings.

The saved bundle includes the sklearn pipeline, explicit classes, dependencies, encoder/preprocessing identities, split identity, and cohort identifiers. Evaluation saves named probabilities, confusion matrix, macro F1, balanced accuracy, per-class precision/recall, OVR AUROC when defined, counts, and error analysis by preparation/site/tile count. Undefined metrics are explicit.

Prediction uses a local slide and model bundle; it never parses a TCGA filename or uses diagnosis metadata. Success JSON includes class, named uncalibrated probabilities, tile count, quality warnings, and model/configuration identifiers. Failure JSON includes error status/reason and no fabricated prediction. Its overlay shows analyzed tile locations only.

## Tests and official references

```bash
python -m pytest -q
```

Executed: 23 tests passed. Synthetic slides, encoders, and classifier fixtures are used exclusively for unit tests. Renamed-fixture inference is not evidence of successful real held-out inference.

- [GDC search and nested biospecimen behavior](https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/)
- [GDC available fields](https://docs.gdc.cancer.gov/API/Users_Guide/Appendix_A_Available_Fields/)
- [GDC barcode hierarchy](https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/)
- [TCGA frozen/FFPE acquisition methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC3822112/)
- [OpenSlide Python API](https://openslide.org/api/python/)
- [Official UNI2-h configuration and transforms](https://huggingface.co/MahmoodLab/UNI2-h)

This is an engineering prototype without clinical validation or comprehensive disease coverage. No deployment, frontend, segmentation, calibration, or attention MIL is included.

## Runtime recovery

Read [STATUS.md](STATUS.md) and [docs/RESUME.md](docs/RESUME.md) before resuming.
The current user boundary is pilot review: no additional downloads, training or
experiments. Profiling is optional deferred work. Recovery includes checksummed
Drive artifacts, source archives, a Git bundle and a separate private Codex
snapshot; credentials and gated weights are excluded.
