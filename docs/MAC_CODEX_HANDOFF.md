# Local Mac Codex handoff: real cached-feature application demo

Execution update — checkpoint 26: this bounded task has now been implemented
and verified on the M1, including actual browser/API interaction. Read
[LOCAL_APP.md](LOCAL_APP.md) and
[checkpoint 26](checkpoints/2026-10-20-26-cached-feature-app.md) for current
commands, evidence and remaining full-pipeline limits. The original canonical
handoff below is preserved as the implementation specification/history.

This is the self-contained context and implementation prompt for Codex on the
user's M1 Mac. The Colab agent is preparing/persisting this handoff, not building
or running the application. When the user gives you this handoff as a task,
implement and verify the bounded local application below.

## 1. Working agreement and first actions

Work in the existing repository, normally:
/Users/shlokdholakia/Documents/Harvard/Semesters/SEM3/AC215/LungCancer

Remote: https://github.com/UltraSpiral/LungCancer.git
Branch: milestone2. The handoff was prepared from d5735aacb28f0844a7d09322142d06a420973b99;
the final handoff commit is newer and is reported to the user. Fetch the current
branch, inspect status/diffs and preserve local work. Fast-forward only when safe.
Do not reset, force-push, discard edits, or replace existing private input/output
directories. Preserve the successful CPU evidence and screenshots.

Read AGENTS.md, this file, STATUS.md, docs/VERIFICATION_MATRIX.md,
docs/checkpoints/2026-10-20-16-modeling-results.md,
docs/checkpoints/2026-10-20-21-native-arm64.md,
docs/checkpoints/2026-10-20-23-m1-evidence-confirmed.md,
docs/checkpoints/2026-10-20-24-next-app-step.md, frontend/README.md,
and docs/CPU_CONTAINER_VERIFICATION.md.
Earlier pending-training/authentication/Mac statements are dated history;
the latest verified checkpoints supersede them.

Execute, inspect results, fix routine errors and rerun necessary checks yourself.
The user does not want to relay terminal errors or execute every processing step.
You can make normal implementation choices and install public build/test
dependencies. Ask only for missing authentication/private inputs, a material
scope change, unresolved scientific ambiguity or resource expansion.
Honor tool approval and filesystem/network boundaries; do not bypass controls.
No subagents are requested.

Use the confirmed Git identity for project commits:
UltraSpiral <UltraSpiral@users.noreply.github.com>
Keep configuration local to this repository. Use supported GitHub authentication;
never request tokens in chat or include credentials in commands/remotes/logs.

## 2. Your concrete task and its limits

Build and verify a minimal working web app entirely on this M1:

browser -> real HTTP backend -> verified cached UNI2 vectors
-> mean pooling -> saved scaler/logistic classifier -> real result in browser.

Use the real slide already present in the CPU bundle. A file-content checksum
selects its verified existing cache. The checksum is an identity lookup, not a
classifier feature. The output must be newly computed by the saved classifier,
not copied from a saved prediction JSON, a diagnosis, a fixture or the filename.

Call the user-facing mode a preprocessed-slide demo, with a clear explanation
that UNI2 embeddings were extracted previously. No fresh UNI2 extraction occurs
in this application stage. Unknown/unprocessed slide bytes must return a clear
error and no predicted class. Identical bytes with a different .svs filename
must yield the same result. One genuine supported slide is enough for this app
skeleton; there is no requirement to add three raw slides or a new cohort.

Containerize frontend and backend for native linux/arm64 and provide one actual
build/start command, documented after it exists. Run and debug the real browser
flow on the M1 and preserve proof. Do not stop at code generation or direct
Python function calls. Existing model artifacts/splits are immutable.

Do not download new slides or gated weights; install/load Torch or UNI2;
retrain/refit the classifier or scaler; change splits/preprocessing/encoder;
recompute test metrics; add calibration, attention MIL, segmentation, tumor
area, diagnostic prose, Kubernetes, paid infrastructure or public deployment.
No HF login, Colab GPU or Colab runtime is required for this bounded app stage.
Ordinary public npm/Python/container build dependencies are allowed.

