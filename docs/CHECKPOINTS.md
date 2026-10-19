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
