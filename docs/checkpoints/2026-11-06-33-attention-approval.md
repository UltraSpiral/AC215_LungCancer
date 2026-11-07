# Checkpoint 33 — Attention-pooling experiment approved; Phase 0 setup

Date: 2026-11-06, America/New_York. Branch: `attention-mil` (from `milestone2` at `5369a89`).

## Decision recorded

Awassada approved a CPU-only gated attention MIL experiment on the existing
cached UNI2-h embeddings, with a per-tile attention heatmap on `sample.svs`.
The plan, including every decision and its reason, is
[ATTENTION_PLAN.md](../ATTENTION_PLAN.md). The approval boundary is recorded at
the top of `AGENTS.md`.

Before this checkpoint, `git fetch` confirmed local `milestone2` equalled
`origin/milestone2` (`5369a89`), the only remote branch.

## Implemented

- `AGENTS.md`: approval section and boundary for this experiment.
- `docs/ATTENTION_PLAN.md`: the reviewed plan.
- This checkpoint, plus entries in `INDEX.md`, `CHECKPOINTS.md`, `COMMANDS.md`.

## Actually executed and verified

Nothing has been trained or evaluated. Phase 0 results are added below once run.

## Not changed

Splits, preprocessing, cached features, the saved logistic-regression bundle,
`lungcancer/`, `backend/`, `frontend/`, `local_data/` and `local_outputs/app/`.
No downloads of slides or weights.

## Persistence

`scripts/persist_records.py` targets a mounted Colab Drive, which does not exist
on this Mac; it was not run. Records are in Git on branch `attention-mil`.
