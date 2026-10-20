# Milestone 2 readiness — 2026-10-20, checkpoint 27

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
The two executed commands are currently separate scoped workflows; a single
combined scientific data-processing run is not established by their existence.
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
| Compose and one-command execution | `compose.cpu.yml` + `make cpu-check`; `compose.app.yml` + tested `make app-up` | Both commands work for their stated scopes. App startup is one command, followed by the user's upload. Neither command proves the full ingestion → preprocessing → fresh UNI2 features → saved-model prediction pipeline. |
| Containerized core pipeline, start-to-finish evidence | Real preprocessing and saved-model/cache checks succeeded separately inside ARM64 containers; real full-slide inference ran in Colab | The broader fresh-UNI2 workflow remains unverified. The rubric does not explicitly require encoder recomputation on every run. Define the versioned cached-feature boundary and document how the chosen ingestion/preprocessing and inference workflow runs; separate checks do not prove an unexecuted larger workflow. |
| Minimal working UI/backend skeleton | Real browser → nginx → API → content-matched cached vectors → saved classifier → UI | Verified: 14 backend tests, frontend type/lint/production build checks, 10 real browser/API scenarios; renamed input invariance, unknown/modified input rejection and real API outage recovery. One supported preprocessed slide is sufficient for this disclosed skeleton. Arbitrary-slide support is not claimed. |
| Milestone 1 mock-up/wireframe, refinement based on feedback | Existing React design, components and retained mock-only design states; HTTP implementation adds honest support boundaries and real results | Working design is present. No separately tracked original wireframe/deck or explicit record of actual TF feedback was found. Include/link the original design and document implementation-driven refinements; do not invent feedback. |
| Screenshot of running instance, sample input/output and logs | [Genuine result screenshot](evidence/2026-10-20-app-result.png), [unknown-input screenshot](evidence/2026-10-20-app-unknown.png), [actual execution summary/result](evidence/2026-10-20-app-verification.json) are committed | App proof is on GitHub. The successful CPU terminal screenshot, raw CPU build/run log, JSON/JUnit, Docker inspections and preprocessing visuals are saved locally/previously backed up, but are not tracked in Git. Publish selected sanitized evidence or explicit accessible evidence links for the submission. Keep raw slides, weights, model binaries, caches and secrets out of Git. |
| Fresh reviewer setup | Source archive extraction and Git recovery-bundle fresh-clone byte comparisons passed | Source recovery is verified. A new reviewer still needs authorized access to the existing private snapshot; a Git clone alone does not contain those inputs. The app has not been rerun from a fresh clone during this audit. |
| GitHub milestone2 and full SHA on Canvas | Implementation commit was pushed normally; local/live remote SHA matched before this audit | Publish final chosen deliverables, recheck live full SHA and submit that exact commit hash on Canvas by the supplied deadline, October 20 at 10:00 PM ET. Canvas submission is unverified. |
| Presentation and individual checks | Code, commands and evidence are available for a walkthrough | No presentation deck is tracked in this checkout. A deck may exist elsewhere; this audit has not verified it. Prepare the team presentation and shared understanding of all components. |
| RAG collection/chunking/vector DB/retrieval | Vision classification project | Not applicable to the vision branch of the supplied rubric. No RAG subsystem is needed for this project. |

The [course milestone2 template](https://raw.githubusercontent.com/dlops-io/project-setup-template/milestone2/README.md)
was consulted. It describes self-contained service Dockerfiles, uv manifests,
documentation and Compose. It is a starting layout; its example PostgreSQL,
ChromaDB and agent services do not establish extra vision-project requirements.
The user's pasted rubric is the basis for this assessment. The chosen pipeline
boundary should be explicit for review; this audit does not determine a grade.

## What remains, in priority order

1. **State and demonstrate the selected pipeline boundary.** Present versioned
   real features produced in Colab as upstream artifacts, then document the
   executed containerized preprocessing checks and cached-feature inference
   with exact commands, inputs and outputs. Check that the chosen scope has a
   reproducible one-command data-processing example; current app startup and
   CPU checks are separate. Caching is not itself a missing feature. Only if
   claiming the larger fresh-UNI2 container workflow must that missing execution
   be implemented and verified. Model loading does not require retraining.
   Current restrictions on weights/downloads and further real experiments
   remain. The rubric does not explicitly demand arbitrary new-slide support
   or fresh encoder execution on every run.
2. **Finish the GitHub evidence package.** Include selected sanitized original
   CPU run log, test report, real preprocessing output/visual, successful Docker
   screenshot, Docker/data identities and early modeling artifacts. Add an
   evidence index explaining input identity, commands and output. Existing app
   result JSON and screenshots are already committed. This is evidence
   publication, not a reason to rerun unchanged CPU checks, refit or redownload.
3. **Finish design and presentation records.** Include or link the original
   Milestone 1 mock-up; explain actual refinements and available feedback.
   Prepare the 10–15-minute team walkthrough, then Q&A and individual checks.
   Everyone should explain specimen labels, patient separation, scaler fitting,
   frozen encoder versus learned head, version identities, container networking,
   cached-feature limits, tests and the actual debugging fixes.
4. **Publish and submit.** Check the exact final diff, push normally to
   `milestone2`, verify local/live full SHA equality and put the final SHA on
   Canvas. The documentation commit containing this audit is not evidence that
   the pending technical work or Canvas submission has been completed.

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
