from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

CLASSES = ('non_tumor', 'adenocarcinoma', 'squamous')
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PERSISTENT = Path('/content/drive/MyDrive/LungCancer_AC215')


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def checksum(path, algorithm='sha256'):
    digest = hashlib.new(algorithm)
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, prefix='.writing-', delete=False) as f:
        f.write(json.dumps(value, indent=2, allow_nan=False) + '\n')
        f.flush()
        os.fsync(f.fileno())
        temporary = f.name
    os.replace(temporary, path)


def persistent_ready(root=DEFAULT_PERSISTENT):
    root = Path(root)
    if not Path('/content/drive').is_mount() or not root.is_dir():
        raise RuntimeError('persistent_storage_unavailable: mount Google Drive first')
    return root


def persist_file(source, relative, root=DEFAULT_PERSISTENT):
    """Copy, close, and reread SHA256; fail closed before permitting raw cleanup."""
    destination = persistent_ready(root) / relative
    source = Path(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + '.partial')
    shutil.copyfile(source, temporary)
    if checksum(source) != checksum(temporary):
        raise RuntimeError('persistent_copy_checksum_mismatch')
    os.replace(temporary, destination)
    return {'path': str(destination), 'sha256': checksum(destination), 'bytes': destination.stat().st_size}


def sync_artifacts(local, relative='artifacts', root=DEFAULT_PERSISTENT):
    files = []
    for source in sorted(Path(local).rglob('*')):
        if source.is_file() and not source.name.startswith('.') and not source.name.endswith('.partial'):
            files.append(persist_file(source, Path(relative) / source.relative_to(local), root))
    return files


def backup_code(root=DEFAULT_PERSISTENT):
    import tarfile
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archive = ROOT / 'artifacts' / 'backups' / f'code-{stamp}.tar.gz'
    archive.parent.mkdir(parents=True, exist_ok=True)
    allowed = ['lungcancer', 'scripts', 'tests', 'configs', 'README.md', 'STATUS.md', 'AGENTS.md',
               'pyproject.toml', 'requirements.txt', '.gitignore', 'docs',
               'containers','frontend','backend','compose.cpu.yml','compose.app.yml',
               'compose.yml','docker-compose.yml','Makefile','.dockerignore']
    excluded_dirs={'__pycache__','.pytest_cache','.venv','node_modules','.cache',
                   'dist','sample-slides','local_data','local_outputs','private_codex_recovery',
                   '.git','.codex','.agents','.aws','artifacts','raw','data','uploads'}
    excluded_suffixes={'.svs','.pt','.pth','.bin','.safetensors','.npz','.joblib',
                       '.sqlite','.sqlite3','.jsonl','.bundle','.pyc','.gz','.zip','.log'}
    def source_file(item):
        relative=item.relative_to(ROOT)
        return (item.is_file() and not item.is_symlink()
                and not set(relative.parts)&excluded_dirs
                and relative.parts[:3]!=('frontend','public','slides')
                and item.suffix.lower() not in excluded_suffixes
                and '.sqlite' not in item.name
                and item.name not in {'auth.json','credentials.json','hosts.yml',
                                      '.npmrc','.pypirc','.netrc','.git-credentials'}
                and (not item.name.startswith('.env') or item.name=='.env.example'))
    with tarfile.open(archive, 'w:gz') as tf:
        for name in allowed:
            path = ROOT / name
            if not path.exists():
                continue
            if source_file(path):
                tf.add(path, arcname=name)
            elif path.is_dir() and not path.is_symlink():
                for item in sorted(path.rglob('*')):
                    if source_file(item):
                        tf.add(item, arcname=str(item.relative_to(ROOT)))
    return persist_file(archive, Path('code_backups') / archive.name, root)


def restore_artifacts(root=DEFAULT_PERSISTENT):
    """Recover missing local artifacts, including the cumulative download ledger."""
    source_root=persistent_ready(root)/'artifacts'
    count=0
    for source in sorted(source_root.rglob('*')):
        if source.is_file() and not source.name.endswith('.partial'):
            target=ROOT/'artifacts'/source.relative_to(source_root)
            if target.exists(): continue
            target.parent.mkdir(parents=True,exist_ok=True)
            temporary=target.with_name(target.name+'.partial')
            shutil.copyfile(source,temporary)
            if checksum(source)!=checksum(temporary): raise RuntimeError('restored_artifact_checksum_mismatch')
            os.replace(temporary,target); count+=1
    return count
