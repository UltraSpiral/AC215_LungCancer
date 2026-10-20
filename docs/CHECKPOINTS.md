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