Full raw SVS -> newly extracted UNI2 embeddings -> prediction in containers
remains a separate unverified task. A cached-feature web demo does not complete
that full-pipeline requirement. Keep this distinction in documentation and the
final report. UI fixtures may remain isolated development fixtures, but cannot
serve the real demo path or silently replace a failed backend.

## 3. Scientific/model state: already executed, not work to repeat

AC215 lung histopathology engineering MVP. Three classes, in explicit task order:
non_tumor, adenocarcinoma, squamous.

Pipeline: physical-scale tissue tiling -> frozen UNI2-h embeddings ->
slide-level mean pooling -> StandardScaler fitted on training slides only ->
L2 multinomial logistic regression. sklearn C=0.01, solver lbfgs.
This is a frozen-encoder linear-probe baseline. UNI2 was not fine-tuned.

45 real slides were processed. A later strict UUID-link audit excluded one
squamous training slide with ambiguous portion links, leaving 44 independent
patients: 15 normal / 15 adenocarcinoma / 14 squamous.
Fixed split: 32 train (11/11/10), 6 validation (2/class), 6 test (2/class).
All nine pilot patients stay in training. Other patient assignments were kept.
Never regenerate splits, retune C, or change the class mapping for the web demo.

Validation macro F1 and balanced accuracy: 0.6666666667.
Test macro F1 and balanced accuracy: 1.0 on only six patients.
Majority-class baseline macro F1: 0.1666666667; balanced accuracy 0.3333333333.
The provisional 45-slide model's test results were already seen before the
metadata-only correction. No test-based tuning occurred, but this is not a
pristine independent final-test estimate. Do not advertise perfect accuracy,
clinical validation, broad disease detection or statistical adequacy.

All 22,483 eligible tile embeddings are finite, dimension 1536, with matching
level-0 coordinates. Most slides have 512 tiles; one eligible slide has 467.
Normal examples include TCGA-LUAD (6) and TCGA-LUSC (9).
Preparation is frozen inferred from TS/BS categories, with is_ffpe=false as
supporting evidence; zero slides are explicitly confirmed Frozen by that field.
Raw preservation_method is Unknown in 40 / OCT in 4. Inferred preparation must
not be relabeled confirmed. Sparse normal lung, site/preparation bias and the
small inspected cohort remain limitations.

GDC labels resolve the actual linked case/sample/portion/slide UUID chain:
Solid Tissue Normal -> non_tumor; Primary Tumor in LUAD -> adenocarcinoma;
Primary Tumor in LUSC -> squamous. A cancer patient's normal slide is normal.
Conflicting/ambiguous specimen chains were excluded. Display-barcode portion
numbers cannot resolve distinct ambiguous portion UUIDs.
Latest discovery audit: 3,220 files, 3,172 included / 48 excluded.
Cumulative raw download: exactly 5,453,285,795 bytes, within a 10,000,000,000-byte
budget. No expansion is authorized.

Model identifier:
42af9fb3f51e1539d994af4f20e2980e4118eac6a8cd665aeb372c1440b2fed5
Classifier joblib SHA256:
c4bf98706e52febb1fe80ac5baeec75748511c6e1d835b272d19c3570647a71d
Split identifier:
964f3b6c073863efbe38b560cfe93b2783cff5d822c64bde12f71241a7a4f2c4
Encoder identifier:
debc5e8769258a2e970772801d440debc2500868f5a6cf93b7b5c0c8c1e41324
UNI2 repository: MahmoodLab/UNI2-h
UNI2 revision: d517a8dd47902dd7c308b3c36f63bce47e7b9a43
UNI2 checkpoint SHA256:
6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e
Do not fetch or bundle those weights for this app.

Frozen model preprocessing: target 0.5 microns/pixel; 224x224 output;
nonoverlapping candidate grid; max 512 tiles; tissue coverage threshold 0.5;
thumbnail max 4096; seed 215; spatially distributed deterministic sampling;
official UNI2 evaluation transforms; float32 encoder inference.
The Mac smoke instead used max 16 tiles / thumbnail 1024. Its outputs are
preprocessing-test evidence, not the model's 512-tile features or tile count.
Keep core preprocess.py/features.py/safety.py implementation fingerprints
compatible. Avoid changing them for web plumbing.

