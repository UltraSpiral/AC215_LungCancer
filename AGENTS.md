# Persistent checkpoint records

The user requested durable Markdown records of every checkpoint summary and all
commands they need to copy. Maintain these records as work proceeds:

- Update `docs/INDEX.md`, append the checkpoint history in `docs/CHECKPOINTS.md`,
  and save a dated summary under `docs/checkpoints/` before a checkpoint response.
- Keep notebook and terminal commands in `docs/COMMANDS.md`, identifying commands
  needed now, previously executed commands, and future stages awaiting review.
- Record what was implemented, actually executed, verified, and still pending.
  Preserve historical summaries; annotate factual corrections explicitly.
- Run `python scripts/persist_records.py` to back up code and copy all Markdown
  records to `/content/drive/MyDrive/LungCancer_AC215/docs/`, with SHA256 verification.
  This may require approved execution for mounted Drive. Do not change security controls.
- Report clickable persistent Markdown paths to the user. Do not rely on terminal
  scrollback. Never include secret values in documents, commands, logs, or backups.

Current work is paused at the user's pilot-review checkpoint. No additional slide
downloads or real-data training are authorized by the documentation request.
Follow subsequent explicit user instructions when this scope changes.
