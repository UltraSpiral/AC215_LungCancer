# Checkpoint 37 — Attention experiment Phase 4: heatmap preview and baseline

Date: 2026-11-06, America/New_York. Branch: `attention-mil`.
Plan: [ATTENTION_PLAN.md](../ATTENTION_PLAN.md), Phase 4. This is a **native
preview, not a reported result**; the final heatmap is rendered by Docker in Phase 5.

## Implemented

- `data.py`: per-row loading factored into `_load_row`; new
  `load_slide(bundle, file_id, allow_test=False)` returns one verified slide and its
  split. The test lock still applies: a test slide needs `allow_test=True`.
- `heatmap.py`: verifies the SVS md5 against the cache's `source_md5`; scores the
  slide's cached tiles with a trained seed (default: `chosen_seed`, else
  `native_preferred_seed`); colours tiles by **within-slide rank** of alpha on an
  OpenSlide thumbnail (≤2048 px) with the plan's ramp `#00F0FF → #0090FF → #1E46FF`
  at 0.55 opacity and thin grey outlines; unsampled tissue stays uncoloured.
  Tile mapping is the same as `backend/model.py:create_overlay`.
  Also renders the **mandatory logistic-regression tile baseline**: the saved model
  applied to each tile; score = per-tile probability of the class it predicts for
  the whole slide, also rank-coloured. Optional seed-averaged map: mean rank over
  the five seeds. Writes `heatmap_<id>.png` (thumbnail | attention | baseline),
  `seed_average_<id>.png`, both overlays, `attention_<id>.json`
  (`[{x,y,w,h,score,rank}]`, level-0 px, raw alpha as score), top-5 tile crops
  and `summary.json`. Refuses to overwrite.
- `tests/test_heatmap.py`: 6 tests (rank order and why min-max is not used, ties,
  ramp colours, tile mapping identical to the backend, wrong SVS rejected,
  single-slide loading keeps the test lock).

## Actually executed and verified

```bash
uv run --project experiments/attention_mil pytest experiments/attention_mil -q   # 31 passed
uv run --project experiments/attention_mil python -m experiments.attention_mil.heatmap \
  --bundle local_data/cpu_bundle --run local_outputs/attention/native-20261107T0037Z \
  --svs local_data/cpu_bundle/sample/sample.svs \
  --file-id a2e48dce-1874-468d-a302-fd30b3107f4a --stage "Native preview, not reported"
```

Rendered three times: the first two figures had a large empty band above the
panels; the layout was changed to matplotlib constrained layout sized to the
slide's aspect. The earlier preview directories (my own outputs, minutes old)
were deleted before re-rendering. Sources: `heatmap.py`
`7a0e31db25e8db09b621c5845393b6626b105165555dd24301bee3a19ed1f83e`, `data.py`
`a3bd6a09a4737d54e204c8f7b2ee05d164a1cbdefdf72830b5d8f4089599ae1e`. ~3 s per render.

### Preview observations (`sample.svs`, test slide, true class non_tumor)

| Quantity | Value |
|---|---|
| SVS md5 | `a86f358f5325b6229035d19ed23440aa` (matches cache) |
| Attention seed 215 prediction | non_tumor 0.997 |
| Existing model prediction | non_tumor 0.951 |
| Max alpha / uniform alpha | 0.0107 / 0.00195 (5.5×) |
| Share of attention in top 10 tiles | 0.073 (uniform: 0.020) |
| Spearman, attention vs logistic tile score | 0.70 |
| Spearman, seed 215 vs seeds 216–219 | 0.93, 0.90, 0.94, 0.93 |

- Every tile square lands on tissue, none on background: the coordinate mapping holds.
- Attention on this normal slide is diffuse; no small region dominates.
- Attention ranks agree substantially with the existing model's per-tile scores
  (0.70), so on this slide attention adds limited new spatial information.
- The top-5 crops show thin alveolar walls, open airspaces and scattered cells,
  some with brown pigment. This is a visual description only, not a pathology read.
- The seed-averaged map is visually close to the single-seed map, consistent with
  the 0.90–0.94 seed agreement.

Nothing seen here changes the frozen configuration or the seed rule.

## Outputs (git-ignored)

`local_outputs/attention/native-20261107T0037Z/heatmap_a2e48dce/` (12 files, 8.6 MB).

## Not changed

No test evaluation was run. Bundle, splits, caches, saved model, `lungcancer/`,
`backend/`, `frontend/` untouched.
