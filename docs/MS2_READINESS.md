# Milestone 2 readiness — 2026-10-20, checkpoint 27

## Pipeline/setup follow-through — checkpoint 32

The [pipeline map](PIPELINE_SCOPE.md) now identifies each stage's environment,
inputs/outputs and boundary. [Reviewer setup](REVIEWER_SETUP.md) includes the
protected archive link, verified access scope and complete instructions. A
fresh isolated source/187-file restore passed make ms2-demo and all ten real
browser/API scenarios on the existing M1, with separate images/port/mounts and
preserved original app. [New evidence](evidence/ms2/2026-10-20/reviewer/README.md)
records clean source commit a25ed2a8aa19a59f7262942a4864ffa59ec7cb53.
The README is current; its intact pilot narrative moved to a linked history
page with unavailable private artifact links annotated. These results supersede
the earlier fresh-clone execution gap below. Another person's actual execution
and full fresh-UNI2 container processing remain unverified.

## Detailed technical explanation — checkpoint 30

Read [TECHNICAL_OVERVIEW.md](TECHNICAL_OVERVIEW.md) for the source/evidence-based
data, model, serving and container explanation. The MS1-to-MS2 scope comparison
is expanded in MS2_DESIGN.md. Public deliverables exclude internal draft
presentation and rehearsal materials. This update performs no new processing
and creates no slide deck. MS2_SUBMISSION.md quotes the supplied submission/
presentation requirements and separates those tasks without imposing a
deck-first repository-submission order.

## Current completion update — checkpoint 29

The bounded MVP now has an actually executed **`make ms2-demo`** command and
a committed evidence package: original CPU/app logs, reports, successful Docker
screenshot, preprocessing visuals, original saved experiment metadata, the
original MS1 mock-up appendix and the new input-to-output replay. See
[MS2_SUBMISSION.md](MS2_SUBMISSION.md) for the current entry point.

The user supplied the original proposal and reported TF approval of MS1 plus
permission to simplify MS2. The [design record](MS2_DESIGN.md) attributes this
feedback and documents concrete refinements. Prior missing-evidence/mock-up
and separate-command statements below are superseded by this update.

Remaining team tasks: actual presentation deck, shared rehearsal, confirmation
of reviewer/teammate access to the existing private input snapshot, and Canvas
submission of the final full SHA. The broader fresh-UNI2 container path remains
unverified; the executed command clearly separates the new 16-tile smoke from
the immutable 512-tile model cache. No training or fresh encoding ran.

## Correction — checkpoint 28: feature caching and pipeline scope

The earlier assessment made fresh UNI2 extraction inside containers sound like
an unconditional MS2 requirement. That overstates the supplied rubric. It asks
for a reproducible containerized pipeline, real ingestion/preprocessing, a
trained/adapted baseline and an app skeleton; it does not explicitly prohibit
versioned precomputed features or demand encoder execution on every run.

Feature caching is an intentional valid design here. The saved classifier
contains learned parameters; cached embeddings contain features for particular
slides. The current app validates slide contents, loads those real features
and computes a new prediction with the saved classifier. It neither retrains
nor merely returns a saved answer. A slide without a supported cache is
rejected, as designed. Training is already complete.

What is unverified is specifically the larger raw-slide → fresh-encoder-features
→ prediction workflow inside containers, including an encoder path for inputs
without a cache. That is a limit on the broader claim, not evidence that the
cached app is broken or that caching fails the assignment. For MS2, document
the selected workflow boundary and its versioned upstream artifacts, and make
the ingestion/preprocessing and sample-input/output evidence easy to reproduce.
At checkpoint 28 the executed commands were separate scoped workflows. At
checkpoint 29, make ms2-demo executes the bounded prepared-feature workflow,
including a separate preprocessing smoke, with preserved input/output evidence.
The rubric's intended breadth remains a grading/scope interpretation; an
extra TF approval step is not imposed merely because features are cached.

This correction supersedes the stronger requirement interpretation in the
original checkpoint-27 narrative below. It changes no execution result,
scientific artifact, supported-input boundary or authorization.

## Original audit context

Assessment of the user's supplied MS2 rubric against the code and saved execution
evidence at `b57329de5fbcbb77a46feb216f32c127cc08a2d7`. The live
`origin/milestone2` SHA matched that commit before this documentation update.
This audit runs no new modeling, data acquisition, containers or browser tests.
It does not establish that Canvas submission or TF review has occurred.