## 4. Private inputs already on the Mac

The previous M1 run restored Git-ignored local_data/cpu_bundle/. Inspect it
before asking for another download or restoring anything. Expected structure:

local_data/cpu_bundle/manifest.json
local_data/cpu_bundle/sample/sample.svs
local_data/cpu_bundle/run/model/model.json
local_data/cpu_bundle/run/model/classifier.joblib
local_data/cpu_bundle/run/cohort.json
local_data/cpu_bundle/run/splits.json
local_data/cpu_bundle/run/evaluation_validation/predictions.json
local_data/cpu_bundle/run/evaluation_test/predictions.json
local_data/cpu_bundle/slides/<file_uuid>/embeddings.npz
local_data/cpu_bundle/slides/<file_uuid>/embeddings.json
local_data/cpu_bundle/slides/<file_uuid>/coordinates.npz
local_data/cpu_bundle/slides/<file_uuid>/preprocessing.json

The bundle has 186 checksum-listed entries plus manifest.json (187 files).
Its data snapshot identifier:
f9491fe4d35f30267df95d26c61d6bb325908694e6df7d746a6acb9826eddb24

The user renamed the downloaded archive on the Mac to:
/Users/shlokdholakia/Downloads/CPU Verification Audit Oct 20 2026.tar.gz
Original Drive name: cpu-verification-20261020T0220Z-audit2.tar.gz
Archive size: 186,505,459 bytes.
Archive SHA256:
c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988

The supplied real SVS is 71,138,367 bytes.
GDC file UUID: a2e48dce-1874-468d-a302-fd30b3107f4a
Source MD5: a86f358f5325b6229035d19ed23440aa
Source SHA256:
544fc4ab2cf62ebc99e01e734907ec4194c71baba8b61bb4cbca92ae739c9a9d
Its real model cache has [512,1536] vectors and [512,2] level-0 coordinates.
Actual physical output scale is about 0.49926116071428567 MPP on both axes.
Its cached warning is embedded_icc_profile_present_not_applied.
Read counts and warnings from verified cache metadata; do not hardcode results.
Do not use the true class as an API answer; compute the answer.

Verify the bundle inventory, saved model hash and matching cache identities
before deserializing the trusted joblib. Do not accept uploaded joblib or pickle
files. SHA256 plus length can identify the supplied supported raw slide;
retain GDC MD5 as provenance. Unknown bytes fail without a prediction.
No input bundles, raw slides, embeddings or classifier binaries belong in Git
or Docker image layers. Mount inputs read-only at runtime.

If inputs are missing, ask for their local location. Do not download another
GDC slide or silently replace real features. The non-overwriting restore helper
is scripts/unpack_cpu_bundle.py; its required checksum is above. It refuses an
existing destination, and that behavior should remain intact.

## 5. Actual M1 Docker proof already passed

make cpu-check exited 0 natively on Apple M1. Host arm64; Linux aarch64.
29 unit tests passed, no failures/errors/skips, three fixture/deprecation warnings.
44 real caches / 22,483 finite vectors, 12 saved probability references,
patient separation and training-only scaler statistics verified.
Largest probability difference was 5.551115123125783e-17 (tolerance 1e-8).
The genuine real-SVS preprocessing smoke selected 16 valid tiles; overlays
and contact sheet were inspected. This did not run UNI2 or a new full-slide fit.

Docker image: lungcancer-cpu:milestone2, linux/arm64
Image ID:
sha256:c78cfbdd188e4c02a5330f110ccdcc77c8a6c7b9c815e893fd6ea3ca0f40a0da
Python 3.13.15; native OpenSlide 4.0.1; openslide-python 1.4.6;
openslide-bin 4.0.1.2; numpy 2.1.3; scipy 1.16.3; sklearn 1.6.1;
Pillow 11.3.0; joblib 1.6.0; pytest 8.4.2. Torch is deliberately absent.
Runtime was offline, root read-only, input mount read-only, output writable.

Existing Docker/uv assets:
containers/cpu/Dockerfile, containers/cpu/pyproject.toml,
containers/cpu/uv.lock, containers/cpu/base-image.json,
compose.cpu.yml, Makefile, .dockerignore.
The Python base's multi-platform index digest is pinned in the Dockerfile.
Use these proven dependencies for model loading and CPU calculations rather
than pulling the root GPU training environment into the app.

