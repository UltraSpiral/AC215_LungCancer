# Training plan after the frontend addition

Reviewed 2026-10-20 against milestone2 commit
`99c52a33ca4f097f27c369af16622740044295ca`.

## Decision

The scientific training plan does **not** need to change. The new commit adds
95 files under frontend/; it changes no lungcancer/, configs/, tests/,
pyproject.toml or requirements.txt file. Its class contract uses the same
non_tumor, adenocarcinoma and squamous labels. Its documented classifier is
already UNI2-h tile embeddings plus logistic regression.

Keep the existing frozen encoder, preprocessing, slide aggregation, classifier
and patient-level evaluation. The A100 supplies more resources; it does not
justify an architecture change, changing labels, increasing tile counts to match
UI fixtures, or replacing the initial baseline with fine-tuning/attention MIL.
Current authorization remains pilot review only: no new slide/model/package
downloads, profiling, training or experiments.

## Modeling sequence — unchanged and awaiting authorization

1. Review the nine-slide visual audit and document preparation/site/masking
   limitations. Preparation remains frozen by TS-barcode inference, not explicit
   Frozen metadata. All pilot patients remain development/training candidates.
2. After review, propose a preparation-matched cohort initially around 30–50
   independent patients per class if feasible. Prefer one slide/patient/class;
   include normals from both projects and document site balance. This is an
   engineering target, not evidence of statistical adequacy.
3. Cost the actual selection and agree any necessary raw-transfer expansion
   before acquisition. Current cumulative budget is 10,000,000,000 bytes, with
   1,020,202,701 already transferred. No expansion is approved. Resolve missing
   OpenSlide, HF login and pinned UNI2 checkpoint only when setup is authorized.
4. Save fixed grouped train/validation/test assignments near 70/15/15 when
   counts support it. Keep all paired tumor/normal slides from a patient together
   and inspected pilot patients in training. Preserve split assignments forever
   across experiments; do not tune preprocessing with final test patients.
5. Use original local SVS files and OpenSlide at ~0.5 MPP, 224×224, max 512
   deterministic spatially distributed tissue tiles. Reuse compatible pilot
   caches. Freeze UNI2-h revision d517a8dd47902dd7c308b3c36f63bce47e7b9a43;
   use official eval transforms, no stain normalization or new aggressive filters.
6. Mean-pool embeddings per slide. Fit scaling on training slides only, train
   multinomial L2 logistic regression, and select from the existing small C grid
   using validation macro F1. Compare with the training-majority baseline.
7. Fix configuration, evaluate held-out test patients, and save named per-slide
   probabilities, metrics, counts and limits. Report undefined metrics honestly.
8. Demonstrate real single-slide inference on a held-out SVS renamed to an
   arbitrary filename. Save the model/configuration identities, QC warnings and
   analyzed-tile location overlay. This is required before claiming the real-data
   scientific MVP is complete. No such real model/evaluation/inference exists yet.

## Proposed later integration milestone — not implementation authorization

If the user chooses to connect the existing frontend, wrap the verified Python
inference pipeline in the UI's POST /jobs and GET /jobs/{id} contract, with
optional cancellation. The Python pipeline currently supplies a CLI, not the
real HTTP job service. Keep slide-level CLI/model validation complete before
claiming the UI is backed by a real model. No backend/deployment is built here.

Preserve the explicit class names and named probabilities, probabilities_calibrated:
false, tile count, QC codes, failure reason and model identity. Case IDs and
filenames may identify jobs/display records but must not select a prediction or
enter model inputs. Keep true no-tile/missing-scale failures as errors without a
fabricated class. Test the same renamed held-out file through CLI and service;
the class/probabilities should agree, and its patient must stay held out.

Concrete source-review findings to address before a real UI demo:

- Default frontend mode is mock. The mock adapter and reference stub choose
  illustrative results using sample identities/filenames. They are UI fixtures,
  not real predictions, valid labels, training examples or evaluation evidence.
  HTTP mode must point to a real inference service; the included stub is still
  a stub even when reached over HTTP. No mocks were executed in this review.
- The Python overlay key is analyzed_tile_locations_overlay, while the UI's
  optional key is analyzed_tiles_overlay. Harmonize the adapter/schema and
  provide a usable artifact URL when that overlay is displayed. Its role is
  analyzed locations, not tumor localization or a tumor heatmap.
- Mock tile counts include 1,862 and 738, exceeding the real 512-tile cap.
  Correct or explicitly label illustrative fixtures later; keep the real
  preprocessing cap and existing caches unchanged for modeling.
