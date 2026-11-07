# Gated attention pooling + slide heatmap — CPU-only plan

Status: plan only, nothing executed. Written 6 Nov 2026 with Awassada after a read-only inspection of `~/Desktop/AC215_LungCancer` (git HEAD `5369a89`). Updated 6 Nov 2026 with Awassada's decisions: native uv for development + Docker for the final run; gated attention only (no ablation); single best seed for the heatmap; **no slide re-download** (heatmap on `sample.svs` only). **Revised 6 Nov 2026 after a second code-level review:** fixed hyperparameters instead of a grid, Docker owns seed selection / test / final heatmap, mandatory logistic-regression tile baseline, outputs under `local_outputs/attention/`, rank-normalised heatmap colours, CPU-only torch index, and confirmed Docker feasibility on this Mac. Changes are marked **(rev)**.

Goal: train a gated-attention MIL head on the **existing cached UNI2-h tile embeddings** of the 32 training slides (no GPU, no UNI2 weights, no downloads) and render a per-tile attention heatmap on the one local slide image, `local_data/cpu_bundle/sample/sample.svs`. The current mean-pooling logistic-regression model stays untouched and remains the app default.

What each input is for:
- **Training:** cached features (`embeddings.npz`) of the 32 train slides; model selection on the 6 validation slides. No image files are read during training.
- **`sample.svs`:** display only. It is a test slide (never trained on); the trained model scores its 512 cached tiles and the scores are painted onto its thumbnail.

## 1. Facts this plan relies on (verified)

- Current model: `local_data/cpu_bundle/run/model/classifier.joblib` = StandardScaler + multinomial LogisticRegression (C=0.01); `model.json` → `"pooling": "mean_of_tile_embeddings"`, validation macro-F1 0.667 (all three C values tied at 0.667). Classes `('non_tumor','adenocarcinoma','squamous')` from `lungcancer/common.py`.
- Cached features: `local_data/cpu_bundle/slides/<file_id>/embeddings.npz` for all 44 slides (123 MB total). Keys: `embeddings` (≤512×1536 float32), `coordinates` (≤512×2, level-0 upper-left x,y in pixels), `metadata_json`. `coordinates.npz` also has `tissue_coverage` (≤512).
- Split: `local_data/cpu_bundle/run/splits.json` → `slides[]` with `file_id`, `md5sum`, `case_id`, `candidate_class`, `split` ∈ train/validation/test. Counts 32 / 6 / 6 (11/11/10 train per class; 2/2/2 val and test).
- Loaders with integrity checks already exist; reuse them read-only:
  - `lungcancer.features.load_features(path)`: shape, finiteness, embedding/coordinate alignment, coordinate fingerprint.
  - **(rev)** `lungcancer.modeling_run.verify_cache(record, directory, config, encoder_id)`: additionally checks preprocessing fingerprint, file_id/md5 identity, npz and coordinates file SHA256. It hashes `openslide.__library_version__`, so openslide-bin must be pinned to exactly 4.0.1.2 or every cache will be rejected.
  - `lungcancer.modeling.check_patient_separation` and `metric_report` for identical split checks and metric definitions.
- `sample.svs` md5 `a86f358f5325b6229035d19ed23440aa` = slide `a2e48dce-1874-468d-a302-fd30b3107f4a`, a **test** slide, label non_tumor. 10,904 grid tiles → 1,205 pass ≥50% tissue mask → 512 kept by farthest-point sampling (`preprocess.distributed_indices`, seed 215). 693 tissue tiles were never embedded.
- Tile geometry: **(rev)** level-0 footprint is **223×223 px** (`preprocessing.json` → `geometry.footprint_level0`), level-0 dimensions 26001×21138, MPP 0.5015. Always read the footprint from `preprocessing.json`; never assume 224.
- **(rev)** Thumbnail-to-tile mapping already exists in `backend/model.py:create_overlay` (thumbnail scale = thumbnail size / `dimensions_level0`, rectangles from `footprint_level0`). Copy that logic rather than reinventing it; do not import the backend.
- **(rev)** The backend refuses to start if torch is importable (`backend/model.py`, `CachedClassifier.__init__`). Torch must therefore never be added to the existing CPU or app images; the separate environment in this plan is required, not just tidy.
- Environments: CPU containers (`containers/cpu`, `backend`) pin numpy 2.1.3 / scikit-learn 1.6.1 / openslide-python 1.4.6 / openslide-bin 4.0.1.2 / Pillow 11.3.0 on python 3.13 with uv 0.12.21, but **no torch**. The Mac's system python is 3.9.6 with neither torch nor sklearn, so native work uses a uv-managed python 3.13.
- `.gitignore` already ignores `local_outputs/`, `*.npz`, `*.pt`, `*.joblib`, `*.svs`, `*.log`, `.venv/`.