Useful reusable code:
scripts/verify_cpu_bundle.py: verify_inventory and the real cache/scaler checks;
lungcancer/modeling_run.py: verify_cache accepts an encoder identity string;
lungcancer/features.py: load_features validates shape/finite/alignment data;
lungcancer/modeling.py: named_probabilities aligns classifier classes explicitly;
lungcancer/common.py: CLASSES, checksum, atomic JSON and persistence helpers.
Compute mean with numpy float64 exactly as the saved pipeline does.
Do not call train, fit_classifier, evaluate or full inference.predict for this
cached app. Full predict would construct UNI2; this task must not.

Preserve local_outputs/cpu/, artifacts/checkpoints/ and the screenshot:
local_outputs/cpu/ms2-docker-success-2026-10-20.png
Other evidence includes verification_all.json, cached_embeddings.json,
real_preprocessing.json, unit-tests.xml, console.log, image_identity.txt,
image_inspect.json, runtime_container.json and preprocessing/ visual audits.
Do not repeat the unchanged CPU suite unless a new relevant change justifies it.

## 6. Existing frontend: use it, inspect before changing

frontend/ is a Vite + React + TypeScript app with Zustand and OpenSeadragon.
It was contributed earlier and has not yet demonstrated real-model HTTP
interaction. Preserve the design and use the existing upload/job/result states.

Key files:
frontend/README.md
frontend/package.json and package-lock.json
frontend/src/api/contracts/inference.ts
frontend/src/api/adapters/httpAdapter.ts
frontend/src/api/adapters/mockAdapter.ts
frontend/src/api/adapters/InferenceAdapter.ts
frontend/src/api/index.ts and client.ts
frontend/src/api/runAnalysis.ts
frontend/src/features/analysis/AnalysisPanel.tsx and PredictionBlock.tsx
frontend/src/features/viewer/useViewerSource.ts and slideMetadata.ts
frontend/src/features/upload/accept.ts
frontend/src/state/types.ts
frontend/src/mocks/sampleSlides.ts and predictions.ts
frontend/tools/stub-model-server/server.py
frontend/tools/convert-slides/convert.py

Default VITE_INFERENCE_MODE is mock; the real demo must explicitly use http.
The stdlib reference stub chooses fake illustrative results from TCGA filename
barcodes. It must not back the real demo or be relabeled a real model server.
Existing sample definitions are illustrative and are not our bundled raw slide.
Avoid offering unsupported fixture slides as real-model examples.
Filename-based matching also exists for viewer/sample selection; keep it
strictly separate from content-based supported-input resolution and prediction.

The existing UI displays predicted class, model ID, tile count and warnings.
It currently hides probabilities; showing them is optional. If displayed, keep
named probabilities and an explicit uncalibrated label. No tumor percentages,
diagnostic narrative, confidence calibration or heatmap claims.
Use plain product wording explaining the preprocessed-slide limitation.
Do not put infrastructure jargon into the UI unless needed to explain that limit.

The viewer currently previews only sample slides with generated Deep Zoom data.
Uploaded SVS files show a preview-unavailable message. It is acceptable to keep
an honest minimal preview state or add a real thumbnail/coordinate overlay
from the supplied slide. Do not display unrelated fixture tissue as that slide.
Do not blindly generate thousands of full-resolution viewer tile files; full
Deep Zoom viewing is not required to prove this basic interaction.
Any analyzed-tile overlay must use the actual cached model coordinates (512
for this slide), not the separate 16-tile smoke, and is not a tumor heatmap.

Existing package-lock versions include Vite 8.3.4 and React plugin 6.1.2.
Their recorded Node engine is ^20.19.0 or >=22.12.0. Inspect actual installed
Node and current official image documentation, select a compatible ARM64 image,
pin it and preserve package-lock. Use npm ci rather than broad dependency updates.
Existing frontend verification: npm run check (typecheck, oxlint, Vite build).
Browser automation tools already appear in the package; use actual executed
browser evidence rather than a fabricated screenshot or a mocked network route.

