# Checkpoint 26 — Native M1 cached-feature application verified

Date: 2026-10-20, America/New_York.

Implemented and executed the bounded application from MAC_CODEX_HANDOFF.md.
The actual browser uploads the existing SVS to the native ARM64 Compose app,
polls a real HTTP job and displays a newly computed saved-classifier result.
The app is running at **http://127.0.0.1:8080/**. From the repository root,
**`make app-up`** is the tested single build/start command.

## Preserved source and scientific state

The checkout was clean at 598bcd79662a72af832db698b9761658bd943736. Fetched and
fast-forwarded through both legitimate Colab commits to
`b9ae02aa7c1315cb5aff4065d560e644cb96f089`. No reset, replacement, force-push or
private-directory overwrite occurred. Read the canonical handoff and required
checkpoints before implementation. Private inputs already existed; no restore
or additional raw-slide/weight acquisition was necessary.

All 186 checksum-listed entries were rechecked after execution and remain
unchanged. The 187-file bundle and previous CPU evidence are preserved.
`features.py`, `preprocess.py`, `safety.py`, offline CPU Compose/lock and frontend
package lock are byte-identical to the handoff. The unchanged CPU suite was not
rerun. The 44-patient cohort, 32/6/6 split, frozen encoder/preprocessing,
training-only scaler and C=0.01 are unchanged. Existing tiny/reused-test,
specimen/preparation, sparse-normal and site limitations remain.

Model: `42af9fb3f51e1539d994af4f20e2980e4118eac6a8cd665aeb372c1440b2fed5`.
Classifier SHA256: `c4bf98706e52febb1fe80ac5baeec75748511c6e1d835b272d19c3570647a71d`.
Input snapshot: `f9491fe4d35f30267df95d26c61d6bb325908694e6df7d746a6acb9826eddb24`.
Encoder: `debc5e8769258a2e970772801d440debc2500868f5a6cf93b7b5c0c8c1e41324`.

## Implemented

The backend verifies inventory, model, split and matching cache before trusted
joblib deserialization. SHA256/length/MD5 identify the one supplied raw slide;
only float64-pooled real vectors enter the saved scaler/classifier. Filename,
case metadata, diagnosis and reference predictions are not answer inputs.
There is no fitting or encoder construction.

The API has bounded/spooled uploads, generated job IDs, genuine job states,
cancellation, explicit no-prediction failures and a served overlay. Temporary
uploads and persisted job outputs are separate. The React production build
explicitly uses same-origin HTTP, suppresses fixture sample/filename matching
and the fixture route, and labels the preprocessed-slide limitation. The stub
is not a runtime service. The actual thumbnail/512 cached coordinate overlay
shows analyzed locations; the older 16-tile smoke is not used.

Separate app Compose and digest-pinned ARM64 images preserve the offline CPU
workflow. Model/cache inputs and roots are read-only. The API network is internal;
the web service also joins ingress for loopback-only port forwarding. uv/npm
locks are used; no input, classifier or embedding binary is baked into images.
Start/resume include an actual host-route readiness check.

## Executed and verified

| Check | Actual outcome |
|---|---|
| Frontend | TypeScript, oxlint and Vite build passed, including Node 24 ARM64 production HTTP build |
| Backend ARM64 tests | **14 passed**, zero failures/errors/skips; one Starlette/httpx test-client deprecation warning |
| Actual browser/API | **10 scenarios passed**, no page errors or network mocking |
| Real supplied slide | Newly computed `non_tumor`, **512** tiles, actual ICC warning and model ID shown in browser |
| Frozen reference | Maximum probability difference **6.938893903907228e-18**, tolerance 1e-8; no metric recomputation |
| Renamed bytes | Exact probability equality despite misleading TCGA/tumor filename |
| Misleading case metadata | Real HTTP result has identical probabilities |
| Modified/unknown bytes | Explicit failed jobs, no result/class payload; browser error inspected |
| Empty/oversized upload | Useful no-prediction errors; declared and streamed bounds tested |
| API unavailable | Actually stopped API; browser showed unavailable error, no mock fallback; API restored |
| Fixture isolation | Fixture query/route cannot preselect fake results or unrelated tissue in HTTP mode |
| Stop/resume | Both Make commands executed; host/API ready afterwards; disk job evidence preserved |
| Runtime/data | aarch64, Torch absent, no private input binaries in app source; all manifest entries unchanged |

