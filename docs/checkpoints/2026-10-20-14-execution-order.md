# Checkpoint 14 — modeling first, explicit approval required

2026-10-20 UTC. The user proposed completing modeling before MLOps work and
explicitly instructed: "dont start training without my ecplicit approval".
This message sets the work order; it does not grant training approval.

## Agreed proposed order

1. After the user explicitly authorizes the modeling run, complete the proposed
   45-slide engineering baseline: required setup and new-slide processing within
   the existing 10 GB cumulative raw budget, reuse nine compatible caches, fix
   patient-level splits, fit the frozen-UNI2/mean-pool/logistic baseline, compare
   the majority baseline, save separate validation/test results, and demonstrate
   renamed held-out SVS inference. Preserve configurations, data/encoder IDs,
   logs, artifacts and dependency versions for subsequent packaging.
2. After the modeling run, complete the MS2 MLOps deliverables: uv/container
   environments, Dockerized components, a one-command pipeline and real execution
   evidence, plus verified basic UI/backend interaction and submission records.
   Containerization still needs a Docker-capable host; it is not available here.
   Packaging includes verifying the saved workflow; a completed model alone
   does not finish the full MS2 rubric.

## Current authorization

**No training is approved yet.** Do not treat a proposed sequence, a question,
a timeout or a preselected unanswered option as approval. Explicit approval
means an unambiguous instruction to start the chosen modeling run; no exact
magic wording is required. Once that approval exists, carry out its necessary
routine steps without requesting the same permission again.

Existing acquisition/experiment pause remains in effect until an authorized
modeling run or another explicit instruction changes it. No slide/model/package
download, training, experiment, container build or frontend execution was run
for this checkpoint. Only durable planning/authorization records were updated.
HF setup is already verified and must not be requested again unnecessarily.
OpenSlide and the pinned UNI2 checkpoint still need routine setup when allowed.

No processing command needs to be copied now. Current plan references:
TRAINING_PLAN.md, ONE_HOUR_PLAN.md, MS2_GAP_ANALYSIS.md, and checkpoint 13.