## 7. HTTP contract and serving pitfalls

Existing routes expected by the frontend:
POST /jobs: multipart field slide (.svs), optional case_id;
response 202 with job_id and a valid status.
GET /jobs/{id}: job_id, status queued|running|done|failed,
optional progress/stage and result/error.
DELETE /jobs/{id}: optional cancellation; implement coherently or disclose limits.

The successful result contract requires:
status: success
predicted_class: one of non_tumor, adenocarcinoma, squamous
class_probabilities: named finite probabilities in [0,1], sum approximately 1
probabilities_calibrated: false
tiles_analyzed: actual positive cached embedding count
quality_warnings: actual model-cache warning strings
model_identifier: actual trusted saved model ID
analyzed_tiles_overlay: optional served browser URL

Can retain encoder/configuration identifiers as additional provenance.
The Colab full prediction uses analyzed_tile_locations_overlay instead of the
frontend's analyzed_tiles_overlay; explicitly map the name and serve a URL
if implementing an overlay. Never expose a host-local absolute file path as
though a browser could open it.

Failure: explicit error/reason, no predicted class/probability payload.
Do not report errors as successful predictions. Keep HTTP/job terminal states
compatible with runAnalysis.ts. Use true job state/progress; do not replay the
stub's fake tissue-detection/UNI2 stages or 16-second simulated delay.
The actual work is identity/cache validation and classification of cached vectors.
Never feed case_id, filename, project, sample code, diagnosis or split labels
to predict_proba. Request labels/metadata must not influence output.

Prefer streamed/bounded uploads, server-generated temporary/job names,
sanitized logging and safe URL/path handling. This is a local demo, not an
authentication/deployment project. Bind published ports to loopback. Choose
same-origin proxying or correct narrowly configured CORS.
The browser cannot resolve a Compose service hostname such as api. Conversely,
localhost inside one container is not the other container. Vite variables are
build-time inputs for a built frontend; changing runtime environment alone
does not rebuild them. Handle service readiness and browser URL routing.

Use a separate app Compose file, for example compose.app.yml, rather than
weakening compose.cpu.yml's existing offline verification behavior.
The app services need their own intentional internal communication network.
Use CPU-only Python dependencies with a uv pyproject/lock for the backend.
Reuse the existing CPU environment where practical; a small normal HTTP
framework/dependency is an implementation choice, not a reason to install Torch.
Keep upload/job/output directories distinct from immutable bundle data.

.dockerignore currently excludes frontend entirely: adjust build contexts or
rules deliberately for the new image, still excluding node_modules, local
bundles, raw SVS, model/embedding binaries, credentials, caches and build output.
Mount real inputs at runtime, read-only. Do not bake them into image layers.
The source backup allowlist now covers frontend, backend, containers and
compose.app.yml, with dependencies/derived inputs/outputs excluded. Check it
if choosing different source paths.

## 8. Verification and definition of done

Work until the implemented bounded app is concrete and reviewable. At minimum:

- Startup/build command actually succeeds on native ARM64. Record image IDs,
  architecture, input/model/config IDs and exact executed commands.
- Frontend type/lint/build checks pass. Existing relevant tests remain intact.
- Backend returns a real saved-model calculation on the verified real cache.
  Compare named probabilities with the frozen reference at tolerance 1e-8,
  without fitting anything or recomputing evaluation metrics.
- A real browser selects/uploads the bundled SVS, submits through HTTP,
  polls a real job and shows the real result. Do not intercept the backend
  with fixture responses. Save screenshot plus request/response or browser trace.
- A renamed copy of identical SVS bytes works with the same probabilities;
  misleading filename/case metadata does not change the output.
- An unknown/modified input fails clearly with no fabricated class.
- A corrupt or incompatible model/cache fails safely; tests may use synthetic
  fixtures for failure/unit checks only. No synthetic data is demo/model proof.
- Empty/oversized uploads and unavailable backend have useful failures.
- The UI discloses preprocessed-slide support; 512 model tiles are not confused
  with the 16-tile smoke. No calibrated-probability or tumor-heatmap claims.
- Preserve and inspect actual logs/screenshots. Make failures visible;
  pipefail matters when tee is used. Do not claim unexecuted stages work.
