# LungCancer — Milestone 2

Research prototype for three lung specimen classes: `non_tumor`,
`adenocarcinoma` and `squamous`. The working app recognizes one supplied slide
by its file contents, loads its verified UNI2 features and computes a prediction
with the real saved classifier. Identical slide bytes renamed to another
`.svs` filename work; an unsupported slide returns an error and no prediction.

[Setup and private input access](docs/REVIEWER_SETUP.md) ·
[Pipeline stages and boundaries](docs/PIPELINE_SCOPE.md) ·
[Technical explanation](docs/TECHNICAL_OVERVIEW.md) ·
[MS2 submission guide](docs/MS2_SUBMISSION.md)

## Prerequisites and inputs

The verified platform is Apple Silicon running Docker Desktop with native
Linux ARM64 containers. Host tools: Git, Make and Python 3.11+. Docker Compose
is included with Docker Desktop. The initial build needs public dependency
access; the CPU verification runtime is offline. Host npm, Torch, HF login and
UNI2 weights are not needed to start this prepared-feature demo.

A Git clone contains source and selected evidence. It does **not** contain the
raw sample, classifier or embeddings. Obtain the existing access-controlled
CPU input archive and follow [the checksum/restore instructions](docs/REVIEWER_SETUP.md)
on a new checkout. It contains 187 files and is 186,505,459 bytes. On the
existing project Mac, `local_data/cpu_bundle/` is already restored; preserve it.

## Run

From the repository root, with Docker running and the input bundle restored:

```bash
make ms2-demo
```

This single command builds/starts the app, validates the prepared snapshot,
runs a real 16-tile preprocessing smoke, uploads the supplied slide to the real
HTTP API, checks the saved-classifier prediction and saves its overlay and
image identities. Open **http://127.0.0.1:8080/**. For browser interaction choose
`local_data/cpu_bundle/sample/sample.svs`, then **Analyse slide**.

Expected result: **Non-cancerous tissue (`non_tumor`)**, **512** cached model
tiles and the recorded ICC-profile warning. The red rectangles show sampled
tile locations, not tumor detections. New run evidence is saved under
`local_outputs/ms2/<UTC>-<id>/`; app jobs are under `local_outputs/app/jobs/`.

The **16 new smoke tiles are a separate preprocessing check**. Classification
uses the immutable **512-tile cache** from the completed Colab run. This command
does not extract fresh UNI2 features or train a model. The
[pipeline map](docs/PIPELINE_SCOPE.md) identifies every stage's environment,
input, output and executed verification boundary.

For an app-only start or later stop/resume:

```bash
make app-up
make app-stop
make app-resume
```

Use the [isolated reviewer instructions](docs/REVIEWER_SETUP.md#parallel-run-with-an-existing-app)
to test another checkout on a separate project/port without replacing the
current app or its image tags.

## Model and data version

The completed baseline uses frozen UNI2-h features → slide mean pooling →
training-only StandardScaler → L2 multinomial logistic regression, **C=0.01**.
The corrected cohort has **44 independent patients**, split **32/6/6**. One
ambiguous specimen chain was excluded without moving other assignments.
Validation macro F1 is **0.667**; test macro F1 is **1.000 on only six patients**,
previously evaluated in the provisional run. These are preliminary engineering
results, without clinical validation. Read the
[results and limitations](docs/checkpoints/2026-10-20-16-modeling-results.md).

The bundle manifest, source SHA256/MD5, encoder, model, classifier and split
identities are verified before use. The exact snapshot and stage paths are in
[PIPELINE_SCOPE.md](docs/PIPELINE_SCOPE.md). Inputs mount read-only and remain
outside image layers and Git.

## Evidence and repository navigation

- [Original logs, JUnit reports, Docker screenshot, preprocessing visuals and replay output](docs/evidence/ms2/2026-10-20/README.md).
- [Real browser result](docs/evidence/2026-10-20-app-result.png) and [unsupported-input error](docs/evidence/2026-10-20-app-unknown.png).
- [App architecture and browser/backend checks](docs/LOCAL_APP.md): 14 backend tests and ten real browser/API scenarios passed in the saved run.
- [CPU verification](docs/CPU_CONTAINER_VERIFICATION.md): 29 tests, 44 real caches, 22,483 finite vectors and 12 frozen prediction references passed.
- [Original MS1 mock-up and deliberate MS2 refinements](docs/MS2_DESIGN.md).
- [Verification matrix](docs/VERIFICATION_MATRIX.md), [current status](STATUS.md) and [checkpoint index](docs/INDEX.md).

GDC acquisition, frozen UNI2 extraction and baseline training ran in Colab.
The complete fresh-UNI2 scientific pipeline has not been verified inside
containers. The app deliberately rejects uncached slides. Further downloads,
weights, experiments or split changes are outside the current task.

The intact [historical pilot README](docs/history/2026-10-20-pilot-readme.md)
is retained as history, with old artifact links annotated. Use the setup and
commands above for the current milestone.
