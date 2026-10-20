# Reviewer and teammate setup

Use a new checkout to reproduce the prepared-feature demo. Preserve the
existing Mac checkout, restored inputs and evidence. Read
[PIPELINE_SCOPE.md](PIPELINE_SCOPE.md) for stage environments and outputs.

## Existing input artifact and access

The protected [CPU input archive on Drive](https://drive.google.com/file/d/1WWVdbGjaL27ckhA7mtr3y5x8j06Hw01i/view?usp=drivesdk)
is `cpu-verification-20261020T0220Z-audit2.tar.gz`. Obtain this existing snapshot
using an account with permission. It is not an instruction to acquire additional
GDC slides or UNI2 weights.

On 2026-10-20, connected Drive metadata confirmed the exact file, its size,
owner access and explicit access for one existing team collaborator. The
saved checksum sidecar agrees with the identity below. This is an access-
metadata check, not a claim that every teammate or the TF opened the file.
Sharing permissions were not changed. If your account is denied, request
access from the project owner before running; GitHub access alone is insufficient.

| Property | Expected value |
|---|---|
| Archive bytes | `186505459` |
| Archive SHA256 | `c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988` |
| Restored files | 187: manifest plus 186 checksum-listed entries |
| Data snapshot | `f9491fe4d35f30267df95d26c61d6bb325908694e6df7d746a6acb9826eddb24` |

The Mac copy was renamed `CPU Verification Audit Oct 20 2026.tar.gz`. Either
name works when its checksum matches. Contents include the real head, 44
caches and one retained raw slide; weights and credentials are excluded. Keep
the archive/binaries outside Git and container image layers.

## Host prerequisites

- Apple Silicon Mac, Docker Desktop running Linux ARM64 containers.
- Docker Compose v2 with `up --wait`. Recorded host: Docker 28.0.4 and Compose
  v2.34.0-desktop.1; Intel/Windows runtime behavior is not verified.
- Git, Make, Python 3.11+. Host npm, uv, Torch and HF login are unnecessary for
  the basic replay. Python environments are locked in containers; frontend npm
  dependencies build inside Docker.
- Network for Git/authorized artifact access and initial public image/package
  builds. The CPU preprocessing runtime is offline.

## Fresh clone, verify and restore

From a directory where `LungCancer-ms2-review` does not already exist:

```bash
git clone --branch milestone2 https://github.com/UltraSpiral/LungCancer.git LungCancer-ms2-review
cd LungCancer-ms2-review
git rev-parse HEAD
python3 scripts/unpack_cpu_bundle.py \
  --archive "$HOME/Downloads/cpu-verification-20261020T0220Z-audit2.tar.gz" \
  --sha256 c7681d5965a9fb318f07c87f109d77ee740b12a323e500734e522c01d16ee988 \
  --destination local_data/cpu_bundle --apply
make ms2-demo
```

Adjust the archive path if using its renamed Mac filename. The helper verifies
SHA256 before extraction and refuses an existing destination. Skip restoration
on the already-restored project Mac. Do not substitute slides/features or the
illustrative filename-based stub.

Open **http://127.0.0.1:8080/**, choose
`local_data/cpu_bundle/sample/sample.svs` and click **Analyse slide**.
Expected: `non_tumor`, 512 cached tiles, model ID `42af9fb3...` and the actual
location overlay. The separate smoke has 16 new tiles; they are not model
inputs. Unsupported content returns no prediction. See
[saved outputs](PIPELINE_SCOPE.md#buildstart-and-outputs).

Runtime commands, from the same checkout and shell:

```bash
make app-stop
make app-resume
make app-logs
make app-down
```

`app-down` removes this project's containers/networks and preserves bind-mounted
inputs/evidence. HTTP job lookup is per API session: upload again after restart.

## Parallel run with an existing app

Before starting, in the new checkout's shell:

```bash
export COMPOSE_PROJECT_NAME=lungcancer-ms2-review
export LC_APP_PORT=18080
export LC_APP_API_IMAGE=lungcancer-review-api:milestone2
export LC_APP_WEB_IMAGE=lungcancer-review-web:milestone2
export LC_CPU_IMAGE=lungcancer-review-cpu:milestone2
make ms2-demo
```

Use an unused project/port/image prefix if these are already occupied. Open
**http://127.0.0.1:18080/**. The project name isolates containers/networks, the
port avoids the 8080 app, and image overrides preserve the original tags.
Default input/output paths resolve inside the new checkout. Use this same
shell/environment for stop/resume/down; reapply exports after closing the shell.

Separate app/CPU Compose files may make the CPU one-off report the project's
app services as orphans. Do not use `--remove-orphans`: those are the live app.

## Reproduction record

Original app/replay evidence is [indexed here](evidence/ms2/2026-10-20/README.md).
An additional isolated checkout/restore/start is being executed for checkpoint
32; this preliminary instruction record does not yet claim that new success.
The final checkpoint will identify the exact source commit, archive checksum,
187-file restore, image identities, HTTP/browser result and original-app
preservation.

This is an isolated setup on the owner's existing M1/Docker installation.
Docker layer caches may be reused. It does not establish a second machine,
a fresh Docker installation or a teammate independently running the commands.
Browser verification uses a separate test client; basic startup needs no
host browser-automation installation.
