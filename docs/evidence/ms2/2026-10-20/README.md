# MS2 real execution evidence — October 20, 2026

This directory publishes selected original evidence plus a new executed
single-command cached-feature demonstration. Raw slides, model binaries,
embeddings, gated weights, authentication and browser caches are excluded.
[manifest.json](manifest.json) records original/published hashes and any local
path substitutions. Screenshots and original design renderings are unmodified.
[SHA256SUMS](SHA256SUMS) covers the selected source evidence files.

## One-command bounded workflow — checkpoint 29

Executed from the project root on Apple M1:

```bash
make ms2-demo
```

The command exited **0**. It built/started the real app, validated its HTTP
health, built the ARM64 CPU image, verified the prepared input inventory and
ran the real-SVS preprocessing smoke, then streamed the actual supplied slide
through nginx to the real API. It polled the new prediction, compared its
probabilities to the frozen reference and fetched the actual overlay.

- [Complete scoped report and Docker image identities](demo/demo.json)
- [App build/start log](demo/app-start.txt), [CPU build log](demo/cpu-build.txt),
  [preprocessing run log](demo/preprocess.txt)
- [Actual HTTP job/result](demo/prediction.json)
- [Real preprocessing report](demo/real_preprocessing.json) and
  [inventory/runtime report](demo/verification_preprocess.json)
- [Actual 512-coordinate location overlay](demo/analyzed_tiles_overlay.jpg)

The result is `non_tumor` with **512** cached model tiles. Maximum probability
difference from the saved reference is **6.938893903907228e-18** (tolerance
1e-8). The source is the existing 71,138,367-byte slide, SHA256
`544fc4ab2cf62ebc99e01e734907ec4194c71baba8b61bb4cbca92ae739c9a9d`.
The snapshot/model identities appear in the report and are checked by the API.

The **16** newly selected preprocessing-smoke tiles are separate from the
immutable **512** model tiles. No features are generated from that smoke, and
those tiles are not supplied to the classifier. This demonstrates the chosen
prepared-feature workflow with a separate real preprocessing check. It does
not prove fresh UNI2 feature extraction inside Docker or uncached-slide support.

The runner was executed before its publication commit; the report therefore
records the parent Git HEAD and a dirty worktree, along with the exact executed
runner SHA256. That script hash matches the source committed with this report.
Image IDs are those from this actual execution; rebuilds can create new IDs.

## Original CPU verification — checkpoint 21

- [Successful real Docker terminal screenshot](cpu/docker-success.png)
- [Original build/run console log](cpu/console.txt)
- [JUnit: 29 passed, zero failures/errors/skips](cpu/unit-tests.xml)
- [Complete run JSON](cpu/verification_all.json): 44 caches, 22,483 finite
  vectors, 12 frozen predictions, patient separation and training-only scaler
- [Image identity/architecture](cpu/image_identity.json),
  [live-container inspection](cpu/runtime_container.json), [host](cpu/host.json)
- [Real 16-tile preprocessing report](cpu/real_preprocessing.json)
- [Tissue mask overlay](cpu/tissue_mask_overlay.jpg),
  [selected-tile locations](cpu/selected_tiles_overlay.jpg),
  [real tile contact sheet](cpu/contact_sheet.jpg)

These are the original successful CPU run, not a newly repeated full unit/cache
suite. The screenshot contains its original image ID and explicit full-encoder
verification limitation. Three recorded unit-fixture/deprecation warnings do
not represent failed tests. The checkpoint-29 replay reruns only the relevant
preprocessing stage to exercise its new orchestration, preserving old outputs.

## Original app verification — checkpoint 26

- [Build/start log](app/build-start.txt), [14-test log](app/backend-tests.txt),
  [JUnit](app/backend-tests.xml), [real browser scenario log](app/browser.txt)
- [Recorded app image/runtime identities](app/runtime_identity.json)
- [Computed result and ten real browser/API scenarios](../../2026-10-20-app-verification.json)
- [Genuine successful browser screenshot](../../2026-10-20-app-result.png) and
  [genuine unknown-input screenshot](../../2026-10-20-app-unknown.png)

The old app run's image IDs belong to that historical execution. The new
bounded workflow's IDs are recorded separately in demo/demo.json. Browser
scenarios covered renamed/misleading metadata invariance, unsupported/modified
input, empty/oversized files, fixture isolation and a genuine API outage.

## Original experiment and design artifacts

[saved-training-metadata.json](model/saved-training-metadata.json) is an exact
copy of the real saved model's JSON metadata from the private snapshot. It
contains the C search and validation results, majority baseline, cohort counts,
frozen encoder/preprocessing identities and classifier checksum. It is not the
classifier binary and does not contain weights or feature arrays. Final test
results and audit limitations are documented in
[checkpoint 16](../../../checkpoints/2026-10-20-16-modeling-results.md); no new
test metrics were calculated for this package.

[MS1 proposal appendix](design/ms1-proposal-appendix.png) is page 4 of the
user-supplied approved proposal, rendered without edits. It is the original
mock-up, not execution evidence. [MS2_DESIGN.md](../../../MS2_DESIGN.md) explains
the implemented simplifications and attributes the TF feedback to the user's
report. The source PDF SHA256 is included in manifest.json.

The complete ignored local evidence and private snapshots remain preserved.
The repository's [submission guide](../../../MS2_SUBMISSION.md) explains
reviewer input access, run commands, remaining presentation work and Canvas.