The real baseline and cached-feature app are verified. The complete fresh-UNI2
scientific pipeline has not been verified start-to-finish inside containers.
The app screenshot establishes the working skeleton and cached inference.
The correction above distinguishes that broader unverified workflow from the
rubric's actual wording and the chosen cached-feature architecture.

## Requirement and evidence mapping

| Supplied requirement | Current evidence | Assessment / remaining verification |
|---|---|---|
| Environment supporting containers; clear setup | Native Apple M1, Docker Desktop Linux ARM64; [CPU guide](CPU_CONTAINER_VERIFICATION.md), [app guide](LOCAL_APP.md) | Executed locally. The supplied rubric permits local instance screenshots; a separate paid cloud VM is not established as necessary. |
| Dockerfiles and reproducible dependencies | `containers/cpu/Dockerfile`, `containers/cpu/pyproject.toml` + `uv.lock`; `containers/app/backend.Dockerfile`, `backend/pyproject.toml` + `uv.lock`; frontend Dockerfile, npm lock and pinned base-image identities | Built and tested for the existing CPU/API/frontend components. Frontend is Node/nginx, with npm dependencies; uv manages the Python components. The full UNI2 extraction/training environment has no separately verified locked container. |
| Robust data ingestion and preprocessing | GDC queries, checksummed downloads/budget ledger, specimen UUID audit and physical tiling ran on real data in Colab; reusable code is committed | Real ingestion exists. The CPU container ran an offline real-SVS 16-tile preprocessing smoke. GDC acquisition/orchestration was not verified as part of a complete containerized pipeline. |
| Train/adapt a baseline | [Corrected modeling results](checkpoints/2026-10-20-16-modeling-results.md), training/evaluation scripts and [44-patient snapshot](../configs/modeling_snapshot_44_audit2.json) | Completed in Colab: frozen UNI2-h, slide mean pooling, training-only scaler and L2 logistic regression C=0.01. UNI2 was not fine-tuned. No new training is needed to establish that a baseline exists. |
| Early experiments, rationale and next decisions | Checkpoint 16, [training plan](TRAINING_PLAN.md), saved private model/evaluation outputs | Results are documented: validation macro F1 0.667, test 1.000 on six previously observed provisional-test patients. Preserve tiny/reused-test, preparation, sparse-normal and site limitations. Add a concise current next-iteration explanation and selected original experiment artifacts to the submission evidence. No new experiments are authorized by this audit. |
| Data/model versions used by containers | Input snapshot, source SHA/MD5, model/classifier hash, split identity, encoder and feature fingerprints are checked and recorded | Verified for CPU/app. The frozen snapshot and explicit identities satisfy the supplied minimum version-tracking approach; DVC is not specifically required. |
| Compose and one-command execution | Existing CPU/app Compose plus new `make ms2-demo`, actually executed at checkpoint 29 | Bounded replay passed: app startup, prepared-input validation, real preprocessing smoke, actual upload/poll/prediction/overlay and image identities. Fresh UNI2 extraction is not part of this command or claim. |
| Containerized core pipeline, start-to-finish evidence | Checkpoint 29 executes the chosen prepared-feature workflow, with a separately identified real 16-tile preprocessing smoke and real 512-tile cached-model inference | Actual scoped input/output evidence is packaged. GDC acquisition and fresh encoder extraction occurred in Colab; their full container path remains unverified. The supplied rubric does not explicitly prohibit cached upstream features. |
| Minimal working UI/backend skeleton | Real browser → nginx → API → content-matched cached vectors → saved classifier → UI | Verified: 14 backend tests, frontend type/lint/production build checks, 10 real browser/API scenarios; renamed input invariance, unknown/modified input rejection and real API outage recovery. One supported preprocessed slide is sufficient for this disclosed skeleton. Arbitrary-slide support is not claimed. |
| Milestone 1 mock-up/wireframe, refinement based on feedback | Original proposal appendix rendered and visually inspected; [MS2_DESIGN.md](MS2_DESIGN.md) compares the four original screens to the working MVP | Packaged in checkpoint 29. TF approval/simplification feedback is attributed to the user's report. Illustrative original design images are separate from actual runtime screenshots. |
| Screenshot of running instance, sample input/output and logs | Existing app proof plus [the full selected evidence index](evidence/ms2/2026-10-20/README.md) | Packaged original CPU Docker screenshot/log/JUnit/JSON/visuals, saved experiment metadata, app logs/reports and new scoped replay outputs with hashes. Private input/model/embedding/weight binaries remain outside Git. |
| Fresh reviewer setup | Updated at checkpoint 32: actual isolated clean-source clone, verified archive restore, bounded replay and browser/API suite passed | Owner/one collaborator permissions checked; protected artifact and instructions linked. This is the existing M1/Docker installation, not another person's observed execution. |
| GitHub milestone2 and full SHA on Canvas | Implementation commit was pushed normally; local/live remote SHA matched before this audit | Publish final chosen deliverables, recheck live full SHA and submit that exact commit hash on Canvas by the supplied deadline, October 20 at 10:00 PM ET. Canvas submission is unverified. |
| Presentation and individual checks | Code, commands and evidence are available for a walkthrough | No presentation deck is tracked in this checkout. A deck may exist elsewhere; this audit has not verified it. Prepare the team presentation and shared understanding of all components. |
| RAG collection/chunking/vector DB/retrieval | Vision classification project | Not applicable to the vision branch of the supplied rubric. No RAG subsystem is needed for this project. |

