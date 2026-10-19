# LungCancer project records

Persistent home: `/content/drive/MyDrive/LungCancer_AC215/docs/`.
Local working copy: `/content/LungCancer/docs/`.

The checkpoint summaries, commands, and factual corrections are stored as Markdown.
The source data, images, and machine-readable evidence are retained separately.

- [Recovery guide, setup cells, session resume and fallback prompt](RESUME.md)
- [Checkpoint history and current execution boundary](CHECKPOINTS.md)
- [All copyable notebook and terminal commands](COMMANDS.md)
- [Exact artifact locations](ARTIFACTS.md)
- [Latest verified source-code backup](LATEST_BACKUP.md)

## Checkpoint snapshots

- [00 — Initial environment inspection and authentication gate](checkpoints/2026-10-18-00-environment.md)
- [01 — Authenticated environment and UNI2-h smoke test](checkpoints/2026-10-18-01-encoder-ready.md)
- [02 — Completed real-slide pilot](checkpoints/2026-10-18-02-pilot.md)
- [03 — Detailed specimen, preparation, and tile evidence](checkpoints/2026-10-18-03-pilot-evidence.md)
- [04 — Persistent records and copyable commands](checkpoints/2026-10-19-04-records.md)
- [05 — One-slide profiling: raw input prerequisite](checkpoints/2026-10-19-05-profiling-prerequisite.md)

- [06 — Complete runtime recovery checkpoint](checkpoints/2026-10-19-06-recovery.md)

## Supporting evidence

- [Visual pilot report with image links](../artifacts/pilot_review/README.md)
- [Full specimen linkage report](../artifacts/pilot_review/details.md)
- Machine-readable fields: `../artifacts/pilot_review/details.json`.
- Copy-verification receipts: `../artifacts/documentation_persistence.json`.

## Current state

Nine real slides from nine patients completed feature extraction; no real-data
classifier, held-out evaluation, or held-out inference has run. Downloads and
training remain paused for the user's pilot review. The documentation work did
not change that boundary.

Future checkpoints must receive dated summaries, updated copyable commands, and
verified persistent copies before their results are reported in chat. This rule
is also recorded in the repository's `AGENTS.md`.

Latest user instruction: profiling is deferred and optional; no new downloads, training or experiments. See RESUME.md before restarting anything.
