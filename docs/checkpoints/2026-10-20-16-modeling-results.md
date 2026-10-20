# Corrected real-data baseline — checkpoint 16

The approved 45-slide acquisition/extraction completed. A final hierarchy audit
excluded file 6125ea6f-c49e-4809-9502-f121e6d35d8c (TCGA-21-1076) because its linked
slide UUID occurs under two distinct portion UUIDs. Both links lead to the same
sample/class and non-FFPE evidence, but the user's conservative ambiguity rule
requires exclusion. No extra slide was downloaded. The corrected model uses
**44 independent patients: 15 non_tumor, 15 adenocarcinoma, 14 squamous**.

## What ran and passed

32 training patients (11/11/10), 6 validation (2/class), 6 test (2/class).
All other assignments were inherited from the original fixed split; no patient
moved and no assignments were regenerated. All nine inspected pilot patients
remain in training. The original 45-slide model is provisional history and is
preserved in the sibling directory; use the audit2 model below.

Frozen UNI2-h → mean pooling → training-only StandardScaler → multinomial L2
logistic regression. Selected C=0.01 using the prespecified three-value
validation search. Validation macro F1=0.6667,
balanced accuracy=0.6667.
Test macro F1=1.0000, balanced accuracy=
1.0000; majority macro F1=
0.1667, balanced accuracy=
0.3333.
Test confusion matrix is diagonal 2/2/2, with per-class precision/recall/AUROC 1.0.

**Six test patients are too few for a stable performance claim.** These patients
were previously evaluated by the provisional model. The correction used only
specimen metadata, independent of predictions; no test-based model choice was
made. This history limits a pristine-test claim. Labels are metadata-derived,
without independent pathologist adjudication. Preparation and source-site
confounding and sparse-normal masking remain limitations.

All 22,483 eligible tile vectors are finite and
coordinate-aligned. Forty-three slides have [512,1536] embeddings; one squamous
slide has [467,1536]. All 397 eligible-slide files and current run outputs passed
Drive SHA256 read-back. Saved scaler statistics match only the 32 training slides.
Real inference from an arbitrary `sample.svs` path passed with explicit named,
uncalibrated probabilities and an analyzed-location overlay. It matched the
held-out cached prediction within the recorded float32 tolerance.

## Provenance and budgets

Labels use file-associated slide UUID → nested specimen → actual linked sample
type/project. A patient's diagnosis never makes a linked normal sample positive.
A portion display-number mismatch is recorded as a warning, not substituted for
an explicit UUID relationship. Distinct compatible portion UUIDs are not silently
collapsed; truly ambiguous chains are excluded. The tightened full discovery
re-audit is 3,172 eligible of 3,220; 48 excluded. Original audit files remain.
Earlier messages proposing barcode equality as a universal portion resolver are
superseded by this conservative UUID-based audit.

Frozen preparation is inferred from TS/BS categories for all 44 eligible slides:
**0 explicit Frozen confirmations**. Raw preservation fields remain Unknown
for 40 and OCT for 4; all 44 linked portions report is_ffpe=false, which is
supporting non-FFPE evidence, not independent proof of freezing. Normals include
6 LUAD and 9 LUSC patients. Full linkage UUIDs, diagnosis checks, per-slide
candidate/accepted/rejected counts and scale warnings are in the provenance JSON.

Cumulative raw transfer/reservation: **5,453,285,795 bytes**, including
1,020,202,701 pilot bytes and 4,433,083,094 new bytes. Approved limit remains
10,000,000,000. Forty-five verified download attempts; zero download failures.
One public 71,138,367-byte SVS is retained in the private portable test archive;
other raw originals are reproducibly downloadable by saved UUID/MD5.
UNI2 checkpoint weights and credentials were not backed up or redistributed.

The initial pipeline ran 49.32 minutes; the audit correction/head rebuild and
real inference took 0.81 additional execution
minutes. Elapsed clock time from initial start to corrected completion was
69.32 minutes because of intervening audit/debugging. The complete verified
handoff did not meet a strict one-hour wall-clock deadline. Profiling remains
optional and deferred; these are not CUDA-synchronized stage timings.

## Exact paths and identities

Current persisted artifacts and complete results:
`/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z-audit2/`

Files: RESULTS.md, verified_results.json, cohort_provenance_and_qc.json,
exclusions.json, cohort.json, splits.json, model/classifier.joblib, model/model.json,
evaluation_validation/, evaluation_test/, inference_arbitrary_filename/,
inference_verification.json, test_confusion_matrix.png and verification_inventory.json.

Shared embeddings/visual audits:
`/content/drive/MyDrive/LungCancer_AC215/artifacts/slides/<file_uuid>/`

Raw metadata/query history:
`/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery/`

Updated strict manifest/audit:
`/content/drive/MyDrive/LungCancer_AC215/artifacts/discovery_v2/`

Encoder: MahmoodLab/UNI2-h revision d517a8dd47902dd7c308b3c36f63bce47e7b9a43;
checkpoint SHA256 6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e.
Official eval transforms, float32, ~0.5 MPP, 224 pixels, max 512, mask coverage 0.5,
seed 215, spatial sampling. Bounded coarser-pyramid thumbnail fallback is recorded
and implementation-pinned; unchanged legacy caches were reused.

Model ID: `42af9fb3f51e1539d994af4f20e2980e4118eac6a8cd665aeb372c1440b2fed5`.
Split ID: `964f3b6c073863efbe38b560cfe93b2783cff5d822c64bde12f71241a7a4f2c4`.
Source snapshot: configs/modeling_snapshot_44_audit2.json.
Code backups: see docs/LATEST_BACKUP.md and its Drive copy.

## Remaining work

M1 CPU container build/run verification belongs to checkpoint 17. Full
slide-to-prediction container execution and real UI/backend interaction remain
separate pending work. No additional cohort downloads, new real training
experiments, or profiling are authorized by the CPU preparation request.
