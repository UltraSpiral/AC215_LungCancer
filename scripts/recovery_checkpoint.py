"""Offline recovery snapshots and checksum verification; never runs ML/acquisition.

Only an explicitly mounted Drive is accepted as a persistence destination.
Source archives include original project documents, but exclude machine state,
credentials, public raw slides, derived artifacts, and gated weights.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DRIVE = Path('/content/drive/MyDrive/LungCancer_AC215')
sys.path.insert(0, str(ROOT))
from lungcancer.common import atomic_json, checksum, persist_file, persistent_ready


def command(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return {'argv': args, 'returncode': p.returncode,
            'stdout': p.stdout.strip(), 'stderr': p.stderr.strip()}


def capture_environment(output):
    sys.path.insert(0, str(ROOT / '.vendor'))
    from preflight import inspect_environment
    packages = sorted({(d.metadata['Name'], d.version)
                       for d in importlib.metadata.distributions()
                       if d.metadata['Name']})
    report = inspect_environment(DRIVE)
    report['all_installed_packages'] = [dict(name=n, version=v) for n, v in packages]
    report['tools'] = [command(c) for c in [
        ['codex', '--version'], ['node', '--version'], ['npm', '--version'],
        ['git', '--version'], ['python', '-m', 'pip', '--version'],
        ['nvidia-smi', '--query-gpu=name,memory.total,memory.used,driver_version',
         '--format=csv,noheader'],
    ]]
    p = command(['dpkg-query', '-W', '-f=${Package}\t${Version}\n'])
    terms = ('cuda', 'nvidia', 'openslide', 'libjpeg', 'libpng', 'libtiff',
             'libglib', 'libcairo', 'libstdc++', 'python3', 'gcc', 'git', 'libc6')
    report['relevant_system_packages'] = [s for s in p['stdout'].splitlines()
                                           if any(t in s.split('\t')[0] for t in terms)]
    report['processes'] = command(['ps', '-eo', 'pid,ppid,stat,etime,comm'])
    report['credential_contents_or_environment_dump_saved'] = False
    output.mkdir(parents=True, exist_ok=True)
    atomic_json(output / 'installed_environment.json', report)
    (output / 'installed_packages.txt').write_text(
        '# Inventory only; do not replace Colab PyTorch/CUDA wholesale.\n' +
        ''.join(f'{n}=={v}\n' for n, v in packages))
    print(f'Captured {len(packages)} installed distributions; no credential values.')


EXCLUDED_DIRS = {'.git', '.codex', '.agents', '.aws', '.vendor', '.venv',
                 '__pycache__', '.pytest_cache', '.ipynb_checkpoints', 'artifacts',
                 'raw', 'data', '.recovery', 'private_codex_recovery'}
EXCLUDED_SUFFIXES = {'.svs', '.pt', '.pth', '.bin', '.safetensors', '.npz',
                     '.joblib', '.sqlite', '.jsonl', '.log', '.bundle', '.pyc'}


def source_files():
    included, excluded = [], []
    for directory, dirs, names in os.walk(ROOT, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS
                         and not d.endswith('.egg-info')
                         and not (Path(directory) / d).is_symlink())
        for name in sorted(names):
            path = Path(directory) / name
            lower = name.lower()
            if (path.is_symlink() or path.suffix.lower() in EXCLUDED_SUFFIXES
                    or any(s in lower for s in ('token', 'credential', 'auth.json'))
                    or lower.startswith('.env') or lower.endswith(('.tar.gz', '.partial'))
                    or '.sqlite' in lower):
                excluded.append(str(path.relative_to(ROOT)))
            elif path.is_file():
                included.append(path)
    return included, excluded


def verify_archive(path, expected=None):
    result = []
    with tarfile.open(path, 'r:gz') as archive:
        for item in archive.getmembers():
            if not item.isfile() or Path(item.name).is_absolute() or '..' in Path(item.name).parts:
                raise RuntimeError(f'Unsafe archive member: {item.name}')
            digest = hashlib.sha256(archive.extractfile(item).read()).hexdigest()
            if expected is not None and digest != expected[item.name]:
                raise RuntimeError(f'Archive member mismatch: {item.name}')
            result.append({'path': item.name, 'bytes': item.size, 'sha256': digest})
    return result


def snapshot(destination, archive_name):
    persistent_ready()
    if destination.parent.resolve() != (DRIVE / 'recovery').resolve():
        raise ValueError('Use a timestamped directory directly under Drive/recovery.')
    destination.mkdir(parents=True, exist_ok=True)
    receipts = []
    for source in sorted((ROOT / 'artifacts').rglob('*')):
        if source.is_file() and not source.is_symlink():
            if source.name.endswith('.partial') or source.name.startswith('.writing-'):
                raise RuntimeError(f'Unfinished write needs review: {source.name}')
            relative = Path('artifacts') / source.relative_to(ROOT / 'artifacts')
            target = destination / relative
            if target.exists():
                if checksum(target) != checksum(source):
                    raise RuntimeError(f'Existing snapshot differs: {relative}')
                receipts.append({'path': str(relative), 'bytes': source.stat().st_size,
                                 'sha256': checksum(source)})
            else:
                receipt = persist_file(source, target.relative_to(DRIVE))
                receipts.append({**receipt, 'path': str(relative)})
    files, excluded = source_files()
    hashes = {str(p.relative_to(ROOT)): checksum(p) for p in files}
    local = Path('/tmp') / archive_name
    target = destination / archive_name
    if target.exists():
        raise FileExistsError('Choose a new archive name; existing backups are preserved.')
    with tarfile.open(local, 'w:gz') as archive:
        for p in files:
            archive.add(p, arcname=str(p.relative_to(ROOT)), recursive=False)
    entries = verify_archive(local, hashes)
    persist_file(local, target.relative_to(DRIVE))
    verify_archive(target, hashes)
    atomic_json(destination / (archive_name + '.members.json'), {
        'members': entries, 'excluded_source_files': excluded,
        'archive_sha256': checksum(target),
    })
    atomic_json(destination / 'artifact_copy_receipts.json', receipts)
    selection = json.loads((ROOT / 'artifacts/pilot_selection.json').read_text())
    atomic_json(destination / 'raw_file_policy.json', {
        'retained_raw_files': [],
        'omitted_public_files': selection['slides'],
        'reason': 'Temporary raw SVS already deleted after verified derived-output persistence.',
        'gated_encoder_weights_included': False,
        'encoder_revision': 'd517a8dd47902dd7c308b3c36f63bce47e7b9a43',
        'raw_downloads_started_by_checkpoint': False,
    })
    print(json.dumps({'destination': str(destination), 'artifact_files_verified': len(receipts),
                      'source_files_archived_and_verified': len(entries), 'archive': str(target)}))


def verify_tree(destination):
    excluded = {'SHA256SUMS', 'inventory.json'}
    entries = []
    for p in sorted(destination.rglob('*')):
        if p.is_file() and p.name not in excluded:
            if p.name.endswith('.partial'):
                raise RuntimeError('Unfinished persistent write')
            if p.name.endswith('.tar.gz'):
                verify_archive(p)
            entries.append({'path': str(p.relative_to(destination)),
                            'bytes': p.stat().st_size, 'sha256': checksum(p)})
    inventory = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
                 'root': str(destination), 'file_count': len(entries),
                 'total_bytes': sum(e['bytes'] for e in entries), 'files': entries}
    atomic_json(destination / 'inventory.json', inventory)
    (destination / 'SHA256SUMS').write_text(''.join(
        f'{e["sha256"]}  {e["path"]}\n' for e in entries) +
        f'{checksum(destination / "inventory.json")}  inventory.json\n')
    for entry in entries:
        if checksum(destination / entry['path']) != entry['sha256']:
            raise RuntimeError(f'Read-back mismatch: {entry["path"]}')
    print(json.dumps({k: v for k, v in inventory.items() if k != 'files'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    env = sub.add_parser('environment'); env.add_argument('--output', type=Path,
        default=ROOT / 'artifacts/recovery_environment')
    save = sub.add_parser('snapshot'); save.add_argument('--destination', type=Path, required=True)
    save.add_argument('--archive-name', default='source-workspace.tar.gz')
    verify = sub.add_parser('verify'); verify.add_argument('directory', type=Path)
    args = parser.parse_args()
    if args.command == 'environment': capture_environment(args.output)
    elif args.command == 'snapshot': snapshot(args.destination, args.archive_name)
    else: verify_tree(args.directory)


if __name__ == '__main__':
    main()
