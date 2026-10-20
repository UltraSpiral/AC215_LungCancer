# Verification scope

Checkpoint 29 adds executed `make ms2-demo` and a selected public evidence
package. It verifies the prepared-input workflow, a separate real preprocessing
smoke and cached-feature HTTP prediction in one command. The new 16 smoke tiles
are not classifier inputs; the immutable 512-tile cache is used. See
[MS2_SUBMISSION.md](MS2_SUBMISSION.md) and
[actual evidence](evidence/ms2/2026-10-20/README.md).

The supplied MS2 rubric has a current detailed mapping in
[MS2_READINESS.md](MS2_READINESS.md), checkpoint 27. Verified cached inference
and a separately executed preprocessing smoke do not establish the complete
scientific pipeline inside containers. Presentation/Canvas and GitHub evidence
packaging are assessed separately from scientific execution.

Checkpoint 28 clarifies the requirement interpretation: feature caching is a
valid design and serving uses saved model parameters without retraining.
Fresh UNI2 execution on every run is not explicitly demanded by the supplied
rubric. Its unverified container path limits broader raw-slide claims; it does
not invalidate the verified cached-feature app. See the correction at the top
of [MS2_READINESS.md](MS2_READINESS.md).

| Component | Evidence/state | Remaining work |
|---|---|---|
| GDC acquisition and specimen audit | Real saved metadata; latest strict audit 3,172 eligible / 3,220, 48 excluded | Future cohorts need a new approved resource plan |
| Physical tiling and frozen UNI2 | 45 real slides processed on L4/A100; 44 eligible after one metadata exclusion | Sparse-normal/site/preparation inference limitations remain |
| Corrected real baseline | 44 patients; 32 train / 6 validation / 6 test; no patient moves or leakage | Tiny/reused test limits inference about generalization |
| Real local SVS inference | Passed in Colab on an arbitrary filename, named uncalibrated probabilities and location overlay | Clinical validation is outside scope |
| Torch-free CPU script sequence | Passed on x86_64 Colab: 29 tests, 44 real caches, real 16-tile SVS smoke | This is not Docker/ARM64 execution evidence |
| Apple Silicon CPU container execution | **Passed on Apple M1, linux/arm64, checkpoint 21:** make exit 0; 29 tests; 44 real caches / 22,483 vectors; 12 frozen probabilities matched within 5.56e-17; real 16-tile smoke and inspected overlays | Logs, reports, image identity and genuine MS2 screenshot saved locally; approved Drive evidence package passed SHA256 readback; see checkpoint 21 |
| Full slide-to-prediction container | Separate pending verification | Real encoder loading, embeddings and prediction in a suitable execution environment |
| Native ARM64 cached-feature app | **Passed, checkpoint 26:** actual Chromium upload/poll/result with saved classifier; 10 browser/API scenarios; 14 backend tests; production frontend checks; genuine screenshots; stop/resume and host readiness | One supplied preprocessed raw slide; no fresh UNI2 extraction; local-demo session/job limits in LOCAL_APP.md |
| Single-command bounded MS2 replay | **Passed, checkpoint 29:** make ms2-demo exited 0; app start, prepared inventory, real 16-tile smoke, actual HTTP prediction from 512 cached tiles, frozen-reference comparison, overlay and ARM64 image identities | Original/new evidence packaged; complete fresh-encoder path remains outside this scope |
| Optional synchronized profiling | Deferred | No stage timings or hardware-only A100 speedup claimed |

Final model artifacts are under
`/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z-audit2/`.
The provisional 45-slide run remains under the sibling 20261020T0220Z/ directory
for audit history. Use the audit2 model as current. The six test patients were
previously observed in the provisional run; correction depended on specimen
metadata, with no test-based tuning. The submission is not yet verified end to
end in containers.
