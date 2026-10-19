"""Conservative secret-pattern scan. Reports counts/locations, never matched values.

This is a focused safeguard, not a guarantee against every possible secret format.
"""
from collections import Counter
from pathlib import Path
import re
import json
import sqlite3

PATTERNS = {
    'huggingface_token': rb'hf_[A-Za-z0-9]{20,}',
    'github_token': rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'openai_key': rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}',
    'google_api_key': rb'AIza[A-Za-z0-9_-]{30,}',
    'google_oauth_token': rb'ya29\.[A-Za-z0-9_.-]{25,}',
    'aws_access_key': rb'(?:AKIA|ASIA)[A-Z0-9]{16}',
    'jwt': rb'eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}',
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'literal_bearer': rb'(?i)bearer[ \t]+[A-Za-z0-9_.-]{28,}',
}


def scan(data):
    return {name: len(re.findall(pattern, data)) for name, pattern in PATTERNS.items()
            if re.search(pattern, data)}


def scan_structured(value):
    findings = Counter()
    if isinstance(value, dict):
        for key, item in value.items():
            # Opaque server-encrypted reasoning is not a plaintext credential.
            # Random base64 occasionally contains a token prefix by chance.
            if key != 'encrypted_content': findings.update(scan_structured(item))
    elif isinstance(value, list):
        for item in value: findings.update(scan_structured(item))
    elif isinstance(value, str): findings.update(scan(value.encode()))
    return dict(findings)


def scan_text(text):
    try: return scan_structured(json.loads(text))
    except (json.JSONDecodeError, ValueError): return scan(text.encode())


def scan_file(path):
    if path.suffix == '.jsonl':
        findings = Counter()
        for line in path.read_text().splitlines(): findings.update(scan_text(line))
        return dict(findings)
    if path.suffix == '.json': return scan_text(path.read_text())
    if path.suffix == '.sqlite':
        findings = Counter()
        c = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
        for name, in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            quoted = '"' + name.replace('"', '""') + '"'
            for row in c.execute(f'SELECT * FROM {quoted}'):
                for cell in row:
                    if isinstance(cell, str): findings.update(scan_text(cell))
        c.close()
        return dict(findings)
    return scan(path.read_bytes())


def require_clean(paths):
    findings = [{'path': str(p), 'patterns': scan_file(Path(p))} for p in paths]
    findings = [f for f in findings if f['patterns']]
    if findings:
        raise RuntimeError('Secret-pattern inspection failed; no matched values shown: ' + str(findings))
    return {'files_scanned': len(paths), 'findings': 0,
            'scope': list(PATTERNS),
            'limitation': 'Pattern scan cannot detect every secret format. Opaque encrypted_content fields cannot be inspected and are excluded from plaintext matching.'}
