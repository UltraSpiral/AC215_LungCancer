# Checkpoint 28 — Clarify model serving, feature caching and MS2 scope

Date: 2026-10-20, America/New_York.

The user asked whether the prior fresh-UNI2 container gap meant training at
runtime and why feature caching would not be appropriate.

The earlier requirement interpretation was too strong: the supplied rubric
does not explicitly demand fresh UNI2 extraction on each run, and caching real
versioned features is a valid architecture. Updated MS2_READINESS.md with an
explicit correction; the original checkpoint-27 record is retained as history.

- Model parameters are learned once and saved. The current saved artifact is
  the training-only scaler and fitted logistic regression head.
- Feature vectors are data for specific inputs, computed by the frozen UNI2
  extractor in Colab and cached. They are distinct from model parameters.
- Current app: validate uploaded bytes → select the supported real cache →
  mean-pool embeddings → saved scaler/head → newly computed prediction.
  It performs no training and does not retrieve a canned prediction.
- Verified: this actual browser/container inference path, cache integrity,
  error handling and a separate real-SVS preprocessing smoke in Docker.
- Unverified: full raw-slide → fresh UNI2 features → prediction in containers,
  including an encoder path for an uncached input. Current app deliberately
  rejects unsupported inputs. The missing broader path does not invalidate
  the demonstrated cached-feature skeleton.

For MS2, explain the selected workflow and versioned upstream artifacts,
publish ingestion/preprocessing and real input/output evidence, and ensure
one-command instructions match the scope actually executed. App startup and
CPU verification are currently separate commands. The rubric's intended
pipeline breadth is a scope interpretation; no mandatory extra TF approval is
inferred solely from the use of cached features.

Updated status, index, commands and verification guidance. No code, input,
model, split, test result or running service changed. No tests, training,
encoder extraction, package installation or data/weight download was run.
The required persistence helper retains its genuine mounted-Drive guard; new
source and Markdown copies are verified locally, with receipts under
`artifacts/ms2_audit/2026-10-20-28/`. No new Drive mirror is claimed.
