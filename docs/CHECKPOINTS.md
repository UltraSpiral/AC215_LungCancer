# Checkpoint history

Updated 2026-10-19T00:02:23.710099+00:00. Persistent home:
`/content/drive/MyDrive/LungCancer_AC215/docs/`.

| Checkpoint | State and executed result | Durable summary |
|---|---|---|
| 00 — initial environment | Repository inspected; proposal preserved; L4 verified with approved execution; Drive/auth setup initially required | [Initial inspection](checkpoints/2026-10-18-00-environment.md) |
| 01 — encoder readiness | Mounted persistence and private cached HF credentials verified; genuine UNI2-h loaded; finite synthetic [2,1536] smoke | [Environment and encoder](checkpoints/2026-10-18-01-encoder-ready.md) |
| 02 — real-data pilot | Nine real slides/nine patients, 1,020,202,701 raw bytes, 4,608 finite features, verified persistence, 23 tests passed | [Pilot completion](checkpoints/2026-10-18-02-pilot.md) |
| 03 — evidence review | Every specimen chain rechecked, three inline class panels prepared, preparation correction documented | [Full evidence](checkpoints/2026-10-18-03-pilot-evidence.md) |
| 04 — durable records | Checkpoint snapshots and copyable commands consolidated; verified persistent Markdown and source archive | [Recordkeeping](checkpoints/2026-10-19-04-records.md) |
| 05 — one-slide profiling prerequisite | No raw SVS remains; profiler implemented; execution awaits a raw input and a decision on reacquiring one pilot file | [Profiling prerequisite](checkpoints/2026-10-19-05-profiling-prerequisite.md) |

## Current verified scientific/engineering state

- Three slides and three independent patients per class; nine distinct patients overall.
- Raw transfer: 1,020,202,701 bytes; no raw expansion during review/documentation.
- All nine are classified as frozen **by inference**; explicit Frozen metadata confirmations: zero.
- Preservation fields: eight Unknown; TCGA-98-A538 OCT; all portion is_ffpe flags false.
- Normals include both projects: two TCGA-LUSC and one TCGA-LUAD.
- UNI2-h revision `d517a8dd47902dd7c308b3c36f63bce47e7b9a43`; each feature array [512,1536], all finite.
- Patient diagnosis alone never makes a linked normal specimen tumor-positive.
- No real-data classifier, held-out metrics, or renamed held-out inference exists yet.
- Source-site confounding, sparse-normal selection, unapplied ICC profiles, and visual quality variation remain review topics.

## Factual correction retained in the record

The early blanket description of pilot preservation fields as all Unknown was
incorrect. Checkpoint 03 verified eight Unknown values and one OCT value. The
corrected raw evidence remains unchanged and all nine frozen assignments remain
inferred. Historical summaries carry this correction explicitly.

## Next work remains pending

The latest request authorizes one-slide profiling using existing downloads. No
raw SVS remains. A decision on reacquiring one 95,344,817-byte pilot file is
pending; no stage timings, profiling peak memory, or A100 benefit is measured yet.

Review the pilot, agree a compatible modeling cohort and expanded cumulative raw
budget, create fixed patient-grouped splits with pilot patients in training,
then train, evaluate, and demonstrate real inference on a renamed held-out slide.
This documentation request authorizes none of those processing stages.

[Copyable commands](COMMANDS.md) · [Artifact paths](ARTIFACTS.md) · [Latest backup](LATEST_BACKUP.md)

## 06 — Runtime recovery checkpoint (2026-10-19)

2026-10-19 UTC. Profiling is explicitly deferred and optional. Do not reacquire a
slide, expand downloads, train or run experiments. This supersedes the earlier
profiling-prerequisite question; it is not an outstanding approval request.

The complete current handoff is STATUS.md and docs/RESUME.md. Existing artifacts
are verified and copied to a new timestamped Drive recovery directory; old backups
are kept. Code is committed on milestone2 and a Git bundle is preserved. The final
verification report, rather than this pre-operation description, records the
actual commit, push, checksums, archive checks and native session-read outcome.
GitHub CLI authentication was absent when recovery began.

A separate late private session snapshot excludes credentials/logs/caches, uses
SQLite online backups and contains only this conversation's records. Readable
export and native records are distinct; interactive resumption remains unverified.
No claims of completed training/evaluation or timing measurements are added.

See [full recovery guide](RESUME.md) and `/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z/VERIFICATION.md`.

Recovery outcome update: source/artifact checks passed; the initial authorized
GitHub push failed for missing credentials and remote milestone2 was absent.
The final Git bundle and full commit SHA are in the timestamped Drive report.

## 07 — Fresh A100 recovery (2026-10-19)

