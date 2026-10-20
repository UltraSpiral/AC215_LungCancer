# Checkpoint 29 — Executed MS2 replay and submission evidence packaged

Date: 2026-10-20, America/New_York.

The user asked what remains to satisfy MS2 and submit. They supplied the local
MS1 proposal and reported TF approval plus permission to simplify for an MS2
MVP. Reviewed all four proposal pages and the original four-interface appendix;
recorded the feedback as user-reported. The original timeline places the
containerized pipeline and app skeleton at MS2, with later advanced model,
backend/cloud, frontend/report and external-validation work.

## Implemented and executed

Added `make ms2-demo` and a standard-library host runner. It builds/starts the
existing ARM64 app, validates the browser-facing route, builds the CPU verifier,
validates the input inventory and executes its real preprocessing smoke, streams
the existing supplied slide to the actual HTTP backend, polls the new result,
checks the frozen prediction reference, and saves its overlay/image identities.
Subprocess failures retain their exit status, logs and an error report. Each
run receives an exclusive new ignored output directory; old evidence is intact.

Executed successfully with exit **0** on the M1:
`local_outputs/ms2/20261020T111730Z-c47c45b5/`.
Real preprocessing selected 16 in-bounds tiles. Real HTTP prediction was
non_tumor from the existing 512 model tiles; maximum frozen-reference difference
6.938893903907228e-18 at tolerance 1e-8. Actual overlay visually inspected.
The new smoke is a separate data-processing check, not the source of the
classifier's features. No UNI2 weights/features were generated, no training or
metric evaluation occurred, and frozen inputs/settings remain unchanged.
The full CPU unit/cache suite and app/browser suites were not repeated.
Two runner guard checks also passed: missing input and an existing output
directory both failed clearly before processing; existing files were unchanged.

## Submission artifacts

Packaged 27 selected existing/new evidence artifacts under
`docs/evidence/ms2/2026-10-20/`, with an index, source/published SHA256 manifest
and checksums. It includes genuine CPU Docker screenshot, original logs,
JSON/JUnit, image/runtime identities, real preprocessing visuals, original
training/search metadata, the MS1 mock-up appendix and new replay outputs.
Three text artifacts have the local absolute checkout path replaced by
`<REPOSITORY_ROOT>`; other selected artifacts are byte-identical originals.
No secret-pattern hits; screenshots are unmodified and visually inspected.
The full proposal PDF, private binaries and raw inputs remain outside Git.

Added MS2_SUBMISSION.md with exact run/restore commands, input-access conditions,
team/presentation walkthrough and Canvas deadline. Added MS2_DESIGN.md mapping
the approved MS1 mock-up to the simpler implemented MVP. Updated current
readiness/status/command/index/verification records, preserving earlier history.

The PDF reader's first unpinned dependency resolution included unnecessary
packages and was interrupted before use. Installed only pinned PyMuPDF 1.26.5
with --no-deps in temporary storage; the project/container environments and
scientific dependency locks were not changed by PDF inspection.

## Remaining and persistence

The actual presentation deck, shared team rehearsal, confirmation of teammate/
reviewer private-snapshot access and Canvas submission remain team tasks.
No deck or Canvas submission is claimed. Full fresh-UNI2 container execution
and uncached-slide support remain outside the verified MVP; caching is valid
and does not imply runtime training. The user-reported TF feedback permits
simplification, without establishing a grade or approving every implementation.

Run the required persistence helper with its genuine mounted-Drive guard;
checksum-verify the local source archive, Markdown and selected evidence.
Receipts and Git recovery verification belong under
`artifacts/ms2_audit/2026-10-20-29/`. The helper refuses Drive copying on this
Mac; no new private Drive mirror is claimed. Publish reviewed deliverables
normally as UltraSpiral, verify local/live full SHA equality and a clean tree.
Final full SHA is recorded in the local publication receipt and response;
this checkpoint does not embed its own commit hash.