## 2. Guardrails

- `AGENTS.md` currently says no refits / new real-data model experiments are authorized. Awassada approved this experiment on 6 Nov 2026; before running anything, record that approval following the repo convention (AGENTS.md section + dated `docs/checkpoints/` entry + `docs/COMMANDS.md`). No raw downloads are part of this plan. Do not change splits, preprocessing, cached files, the existing model bundle, or `local_outputs/app/`.
- All new code lives in a new isolated folder `experiments/attention_mil/` with its own environment. No edits to `lungcancer/`, `backend/` or `frontend/` in phases 0–6. The only shared-file edits are the additive Docker service/make targets in Phase 5 and the records in Phase 6.
- Model selection uses **train + validation only**. Test slides are evaluated **once**, at the end, inside Docker, with a frozen config; note that this test set was already used by the mean-pool model (no pristine-test claim). The final `sample.svs` heatmap is rendered only after the config and seed are frozen, and nothing seen in any heatmap (preview or final) feeds back into training choices.
- The heatmap is labelled "attention over a 512-tile sample of tissue; not a tumor segmentation". Unsampled tissue is drawn as blank/hatched, never as low attention.

## 3. Integrity checks (what is and isn't needed)

- **Needed, already built in:** `load_features` + `verify_cache` on every cached slide, plus one shared `encoder_identifier` and preprocessing config across all slides, and `check_patient_separation` on the split. These are the same checks `modeling.pooled_dataset` and the app use. They are automatic and cost milliseconds; they guarantee the new model sees exactly the data the existing model saw.
- **Not needed:** no download checksum step, because nothing is downloaded. Training never reads slide images.
- **One line before drawing any heatmap:** confirm `sample.svs` md5 equals `source_md5` in `slides/a2e48dce…/embeddings.json` (verified once on 6 Nov 2026), so tile squares land in the right place.

## 4. Environment strategy (decided)

Two stages sharing one `pyproject.toml` + `uv.lock`, so code and versions are identical:

1. **Develop natively with uv on the M1 (Phases 0–4).** Fast iteration, no image rebuilds, direct viewing of PNGs. Native results are **exploratory**: they are used to freeze the hyperparameters and the selection rule, and to preview the heatmap.
2. **Reproduce in a torch-CPU Docker service (Phase 5).** **(rev)** Docker is the only place where the **seed is chosen, the test set is evaluated, and the final heatmap is rendered**. Reason: macOS and linux-arm64 torch wheels use different math backends, so results can differ in the last decimals and two near-tied seeds could swap. Letting Docker apply the frozen rule removes that ambiguity. Native-vs-Docker differences are still measured and recorded.

### 4a. Docker feasibility on this Mac (verified 6 Nov 2026) **(rev)**

| Resource | Available | Needed |
|---|---|---|
| Architecture | Mac arm64, Docker aarch64 | linux/arm64 image |
| Docker memory | 8 GB | well under 1 GB (≈140 MB features + torch) |
| Docker CPUs | 14 | 1 thread for determinism |
| Free disk | ≈660 GB | ≈1–1.5 GB image |
| Docker version | 29.8.2 | any recent |

