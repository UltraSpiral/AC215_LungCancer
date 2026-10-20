# Approved MS1 design and the simpler MS2 MVP

The user reported on 2026-10-20 that the TF approved MS1 and allowed liberties
to simplify the MS2 MVP. This is user-reported feedback, not an independent
claim that the TF approved every current implementation or result.

Reviewed all four pages of the supplied proposal,
`Milestone 1 Project Proposals Shlok Dholakia.pdf`.
Source SHA256 is recorded in the evidence provenance below. Page 3 assigns
MS2 to the containerized data pipeline and app skeleton; more advanced model,
backend/cloud, frontend/report and external-validation work appears in later
milestones. Page 4 contains the original four interface mock-ups:

1. Technician scan review and rescan/escalation.
2. Pathologist comparison of original and analyzed slides.
3. Uncertain-result review with pathologist decisions.
4. Editable pathology report and human sign-off.

[Original MS1 mock-up appendix](evidence/ms2/2026-10-20/design/ms1-proposal-appendix.png)
is an unmodified rendering of page 4. Its images are illustrative MS1 designs,
not screenshots of executed model results. The proposal's
[original Figma prototype](https://www.figma.com/proto/kD9uemO4wTbU3gs1JpVSsA/AI-Assisted-Lung-Cancer-Screening?node-id=1-801&page-id=0%3A1)
is linked for reference; the PDF rendering is the reviewed source, and current
Figma access/content has not been verified. The original full PDF remains at
the user-supplied Downloads path and is not added to Git.

## Changes made for the working milestone

| Original design / aspiration | Implemented MS2 behavior and rationale |
|---|---|
| Multiple technician/pathologist/report screens | One real upload-and-review flow. It demonstrates basic UI/backend interaction with a smaller executable scope. |
| Broad new-slide analysis | One genuine preprocessed slide, recognized by its bytes. Cached real features avoid new encoder/weight setup; unsupported inputs fail clearly. |
| CNN/ViT comparisons and attention MIL | A frozen pathology ViT encoder plus mean pooling and a regularized logistic head establishes an interpretable first engineering baseline with limited learned parameters. |
| Confidence scores and confidence-based abstention | API probabilities are explicitly uncalibrated; the UI keeps them hidden. Unsupported-input rejection is a support check, not statistical uncertainty abstention. Calibration/selective prediction remains future work. |
| Highlighted tumor regions / explanation heatmaps | Actual thumbnail plus cached analyzed-tile locations. Rectangles show sampled areas, not tumor predictions or attribution. No invented explanatory heatmap. |
| Tissue-characteristic report, editable diagnosis and sign-off | Deferred. The current panel displays predicted class, model identity, actual tile count and recorded quality warnings. |
| Cross-dataset/cloud/monitoring expansion | Current TCGA cohort and native ARM64 local Compose. Additional acquisition, experiments or cloud deployment require their own later scope. |

Implementation also isolated mock fixtures from production HTTP mode, removed
filename-based result/viewer matching, provided genuine queued/running/terminal
states, and added useful unsupported-input, upload-bound and unavailable-backend
errors. These changes follow what the real bounded backend can support.

## Evidence and future technical decisions

[Actual working result](evidence/2026-10-20-app-result.png) and
[actual unsupported-input error](evidence/2026-10-20-app-unknown.png) show the
implemented interface. The [browser/API report](evidence/2026-10-20-app-verification.json)
records ten real scenarios; no browser request interception supplied answers.

The original saved training metadata shows the prespecified C search
0.01/0.1/1.0, each with validation macro F1 0.667; C=0.01 is current. Six test
patients are insufficient for a reliable performance claim and were previously
observed in the provisional run. Further model complexity is not established
as necessary by those results. Preserve the fixed splits and inspect data/QC
limitations before proposing a new approved experiment. Candidate future work
includes better sparse-normal masking/QC, a justified pooling comparison,
validation-based calibration and meaningful region explanations. None of this
document launches new training, acquisitions or changes to frozen settings.

The proposal source identity, original image source hash and all published
artifact hashes are in [the evidence manifest](evidence/ms2/2026-10-20/manifest.json)
and [evidence index](evidence/ms2/2026-10-20/README.md).
