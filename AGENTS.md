# Current native M1 cached-feature app — checkpoint 26

The bounded app task is complete: native ARM64 Compose frontend/API, real saved
classifier over content-matched cached features, actual browser proof and error
checks. Read docs/LOCAL_APP.md and checkpoint 26 for current commands/evidence.
Preserve local_data/cpu_bundle/, local_outputs/cpu/ and local_outputs/app/.
Full fresh-UNI2 container verification remains pending; no further raw downloads,
weights, refits, split/preprocessing changes, metric reruns or profiling are
authorized. Earlier pending-app statements below are historical handoff context.

# Historical local Mac application handoff — checkpoint 25

The user requested persisted/pushed context for local Codex. Read
docs/MAC_CODEX_HANDOFF.md first for the next bounded task: native M1 UI/backend
interaction using the real saved classifier and verified cached UNI2 embeddings.
The Colab handoff task does not implement the app. The successor local session
should execute the provided task when the user invokes it. CPU Docker checks are
already complete; no new slides, UNI2 weights, real training, split changes,
test-metric reruns or profiling are authorized. Full raw-slide-to-UNI2 container
verification remains separate. Preserve the existing Mac evidence and approvals.

# Native M1 CPU verification completed — checkpoint 21

On 2026-10-20, actual `make cpu-check` passed in `linux/arm64` Docker on Apple
M1: 29 tests, 44 real caches / 22,483 vectors, 12 frozen reference predictions
and the real 16-tile preprocessing smoke. Pipeline code, locks, saved model and
splits were unchanged. Read docs/checkpoints/2026-10-20-21-native-arm64.md for
image identity, logs, screenshot/persistence status and remaining scope.
Earlier pending-Mac statements below are historical. Full slide-to-prediction
container verification and UI/backend interaction remain pending separately.
No additional downloads, real training or optional profiling are authorized.

# Persistent checkpoint records

The user requested durable Markdown records of every checkpoint summary and all
commands they need to copy. Maintain these records as work proceeds:

- Update `docs/INDEX.md`, append the checkpoint history in `docs/CHECKPOINTS.md`,
  and save a dated summary under `docs/checkpoints/` before a checkpoint response.
- Keep notebook and terminal commands in `docs/COMMANDS.md`, identifying commands
  needed now, previously executed commands, and future stages awaiting review.
- Record what was implemented, actually executed, verified, and still pending.
  Preserve historical summaries; annotate factual corrections explicitly.
- Run `python scripts/persist_records.py` to back up code and copy all Markdown
  records to `/content/drive/MyDrive/LungCancer_AC215/docs/`, with SHA256 verification.
  This may require approved execution for mounted Drive. Do not change security controls.
- Report clickable persistent Markdown paths to the user. Do not rely on terminal
  scrollback. Never include secret values in documents, commands, logs, or backups.

Current work is paused at the user's pilot-review checkpoint. No additional slide
downloads or real-data training are authorized by the documentation request.
Follow subsequent explicit user instructions when this scope changes.

# Latest execution order and training approval

The user prefers the real modeling baseline first, then the MLOps/container/app
work. Their sequencing message explicitly withheld training approval. Do not
start real training until the user unambiguously approves the chosen run. No
exact phrase is required, and do not re-request approval after it is granted.
Existing acquisition/experiment pauses remain until an explicit instruction
changes them. See docs/checkpoints/2026-10-20-14-execution-order.md. HF setup is
already verified; do not request it again without evidence it has been lost.


## Authorized modeling run — 2026-10-20 checkpoint 15

User explicitly approved: go ahead and start. This authorizes the proposed 45-slide, 45-patient cohort (15/class), necessary OpenSlide/pinned-UNI2 setup, 36 additional downloads within the unchanged cumulative 10,000,000,000-byte raw budget, real baseline fitting, fixed patient-level validation/test evaluation, and renamed held-out inference. All nine pilot patients remain in training. Modeling precedes MLOps; profiling remains deferred. Prior pause/pending-auth statements above are historical.

Run directory: `artifacts/modeling/20261020T0220Z/`; persistent counterpart: `/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z/`. A100 80GB and HF cached login verified; pinned OpenSlide wheels installed without replacing PyTorch/CUDA. Frozen UNI2 float32, 512 tiles, physical-scale config and pilot cache identities are preserved. No performance result is claimed at launch.


# Current task boundary — after completed modeling and Mac CPU preparation

User approved and completed real modeling; one ambiguous portion-link slide was
excluded conservatively, leaving 44 eligible patients. The corrected audit2
model is current. Do not rerun the provisional 45-slide training command.
User explicitly authorized Apple Silicon CPU containers, cached-embedding checks,
and a small real-slide preprocessing test; they will use Codex on their M1 to
execute/debug Docker. These offline checks are authorized. Full slide-to-prediction
container verification must be tracked separately. Additional raw downloads,
new real-data model experiments and optional profiling still require a new request.
Read docs/CPU_CONTAINER_VERIFICATION.md and docs/VERIFICATION_MATRIX.md first.
No HF credentials or UNI2 weights belong in the CPU image or portable bundle.
The Colab Drive persistence helper requires a genuine mounted Drive; on the Mac,
record real local/Drive Desktop persistence explicitly without faking that mount.

# User-selected Git identity

The user explicitly selected UltraSpiral <UltraSpiral@users.noreply.github.com>
for project commits. Use this identity; do not substitute a Codex author.
Authentication must use the user's supported GitHub login. Never ask them to
paste a token into chat or include credentials in code, documents, or remotes.
