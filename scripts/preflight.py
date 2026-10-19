"""Inspect the actual processing environment without logging credentials.

Exit 2 indicates that a prerequisite is missing. No packages are installed,
credentials changed, or Drive mounts attempted by this command.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone

_vendor = Path(__file__).resolve().parents[1] / '.vendor'
if _vendor.is_dir():
    sys.path.insert(0, str(_vendor))


def inspect_environment(persistent_root: Path) -> dict:
    import torch
    from huggingface_hub import constants, get_token

    memory = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in {'MemTotal', 'MemAvailable'}:
            memory[key + '_bytes'] = int(value.strip().split()[0]) * 1024

    packages = {}
    for package in (
        'torch', 'torchvision', 'timm', 'huggingface-hub', 'openslide-python',
        'openslide-bin', 'numpy', 'pandas', 'scipy', 'scikit-learn',
        'Pillow', 'requests', 'pytest',
    ):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None

    credential_files = []
    for path in (Path(constants.HF_TOKEN_PATH), Path(constants.HF_STORED_TOKENS_PATH)):
        exists = path.is_file()
        mode = stat.S_IMODE(path.stat().st_mode) if exists else None
        credential_files.append({
            'path': str(path), 'exists': exists,
            'mode': oct(mode) if mode is not None else None,
            'private': (mode & 0o077) == 0 if mode is not None else None,
        })

    cuda_available = torch.cuda.is_available()
    gpus = []
    if cuda_available:
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            gpus.append({'index': index, 'name': props.name,
                         'total_memory_bytes': props.total_memory})

    drive_mount = Path('/content/drive')
    drive_ready = drive_mount.is_mount() and (drive_mount / 'MyDrive').is_dir()
    cached_authentication = bool(get_token())
    blockers = []
    if not cuda_available:
        blockers.append('cuda_unavailable_in_this_process')
    if not drive_ready:
        blockers.append('google_drive_not_mounted')
    elif not persistent_root.is_dir():
        blockers.append('persistent_project_directory_missing')
    if not cached_authentication:
        blockers.append('huggingface_authentication_missing')
    if any(item['private'] is False for item in credential_files):
        blockers.append('huggingface_credential_file_permissions_not_private')

    disk = shutil.disk_usage('/content/LungCancer')
    return {
        'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'blocked' if blockers else 'ready',
        'blockers': blockers,
        'python': sys.version,
        'platform': platform.platform(),
        'packages': packages,
        'compiled_cuda': torch.version.cuda,
        'cuda_available': cuda_available,
        'gpus': gpus,
        'system_memory': memory,
        'workspace_disk_bytes': {'total': disk.total, 'used': disk.used, 'free': disk.free},
        'drive_mounted': drive_ready,
        'persistent_root': str(persistent_root),
        'persistent_root_exists': persistent_root.is_dir(),
        'huggingface_credential_available': cached_authentication,
        'credential_files': credential_files,
        'uni2_checkpoint_downloaded_or_loaded_by_this_check': False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--persistent-root', type=Path,
                        default=Path('/content/drive/MyDrive/LungCancer_AC215'))
    parser.add_argument('--output', type=Path, default=Path('artifacts/environment.json'))
    args = parser.parse_args()
    report = inspect_environment(args.persistent_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=args.output.parent,
                                     prefix='.environment-', delete=False) as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
        temporary = Path(handle.name)
    os.replace(temporary, args.output)
    print(json.dumps(report, indent=2))
    return 2 if report['blockers'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
