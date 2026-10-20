# Checkpoint 25 — Persisted local-Mac application handoff

The user requested that all necessary state be saved/pushed, followed by a
self-contained context prompt for local Codex. The full task and context are
in docs/MAC_CODEX_HANDOFF.md. This checkpoint prepares that handoff; it does
not implement or run the new UI/API application.

The handoff records the current frozen model/splits, actual results and limits,
UNI2 identity, preprocessing, private bundle identities/paths, verified native
ARM64 evidence, existing frontend/job contracts, cache-only app boundaries,
proposed container/browser verification, persistence requirements and Git finish.
It explicitly distinguishes real cached classification from fresh UNI2 encoding,
and preserves the rejected optional Mac sync-receipt boundary.

Checkpoint 24's next-step plan is included in this publication. AGENTS.md,
STATUS.md, docs/RESUME.md, docs/INDEX.md and docs/COMMANDS.md identify the latest
handoff. No manual app startup command exists yet. Giving the saved task prompt
to local Codex is the next action; routine implementation and actual local
verification belong to that successor task.

One recovery fix was necessary: the source archive allowlist previously omitted
the tracked frontend. It now includes frontend source/lock/assets, backend source
when present and app Compose filenames, while excluding dependency directories,
generated viewer tiles, raw/model/cache binaries, symlinks and credential files.
This changes source backup coverage only; encoder/preprocessing/features/model
implementation and all scientific artifacts are unchanged.

The first extended archive was actually read and verified: all 187 members,
including all 95 tracked frontend files, matched the intended source inventory.
The sanitized frontend .env.example and package-lock are included; forbidden
artifact/dependency paths are absent. Secret-pattern scanning found no matches.
The persistence helper verified 45 document/source copies plus the archive.
The final source archive pointer is in docs/LATEST_BACKUP.md.

Verification checks the new archive can be read, includes the existing frontend
source, package lock, assets and sanitized .env.example, excludes generated/private
content, and contains no secret-pattern matches. The exact staged diff receives
whitespace, size/path and secret checks before committing. A normal push is
verified against the live branch SHA; the final SHA and refreshed recovery copy
are recorded separately in persistent docs/GIT_PUBLICATION.md to avoid a
self-referential commit hash.

Source/doc persistence is performed with scripts/persist_records.py on the
genuine Colab Drive mount, with SHA256 readback. Existing Mac backup-pointer
history remains preserved in checkpoint 22's backup-history document.
No new slide or model downloads, training, evaluation, profiling, web app build,
service startup or Docker execution were performed in this handoff task.

Persistent full prompt:
/content/drive/MyDrive/LungCancer_AC215/docs/MAC_CODEX_HANDOFF.md

Persistent summary:
/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-20-25-mac-app-handoff.md