Verified A100-SXM4-80GB, 167.1 GiB RAM and unchanged working PyTorch/CUDA.
All 155 saved checksum entries and 126 restored artifact files pass; all nine
finite embedding arrays align with in-bounds coordinates. Restored Git linkage
and 95 missing tracked frontend files without overwriting existing files.
The user's subsequent push is verified: milestone2 `99c52a33ca4f097f27c369af16622740044295ca`.
Earlier push-failure notes describe the older checkpoint only. OpenSlide, HF
login and gated checkpoint cache are missing; no installs/downloads/reprocessing
or training were performed. Ready for pilot review/offline cohort planning.
See [the dated checkpoint](checkpoints/2026-10-19-07-a100-recovery.md); future acquisition and
training remain unauthorized.

## 08 — A100 readiness recheck (2026-10-20)

All 155 saved checksum entries, 126 restored artifacts and nine finite aligned
embedding arrays pass; specimen links re-audited from saved GDC metadata.
Core dependencies/CUDA work; OpenSlide/HF login/pinned weights are absent.
Ready for pilot review. Remote milestone2 verified; local Git metadata absent
in this fresh archive restore. Recovered newer checkpoint-07 documentation
from verified Drive copies before persisting this report. No downloads, package
changes, encoder loading, profiling or training ran. See [checkpoint 08](checkpoints/2026-10-20-08-readiness.md).

## 09 — Git synchronization (2026-10-20)

On the user's explicit request, restored Git linkage and fetched milestone2.
Local and remote HEAD both match `99c52a33ca4f097f27c369af16622740044295ca` with zero divergence. Restored only
95 absent tracked frontend files; all 52 preexisting source files and 135
artifact hashes stayed unchanged during synchronization. Newer local docs and
helpers remain uncommitted and are backed up. No slide/model/package downloads,
frontend execution, profiling or training ran. Full source/Git recovery copies
are in `/content/drive/MyDrive/LungCancer_AC215/sync_checkpoints/20261020T014239Z`. See [checkpoint 09](checkpoints/2026-10-20-09-git-sync.md).

## 10 — Training plan after frontend addition (2026-10-20)

Static Git/source review confirms the scientific pipeline is unchanged. Keep
frozen UNI2-h, mean pooling, training-only scaling, multinomial L2 logistic
regression and fixed patient-level evaluation. Proposed later UI integration
must replace filename-based fixtures, align the output contract and keep viewer
tiles separate from model preprocessing. No new work is authorized by this plan
review. See [TRAINING_PLAN.md](TRAINING_PLAN.md). No downloads or training ran.

## 11 — One-hour goal (2026-10-20)

Prepared an offline 45-slide/15-per-class draft reusing nine caches. New raw
4,433,083,094 bytes; cumulative 5,453,285,795 within 10 GB. Historical-rate
new-data estimate ~33 minutes plus setup/fitting/evaluation/inference; no actual
A100 speed measurement or completion guarantee. Cohort reduction approval and
HF login are pending. No model or data downloads/training started. See
[ONE_HOUR_PLAN.md](ONE_HOUR_PLAN.md).

## 12 — Full MS2 rubric supplied (2026-10-20)

UNI2 plus a learned logistic head fits the baseline adaptation requirement, but
the submission still lacks containerization/one-command execution, uv locks,
real baseline results and tested UI/backend interaction. Existing Docker
exclusion from the original brief conflicts with the newly supplied rubric's
requirements. Revised infrastructure priorities and host/time limits are saved
in [MS2_GAP_ANALYSIS.md](MS2_GAP_ANALYSIS.md). No experiment, installation or
container execution occurred. The prior one-hour forecast was modeling-only.

## 13 — Setup and 45-slide modeling readiness (2026-10-20)

HF login is now present with 0600 credential permissions; CUDA/Drive work.
OpenSlide and pinned weights are still absent. The metadata-only draft split
check gives 11 train / 2 validation / 2 test patients per class, all nine pilot
patients in training, no patient leakage. No persistent split or training was
created. A 45-slide linear-probe run is a reasonable initial MS2 experiment;
its tiny test set requires explicit limitations. See [checkpoint 13](checkpoints/2026-10-20-13-modeling-readiness.md).

## 14 — Modeling first; training not yet authorized (2026-10-20)

The user proposed modeling before MLOps and explicitly withheld training
approval. Recorded the sequence and gate in AGENTS.md/STATUS.md and checkpoint
14. No training/download/experiment/build started. HF setup remains verified.
Proceed only after unambiguous approval; then do not request that approval again.

## 15 — Approved real modeling run

