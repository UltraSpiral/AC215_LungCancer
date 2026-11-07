# Local preprocessed-slide application

For a new checkout, use [REVIEWER_SETUP.md](REVIEWER_SETUP.md): protected bundle
access, checksum/restore and a separate project/port/image configuration for
testing alongside the existing app. [PIPELINE_SCOPE.md](PIPELINE_SCOPE.md)
maps the upstream Colab stages and exact local input/output boundaries.

For MS2, **`make ms2-demo`** is now the tested single-command bounded replay:
it builds/starts this app, verifies the prepared snapshot and runs a separate
16-tile real preprocessing smoke, then uploads the real supplied slide and
captures its saved-classifier result/overlay. Existing 512-tile embeddings stay
immutable; the new smoke is not passed to UNI2 or the classifier. See
[MS2_SUBMISSION.md](MS2_SUBMISSION.md) and
[the actual replay evidence](evidence/ms2/2026-10-20/README.md).

The existing React interface now calls a real Python HTTP backend. The backend
matches uploaded file contents to one previously processed slide, verifies its
cached UNI2 vectors, mean-pools them in float64 and applies the saved audit2
StandardScaler/logistic pipeline. It computes new named probabilities on every
successful job. It does not copy reference predictions or use the filename,
case metadata or diagnosis as classifier inputs.

The native Apple M1 build, browser interaction, error paths and stop/resume
commands were executed. See [checkpoint 26](checkpoints/2026-10-20-26-cached-feature-app.md),
[the concise verification report](evidence/2026-10-20-app-verification.json),
[the actual result screenshot](evidence/2026-10-20-app-result.png) and
[the actual unknown-input screenshot](evidence/2026-10-20-app-unknown.png).

## Start, stop and resume

From the existing Mac checkout:

```bash
cd /Users/shlokdholakia/Documents/Harvard/Semesters/SEM3/AC215/LungCancer
make app-up
```

This is the tested single build/start command. It builds both native
`linux/arm64` images, starts them, waits for container health, and verifies the
actual browser-facing API route. Open **http://127.0.0.1:8080/**.
Docker Desktop and the already-restored private bundle are required. Host npm,
HF login and Torch are not required to start the app. Public build dependencies
are fetched on the initial image build.

```bash
make app-stop      # stop the app; preserve the private bundle and job evidence
make app-resume    # restart existing images and verify the browser route
make app-logs      # actual API/nginx logs
make app-down      # remove this app's containers/network; preserve bind-mounted evidence
```

Stop and resume were tested; the app was left running for review. Job JSON is
retained on disk, but in-memory HTTP job lookup is per app session. Old job IDs
are not resumed after restarting the API. Submit the slide again for a new job.

## Supported input and output

Upload `local_data/cpu_bundle/sample/sample.svs`, already present on the Mac.
Identical bytes under another `.svs` filename produce exactly the same result.
Only that supplied raw slide has an enabled content-to-cache mapping. Other
slides, including a one-byte-modified copy, return an explicit unsupported-input
failure and no prediction. Do not download slides to expand the demo.

Maximum file size is **80,000,000 bytes**; multipart requests are capped at
82,000,000 bytes. Upload streams spool to a bounded temporary area, one upload
at a time, and are discarded after hashing. Jobs receive generated UUIDs; user
filenames never become filesystem paths. Request metadata is ignored by the
classifier. A separate writable job directory stores JSON and the real overlay.

The UI shows the computed class, model ID, **512** actual model tiles and the
cached ICC-profile warning. Probabilities remain hidden in the UI; the API
returns explicit class names and `probabilities_calibrated: false`. The preview
uses the actual supplied SVS thumbnail and all 512 cached model coordinates.
It shows analyzed locations, not a tumor heatmap. The older 16-tile smoke
outputs are not used for model features, tile count or this overlay.

## Containers and API

`compose.app.yml` is separate from the unchanged offline CPU verifier. The
Python image uses a frozen uv lock with the proven model dependency versions
and FastAPI/uvicorn. The frontend uses `npm ci` with the original package lock;
Node and nginx image indexes are digest-pinned with ARM64 metadata in
`containers/app/base-images.json`.

The frontend is compiled with `VITE_INFERENCE_MODE=http` and API base `/api`.
nginx proxies same-origin requests to the internal API. Only web port 8080 is
published, bound to 127.0.0.1; the API has no published host port. Its network is
internal; the web service also joins the ingress network needed for host port
forwarding. Both roots and the trusted input mount are read-only. No raw slide,
classifier, embedding array, HF credential or UNI2 weight is baked into images.

Routes through the browser origin:

- `GET /api/health`: verified readiness and mode/model/snapshot identifiers.
- `POST /api/jobs`: bounded multipart `slide`, optional ignored `case_id`; 202 job ID.
- `GET /api/jobs/{id}`: genuine queued/running/done/failed state and result or error.
- `DELETE /api/jobs/{id}`: cancellation cannot be overwritten by a finishing worker.
- `GET /api/jobs/{id}/overlay`: actual overlay only for a successful current-session job.

The illustrative filename-based stub is not started. HTTP mode suppresses
fixture sample selection, filename-based viewer matching and the kitchen-sink
fixture route. Backend failures never fall back to mock predictions.

## Reproduce the executed checks

```bash
make app-test
PLAYWRIGHT_BROWSERS_PATH=local_outputs/app/browser-cache \
  LC_APP_EVIDENCE_DIR=local_outputs/app/browser-recheck \
  node frontend/scripts/test-app.mjs
```

The browser test requires the frontend's locked development dependencies and
native Chromium, installed by Codex during this run. Setup and all exact
executed commands are recorded in [COMMANDS.md](COMMANDS.md). The test genuinely
stops/restores the API for its outage case; it uses no mocked network routes.
It refuses unsupported content, compares the one real result with its frozen
reference at 1e-8, and checks filename/case invariance, fixture isolation,
empty/oversized uploads and no-prediction errors. Backend tests separately cover
corrupt/incompatible inputs, safe deserialization, streamed request bounds and
cancellation. Synthetic fixtures are only error/unit checks.

Bulk logs, JSON, JUnit and screenshots are preserved under `local_outputs/app/`.
The first failed browser run and its networking diagnosis remain alongside the
successful `browser-final/` evidence. Existing `local_outputs/cpu/` is preserved.

## Verification boundary

This is a real cached-feature application demo. Full arbitrary raw SVS → fresh
UNI2 extraction → prediction inside containers remains **unverified**. No
weights, additional slides, training, split changes, new test metrics or optional
profiling ran. The model's tiny/reused test set, inferred preparation,
sparse-normal and source-site limitations remain as documented in checkpoint 16.
This does not establish clinical validity or completion of every MS2 requirement.

Configuration references: [official Node image](https://hub.docker.com/_/node/),
[FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/),
[Starlette multipart requests](https://www.starlette.io/requests/) and
[uv Docker integration](https://docs.astral.sh/uv/guides/integration/docker/).
