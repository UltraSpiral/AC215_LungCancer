# Exact artifact and record locations

Persistent root: `/content/drive/MyDrive/LungCancer_AC215`.
Local workspace: `/content/LungCancer`.

## Persistent Markdown

- `/content/drive/MyDrive/LungCancer_AC215/docs/INDEX.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/CHECKPOINTS.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/COMMANDS.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/ARTIFACTS.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/LATEST_BACKUP.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-18-00-environment.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-18-01-encoder-ready.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-18-02-pilot.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-18-03-pilot-evidence.md`
- `/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-19-04-records.md`

## Existing pilot evidence

- `/content/drive/MyDrive/LungCancer_AC215/artifacts/environment.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/encoder_smoke.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/encoder_source.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery/query.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery/manifest.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery/manifest.csv`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery/audit.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_selection.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/download_ledger.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_results.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/unit_tests.xml`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/README.md`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/details.md`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/details.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/summary.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/visual_audit_notes.json`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/documentation_persistence.json`

Raw GDC pages are preserved under `/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery/` as `raw_page_*.json`, with requests and retrieval timestamps.

## Three inline audit panels

- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/non_tumor_audit.jpg`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/adenocarcinoma_audit.jpg`
- `/content/drive/MyDrive/LungCancer_AC215/artifacts/pilot_review/squamous_audit.jpg`

## Per-slide persistent directories

- **TCGA-33-4547 — non_tumor:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/ee261db5-3576-4c52-90b4-4c8e16f7937e/`
- **TCGA-05-4403 — adenocarcinoma:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/f6c36a27-f310-4c96-b5bf-1b6adc5f86f9/`
- **TCGA-66-2794 — squamous:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/bc589465-32ab-406a-94b1-ed48f412f2d9/`
- **TCGA-58-8391 — non_tumor:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/2908ac70-541d-4521-9cf5-83e1178263ea/`
- **TCGA-55-A493 — adenocarcinoma:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/179c64eb-e8ae-46fa-ba37-a2180dcd4ad2/`
- **TCGA-98-A538 — squamous:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/660c880b-d78b-4b8b-aceb-5dc7c8e4a3f1/`
- **TCGA-55-7910 — non_tumor:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/615609e8-fb52-41f7-8abe-d0e9d4d14742/`
- **TCGA-69-7761 — adenocarcinoma:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/8cc3b5f7-1f74-4bb9-a046-9870d8cdf912/`
- **TCGA-60-2715 — squamous:** `/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/90c06ba4-30bf-49d5-a84b-ddc213de048d/`

Each directory contains `thumbnail.jpg`, `contact_sheet.jpg`, `tissue_mask.png`, `tissue_mask_overlay.jpg`, `selected_tiles_overlay.jpg`, `coordinates.npz`, `preprocessing.json`, `embeddings.npz`, and `embeddings.json`. The details JSON lists every exact file path.

## Source and helpers

- Archive directory: `/content/drive/MyDrive/LungCancer_AC215/code_backups/`.
- Latest exact archive path and SHA256: `/content/drive/MyDrive/LungCancer_AC215/docs/LATEST_BACKUP.md`.
- Direct display helper copy: `/content/drive/MyDrive/LungCancer_AC215/code/scripts/show_pilot.py`.
- Direct documentation persistence helper copy: `/content/drive/MyDrive/LungCancer_AC215/code/scripts/persist_records.py`.
- Source archives include reusable modules, scripts, tests, configs, documentation, and AGENTS.md.
- Credentials, raw SVS files, and encoder checkpoint weights are excluded from these archives.
- Temporary raw storage `/tmp/lungcancer-raw` is empty after verified cleanup; it is not persistent.

Download files can be reacquired by UUID/MD5 after authorization. No original or persistent slide was deleted.

## Full runtime recovery checkpoint

- Project snapshot: `/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z`.
- Archive member hashes, SHA256 inventory, artifact receipts, Git bundle and final
  `VERIFICATION.md` are stored there; no gated weights or raw SVS are included.
- Original proposal PDF is included in the private source archive, not public Git.
- Private session: `/content/drive/MyDrive/LungCancer_AC215/private_codex_recovery/20261019T002107Z/01a1513c-c07c-7100-8c49-70f63dff2251` (never commit to GitHub).
- Native session ID: `01a1513c-c07c-7100-8c49-70f63dff2251`; actual home `/root/.codex`.
- Recovery instructions and every required setup cell: persistent `docs/RESUME.md`.
- Exact installed versions: `artifacts/recovery_environment/installed_environment.json`.
