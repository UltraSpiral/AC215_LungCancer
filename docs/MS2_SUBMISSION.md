# Milestone 2 submission and presentation checklist

Current as of checkpoint 29, 2026-10-20. This is the submission entry point for
the bounded, preprocessed-slide MVP. [Readiness details](MS2_READINESS.md),
[design evolution](MS2_DESIGN.md) and [execution evidence](evidence/ms2/2026-10-20/README.md)
provide the supporting records.

Checkpoint 30 adds the detailed, source-based
[technical overview](TECHNICAL_OVERVIEW.md). Internal draft presentation and
rehearsal materials are excluded from the public deliverables.

## Supplied submission and presentation requirements

The user supplied these course instructions:

> All deliverables must be submitted via GitHub (milestone2 branch); submit the full commit hash on Canvas by 10:00 PM ET, October 20th.

> Slides: Bring slides that walk through what you built, why, and what's next.

The dated requirement is **October 20, 10:00 PM ET for the full commit hash on
Canvas**, pointing to the repository deliverables. Slides are required for the
TF presentation. Follow the course platform for any additional deck-submission
instruction. The task list below does not impose a deck-first order. Preserve
the exact submitted SHA: later commits do not alter the earlier snapshot.
Canvas submission has not been executed or verified by this project record.

## Technical deliverables prepared

- Native Apple M1 / Linux ARM64 CPU, Python API and Node/nginx frontend images;
  Dockerfiles, Python uv manifests/locks, npm lock and separate Compose files.
- Real GDC ingestion/specimen auditing, physical tiling, frozen UNI2 embeddings
  and an actually fitted baseline. The eligible cohort is 44 independent
  patients, split 32 training / 6 validation / 6 test. Source/configuration,
  selected saved experiment metadata and the original result summary are in Git.
- Data snapshot, source checksums, encoder/model/split identities and a
  read-only input mount. Inputs remain outside images and Git.
- A real browser/backend skeleton using one supported raw slide, content-based
  cache resolution and new predictions from the saved classifier.
- A tested single-command bounded demonstration, with complete logs, actual
  input identity, real preprocessing output, HTTP prediction and overlay.
- The original successful Docker screenshot, CPU and backend JUnit reports,
  image identities, preprocessing visuals, original saved training metadata,
  browser result/error screenshots and the original MS1 design appendix.
- A documented MS1 → simpler MS2 scope change, including the user's report
  that the TF approved MS1 and allowed simplification for an MS2 MVP.

These are implementation/evidence records, not a guarantee of course credit.
GDC acquisition and UNI2 feature extraction ran in Colab. Docker demonstrates
ingestion/validation of the prepared snapshot, a real preprocessing smoke and
cached-feature classification. Fresh UNI2 extraction inside Docker remains
unverified. The current demo does not claim arbitrary uncached-slide support.

## Exact demo commands

On the current Mac, the inputs are already restored. Working directory:

```bash
cd /Users/shlokdholakia/Documents/Harvard/Semesters/SEM3/AC215/LungCancer
make ms2-demo
```

Codex executed this command successfully on the M1. It builds/starts the app,
checks the browser-facing backend, builds the CPU verifier, verifies the input
inventory, runs the real 16-tile preprocessing smoke, streams the supplied raw
slide to the real HTTP API, polls the result, checks it against the frozen
reference and saves the actual overlay and image identities. It leaves the app
running at **http://127.0.0.1:8080/**.

Each invocation creates a new ignored `local_outputs/ms2/<UTC>-<id>/` directory.
Commands retain their exit status and combined logs. Existing CPU/app evidence
is preserved. A failed stage produces an error report and a failing command
exit; there is no fabricated success or mock prediction fallback.

The new preprocessing smoke uses **16** tiles and is a separate real-data
check. The classifier consumes the existing **512** model tiles from the
immutable cache. The smoke's new tiles are not described as fresh model
features. No weights, additional slides, training, split changes or new test
metrics are involved.

For the live browser demo, these simpler commands remain valid:

```bash
make app-up
# Open http://127.0.0.1:8080/ and upload:
# local_data/cpu_bundle/sample/sample.svs
make app-stop
make app-resume
```

The original CPU and app test suites already passed. Their reports are in the
evidence directory; reruns are unnecessary merely to read the submission.

## Reviewer and teammate access

