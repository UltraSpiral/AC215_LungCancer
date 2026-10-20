# MS2 rubric alignment and remaining deliverables

Assessed 2026-10-20 against the rubric supplied in chat and the current
milestone2 repository at 99c52a33ca4f097f27c369af16622740044295ca plus local handoff
updates. This is an assessment, not a claim of completed infrastructure or
permission to start previously paused data/model acquisition or training.

## Does the baseline respect the assignment?

Yes, as a technical interpretation of the supplied vision-team requirement to
train or adapt a baseline. The planned visual classifier uses a pretrained
UNI2-h pathology vision transformer, frozen tile feature extraction, mean
pooling into a slide representation, and a learned multinomial L2 logistic
classification head. It is a foundation-model transfer-learning/linear-probe
baseline. Only the head is trained; we must not claim to have trained or
fine-tuned UNI2-h. Mean pooling is our simple slide-level baseline design,
not a claim that the UNI authors prescribe it for every WSI task.

This is a defensible first baseline for a small engineering cohort: it isolates
representation extraction from fitting, limits learned parameters, and makes
reproducible versions/cache reuse straightforward. A bigger trainable network
is not a stated MS2 requirement. Its suitability still needs an actual honest
experiment, a majority baseline, patient-separated evaluation and limitations.
No classifier has actually been trained on our real cohort yet.

The official UNI repository includes a linear-probe evaluation implementation
using logistic regression on extracted features, including a sklearn option:
[official linear-probe code](https://github.com/mahmoodlab/UNI/blob/main/uni/downstream/eval_patch_features/linear_probe.py).
[Official model/feature documentation](https://github.com/mahmoodlab/UNI).
This supports the baseline choice, not a guarantee of course credit or lung
slide accuracy.

## Current repository against the provided rubric

| MS2 requirement | Current verified evidence | Remaining work |
|---|---|---|
| Reproducible environment | Colab environment/package/system records, setup helper, pyproject.toml, pinned OpenSlide wheels, verified code/artifact recovery | Per-Python-container uv manifests/locks and build/run instructions; capture actual running-environment screenshot |
| Robust ingestion/preprocessing | Real GDC query/raw responses, specimen-linked labels, checksummed downloads, region-based physical-scale tiling; 9 slides processed | Containerize and run the components with a documented small real-data example |
| Data/model version tracking | File UUID/MD5, exact query/timestamps, manifest, pinned UNI2 revision/checksum, configs and cache fingerprints | Tie these existing identifiers to each container/run; DVC is optional under the supplied minimum |
| Baseline training/adaptation | Frozen UNI2 real embeddings; classifier/scaler/split/evaluation code and prior focused tests | Actually fit/save a real baseline; log dataset IDs, parameters, results and next decisions. No real models/evaluation directories exist yet |
| One-command containerized end-to-end run | Reusable individual Python CLIs | No Dockerfile, compose file, Makefile run target or uv.lock exists; implement orchestration and prove a real run |
| Basic UI/backend interaction | React UI, HTTP adapter, job contract and stdlib stub are present | Default mode is in-browser mock; no UI build or actual UI-to-HTTP interaction has been tested here. A clearly labeled stub can support a skeleton demonstration, but its fixture predictions are not baseline/model evidence |
| Submission evidence | Pilot images, embedding audits, raw metadata and tests from prior work | Actual model/run logs, sample input-to-output artifact, container evidence, runtime screenshot, presentation and final committed/pushed full SHA |

The current repository is **not yet a complete MS2 submission**. The material
missing deliverables are MLOps execution/evidence and a fitted baseline, rather
than model complexity. No grade is inferred from this audit.

## Scope correction from the newly supplied rubric

The original project brief explicitly deferred Docker, deployment and frontend
implementation. The course rubric now makes containerization and a working app
skeleton part of MS2. Therefore the earlier data/model-only scope is insufficient
for the submission, even though the classifier design is suitable. The model
plan can stay; the submission implementation plan needs an infrastructure work
track. This assessment does not silently launch Docker installation, provision a
VM, add deployment/Kubernetes or expand the cohort/download budget.

Use the [course template](https://github.com/dlops-io/project-setup-template) for
structure and uv/container conventions. Its broader RAG/vector-database,
Kubernetes and cloud examples are not all requirements for this vision MS2.
Keep the actual project small and explain the chosen boundaries.

## Revised priorities for a time-limited submission

1. Keep the frozen-backbone linear probe. Finish one real, versioned baseline
   experiment after the cohort/authentication choices are resolved. Keep patient
   separation and honest small-sample reporting. Do not substitute filename-based
   UI fixtures or synthetic embeddings for a real model result.
2. Containerize the core ingest/preprocess/feature/model workflow with uv-managed
   Python dependencies, shared versioned input/artifact locations and credentials
   supplied at runtime. Reuse images where practical; preserve each component's
   documented command/environment. Never bake gated UNI2 weights or tokens into
   source/images or publish them.
3. Add a real one-command start-to-finish entrypoint (for example make run backed
   by Compose). Save the selected data snapshot, preprocessing/encoder revision,
   classifier config and logs with the output. A command written in documentation
   without an actual run is insufficient evidence.
4. Exercise the existing UI's HTTP interaction with an actual backend endpoint.
   Real-model inference gives the strongest coherent demo; a disclosed stub can
   demonstrate the app skeleton if clearly separated from the real baseline
   experiment. Show a request and response, including a real error path. No
   mock probability is an evaluation result.
5. Capture screenshots and a small input-to-output example; update README and
   early-experiment/next-iteration notes, commit/push deliverables to milestone2,
   verify remote SHA, and prepare a short presentation/Q&A walkthrough.

## Current host and deadline limits

Inspection found uv 0.12.21 installed, no docker executable and no
/var/run/docker.sock. A Docker-capable host/daemon has not been established.
We cannot claim a container build/run from this Colab. Do not assume that
installing a client creates a usable Docker host, and do not bypass security
controls or provision new paid resources without authorization.

The earlier 45–60-minute target in ONE_HOUR_PLAN.md covered a reduced modeling
run AFTER authentication/approval. It excluded container builds, runtime
provisioning and verified UI/backend execution. It is **not** an estimate or
guarantee for completing the entire MS2 rubric. Model fitting itself is expected
to be small relative to data preparation; no real cohort fitting benchmark exists.
Prioritize the missing runnable infrastructure/evidence before adding model
complexity. The 15-patients/class scope choice and HF login remain pending.

## Presentation explanation

A concise accurate description is: We adapt a pretrained pathology vision
transformer to three lung slide classes by extracting frozen tile embeddings,
mean-pooling them and training a regularized linear classifier. We version each
specimen/file, preprocessing configuration and encoder checkpoint, group splits
by patient, and package the pipeline into reproducible components. Only claim
the final packaging and training once they have actually run.

Be prepared to explain why UNI2 is frozen, what parameters the linear head
learns, how labels resolve to the actual specimen, why normal samples from
cancer patients are not automatically tumor, how patient leakage is prevented,
what mean pooling loses, and how credentials/data/model versions flow through
containers without exposing secrets.

## What this assessment ran

Read local source/configuration, compared existing deliverables to the supplied
rubric, checked Docker/uv availability, and consulted official UNI/template
sources. No data/model/package download, installation, training, frontend build,
backend service or Docker build/run was started. Documentation is persisted with
SHA256 read-back via scripts/persist_records.py.

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
