# Checkpoint 24 — Recommended next step: working application interaction

This is a recommendation and source review, not execution authorization or a
claim that the new backend/containers already work. No dependencies, services,
slides, weights, training or model experiments were started.

Modeling and native M1 CPU verification are complete. The remaining immediate
application gap is real UI/backend interaction: frontend/README.md documents
the React HTTP adapter and POST /jobs / GET /jobs/{id}, but default mode is
mock. The reference server in frontend/tools/stub-model-server/server.py
returns filename-selected fixtures and does not run the saved classifier.

## Recommended bounded implementation

1. Add a real backend that loads the trusted checksum-verified saved classifier
   and verifies cached UNI2 embeddings, then mean-pools and computes named
   probabilities with the existing scaler/model. No model refitting or new
   test-metric evaluation is needed.
2. Use the real SVS already in the private CPU bundle as the demo input. Resolve
   it by file-content checksum, never by filename, diagnosis or class metadata.
   The checksum identifies an existing cache; it is not a prediction feature.
   The browser must clearly identify this as a preprocessed-slide demo.
   An unknown slide without a matching cache returns an explicit unsupported
   processing error and no prediction. Renaming identical file bytes must work.
3. Connect the existing frontend HTTP adapter to this service. Show the real
   model class, identifier, tile count and quality warnings. Any displayed
   probabilities remain explicitly uncalibrated. Use real cached coordinates
   if rendering analyzed tile locations, and keep the 16-tile preprocessing
   smoke separate from the frozen model's 512-tile embedding configuration.
4. Package frontend plus backend for native ARM64 using Docker Compose, with
   uv-managed Python dependencies, verified read-only model/cache inputs and
   a documented single startup command. Implement and document the actual
   command before offering it to the user; no app startup command exists yet.
5. On the M1, run frontend checks and an actual browser-to-API test: known
   real-slide success, arbitrary renamed filename consistency, and unknown
   input failure. Preserve logs, output JSON, image identities and screenshots.
   Tests must exercise the running app rather than just direct Python calls.

This would demonstrate a minimal application skeleton backed by genuine
model computation using previously extracted features. It does not verify
arbitrary SVS -> fresh UNI2 embeddings -> prediction inside containers.
That full workflow remains separately pending and needs an appropriate
execution host and resource plan; the existing native CPU image has no Torch
or UNI2 checkpoint. UI/HTTP-only or cached-feature evidence must not be
described as complete containerized ingestion/encoding/inference.

After the app interaction, close that full-pipeline container verification
gap or disclose it explicitly as incomplete, then assemble the MS2 README,
experiment narrative, environment screenshots, presentation and final SHA.
Keep the current model/splits frozen and do not expand the cohort for this step.

## Commands and scope

No manual command is needed now. Existing make cpu-check has already passed
and need not be repeated for this plan. App build/start/browser-test commands
will be recorded in docs/COMMANDS.md after implementation and actual execution.
Implementation and M1 app execution await the user's next instruction.

Reviewed frontend/README.md, package.json, the TypeScript prediction/job
contract, HTTP adapter, reference stub and current verification matrix.
Compose packaging reference:
https://docs.docker.com/compose/gettingstarted/

Persistent copy:
`/content/drive/MyDrive/LungCancer_AC215/docs/checkpoints/2026-10-20-24-next-app-step.md`.
