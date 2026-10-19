"""Back up only the current Codex conversation, excluding authentication and caches.

SQLite Connection.backup captures each live database consistently. It is then
filtered to the requested thread, vacuumed, integrity-checked and secret-scanned
locally BEFORE any record is copied to Drive. No active database file is copied.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_secrets import require_clean
from recovery_checkpoint import DRIVE, atomic_json, checksum, persist_file, persistent_ready, verify_tree


def filtered_database(source, target, sid, state):
    src = sqlite3.connect(f'file:{source}?mode=ro', uri=True)
    dst = sqlite3.connect(target)
    src.backup(dst); src.close()
    dst.execute('PRAGMA foreign_keys=OFF')
    tables = [r[0] for r in dst.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    for table in tables:
        quoted = '"' + table.replace('"', '""') + '"'
        if table in {'_sqlx_migrations', 'sqlite_sequence'}: continue
        columns = [r[1] for r in dst.execute(f'PRAGMA table_info({quoted})')]
        if state and table == 'threads':
            dst.execute(f'DELETE FROM {quoted} WHERE id != ?', (sid,))
            # Unnecessary organization/UI links are not part of recovery.
            dst.execute('UPDATE threads SET project_id=NULL,thread_section_id=NULL WHERE id=?', (sid,))
        elif 'thread_id' in columns and table in {
                'thread_read_receipts', 'thread_dynamic_tools', 'thread_turns',
                'thread_items', 'thread_history_projection_state', 'thread_realtime_items'}:
            dst.execute(f'DELETE FROM {quoted} WHERE thread_id != ?', (sid,))
        else:
            dst.execute(f'DELETE FROM {quoted}')
    dst.commit(); dst.execute('VACUUM')
    integrity = dst.execute('PRAGMA integrity_check').fetchone()[0]
    counts = {t: dst.execute('SELECT count(*) FROM "' + t + '"').fetchone()[0]
              for t in tables if not t.startswith('sqlite_')}
    if integrity != 'ok': raise RuntimeError('SQLite backup integrity failure')
    dst.close(); target.chmod(0o600)
    return {'source': str(source), 'method': 'sqlite3.Connection.backup, thread filter, VACUUM',
            'integrity_check': integrity, 'row_counts': counts}


def snapshot(home, sid, destination):
    persistent_ready()
    if not destination.resolve().is_relative_to((DRIVE / 'private_codex_recovery').resolve()):
        raise ValueError('Private Codex snapshots must be outside source/artifact/public Git paths.')
    if destination.exists(): raise FileExistsError('Preserve previous private snapshots.')
    paths = []
    for p in (home / 'sessions').rglob('*.jsonl'):
        with p.open() as f:
            first = json.loads(f.readline())
        if first.get('payload', {}).get('id') == sid: paths.append(p)
    if len(paths) != 1: raise RuntimeError('Current session must resolve to exactly one rollout.')
    rollout = paths[0]
    with tempfile.TemporaryDirectory(prefix='codex-session-snapshot-') as scratch:
        scratch = Path(scratch); scratch.chmod(0o700)
        records = scratch / 'records'; records.mkdir(mode=0o700)
        database_reports = {}
        for name, state in [('state_5.sqlite', True), ('thread_history_1.sqlite', False)]:
            if (home / name).exists():
                database_reports[name] = filtered_database(home / name, records / name, sid, state)
        # Freeze a complete JSONL prefix, avoiding an in-flight trailing record.
        with rollout.open('rb') as stream:
            prefix = stream.read(os.fstat(stream.fileno()).st_size)
        prefix = prefix[:prefix.rfind(b'\n') + 1]
        lines = prefix.splitlines()
        parsed = [json.loads(line) for line in lines]
        if parsed[0]['payload']['id'] != sid: raise RuntimeError('Session identity mismatch')
        relative = rollout.relative_to(home)
        target = records / relative; target.parent.mkdir(parents=True, mode=0o700)
        target.write_bytes(prefix); target.chmod(0o600)
        for name in ['history.jsonl', 'session_index.jsonl']:
            source = home / name
            if not source.exists(): continue
            selected = []
            for line in source.read_text().splitlines():
                try: item = json.loads(line)
                except json.JSONDecodeError: continue
                if item.get('session_id', item.get('id')) == sid: selected.append(item)
            if selected:
                (records / name).write_text(''.join(json.dumps(i) + '\n' for i in selected))
                (records / name).chmod(0o600)
        visible = ['# Readable Codex conversation export\n',
                   f'Session: {sid}. Snapshot excludes later messages and the final response.\n',
                   'This Markdown is readable only. The records/ directory contains native session data.\n',
                   'User and assistant visible text only; tool output and internal reasoning are omitted.\n']
        count = 0
        for record in parsed:
            p = record.get('payload', {})
            if record.get('type') != 'response_item' or p.get('type') != 'message': continue
            if p.get('role') not in {'user', 'assistant'} or p.get('channel') in {'analysis', 'summary'}: continue
            chunks = [i.get('text', '') for i in p.get('content', [])
                      if i.get('type') in {'input_text', 'output_text', 'text'}]
            if chunks:
                visible.append('\n## ' + p['role'] + '\n\n' + '\n'.join(chunks) + '\n'); count += 1
        (scratch / 'conversation-readable.md').write_text('\n'.join(visible))
        inspected = require_clean([p for p in scratch.rglob('*') if p.is_file()])
        manifest = {
            'snapshot_at_utc': datetime.now(timezone.utc).isoformat(), 'session_id': sid,
            'source_codex_home': str(home), 'source_workspace': '/content/LungCancer',
            'cli_version': subprocess.check_output(['codex', '--version'], text=True).strip(),
            'rollout_relative_path': str(relative), 'rollout_complete_records': len(lines),
            'rollout_bytes': len(prefix), 'source_file_bytes_at_read': rollout.stat().st_size,
            'visible_export_messages': count, 'secret_inspection': inspected,
            'database_backups': database_reports,
            'excluded': ['auth.json', 'config.toml', 'credential stores', 'environment dumps',
                         'logs', 'queue databases', 'goals', 'memories', 'shell_snapshots',
                         'plugins', 'caches', 'other sessions'],
            'databases_are_individually_consistent': True,
            'cross_file_atomic_snapshot': False,
            'restored_session_read_verified': False,
            'interactive_resume_verified': False,
            'current_final_response_included': False,
        }
        atomic_json(scratch / 'session_manifest.json', manifest)
        require_clean([p for p in scratch.rglob('*') if p.is_file()])
        destination.mkdir(parents=True, mode=0o700)
        for p in sorted(scratch.rglob('*')):
            if p.is_file(): persist_file(p, (destination / p.relative_to(scratch)).relative_to(DRIVE))
        verify_tree(destination)
        print(json.dumps({'session_id': sid, 'backup': str(destination),
                          'rollout_records': len(lines), 'secret_findings': 0,
                          'databases': list(database_reports), 'readable_messages': count}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path,
                        default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    parser.add_argument('--session-id', default=os.environ.get('CODEX_THREAD_ID'))
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    if not args.session_id: parser.error('Pass --session-id explicitly')
    snapshot(args.codex_home, args.session_id, args.destination)
