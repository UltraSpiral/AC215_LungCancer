# Checkpoint 22 — Publish the native M1 verification records

Date: 2026-10-20 (America/New_York).

The user explicitly requested committing and pushing the completed CPU
verification documentation to `origin/milestone2`. This publication includes
checkpoint 21, the verification matrix, current status, commands and backup
records. Pipeline code, dependencies, classifier and fixed splits are unchanged.

Before publication, the local branch and live GitHub branch both resolved to
`95fff6baab9e6942992356d70ee56e6c848da2c3`; a fresh fetch confirmed zero commits
ahead or behind. Existing local documentation was preserved. The publication
uses the selected repository identity:
`UltraSpiral <UltraSpiral@users.noreply.github.com>` for author and committer.
The previous email setting was corrected locally, without changing global Git
configuration. Git uses the existing supported credential setup; the GitHub CLI
is absent on this Mac. No credential values were read or recorded.

Validation consists of a whitespace/error check, a secret-pattern scan of the
exact staged files, and inspection that only the documentation allowlist is
staged. CPU/model tests are not repeated for this documentation-only change;
the actual successful native run is documented in checkpoint 21.

The commit is pushed normally, without force. Afterwards Codex compares the
local full commit SHA with the live GitHub `refs/heads/milestone2`, checks the
author/committer, and verifies the working tree is clean. The final observed
SHAs, commit contents, validation results and push output are saved in the
local publication receipts under
`artifacts/publication/2026-10-20-22-cpu/`. Those receipts are written after
the push, so this committed document does not contain its own commit hash.

`python3 scripts/persist_records.py` is executed for a fresh source archive.
Its genuine mounted-Drive guard remains unchanged; on the Mac it refuses
Colab copying. Current Markdown and the archive receive SHA256-verified local
copies under the publication directory. [LATEST_BACKUP.md](../LATEST_BACKUP.md)
records the current local archive. The checkpoint-21 Drive package remains an
immutable earlier snapshot; this publication does not claim that the new Git
publication receipts were uploaded to Drive. The optional cloud receipt upload
rejected previously is not retried.

Data bundles, raw slides, weights, classifier/embedding files, logs, test
reports, overlays, screenshots and private synchronization receipts stay outside
Git. Existing local and approved Drive evidence is preserved. Full containerized
slide-to-prediction verification and UI/backend interaction remain pending.
No downloads, training, split changes or profiling are part of this publication.

See [COMMANDS.md](../COMMANDS.md) for the publication commands. No manual user
command is required after Codex finishes the requested commit and push.
