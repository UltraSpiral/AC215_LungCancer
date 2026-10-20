# Checkpoint 32 — Pipeline scope, onboarding and isolated reviewer reproduction

Date: 2026-10-20, America/New_York.

## Implemented

Added [PIPELINE_SCOPE.md](../PIPELINE_SCOPE.md): diagram and table covering
GDC metadata/acquisition, specimen audit, full preprocessing, frozen UNI2,
baseline fitting/evaluation, portable packaging, restore, container input
validation, separate real preprocessing smoke, saved-head inference and UI.
Every stage identifies its environment, input, output and executed boundary.
The 16-tile smoke is explicitly separate from the 512-tile cached model input.
Colab acquisition/encoding/training are not described as Docker execution.

Added [REVIEWER_SETUP.md](../REVIEWER_SETUP.md) with the exact protected archive
link, access-check scope, SHA256/size, host prerequisites, clone/restore/start,
expected output and isolated project/port/image configuration. Drive metadata
confirmed owner and one existing team collaborator's explicit permissions;
the saved checksum sidecar matches the expected artifact. No sharing change or
another person's login/execution is claimed. Additional accounts need their
own access to the private file.

The root README now provides current onboarding and evidence navigation. The
entire prior pilot narrative is retained in
[the history page](../history/2026-10-20-pilot-readme.md), with only documented
link destinations repaired/rebased. The three unavailable artifact links now
have an explicit historical private-storage note. Git history retains the
original bytes; a local preservation receipt compares the narrative.

Added optional CPU/API/web image-tag overrides for parallel checkouts. Their
defaults remain the original tags. The replay inspects the selected CPU image
instead of a hardcoded tag. Classifier/feature/preprocessing/split code, weights,
locks and scientific artifacts did not change.

## Actually executed and verified

Tested clean implementation commit:
`a25ed2a8aa19a59f7262942a4864ffa59ec7cb53`.

A fresh GitHub clone was fast-forwarded to that exact local implementation
commit before publication. Its source tree was clean when executed. It had
neither restored inputs nor host node_modules. Verified the existing archive
SHA256 `c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988`
and size 186,505,459, then restored 187 files into the new checkout using the
unchanged non-overwriting helper.

Executed `make ms2-demo` with separate project `lungcancer-ms2-review`, port
18080, image tags and input/output locations. Exit **0**. The actual native
ARM64 app built/started, verified the inventory, ran the real 16-tile smoke,
streamed the supplied 71,138,367-byte slide through HTTP and computed
`non_tumor` from its 512-vector cache. Maximum frozen-reference difference:
`6.938893903907228e-18`. Image identities/architecture are in the run report.

All **ten real browser/API scenarios passed**, with zero page errors and no
network interception: genuine known/renamed result, filename/case invariance,
fixture isolation, modified/unknown input rejection, empty/oversized input and
actual isolated-API outage/restoration. The existing host Playwright/Chromium
test client was reused against the new containers. Docker could reuse build
layers; this is not a second machine or a fresh Docker installation. Inspected
the actual successful and unknown-input screenshots.

Executed isolated stop/resume, verified ready health, then removed only that
project's containers/networks. Original app container IDs, image tags and all
186 inventory entries plus manifest remained unchanged. Original 8080 health
was ready. The isolated source remains clean, and its restored inputs and
all outputs are preserved locally.

## Evidence and exact locations

[Public reproduction package](../evidence/ms2/2026-10-20/reviewer/README.md):
actual logs, clean-commit report, HTTP output, browser report, unmodified
screenshots/overlay, runtime identities, preservation checks and hashes.

Original working directory:
`/Users/shlokdholakia/Documents/Harvard/Semesters/SEM3/AC215/LungCancer`.

Isolated checkout:
`artifacts/reviewer_setup/2026-10-20-32/checkout/` relative to that directory.
Its replay output is
`local_outputs/ms2/20261020T143655Z-d7535f83/`; browser evidence is
`local_outputs/app/browser/`. Local inspection, private permission details,
backup/publication receipts and full commands are retained under
`artifacts/ms2_audit/2026-10-20-32/`.

The unchanged original app remains **http://127.0.0.1:8080/**. The isolated
18080 test project was cleaned up; its instructions can start it again. Exact
commands and working directories are in [COMMANDS.md](../COMMANDS.md).

## Pending and persistence

Full fresh-UNI2 container execution remains unverified. This checkpoint closes
the documentation ambiguity and exercises fresh source/artifact restoration
for the chosen prepared-feature workflow. It does not claim a complete
containerized scientific acquisition/encoder/training pipeline or a guaranteed
rubric grade. No additional slides/weights, new embeddings, refit, split change,
new test metrics or profiling ran. The unchanged full CPU/backend unit suites
were not repeated. Presentation, individual understanding and Canvas remain
team tasks; another person's independent setup was not observed.

The required persistence helper retains its genuine Colab Drive mount guard.
New source/Markdown/evidence and Git recovery backups are verified locally;
no new Drive mirror or permission change is claimed. Normal publication uses
UltraSpiral and preserves remote history. The final full publication SHA lives
in the local receipt, rather than being embedded in its own committed file.
