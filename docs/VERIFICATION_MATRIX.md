# Verification scope

| Component | Evidence/state | Remaining work |
|---|---|---|
| GDC acquisition and specimen audit | Real saved metadata; latest strict audit 3,172 eligible / 3,220, 48 excluded | Future cohorts need a new approved resource plan |
| Physical tiling and frozen UNI2 | 45 real slides processed on L4/A100; 44 eligible after one metadata exclusion | Sparse-normal/site/preparation inference limitations remain |
| Corrected real baseline | 44 patients; 32 train / 6 validation / 6 test; no patient moves or leakage | Tiny/reused test limits inference about generalization |
| Real local SVS inference | Passed in Colab on an arbitrary filename, named uncalibrated probabilities and location overlay | Clinical validation is outside scope |
| Torch-free CPU script sequence | Passed on x86_64 Colab: 29 tests, 44 real caches, real 16-tile SVS smoke | This is not Docker/ARM64 execution evidence |
| Apple Silicon CPU container recipe | Dockerfile, Compose, uv project/lock, pinned ARM64-capable base, portable data and guide prepared | User's M1 Codex must build/run/debug and record proof |
| Full slide-to-prediction container | Separate pending verification | Real encoder loading, embeddings and prediction in a suitable execution environment |
| UI/backend interaction | Existing frontend and reference stub preserved | Run and document actual interaction; fixtures remain UI fixtures |
| Optional synchronized profiling | Deferred | No stage timings or hardware-only A100 speedup claimed |

Final model artifacts are under
`/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z-audit2/`.
The provisional 45-slide run remains under the sibling 20261020T0220Z/ directory
for audit history. Use the audit2 model as current. The six test patients were
previously observed in the provisional run; correction depended on specimen
metadata, with no test-based tuning. The submission is not yet verified end to
end in containers.
