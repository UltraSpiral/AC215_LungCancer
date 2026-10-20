# Checkpoint 11 — one-hour feasibility and reduced-cohort proposal

2026-10-20 UTC. User requested completion under one hour. The classifier is
already a small frozen-feature logistic model; acquisition/extraction dominates.
Read actual pilot timers and saved metadata, rechecked the current A100/setup,
and prepared deterministic draft cohorts offline. No training/downloads ran.

A resource-bounded 15/class cohort is complete at 45 slides, reuses all nine
pilot caches and needs 36 new files / 4,433,083,094 raw bytes. Cumulative raw
would be 5,453,285,795 bytes within the unchanged 10 GB budget. A historical-rate
forecast gives 33.07 minutes for new data work, before setup/model/evaluation/
inference/backup; it is not an A100 measurement or deadline guarantee.

The cohort reduction from 30–50/class is a material scope change. A choice was
requested; approval is pending. Supported notebook HF login is also required.
No answer is inferred from time passing. Full proposal, constraints, limitations,
optimization candidates and the one-cell setup command: [ONE_HOUR_PLAN.md](../ONE_HOUR_PLAN.md).

Full modeling still requires fixed patient groups, a small training-only C
search, baseline, untouched test evaluation, and real renamed-file inference.
Small held-out counts must be disclosed. Frontend integration stays separate.

Persistent plan: /content/drive/MyDrive/LungCancer_AC215/docs/ONE_HOUR_PLAN.md.
Persistent evidence: /content/drive/MyDrive/LungCancer_AC215/artifacts/time_budget/2026-10-20/.
