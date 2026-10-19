"""Persist checkpoint Markdown and a source archive without running the pipeline."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    from lungcancer.common import (DEFAULT_PERSISTENT, atomic_json, backup_code,
                                   persist_file, utcnow)

    docs = ROOT / 'docs'
    for name in ('INDEX.md', 'CHECKPOINTS.md', 'COMMANDS.md'):
        if not (docs / name).is_file():
            raise RuntimeError(f'Missing required checkpoint record: {name}')
    backup = backup_code()
    latest = docs / 'LATEST_BACKUP.md'
    text = (
        '# Latest verified source-code backup\n\n'
        f'Updated: {utcnow()}\n\n'
        f'Archive: `{backup["path"]}`\n\n'
        f'SHA256: `{backup["sha256"]}`\n\n'
        f'Archive size: {backup["bytes"]:,} bytes.\n\n'
        'The archive contains source modules, scripts, tests, configurations, '
        'repository instructions, and the checkpoint Markdown available when '
        'the archive was created. Credentials, raw slides, and encoder weights '
        'are excluded. Derived outputs remain in the persistent artifacts directory.\n\n'
        'This pointer is updated after archive creation. Historical checkpoint '
        'reports retain the backup identifiers current at their own timestamps.\n'
    )
    temporary = latest.with_name('.LATEST_BACKUP.md.partial')
    temporary.write_text(text)
    temporary.replace(latest)

    receipts = []
    for source in sorted(docs.rglob('*.md')):
        receipts.append(persist_file(source, Path('docs') / source.relative_to(docs)))
    for name in ('README.md', 'STATUS.md', 'AGENTS.md', 'scripts/persist_records.py'):
        receipts.append(persist_file(ROOT / name, Path('code') / name))
    record = {'verified_at_utc': utcnow(), 'source_backup': backup, 'files': receipts,
              'slide_downloads_run': False, 'model_training_run': False}
    output = ROOT / 'artifacts/documentation_persistence.json'
    atomic_json(output, record)
    persist_file(output, 'artifacts/documentation_persistence.json')
    print(f'Verified {len(receipts)} document/source copies and one code archive.')
    for name in ('INDEX.md', 'CHECKPOINTS.md', 'COMMANDS.md', 'LATEST_BACKUP.md'):
        print(DEFAULT_PERSISTENT / 'docs' / name)


if __name__ == '__main__':
    main()
