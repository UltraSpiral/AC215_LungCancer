# Checkpoint 39 — Attention heatmap wired into the app

Date: 2026-11-06, America/New_York. Branch: `attention-mil`.
Scope change approved by Awassada ("wire it with the front end so I can try the
sample.svs upload to see the heatmap"); recorded at the top of `AGENTS.md`.
This is plan Phase 7 (backend + frontend items). The tumor-slide download and a
zoomable heatmap layer remain out of scope.

## Implemented

- `experiments/attention_mil/export_for_app.py`: exports the authoritative Docker
  run's chosen seed (215) to torch-free `attention_head.npz` + `manifest.json` in a
  dedicated folder, `local_outputs/attention_app/` (not inside a run directory, so
  a Docker bind mount can never pre-create a run folder and block `attention-train`).
  Refuses non-authoritative runs, a changed `model.pt`, an existing output, or a
  numpy/torch mismatch above 1e-5.
- `backend/attention.py`: numpy float64 gated attention head (same math as the torch
  model), checksum-verified loading, rank colouring with the frontend tokens
  `--color-heatmap-low/mid/high` (`#1e46ff → #0090ff → #00f0ff`), top 10% outlined white.
  Note: the experiment figures used the reverse ramp (cyan low); the app follows the
  Figma tokens.
- `backend/app.py`: fail-soft `AttentionView` loaded at startup from `LC_APP_ATTENTION`
  (default `/attention`). Successful jobs gain `result.attention` (prediction,
  probabilities, agreement with the default model, heatmap URL, disclaimer); new
  `GET /jobs/{key}/heatmap`; `/health` reports `attention_available` and the reason.
  The default prediction path is unchanged; attention is attached only after the
  existing model has verified the upload.
- `compose.app.yml`: read-only mount `${LC_APP_ATTENTION:-./local_outputs/attention_app}:/attention`
  for `api` and `app-tests`. No new backend dependencies; the image stays torch-free.
- Frontend: `AttentionResult` type and a validator that drops a malformed block
  without affecting the default prediction; viewer shows the heatmap with a
  token-coloured legend when the switch is on; new `AttentionBlock` panel section
  (experimental label, agreement line, switch, caveat); switch state in `ReviewPage`.
- `backend/tests/test_attention.py`: 6 tests; `docs/LOCAL_APP.md` section.

## Actually executed and verified

```bash
uv run --project experiments/attention_mil python -m experiments.attention_mil.export_for_app \
  --bundle local_data/cpu_bundle --run local_outputs/attention/docker --out local_outputs/attention_app
LC_APP_OUTPUT=./local_outputs/attention/app_jobs make app-test     # 20 passed, 0 skipped
(cd frontend && npm run check)                                      # typecheck, lint, build passed
LC_APP_OUTPUT=./local_outputs/attention/app_jobs make app-up
```

The export was first written to `local_outputs/attention/docker/app_export` and
moved to `local_outputs/attention_app/` before the app used it; checksum re-verified.

| Check | Result |
|---|---|
| numpy vs torch, 39 slides (38 train/validation + sample.svs) | max prob diff 1.3e-07, max alpha diff 4.7e-08 |
| Export identity (`attention_head.npz` SHA256) | `e9951bf0784c85ae78cff3b94da78e061b7426d8fd1a6054150f555e017ba041` |
| Backend tests in the app test container | 20 passed (14 existing + 6 new), real-export test ran |
| `/api/health` | `attention_available: true` |
| `sample.svs` upload via `/api/jobs` | default non_tumor 0.951 (unchanged); attention non_tumor, agrees; heatmap JPEG 204,183 bytes |
| Unknown `.svs` | `failed`, `unsupported_slide`, no result; heatmap 404 |
| Real Chromium upload through the page | result + heatmap + legend shown; switch returns the original overlay; 0 page/console errors |

Verification runs wrote job files to `local_outputs/attention/app_jobs/`;
`local_outputs/app/jobs/` was checked byte-for-byte unchanged. Screenshots and the
browser script are in `local_outputs/attention/app_check/`
(`browser_heatmap_on.png` `71e10d50…`, `browser_heatmap_off.png` `ada558cc…`).
Not executed: a full app restart without the export mounted (covered by the
missing-export unit test and the fail-soft path exercised by the 14 existing tests).

## Not changed

`lungcancer/`, splits, caches, the saved logistic bundle, `local_outputs/app/`. No
downloads, retraining or test evaluation. The app's default prediction and identifiers
are unchanged.
