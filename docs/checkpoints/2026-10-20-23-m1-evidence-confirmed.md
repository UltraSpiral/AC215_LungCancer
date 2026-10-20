# Checkpoint 23 — M1 evidence confirmed from Colab

The user reported successful native M1 Docker verification. Colab fetched and
fast-forwarded milestone2 from 95fff6baab9e6942992356d70ee56e6c848da2c3 to
the Mac's published commit 598bcd79662a72af832db698b9761658bd943736. Existing
Mac checkpoint 21, publication checkpoint 22, status and commands were preserved.
No pipeline code, dependency lock, model or split changed.

Independently inspected the already-approved Drive evidence archive:
`/content/drive/MyDrive/LungCancer_AC215/artifacts/cpu_verification/2026-10-20-native-arm64/cpu-evidence-2026-10-20-21-native-arm64.tar.gz`.

Actual SHA256 matches
`70493e8e5086ad83fc339bc649d13d52f2411b39dbe6e365a4202ffff5c4effa`.
All 72 entries in its SHA256SUMS inventory matched archived file bytes.
JUnit records 29 tests, zero failures/errors/skips. Make exit code is 0.
JSON confirms aarch64 runtime, linux/arm64 image, 44 real caches / 22,483
finite vectors, 12 saved predictions, patient separation and training-only
scaling. The real smoke selected 16 tiles at 0.49926116071428567 MPP.
Image and live-container identities match:
`sha256:c78cfbdd188e4c02a5330f110ccdcc77c8a6c7b9c815e893fd6ea3ca0f40a0da`.
Recorded runtime isolation is offline, read-only root and read-only inputs.

The genuine screenshot, contact sheet and selected-tile overlay were opened
from the checksum-verified package and inspected in Colab. The screenshot
shows the successful native run and its full-inference limitation. The tile
sheet is populated and the overlay shows distributed analyzed locations.
This is evidence review of the saved Mac run, not another container execution
or a new scientific/clinical assessment.

CPU container verification is complete. Full slide-to-UNI2-to-prediction
container verification and actual UI/backend interaction remain separately
pending. No slides, weights, model fits, split changes, test-metric reruns or
profiling were performed. The optional Mac sync-receipt upload rejected as
outside its approved payload was not retried or copied through another route.
It remains local to the Mac as the user reported.

No manual command is needed now. Existing Mac reproduction commands remain
in docs/CPU_CONTAINER_VERIFICATION.md and docs/COMMANDS.md. Completed source
and records are backed up by the genuine mounted-Drive persistence helper;
docs/LATEST_BACKUP.md identifies the newest verified source archive. The
earlier Mac backup pointers remain in commit 598bcd7 and are retained verbatim
in docs/checkpoints/2026-10-20-22-backup-history.md.

Local evidence review: artifacts/cpu_verification/native_m1_review/.
The review JSON and extracted images are local derivatives of the approved
archive; they are not the rejected Mac sync receipt. Persistent checkpoint:
`/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-20-23-m1-evidence-confirmed.md`.
