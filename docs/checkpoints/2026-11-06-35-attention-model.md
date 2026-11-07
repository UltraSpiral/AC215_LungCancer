# Checkpoint 35 — Attention experiment Phase 2: gated attention model

Date: 2026-11-06, America/New_York. Branch: `attention-mil`.
Plan: [ATTENTION_PLAN.md](../ATTENTION_PLAN.md), Phase 2.

## Implemented

`experiments/attention_mil/model.py`: `GatedAttentionMIL` (Ilse et al. 2018).
One slide in (`[n_tiles, 1536]`), class logits `[3]` and attention `alpha [n_tiles]`
out. Tile embedding 1536→256 (ReLU, dropout 0.25); gated attention
`w · (tanh(V h) ⊙ sigmoid(U h))` with V, U 256→128 and w 128→1 without bias
(softmax ignores a shared constant); softmax over tiles; weighted sum; dropout;
256→3 classifier. `build_model(config, seed)` seeds torch before creating the
weights. 460,163 parameters, of which 393,472 are in the first layer.
The plan's estimate of ~0.47 M is corrected to 0.46 M.

`experiments/attention_mil/tests/test_model.py`: 14 test cases.

## Actually executed and verified

```bash
uv run --project experiments/attention_mil pytest experiments/attention_mil -v
```

20 passed (6 data + 14 model): output shapes for 1, 467 and 512 tiles; alpha
non-negative and summing to 1; malformed input rejected; parameter count;
tile-order invariance; equal attention scores reduce exactly to mean pooling
(the existing model's pooling); seeded initialisation reproducible; dropout
only in training mode; gradients reach every parameter; an untrained model
runs on a real normalised validation slide.

Synthetic attention test: bags of 47 noise tiles plus 3 class-marker tiles,
150 Adam steps. 30/30 correct. Marker tiles received min 0.34 / mean 0.55 of
the attention against 0.06 for uniform attention. The first threshold
(min > 0.5) failed; 300 and 600 steps gave the same values, because the loss
stops pushing attention to sharpen once bags are classified correctly. The
threshold was restated as more than 5× uniform (0.30) after this observation.

Mutation check: forcing uniform attention made the synthetic test and the
gradient test fail; restoring the file returned 20 passed.

## Not changed

No training on real labels, no evaluation. Bundle, splits, caches, saved
model, `lungcancer/`, `backend/`, `frontend/` untouched.