- No GPU: Docker on macOS cannot use the Apple GPU (no MPS in containers). Everything runs on CPU, which is fine at this size: expected a few minutes per seed, under ~30 min for all five seeds single-threaded.
- Network is needed only while building the image; train/test/heatmap services run with `network_mode: none`, like the existing CPU services.
- **CPU-only torch index (required).** Recent linux-arm64 torch packages on the default index can pull in large NVIDIA libraries that are useless on a Mac. Pin torch to PyTorch's CPU index in `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cpu" }
```

- **uv version alignment.** The host has uv 0.13.0; the existing images install uv 0.12.21. Either install the same uv version in the new image as the one that wrote `uv.lock`, or lock with the image's version, so `uv sync --frozen` reads the lock without surprises.

## 5. Phases

### Phase 0 — Records + native environment (≈30 min)
- **(rev) Records first, no code yet:** copy this plan to `docs/ATTENTION_PLAN.md`; add an AGENTS.md section recording the 6 Nov 2026 approval and its boundary (no downloads; splits, caches, bundle, existing model and app untouched); add a dated checkpoint under `docs/checkpoints/` and a `docs/COMMANDS.md` entry; commit with the UltraSpiral identity.
- `experiments/attention_mil/pyproject.toml` (uv, `package = false`): python 3.13, `torch` (exact version, CPU index per §4a), numpy 2.1.3, scikit-learn 1.6.1, openslide-python 1.4.6, openslide-bin 4.0.1.2, Pillow 11.3.0, matplotlib, pytest. Commit `uv.lock`.
- Make the repo importable read-only (`pythonpath` to repo root) to reuse `load_features`, `verify_cache`, `check_patient_separation`, `metric_report`.
- Smoke: `uv run python -c "import torch; print(torch.__version__)"`; load one slide through `load_features` and `verify_cache`.
- Scripts take all paths as CLI args (`--bundle`, `--slide`, `--out`) so the same commands work natively and inside the container.

### Phase 1 — Data module
- `data.py`: read `splits.json`, run `check_patient_separation`, return per-split lists of `(file_id, X[n,1536], coords[n,2], label_idx)` using the §3 checks.
- A training call can only request train and validation rows; requesting test rows outside the test command raises.
- Feature normalisation: per-dimension mean/std computed on **train tiles only**, saved with the model.

### Phase 2 — Model (gated ABMIL, Ilse et al. 2018)
```
h_i  = Dropout(ReLU(Linear(1536→256)(x_i)))
a_i  = w · ( tanh(V h_i) ⊙ sigmoid(U h_i) )      V,U: 256→128, w: 128→1
α    = softmax(a)  over tiles
z    = Σ α_i h_i
ŷ    = Linear(256→3)(Dropout(z))
```
- Return logits and α (one weight per tile). ~0.47 M params.
- Gated attention only (decided). No plain-attention variant or ablation is trained; the write-up cites Ilse et al. (2018) as the reason for the gated design.

### Phase 3 — Training (native, CPU, minutes)
- **(rev) Fixed hyperparameters, no grid:** hidden 256, attention 128, dropout 0.25. Reason: with 6 validation slides macro-F1 can only take a few discrete values, so a grid over hidden size / dropout cannot be told apart and only adds selection noise.
- Batch = 1 slide; AdamW lr 2e-4, weight decay 1e-4; class-balanced cross-entropy; ≤100 epochs.
- **(rev) Early stopping on validation loss** (continuous; patience 15), keeping the checkpoint with the lowest validation loss. Validation macro-F1 and balanced accuracy are reported at that checkpoint.
- Small-data regularisation: random tile subsampling per step (keep 50–100% of tiles), optional Gaussian feature noise. Decide on/off once, natively, then freeze.
- Determinism: `torch.manual_seed`, `torch.use_deterministic_algorithms(True)`, `torch.set_num_threads(1)`.
- 5 seeds (215–219). Report per-seed and mean ± sd of validation loss / macro-F1 / balanced accuracy, and attention stability (Spearman of α across seeds on each validation slide).
- Compare against the existing mean-pool LR on the same validation slides (macro-F1 0.667 from `model.json`).
- **Seed selection rule (fixed before training, applied in Docker):** highest validation macro-F1; ties broken by lowest validation loss, then by lowest seed number.
- **(rev)** Write `frozen_config.json` (hyperparameters, regularisation choices, selection rule, torch version, split sha256, encoder_identifier, preprocessing config) at the end of Phase 3. The chosen seed is **not** fixed natively; Docker applies the rule in Phase 5.

### Phase 4 — Heatmap preview + baseline (native)
- Preview heatmap for `a2e48dce…` (`sample.svs`, normal tissue) from the natively best seed, clearly marked "native preview, not reported":
  - md5 check from §3 first.
  - Thumbnail via OpenSlide `get_thumbnail` (≤2048 px); map tiles with the `create_overlay` logic (coords + 223 px footprint scaled by thumbnail / level-0 size).
  - **(rev) Colour by rank (percentile) of α**, not min-max. Softmax over 512 tiles leaves most tiles near 1/512 with a few spikes, so min-max would paint almost everything the lowest colour. The raw α values are kept unchanged in the JSON.
  - Figma ramp `#00F0FF → #0090FF → #1E46FF`, alpha ~0.55; thin grey outline on the 512 analysed tiles; unsampled tissue left uncoloured. Legend "Low → High attention (rank within slide)"; caption with predicted class + probabilities + "512 of 1,205 tissue tiles analysed".