Git contains source, configuration, selected evidence and exact commands.
The private portable input archive is deliberately separate. Before the demo,
ensure the presenting teammate/reviewer has authorized access to the existing
snapshot and understands that a Git clone alone does not contain model/cache
binaries. Do not download additional slides or UNI2 weights for this MVP.

On a new ARM64 checkout only, with an already-obtained copy of the archive:

```bash
python3 scripts/unpack_cpu_bundle.py \
  --archive '/path/to/CPU Verification Audit Oct 20 2026.tar.gz' \
  --sha256 c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988 \
  --destination local_data/cpu_bundle --apply
make ms2-demo
```

The restore command refuses an existing destination. On the current Mac, skip
restoration and preserve `local_data/cpu_bundle/`. Python 3.11+ and Docker
Desktop/Compose are required on the host; model dependencies run in containers.
Public image-build dependencies require network on the initial build. Runtime
CPU preprocessing is offline. Host npm/HF login/Torch are unnecessary for this
command. Full browser regression testing has separate development prerequisites
in [LOCAL_APP.md](LOCAL_APP.md).

## Remaining team tasks, separated by when they are needed

1. **By October 20, 10:00 PM ET: submit the full repository commit hash on Canvas.**
   Use the full pushed SHA for the chosen code/documentation/evidence snapshot.
   Compare `git rev-parse HEAD` with `git ls-remote origin refs/heads/milestone2`
   if source changes are made before submission. Canvas submission must be
   completed in the course UI; Codex has not executed or verified it.
2. **Before the TF presentation: prepare the actual deck**, subject to any
   additional explicit slide-submission rule. Use the repository's original
   mock-up, figures, scope comparison and actual execution records. Keep the
   team talk within the supplied 10–15-minute range. No draft presentation
   materials are included as an executed technical deliverable.
3. **Before presenting: rehearse together and confirm demo input access.**
   Everyone should explain the whole repository and their actual contribution.
   Verify the demo machine and existing private snapshot access. Use the
   technical overview and walkthrough below; do not invent team roles.

## Presentation and repository walkthrough

| Topic | Show / explain | Useful files |
|---|---|---|
| Problem and approved MVP | Three specimen classes; research demo; original four-screen design simplified to one review flow | MS2_DESIGN.md and original appendix image |
| Data operations | Specimen UUID chain, MD5/SHA, raw budget, one ambiguous exclusion, patient-level assignments | lungcancer/gdc.py, download.py, configs/modeling_snapshot_44_audit2.json |
| Preprocessing | Both MPP axes, ~0.5 MPP, 224px tiles, tissue fraction, deterministic coordinates; sparse-normal limitations | lungcancer/preprocess.py, safety.py, configs/preprocessing.json |
| Baseline | Frozen UNI2-h; 1536-dimensional features; slide mean pooling; training-only scaler; C=0.01 logistic head | lungcancer/features.py, modeling.py; saved-training-metadata.json |
| Results and next decisions | Validation F1 0.667; six-patient test F1 1.000 with reused-test caveat; compare majority baseline; no clinical claim | checkpoint 16 and saved experiment metadata |
| Runtime architecture | Versioned prepared features upstream; byte-content cache matching; newly computed probabilities; unsupported input failure | backend/model.py, backend/app.py, compose.app.yml |
| UI refinement | Original design → supported-slide upload → real result; tile-location overlay; no invented certainty/heatmap | frontend/src/features/ and MS2_DESIGN.md |
| Verification/debugging | 29 CPU tests, 14 backend tests, 10 browser/API scenarios; fixed internal-network host-port failure; new command passed | evidence directory, scripts/run_ms2_demo.py, checkpoint 26 |
| Limitations and next work | No uncached-slide encoder path in Docker; uncalibrated probabilities; tiny/reused test; preparation/site confounding | VERIFICATION_MATRIX.md and checkpoint 16 |

Be ready to answer: Why are normal samples from cancer patients still normal?
Why was one slide excluded? Where is the scaler fitted? Why is the encoder
frozen? How do cached features differ from model weights? Why do renamed bytes
work? What happens to an unknown slide? Why are red rectangles not a tumor
heatmap? How does the browser reach the API? What does each lock/version ID
protect? Which checks used real data and which used unit fixtures?

The local demo uses no HF/cloud credentials. Model/cache inputs are mounted
read-only, with upload/job output locations separate. Colab used supported HF
authentication for gated weights; credentials and weights were not copied into
the images, Git or portable input snapshot. Explain credential flow without
displaying secret values.
