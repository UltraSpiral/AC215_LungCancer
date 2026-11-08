"""Download a selected cohort from GDC, verify each slide, and copy it to Cloud Storage."""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lungcancer.common import read_json, utcnow  # noqa: E402
from lungcancer.download import download_slide  # noqa: E402


def split_gcs(uri: str) -> tuple[str, str]:
    if not uri.startswith('gs://'):
        raise ValueError(f'not a gs:// path: {uri}')
    bucket, _, name = uri[5:].partition('/')
    return bucket, name


def load_selection(path: str, client) -> dict:
    if path.startswith('gs://'):
        bucket, name = split_gcs(path)
        return json.loads(client.bucket(bucket).blob(name).download_as_text())
    return read_json(path)


def already_uploaded(blob, record: dict) -> bool:
    if not blob.exists():
        return False
    blob.reload()
    md5 = base64.b64decode(blob.md5_hash).hex() if blob.md5_hash else None
    return blob.size == int(record['file_size']) and md5 == record['md5sum']


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', required=True, help='selection.json, local or gs://')
    parser.add_argument('--destination', required=True, help='gs://bucket/prefix for the slides')
    parser.add_argument('--work-dir', default='/tmp/lungcancer-raw')
    parser.add_argument('--budget', type=int, default=10_000_000_000)
    args = parser.parse_args()

    from google.cloud import storage
    client = storage.Client()
    selection = load_selection(args.selection, client)
    slides = selection['slides']
    bucket_name, prefix = split_gcs(args.destination.rstrip('/'))
    bucket = client.bucket(bucket_name)
    work = Path(args.work_dir)
    ledger = work / 'download_ledger.json'

    results = []
    for i, record in enumerate(slides, 1):
        file_id = record['file_id']
        blob = bucket.blob(f'{prefix}/{file_id}.svs')
        label = f'[{i}/{len(slides)}] {file_id} ({record["candidate_class"]})'
        if already_uploaded(blob, record):
            print(f'{label} already in bucket, skipping', flush=True)
            results.append({'file_id': file_id, 'status': 'already_present'})
            continue
        try:
            path = download_slide(record, raw_root=work, ledger_path=ledger, budget=args.budget, persist=False)
            blob.upload_from_filename(str(path), checksum='md5')
            if not already_uploaded(blob, record):
                raise RuntimeError('uploaded_object_does_not_match_manifest')
            path.unlink()
            print(f'{label} uploaded', flush=True)
            results.append({'file_id': file_id, 'status': 'uploaded'})
        except Exception as exc:
            print(f'{label} FAILED: {exc}', flush=True)
            results.append({'file_id': file_id, 'status': 'failed', 'reason': str(exc)})

    failed = [r for r in results if r['status'] == 'failed']
    report = {
        'finished_at': utcnow(),
        'selection': args.selection,
        'destination': args.destination,
        'total': len(results),
        'failed': len(failed),
        'slides': results,
    }
    bucket.blob(f'{prefix}/download_report.json').upload_from_string(
        json.dumps(report, indent=2), content_type='application/json')
    print(f'Done: {len(results) - len(failed)} of {len(results)} slides in {args.destination}', flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
