"""Verify native thread reading after restore into an isolated, credential-free home.

No model turn, login, training or acquisition is started. Only initialize and
thread/read JSON-RPC methods are sent to this verifier's own stdio server.
"""
import argparse
import json
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import time

from restore_checkpoint import session


def verify(backup):
    sid = json.loads((backup / 'session_manifest.json').read_text())['session_id']
    with tempfile.TemporaryDirectory(prefix='codex-read-restore-') as scratch:
        home = Path(scratch) / '.codex'
        restored = session(backup, home, True, True)
        # Allowlist environment; do not pass inherited API keys or credentials.
        env = {'PATH': os.environ['PATH'], 'HOME': scratch, 'CODEX_HOME': str(home),
               'LANG': 'C.UTF-8'}
        with tempfile.TemporaryFile() as errors:
            p = subprocess.Popen(['codex', 'app-server', '--listen', 'stdio://'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
                env=env, bufsize=0)
            selector = selectors.DefaultSelector(); selector.register(p.stdout, selectors.EVENT_READ)
            buffer = b''

            def request(number, method, params):
                nonlocal buffer
                p.stdin.write((json.dumps({'id': number, 'method': method, 'params': params}) + '\n').encode())
                p.stdin.flush()
                end = time.monotonic() + 40
                while time.monotonic() < end:
                    if b'\n' not in buffer:
                        if not selector.select(timeout=1): continue
                        chunk = os.read(p.stdout.fileno(), 65536)
                        if not chunk: raise RuntimeError('Verifier app-server exited before responding')
                        buffer += chunk
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        item = json.loads(line)
                        if item.get('id') == number:
                            if 'error' in item: raise RuntimeError('Read-only RPC failed: ' + str(item['error'].get('code')))
                            return item['result']
                raise TimeoutError('Read-only app-server response timed out')

            try:
                request(1, 'initialize', {'clientInfo': {'name': 'recovery_verifier', 'version': '1.0'},
                                         'capabilities': {'experimentalApi': True}})
                p.stdin.write(b'{"method":"initialized"}\n'); p.stdin.flush()
                result = request(2, 'thread/read', {'threadId': sid, 'includeTurns': True})
                thread = result['thread']
                if thread['id'] != sid: raise RuntimeError('Restored thread identity mismatch')
                if thread.get('path') and not Path(thread['path']).is_relative_to(home):
                    raise RuntimeError('Thread read escaped isolated restored home')
                turns = thread.get('turns', [])
                if not turns: raise RuntimeError('Restored thread contains no readable turns')
                return {'session_id': sid, 'cli_version': subprocess.check_output(['codex', '--version'], text=True).strip(),
                        'isolated_restore_verified': restored, 'thread_read_verified': True,
                        'readable_turns': len(turns), 'cwd': thread.get('cwd'),
                        'interactive_resume_verified': False, 'model_turns_started': 0,
                        'credentials_restored_or_inherited': False,
                        'limitation': 'Native records can be read; interactive authenticated continuation on a fresh runtime remains unverified.'}
            finally:
                p.stdin.close()
                try: p.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    # Stop only the isolated verifier process that this script owns.
                    p.terminate(); p.wait(timeout=8)
                selector.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.backup)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
