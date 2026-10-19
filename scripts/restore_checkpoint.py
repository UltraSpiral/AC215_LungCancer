"""Restore verified recovery data without overwriting different files or credentials.

Stdlib only. Does not download, install, execute archived code, or start Codex.
Use project mode for a recovery/ timestamp directory; session mode for a private
Codex snapshot. Run session restore before starting Codex in a fresh home.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tarfile
import tempfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()


def verify_inventory(root):
    inv = json.loads((root / 'inventory.json').read_text())
    for item in inv['files']:
        p = root / item['path']
        if not p.resolve().is_relative_to(root.resolve()) or digest(p) != item['sha256']:
            raise RuntimeError(f'Invalid backup member: {item["path"]}')
    return inv


def restore_files(mapping, apply):
    conflicts = [str(dst) for src, dst in mapping
                 if dst.exists() and (not dst.is_file() or digest(src) != digest(dst))]
    if conflicts:
        raise RuntimeError('No changes made; preserve/reconcile existing files first: ' + ', '.join(conflicts[:10]))
    missing = [(src, dst) for src, dst in mapping if not dst.exists()]
    if apply:
        for src, dst in missing:
            dst.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=dst.parent, delete=False) as f:
                temporary = Path(f.name)
                with src.open('rb') as source: shutil.copyfileobj(source, f)
                f.flush(); os.fsync(f.fileno())
            if digest(src) != digest(temporary): raise RuntimeError('Copy checksum mismatch')
            temporary.chmod(0o600)
            # Atomic link refuses to overwrite a file that appeared after preflight.
            os.link(temporary, dst); temporary.unlink()
    return {'verified_files': len(mapping), 'missing_files': len(missing), 'applied': apply}


def project(root, workspace, apply):
    verify_inventory(root)
    archive_name = 'source-final.tar.gz' if (root / 'source-final.tar.gz').exists() else 'source-workspace.tar.gz'
    with tempfile.TemporaryDirectory(prefix='lungcancer-restore-') as scratch:
        with tarfile.open(root / archive_name) as archive:
            for m in archive.getmembers():
                if not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts:
                    raise RuntimeError('Unsafe source archive')
            archive.extractall(scratch, filter='data')
        scratch = Path(scratch)
        mapping = [(p, workspace / p.relative_to(scratch)) for p in scratch.rglob('*') if p.is_file()]
        mapping += [(p, workspace / 'artifacts' / p.relative_to(root / 'artifacts'))
                    for p in (root / 'artifacts').rglob('*') if p.is_file()]
        return restore_files(mapping, apply)


def session(root, home, apply, include_state):
    verify_inventory(root)
    # Explicit allowlist: auth/config/credentials/logs/queues/caches never restored.
    base = root / 'records'
    allowed = [p for p in (base / 'sessions').rglob('*.jsonl') if p.is_file()]
    for name in ['history.jsonl', 'session_index.jsonl']:
        if (base / name).exists(): allowed.append(base / name)
    if include_state:
        for name in ['state_5.sqlite', 'thread_history_1.sqlite']:
            if (base / name).exists(): allowed.append(base / name)
    manifest = json.loads((root / 'session_manifest.json').read_text())
    mapping = [(p, home / p.relative_to(base)) for p in allowed]
    with tempfile.TemporaryDirectory(prefix='codex-state-relocate-') as scratch:
        # The thread index stores an absolute rollout path. Relocate ONLY our
        # temporary DB copy when restoring into a different empty Codex home.
        if include_state and str(home) != manifest['source_codex_home']:
            for i, (source, destination) in enumerate(mapping):
                if source.name == 'state_5.sqlite':
                    relocated = Path(scratch) / source.name
                    shutil.copyfile(source, relocated)
                    c = sqlite3.connect(relocated)
                    c.execute('UPDATE threads SET rollout_path=? WHERE id=?',
                              (str(home / manifest['rollout_relative_path']), manifest['session_id']))
                    c.commit()
                    if c.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                        raise RuntimeError('Relocated state integrity failure')
                    c.close()
                    mapping[i] = (relocated, destination)
        if apply: home.mkdir(parents=True, exist_ok=True, mode=0o700)
        result = restore_files(mapping, apply)
    result.update(session_id=json.loads((root / 'session_manifest.json').read_text())['session_id'],
                  database_restore_requested=include_state,
                  note='For a nonempty Codex home, reconcile conflicts manually; never overwrite live databases.')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('kind', choices=['project', 'session']); p.add_argument('backup', type=Path)
    p.add_argument('--workspace', type=Path, default=Path('/content/LungCancer'))
    p.add_argument('--codex-home', type=Path,
                   default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    p.add_argument('--include-state', action='store_true')
    p.add_argument('--apply', action='store_true', help='Default is read-only preflight.')
    a = p.parse_args()
    result = project(a.backup, a.workspace, a.apply) if a.kind == 'project' else session(a.backup, a.codex_home, a.apply, a.include_state)
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