- **(rev) Mandatory logistic-regression tile baseline** (no training): apply the existing saved LR to each tile vector (`predict_proba` per tile) and render the same way. It is the only evidence of whether attention shows something the existing model does not. Read-only use of `classifier.joblib`.
- **(rev) Optional, no extra training:** a seed-averaged α heatmap (mean rank over the 5 seeds), shown next to the single-seed map and labelled as averaged. The single-seed map remains the decided deliverable.
- Native test evaluation is **not** run.

### Phase 5 — Docker: seed selection, single test evaluation, final heatmap
- `containers/attention/Dockerfile`: same `PYTHON_IMAGE` base as `containers/cpu/Dockerfile`; install `libgomp1` and `libstdc++6` in the runtime stage; uv version aligned with the lock (§4a); `uv sync --frozen` from `experiments/attention_mil/uv.lock`; `linux/arm64`; runs as a non-root user; no HF credentials, no UNI2 weights.
- New `compose.attention.yml` (keeps `compose.cpu.yml` and `compose.app.yml` untouched): `network_mode: none`, `read_only: true`, tmpfs `/tmp`, `local_data/cpu_bundle` mounted **read-only**, `local_outputs/attention/` read-write, host UID/GID like the existing services.
- Make targets:
  - `attention-build`
  - `attention-train`: trains all 5 seeds with `frozen_config.json`, applies the selection rule, writes `seed_search.json` and the chosen `model.pt`.
  - `attention-test`: single test evaluation with `modeling.metric_report` → `test.json`; refuses if `test.json` already exists, like `modeling.evaluate`.
  - `attention-heatmap`: final `sample.svs` heatmap, attention JSON, top-5 tile crops, and the LR tile-baseline image.
  - `attention-unit`: runs the pytest suite in the container.
- Verify and record native-vs-Docker agreement: per-seed validation metrics, chosen seed, and max abs difference in α. Differences in the last decimals are expected; a different chosen seed or a different validation prediction is investigated and recorded before reporting.
- **(rev) Output layout** `local_outputs/attention/<UTC>/` (already git-ignored): `model.pt`, `normalization.npz`, `config.json`, `seed_search.json`, `validation.json`, `test.json`, `heatmap_a2e48dce.png`, `attention_a2e48dce.json` (`[{x,y,w,h,score,rank}]` in level-0 px, the shape of `tiles` in the frontend `InferenceResponse`), `lr_tiles_a2e48dce.png`, top-5 crops, run logs.

### Phase 6 — Records
- **(rev)** Commit only small evidence files: `experiments/attention_mil/RESULTS.md` plus copies of the metrics JSONs and heatmap PNGs under `docs/evidence/attention/2026-11-06/` with their SHA256. Model weights and npz stay in `local_outputs/attention/`.
- `RESULTS.md`: what ran (Docker numbers are authoritative), metrics vs mean-pool baseline with the 6-patient caveats, all-seed table + chosen seed, native-vs-Docker agreement, the attention heatmap next to the LR tile-baseline heatmap, limitations (§6).
- Repo checkpoint docs per AGENTS.md (`docs/checkpoints/`, `docs/CHECKPOINTS.md`, `docs/INDEX.md`, `docs/COMMANDS.md` with both native and `make` commands).
- Tests in `experiments/attention_mil/tests/`: shapes, α sums to 1, determinism with fixed seed, seed-selection rule, no test-split access during training, coordinate→thumbnail mapping with the 223 px footprint, rank normalisation. Runnable via `uv run pytest` and `make attention-unit`.

