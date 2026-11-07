# Gated attention MIL on cached UNI2-h features

CPU-only experiment approved 2026-11-06. Plan and decisions:
[docs/ATTENTION_PLAN.md](../../docs/ATTENTION_PLAN.md).

This folder has its own environment (`pyproject.toml` + `uv.lock`) because the
experiment needs PyTorch, and the existing CPU and app images must stay
torch-free. The lock covers macOS arm64 (native development) and Linux arm64
(the Docker run) only, and takes torch from PyTorch's CPU-only index.

Scripts reuse the repository's own read-only checks (`lungcancer.features`,
`lungcancer.modeling_run.verify_cache`). Run them from the repository root so
`lungcancer` is importable, and pass every path on the command line:

```bash
uv sync --project experiments/attention_mil
uv run --project experiments/attention_mil python -m experiments.attention_mil.smoke --bundle local_data/cpu_bundle
```

Outputs belong in `local_outputs/attention/` (git-ignored), never in this folder.
