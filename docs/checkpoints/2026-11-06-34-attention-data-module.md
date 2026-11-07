# Checkpoint 34 — Attention experiment Phase 1: data module

Date: 2026-11-06, America/New_York. Branch: `attention-mil`.
Plan: [ATTENTION_PLAN.md](../ATTENTION_PLAN.md), Phase 1.

## Implemented

`experiments/attention_mil/data.py`:

- `bundle_identity(bundle)`: requires `splits.json` to match the saved model's
  `split_file_sha256` and `split_identifier` byte for byte, and checks patient
  separation. Returns the encoder and preprocessing identities every slide must share.
- `load_split(bundle, name, allow_test=False)`: verified slides of one split.
  Each slide passes `verify_cache` (file hashes, md5/file_id, preprocessing and
  encoder fingerprints) and `load_features`. Returns raw float32 features,
  level-0 coordinates, the slide's tile footprint and dimensions.
  Asking for `test` raises `LockedTestSplit` unless `allow_test=True`; only the
  Phase 5 single test evaluation will pass that flag.
- `Normalizer`: per-dimension mean/std over all training tiles. `fit` refuses
  any slide set other than exactly the 32 training slides. Standard deviations
  are floored at 1e-6. Saved/loaded as npz with the model.

`experiments/attention_mil/tests/`: `conftest.py` provides the real bundle
(`ATTN_BUNDLE` overrides the path for Docker); `test_data.py` has six tests.
`pyproject.toml` gained a pytest section putting the repository root on the
import path.

## Actually executed and verified

```bash
uv run --project experiments/attention_mil pytest experiments/attention_mil -v
```

Six passed: 32/6 slides with the expected per-class counts, no shared
patient or slide between train and validation, test split locked, a modified
split file rejected, normaliser fitted on training tiles only (mean 0, std 1
within 1e-3) and an npz round trip with a constant dimension.

Mutation check: replacing the lock with `pass` made exactly the lock test fail
(`DID NOT RAISE LockedTestSplit`); restoring the file returned 6 passed.

Observed: per-dimension std of raw UNI2-h features ranges about 0.06 to 0.58
on the sample slide, which is why features are standardised.

## Not changed

No training or evaluation. Bundle, splits, caches, saved model, `lungcancer/`,
`backend/`, `frontend/` untouched. Drive persistence not run (no mounted Drive).