The [course milestone2 template](https://raw.githubusercontent.com/dlops-io/project-setup-template/milestone2/README.md)
was consulted. It describes self-contained service Dockerfiles, uv manifests,
documentation and Compose. It is a starting layout; its example PostgreSQL,
ChromaDB and agent services do not establish extra vision-project requirements.
The user's pasted rubric is the basis for this assessment. The chosen pipeline
boundary should be explicit for review; this audit does not determine a grade.

## Original priorities, updated at checkpoint 29

1. **Selected pipeline boundary and replay: completed for the bounded MVP.**
   `make ms2-demo` passed; exact commands, source identities, scope and outputs
   are saved. It reuses versioned real features and the saved model. Broader
   fresh-UNI2 container execution stays outside this verification claim.
2. **Selected evidence package: prepared at checkpoint 29.** Original CPU/app
   evidence and modeling metadata are indexed with hashes; the unchanged full
   suites were not repeated. The new runner's relevant preprocessing/inference
   sequence was actually executed with new output paths.
3. **Design record: prepared; actual presentation and team rehearsal remain.**
   The original MS1 mock-up, implementation refinements and user-reported TF
   feedback are recorded. Prepare the deck and shared repository understanding.
   Confirm authorized private-snapshot access on the demo machine.
4. **Final publication and Canvas submission.** Publication receipts identify
   the final reviewed commit and live-SHA comparison. Put that full SHA on
   Canvas by the supplied deadline. Canvas submission has not been verified.

No extra slides, retraining, split changes, clinical validation, Kubernetes,
public hosting or optional profiling is needed merely to demonstrate the
already-completed baseline and app skeleton. New technical work must respect
the existing acquisition/weights/experiment boundaries.

## Existing evidence to package, without rerunning it

Working directory:
`/Users/shlokdholakia/Documents/Harvard/Semesters/SEM3/AC215/LungCancer`.

- `local_outputs/cpu/console.log`, `verification_all.json`,
  `cached_embeddings.json`, `real_preprocessing.json`, `unit-tests.xml`,
  `image_inspect.json`, `runtime_container.json`, `host.json` and
  `ms2-docker-success-2026-10-20.png`; preprocessing visuals are in the same tree.
- `local_outputs/app/` holds build/test logs, `jobs/backend-tests.xml`,
  `runtime-verification.json`, real job JSON/overlays and `browser-final/`.
- Current full modeling evidence is historically under
  `/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z-audit2/`.
  That is a Colab/Drive path, not a Mac directory to create. Existing restored
  model metadata, cohort, splits and prediction references are in
  `local_data/cpu_bundle/run/`.

This audit inspected saved evidence and Git state. It did not rerun tests,
change scientific data/code, add weights/slides, alter the running app, build
presentation slides or submit to Canvas. Local checkpoint source/Markdown
backups are recorded in [LATEST_BACKUP.md](LATEST_BACKUP.md). New private Drive
mirroring remains unavailable on this Mac; no upload permission is inferred.