User authorized the proposed 45-slide run. Setup, immutable patient splits, budgeted acquisition, frozen features, real logistic baseline, held-out evaluation and arbitrary-name inference are authorized. MLOps follows. Results pending execution; see checkpoint 15.

## 16 — Real modeling completed, conservative audit correction

45 slides processed; one multiply linked slide excluded; final cohort 44 patients,
32/6/6 split, no patient moves. Validation macro F1 .667, test 1.000 on six patients
with explicit reused-provisional-test limitations. All caches/Drive hashes,
training-only scaling and renamed real-slide inference verified. Raw 5,453,285,795
bytes. See checkpoint 16; the original model is retained as provisional history.

## 17 — Apple Silicon CPU preparation

Locked CPU Docker recipe/Compose/Make targets and a private 186.5 MB data bundle
prepared. Torch-free x86_64 script sequence passed 29 tests, 44 real caches,
12 frozen reference predictions and real 16-tile preprocessing. Actual M1 Docker
execution is pending and belongs to the user's Mac Codex. Full slide-to-prediction
container verification remains separately pending. See checkpoint 17/CPU guide.

# Checkpoint 18 — user-selected Git identity and publication recovery

User explicitly selected UltraSpiral <UltraSpiral@users.noreply.github.com>.
Applied repository-local author settings. No alternative-author commit was
created. GitHub CLI authentication is missing in this runtime; Git publication
will be verified separately and recorded in persistent docs/GIT_PUBLICATION.md.
Added browser-login instructions and a non-destructive Mac Git-bundle fallback.
No data/model work was repeated. See
[checkpoint 18](checkpoints/2026-10-20-18-git-identity.md).

## 19 — Return to the same chat after GitHub login

Verified the installed resume command, actual session UUID/home and existing
rollout record. Saved exact quit/login/resume steps and a new-session fallback
in docs/RETURN_TO_CHAT.md. Authentication/push remain pending. No ML stages
were rerun. These Markdown updates are pending commit after login and are
included in the verified persistent source/document backup.

## 20 — GitHub publication verified after user login

Verified authenticated account UltraSpiral, configured the supported Git helper,
preserved remote work and committed the return instructions. Push succeeded;
local/live remote both matched c6627377194d21711b6814be771de70da96cb9b1.
This checkpoint receives a final documentation commit; its exact verified SHA
and refreshed recovery bundle are saved in the private Drive GIT_PUBLICATION.md
receipt. Auth-failure notes above are historical. No ML/container stages reran.
Next action: actual M1 Docker verification using the saved guide.

## 21 — Native Apple M1 Docker verification passed (2026-10-20)

Opened the existing clean milestone2 checkout and verified HEAD against live
GitHub at 95fff6baab9e6942992356d70ee56e6c848da2c3. The renamed Downloads archive
matched the exact guide SHA256/size; restored all 187 files without overwriting.
Native linux/arm64 `make cpu-check` exited 0: 29 tests, 44 real caches / 22,483
vectors, 12 frozen prediction references (max difference 5.56e-17), fixed patient
separation/training-only scaling and real 16-tile preprocessing all passed.
Live Docker inspection confirmed offline execution and read-only inputs.
Saved logs, JUnit/JSON, image/layer identity, coordinates and inspected overlays.
No source/lock/model/split fix or further processing rerun was necessary.
The genuine successful-run screenshot was captured and visually verified.
Cloud persistence status is recorded in
[checkpoint 21](checkpoints/2026-10-20-21-native-arm64.md); local verified backups
are indexed by [LATEST_BACKUP.md](LATEST_BACKUP.md). The Colab persistence helper
correctly refused a nonexistent mounted Drive on the Mac; Drive Desktop timed
out and automatic review rejected the initial connected Drive upload. The user
subsequently explicitly approved the package/Markdown backup. The 3,217,295-byte
evidence package was uploaded and its SHA256 matched after downloading it back;
the Markdown mirror is tracked by the final cloud persistence receipt.
Full slide-to-prediction containers/UI integration remain
pending. No weights, slides, real training, split changes or profiling ran.

## 22 — Publish the native M1 verification records (2026-10-20)

The user explicitly authorized the commit and push to milestone2. A fresh
fetch confirmed the unchanged parent 95fff6baab9e6942992356d70ee56e6c848da2c3.
Applied the selected UltraSpiral noreply author/committer identity locally.
The publication includes the CPU checkpoint, current status/matrix/commands
and backup records, with only Markdown staged. Whitespace checks and focused
secret-pattern inspection cover the exact staged files. Push uses the existing
supported Git credentials and no force. Live/local SHA, clean-tree and identity
verification receipts are saved after the push under
artifacts/publication/2026-10-20-22-cpu/. Fresh source/Markdown persistence is
local on this Mac; the immutable checkpoint-21 Drive snapshot is preserved.
No CPU processing or model tests need repeating for these documentation edits.
See [checkpoint 22](checkpoints/2026-10-20-22-cpu-publication.md).