Real browser POST/GET responses and screenshots are saved. Selected genuine,
unmodified lightweight outputs are committed for review:
[result](../evidence/2026-10-20-app-result.png),
[unknown input](../evidence/2026-10-20-app-unknown.png), and
[execution summary](../evidence/2026-10-20-app-verification.json).
The real overlay and successful/error screenshots were visually inspected.

## Running image identities

- API `lungcancer-app-api:milestone2`, `linux/arm64`:
  `sha256:d4371e618895c27ca080419b2568b99d2960a85f345844af221e9d3a172ec738`.
- Web `lungcancer-app-web:milestone2`, `linux/arm64`:
  `sha256:168848a062c54823adb83a0a93fc3c11b3d33ffdc20ab97681e9ed5a42d6efbd`.

Live container/image identities match. API has no published host port; web is
bound only to 127.0.0.1:8080. Python 3.13.15, numpy 2.1.3, sklearn 1.6.1,
OpenSlide Python 1.4.6, FastAPI 0.150.0, Starlette 1.9.0, uvicorn 0.54.0.
Browser: native mac-arm64 Chromium 156 / Playwright 1.64.1.

## Failures retained and fixed

The first npm install finished with zero audit findings, but an incorrectly
located `tee` directory made the pipeline exit 1. Removed only the newly created
empty directories, corrected logging and retained the installed locked packages
and failure note. No failing exit was treated as successful verification.

The first browser run failed with ECONNREFUSED despite healthy containers:
Docker had no actual published mapping on the internal-only network. Preserved
the failed report/screenshot and port inspection. Adding web-only ingress and a
host readiness probe fixed it; the subsequent browser run passed all 10 cases.

Ignored `local_outputs/app/` contains build/start/check logs, JUnit in
`jobs/backend-tests.xml`, job JSON/real overlay, initial failed `browser/`,
successful `browser-final/`, `runtime-verification.json`,
`preserved_identities.json`, `network-debug-before.json`, stop/resume logs and
`compose.log`. Browser cache/raw test copies stay private and out of backups.
Existing `local_outputs/cpu/` is untouched.

## Persistence, publication and limits

[LOCAL_APP.md](../LOCAL_APP.md), [COMMANDS.md](../COMMANDS.md) and
[RESUME.md](../RESUME.md) contain exact start/test/stop/resume commands.
Backups cover frontend/backend, locks, containers and selected lightweight
evidence, excluding private inputs/dependencies/authentication.
[LATEST_BACKUP.md](../LATEST_BACKUP.md) points to the fresh verified source
archive. Source/Git-bundle fresh-clone and post-push full-SHA receipts are saved
under `artifacts/app_checkpoints/2026-10-20-26/`; this committed checkpoint does
not embed its own commit hash.

The Colab persistence helper is executed with its genuine mount guard unchanged.
New private app/source/evidence backups are local; sanitized source and selected
evidence are published to GitHub. No new private app archive or previously
rejected sync receipt is uploaded to Drive by implication. Earlier approved
Drive snapshots are preserved; refreshed private app Drive persistence remains
an explicit gap, not a fabricated mount or synchronization claim.

**Full raw slide → fresh UNI2 features → prediction in containers remains
pending.** This local app supports one preprocessed raw slide. No weights,
additional slides, training, split/encoder/preprocessing changes, calibration,
new test metrics, profiling, paid infrastructure or public deployment occurred.
Do not claim clinical validity or completion of every MS2 requirement.
