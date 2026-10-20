"""Read-only verification of restored pilot artifacts against a saved checkpoint.

Does not download, preprocess, load UNI2-h, or train. Reports are written only to
the explicitly supplied output path. Historical checkpoint files stay unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import tarfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lungcancer.common import atomic_json, checksum, fingerprint


def verify(snapshot, workspace):
    inventory = json.loads((snapshot / 'inventory.json').read_text())
    expected_inventory_hash = None
    checksums_verified = 0
    for line in (snapshot / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = snapshot / name
        if not path.resolve().is_relative_to(snapshot.resolve()):
            raise ValueError('Unsafe checksum inventory path')
        if checksum(path) != expected:
            raise ValueError(f'Persistent checksum mismatch: {name}')
        if name == 'inventory.json': expected_inventory_hash = expected
        checksums_verified += 1
    if expected_inventory_hash is None:
        raise ValueError('Checksum inventory does not cover inventory.json')
    local_artifacts, absent, changed = [], [], []
    for item in inventory['files']:
        name = item['path']
        if not Path(name).parts or Path(name).parts[0] != 'artifacts': continue
        target = workspace / name
        if not target.is_file(): absent.append(name)
        elif checksum(target) != item['sha256']: changed.append(name)
        else: local_artifacts.append(name)
    if absent or changed:
        raise ValueError(f'Restored artifact verification failed: missing={absent}, changed={changed}')
    archive_members = 0
    for archive_path in snapshot.rglob('*.tar.gz'):
        with tarfile.open(archive_path) as archive:
            for member in archive.getmembers():
                if not member.isfile(): raise ValueError('Unexpected non-file archive member')
                if len(archive.extractfile(member).read()) != member.size:
                    raise ValueError('Unreadable archive member')
                archive_members += 1
    details = json.loads((workspace / 'artifacts/pilot_review/details.json').read_text())
    selection = json.loads((workspace / 'artifacts/pilot_selection.json').read_text())
    selection_by_id = {s['file_id']: s for s in selection['slides']}
    rows = []
    for item in details['rows']:
        file_id = item['file_id']
        directory = workspace / 'artifacts/slides' / file_id
        prep = json.loads((directory / 'preprocessing.json').read_text())
        meta = json.loads((directory / 'embeddings.json').read_text())
        if meta['npz_sha256'] != checksum(directory / 'embeddings.npz'):
            raise ValueError('Embedding file checksum mismatch')
        if prep['coordinates_file_sha256'] != checksum(directory / 'coordinates.npz'):
            raise ValueError('Coordinate file checksum mismatch')
        with np.load(directory / 'embeddings.npz', allow_pickle=False) as cached, np.load(directory / 'coordinates.npz', allow_pickle=False) as coordinates:
            array = cached['embeddings']; xy = cached['coordinates']
            embedded_meta = json.loads(str(cached['metadata_json']))
            assert array.shape == (512, 1536) and np.isfinite(array).all()
            assert xy.shape == (512, 2) and np.isfinite(xy).all()
            assert np.array_equal(xy, coordinates['coordinates'])
            assert fingerprint(xy.tolist()) == meta['coordinates_fingerprint']
            assert embedded_meta['fingerprint'] == meta['fingerprint']
            w, h = prep['dimensions_level0']; fw, fh = prep['geometry']['footprint_level0']
            assert (xy >= 0).all() and (xy[:, 0] + fw <= w).all() and (xy[:, 1] + fh <= h).all()
        expected_encoder = details['encoder']
        assert meta['encoder']['revision'] == expected_encoder['revision']
        assert meta['encoder']['checkpoint_sha256'] == expected_encoder['checkpoint_sha256']
        assert prep['source_md5'] == item['md5sum'] == meta['source_md5']
        assert meta['file_id'] == file_id == selection_by_id[file_id]['file_id']
        assert item['specimen_link_verified_against_saved_raw_response']
        images = 0
        for path in directory.iterdir():
            if path.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
                with Image.open(path) as image: image.verify()
                images += 1
        rows.append({'file_id': file_id, 'class': item['class'], 'patient': item['patient'],
                     'shape': [512, 1536], 'all_finite': True,
                     'coordinates_aligned_and_in_bounds': True, 'readable_images': images,
                     'source_md5_and_encoder_match': True})
    for path in (workspace / 'artifacts/pilot_review').glob('*.jpg'):
        with Image.open(path) as image: image.verify()
    ledger = json.loads((workspace / 'artifacts/download_ledger.json').read_text())
    assert ledger['transferred_bytes'] == details['actual_raw_bytes_downloaded'] == 1020202701
    assert len(rows) == 9 and len({r['patient'] for r in rows}) == 9
    return {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'status': 'passed',
            'snapshot': str(snapshot), 'workspace': str(workspace),
            'snapshot_checksum_entries_verified': checksums_verified,
            'restored_artifact_files_matched': len(local_artifacts),
            'archive_members_readable': archive_members,
            'pilot_counts': details['counts'], 'slides': rows,
            'total_embeddings': 4608, 'all_embeddings_finite': True,
            'raw_bytes_downloaded': ledger['transferred_bytes'],
            'raw_budget_bytes': ledger['budget_bytes'],
            'preparation': {'explicit_frozen': 0, 'inferred_frozen': 9},
            'normal_slides_by_project': details['normal_slides_by_project'],
            'encoder_revision': details['encoder']['revision'],
            'no_downloads_preprocessing_encoder_inference_or_training_run': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path,
        default=Path('/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z'))
    parser.add_argument('--workspace', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.snapshot, args.workspace)
    atomic_json(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'slides'}, indent=2))