- Keep full raw-to-UNI2 container verification pending in the matrix.

No large hyperparameter sweep, new cohort, new train/test split or additional
test-set score is part of these acceptance checks. If a genuine blocker needs
user authentication/input, finish independent work, explain precisely what is
missing and ask only for that. Do not silently substitute a fake result.

## 9. Persistent records, approvals and Git finish

Keep dated summaries in docs/checkpoints/, append docs/CHECKPOINTS.md, and update
docs/INDEX.md, docs/COMMANDS.md, STATUS.md, docs/RESUME.md and the verification
matrix. Preserve historical notes and explicitly mark factual corrections.
Record implemented / actually executed / verified / pending separately.
Save the app startup/test/stop/resume commands and their exact working directory.

On this Mac, scripts/persist_records.py's genuine Colab Drive mount guard can
refuse copying. Do not fabricate /content/drive, alter security controls or
restore credentials to make it pass. Use verified local backups and an actual
available Drive Desktop path or connected Drive service within authorization.
Report any persistence gap clearly.

The approved Mac CPU package was read back from Drive with SHA256:
70493e8e5086ad83fc339bc649d13d52f2411b39dbe6e365a4202ffff5c4effa
Size 3,217,295 bytes. Its immutable contents include the earlier pre-cloud
notes; later checkpoint-21/22 addenda describe completed approved persistence.
All 35 project Markdown records plus three root records were readback-verified
on the Mac. Colab subsequently verified the archive and its 72-entry inventory.

An optional later sync-receipt upload was rejected by automatic approval as
outside the specifically approved payload. That receipt remains local. Do not
upload it through another route or broaden approval by implication. New app
evidence must respect the actual payload/destination authorization; ask when
an approval is required. Never dump auth stores or environment variables.
No chat transcripts, Codex state, tokens or credentials belong in Git.

Use ignored local_outputs/app/ for bulk app logs/reports and preserve
local_outputs/cpu/. Keep raw inputs, classifier/NPZ files, node_modules, build
caches, large generated outputs and private receipts out of commits. Commit
source, uv/npm locks, container recipes, tests, sanitized docs and intentionally
selected lightweight submission evidence only after inspecting the exact diff.

At completion, fetch/preserve remote work, review staged content and secrets,
commit using UltraSpiral identity and push normally to origin/milestone2.
Verify the live branch's full SHA matches local HEAD. Do not force-push.
Make a readable, checksum-verified source backup. Keep existing backups.

Final report: what works, exact local start command/URL, actual browser/API and
container checks, evidence/backup paths, full published SHA, and remaining
full-pipeline verification limits. Do not claim the entire MS2 rubric is
complete just because this app demo passes.

## 10. Colab/Drive context for recovery, not a Mac mount to create

Colab workspace: /content/LungCancer
Persistent project: /content/drive/MyDrive/LungCancer_AC215
Current model: artifacts/modeling/20261020T0220Z-audit2/
Provisional model history: artifacts/modeling/20261020T0220Z/
Shared full embeddings/visuals: artifacts/slides/<file_uuid>/
Raw GDC query/metadata: artifacts/discovery/
Strict re-audit: artifacts/discovery_v2/
Raw download ledger: artifacts/download_ledger.json
Portable bundle: portable/cpu-verification-20261020T0220Z-audit2.tar.gz
CPU Mac evidence package:
artifacts/cpu_verification/2026-10-20-native-arm64/cpu-evidence-2026-10-20-21-native-arm64.tar.gz
Current records: docs/; current source archive pointer: docs/LATEST_BACKUP.md.
Private publication receipt: docs/GIT_PUBLICATION.md (not a source of new app code).

No raw-slide redownload is needed for this app. The one retained real SVS is
already in the private portable bundle. The original Codex conversation is not
required; this handoff and repository checkpoints are the recovery context.
Do not copy private session state or authentication between machines.

Official documentation to consult as needed during implementation:
https://docs.docker.com/compose/gettingstarted/
https://docs.astral.sh/uv/guides/integration/docker/
https://openslide.org/api/python/
https://huggingface.co/MahmoodLab/UNI2-h
Use current primary documentation for actual framework/build choices.