- Deep Zoom viewer tiles are overlapping JPEG display tiles. They are not
  the physical-scale-normalized classification tiles. Extract embeddings from
  the original SVS with the saved classifier configuration. Viewer pyramid
  conversion/storage, if needed later, is separate work and was not run here.
- UI wording non_tumor → "Non-cancerous tissue" is broader than the TCGA
  solid-tissue-normal training definition. Before a real demonstration, use
  wording that accurately conveys the trained class and limited disease scope.
- Confidence thresholds, tumor area, segmentation, growth-pattern subtyping
  and heatmaps remain deferred. The frontend already disables those sections;
  their presence as placeholder types creates no requirement to train them.

## Evidence and execution boundary

Read: frontend/README.md, api/contracts/inference.ts, api/adapters/mockAdapter.ts,
api/adapters/httpAdapter.ts, api/index.ts, mocks/predictions.ts,
features/analysis/deferred.ts, features/analysis/labels.ts,
tools/stub-model-server/server.py and tools/convert-slides/convert.py, plus the
Python training and inference modules. Compared the actual Git commit paths.
No installation, build, HTTP service, converter, model, training or test that
fits a model was run. This is a static plan/contract review, not integration
validation or a claim that the frontend works end to end.

## Subsequent one-hour deadline request

A smaller engineering cohort (15/class) is proposed in ONE_HOUR_PLAN.md to fit
the new deadline. This changes the original cohort target and needs the user's
pending choice. Frozen features, patient separation and held-out evaluation
remain required. No scope reduction, downloads or training have been executed.

## Full MS2 rubric subsequently supplied

The model choice remains a valid baseline. Submission priorities must now include
containerization, uv-managed environments, a one-command pipeline and execution
evidence, plus tested basic UI/backend interaction. These were deferred by the
original brief and have not been implemented or verified. See MS2_GAP_ANALYSIS.md.
Do not spend the limited time changing model complexity while these rubric
requirements are incomplete. The one-hour estimate was modeling-only.

## 45-slide readiness check — checkpoint 13

The proposed 15-patients/class cohort supports 11 train / 2 validation /
2 test per class in the metadata-only split check; all nine pilot patients stay
in training. Reasonable for an initial MS2 baseline experiment, with a tiny
held-out test and no stable/generalization claim. HF setup is now complete;
OpenSlide and pinned checkpoint acquisition still precede an authorized run.
No real model training has executed. See checkpoint 13.

## Latest execution order — checkpoint 14

User preference: finish modeling first, then MLOps deliverables. Their message
explicitly withholds training approval. No run is authorized yet. After explicit
approval, save a real baseline and evaluation/inference evidence with reproducible
configuration and data identities, then package and verify the workflow and app
interaction. Follow checkpoint 14 and AGENTS.md.


## Authorized modeling run — 2026-10-20 checkpoint 15

User explicitly approved: go ahead and start. This authorizes the proposed 45-slide, 45-patient cohort (15/class), necessary OpenSlide/pinned-UNI2 setup, 36 additional downloads within the unchanged cumulative 10,000,000,000-byte raw budget, real baseline fitting, fixed patient-level validation/test evaluation, and renamed held-out inference. All nine pilot patients remain in training. Modeling precedes MLOps; profiling remains deferred. Prior pause/pending-auth statements above are historical.

Run directory: `artifacts/modeling/20261020T0220Z/`; persistent counterpart: `/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z/`. A100 80GB and HF cached login verified; pinned OpenSlide wheels installed without replacing PyTorch/CUDA. Frozen UNI2 float32, 512 tiles, physical-scale config and pilot cache identities are preserved. No performance result is claimed at launch.

## Current outcome — checkpoints 16–17

The model was actually fitted/evaluated and real arbitrary-name inference passed.
Initial 45-slide processing took 49.32 minutes; a later conservative UUID-hierarchy
audit excluded one slide, and a corrected head/inference rebuild took 48.60 seconds.
The full audit/verification/CPU preparation exceeded a strict one-hour clock.
Final eligible cohort 44 (32 train / 6 validation / 6 test), validation macro F1
.667, test 1.000 on six previously observed provisional-test patients. No test-based
choice was made; small-sample/reused-test limits are explicit. Current model is
audit2. The user now requested M1 CPU containers and a guide; script logic passed
without Torch. Actual Docker/ARM64 execution and full slide-to-prediction container
proof remain pending. See the verification matrix and CPU container guide.