## 23 — M1 evidence confirmed from Colab

Fast-forwarded to the published Mac commit 598bcd7, preserving its records.
Verified the approved evidence archive SHA256, all 72 inventory entries,
JUnit/JSON success, ARM64 identity and runtime isolation; inspected screenshot
and tiles. CPU container verification is complete. Full inference containers
and UI/backend interaction remain pending. No processing reran and the rejected
optional Mac sync receipt was not uploaded. See checkpoint 23.

## 24 — Recommended next step: real application interaction

Source review confirms the frontend defaults to fixtures and the reference
HTTP server does not run the classifier. Recommend a native ARM64 UI/API demo
using the actual saved model and content-verified cached features for the
already-bundled slide, with explicit cache-only scope and unknown-input errors.
Full containerized slide-to-UNI2 inference remains separate. This is planning
only; no implementation, service startup, installation or ML run occurred.
See checkpoint 24; no manual command is needed now.

## 25 — Complete Mac application handoff and recovery coverage

Saved the comprehensive local task/context in docs/MAC_CODEX_HANDOFF.md and
prepared checkpoint 24 for publication. App implementation/execution remains
pending the successor session. Extended source backups to include frontend
source/lock/assets and future backend/app Compose files, excluding generated
inputs, dependencies and credentials. Verify the actual archive and staged
diff, persist to mounted Drive, publish normally and verify matching SHAs.
No scientific artifacts or processing stage changed. See checkpoint 25.


## 26 — Native M1 cached-feature app implemented and verified (2026-10-20)

Safely fast-forwarded through the Colab handoff to b9ae02a, preserving all local
private inputs and CPU evidence. Implemented a real content-matched saved-model
backend, HTTP frontend, 512-coordinate preview and native ARM64 Compose app.
The tested build/start command is make app-up; browser URL 127.0.0.1:8080.
14 backend tests and all 10 actual browser/API scenarios passed, including
renamed/misleading metadata invariance, unsupported/modified input, upload bounds,
fixture isolation and an actual API outage. Frontend checks and stop/resume passed.
The first browser connection failed because the internal-only network did not
publish the host port; retained failure evidence, fixed web ingress and added a
host readiness probe. Real screenshots/responses and runtime identity evidence
are saved; selected lightweight proof is committed. All private manifest entries
and core frozen fingerprints/locks remain unchanged. Source/local evidence backups
and publication receipts are tracked in LATEST_BACKUP.md and checkpoint 26.
No new private Drive upload is inferred from the earlier CPU archive approval.
Full fresh-UNI2 container verification remains pending. No new raw/weight download,
training, split changes, test-metric rerun or profiling occurred. See
[checkpoint 26](checkpoints/2026-10-20-26-cached-feature-app.md) and
[LOCAL_APP.md](LOCAL_APP.md).

## 27 — Current MS2 requirement/evidence audit (2026-10-20)

Compared the user-supplied rubric to committed source and saved execution proof.
Confirmed the baseline and cached-feature app, two Python uv environments,
native ARM64 checks and version identities. The main technical gap is a complete
scientific pipeline executed inside containers. CPU screenshots/logs/reports
exist privately but selected evidence still needs GitHub publication; original
mock-up/refinement records, presentation and final Canvas SHA need confirmation.
RAG does not apply to this vision project. Annotated the prior gap analysis
without removing history. No processing, tests, new data/weights or modeling
ran. Persistence/publication receipts are local; a new Drive mirror is not
claimed. See [checkpoint 27](checkpoints/2026-10-20-27-ms2-readiness.md) and
[the complete current checklist](MS2_READINESS.md).

## 28 — Feature caching, model serving and scope correction (2026-10-20)

The user asked whether missing fresh-encoder container verification meant
training at runtime. Clarified that model parameters and per-slide feature
vectors are different artifacts, and that the verified app computes new
predictions from real cached embeddings with the saved model. Caching is a
valid design. Corrected checkpoint 27's overly strong rubric interpretation:
fresh UNI2 execution on every run is not explicitly required. The broader
uncached-slide container path remains unverified; chosen pipeline boundaries
and one-command input/output evidence should be documented accurately.
No processing, scientific artifact change or authorization expansion occurred.
Records/source are backed up locally; no new Drive mirror is claimed. See
[checkpoint 28](checkpoints/2026-10-20-28-cache-scope-clarification.md) and the
correction in [MS2_READINESS.md](MS2_READINESS.md).