### Phase 7 — Later, separate approval (not in this plan's scope)
- **Tumor-slide heatmap (dropped for now, can be added without changing anything above).** `sample.svs` is normal tissue, so its heatmap shows where the model looked, not a tumor lighting up. For a tumor example, re-download one tumor test slide purely for display (e.g. `1d41c293-56aa-4adc-9425-7fa73ca1b1f4`, squamous, 120.7 MB, open access) via `lungcancer.download.download_slide` within the 10 GB raw budget (5,453,285,795 bytes used), verify its md5 matches the cached `source_md5` so tiles line up, and rerun `attention-heatmap` on it. Needs a fresh approval at that time.
- Backend: second model type in `backend/model.py` (currently hard-codes `vectors.mean(...)` and refuses to run with torch installed) and a `/jobs/{key}/heatmap` endpoint; `lungcancer/inference.py` rejects non-mean pooling and would need a branch. Preferred route: export the head to numpy weights (inference is a few matrix multiplies) so the backend stays torch-free.
- Frontend: populate `tiles` / `heatmapUrl` and enable the HeatmapLayer + legend slot already reserved in the MVP plan.
- GPU later: re-extract with higher/no tile cap for a dense heatmap; the trained head accepts any tile count.

## 6. Known limitations to state up front
- 32 training slides: attention maps may be unstable, and a single seed hides that variance in the picture (the seed table and optional averaged map show it). Validation/test have 2 patients per class (one error = 16.7 pts accuracy).
- The heatmap covers only the cached 512-tile sample, on a **normal-tissue** slide: it shows where the model looked, not a tumor region.
- Colours show attention rank within one slide, not absolute importance or probability.
- Attention ≠ localisation; no pathologist annotation exists to validate the map.
- Native and Docker results may differ in the last decimals; Docker numbers are the reported ones.

## 7. Execution order (rev)

1. Records first: plan copy, AGENTS.md approval section, checkpoint, COMMANDS entry, commit.
2. Phase 0: native uv env with CPU torch index; smoke tests.
3. Phases 1–2: data module, gated ABMIL, unit tests.
4. Phase 3 natively: 5 seeds with fixed hyperparameters; write `frozen_config.json`.
5. Phase 4 natively: heatmap preview, LR tile baseline, optional averaged map. Nothing here feeds back.
6. Phase 5 in Docker: build, train + seed selection, single test evaluation, final heatmap, native-vs-Docker comparison.
7. Phase 6: RESULTS.md, evidence copies, checkpoint docs, commit.

Estimated effort: about one working day; the torch image build is the slowest single step.

## 8. Decisions
Decided (6 Nov 2026):
- Environment: native uv for development, torch-CPU Docker service (`linux/arm64`) for the final reproducible run. Confirmed feasible on this Mac (§4a).
- Pooling: gated attention only; no plain-attention ablation.
- Heatmap model: single best seed by the fixed rule in Phase 3 (5 seeds still trained to report variance).
- Downloads: none. Heatmap on `sample.svs` only; tumor-slide heatmap moved to Phase 7 (later, separate approval).
- Integrity checks: reuse `load_features` + `verify_cache` (§3); no download checksum step.
- **(rev)** Hyperparameters fixed (hidden 256, dropout 0.25), no grid; early stopping on validation loss.
- **(rev)** Docker chooses the seed, runs the single test evaluation and renders the final heatmap; native runs are exploratory.
- **(rev)** LR tile-score baseline is mandatory; seed-averaged map is optional.
- **(rev)** Heatmap colours use within-slide rank of α; raw α kept in JSON.
- **(rev)** Outputs in `local_outputs/attention/`; only small evidence files are committed.
- **(rev)** torch from PyTorch's CPU-only index; uv version aligned between lock and image.

Open: none. Next step is execution order step 1 when Awassada says go.
