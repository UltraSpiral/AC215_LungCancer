"""Offline verification of restored artifacts/dependencies; never acquires or fits.

Reads the immutable checkpoint inventory and saved GDC/embedding data. Imports
dependencies without creating an encoder, loading weights, or fitting a model.
An optional GitHub reference report must have been collected separately.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lungcancer.common import checksum, fingerprint, atomic_json, utcnow


def verify(environment, backup, remote_report=None):
    import numpy as np
    from PIL import Image
    from lungcancer.features import load_features
    from lungcancer.gdc import normalize_file

    env = json.loads(environment.read_text())
    inventory = json.loads((backup / 'inventory.json').read_text())
    files = [e for e in inventory['files'] if e['path'].startswith('artifacts/')]
    for item in files:
        local = ROOT / item['path']
        persisted = backup / item['path']
        if not local.is_file() or checksum(local) != item['sha256']:
            raise RuntimeError(f'Restored artifact missing or changed: {item["path"]}')
        if not persisted.is_file() or checksum(persisted) != item['sha256']:
            raise RuntimeError(f'Persistent checkpoint mismatch: {item["path"]}')

    imports = {}
    for name in ['torch', 'torchvision', 'timm', 'huggingface_hub', 'openslide',
                 'numpy', 'scipy', 'sklearn', 'PIL', 'requests', 'joblib', 'pytest']:
        try:
            module = importlib.import_module(name)
            imports[name] = {'import_ok': True, 'version': str(getattr(module, '__version__', 'unknown'))}
            if name == 'openslide': imports[name]['native_version'] = module.__library_version__
        except Exception as error:
            imports[name] = {'import_ok': False, 'error_type': type(error).__name__, 'reason': str(error)}

    from huggingface_hub import try_to_load_from_cache
    revision = 'd517a8dd47902dd7c308b3c36f63bce47e7b9a43'
    expected_weight = '6e077eda234bebc595868d918d3458d9dd32a050199b0ff04443b2f46a0a3b1e'
    cached = try_to_load_from_cache('MahmoodLab/UNI2-h', 'pytorch_model.bin', revision=revision)
    checkpoint_present = isinstance(cached, str) and Path(cached).is_file()
    weight = {'repository': 'MahmoodLab/UNI2-h', 'revision': revision,
              'checkpoint_present': checkpoint_present, 'loaded_on_this_runtime': False,
              'expected_sha256': expected_weight, 'network_requested': False}
    if checkpoint_present:
        weight['sha256'] = checksum(cached)
        if weight['sha256'] != expected_weight: raise RuntimeError('Pinned encoder checkpoint checksum mismatch')

    selection = json.loads((ROOT / 'artifacts/pilot_selection.json').read_text())
    raw = {}
    for page in sorted((ROOT / 'artifacts/discovery').glob('raw_page_*.json')):
        for hit in json.loads(page.read_text())['response']['data']['hits']:
            if hit['file_id'] in raw: raise RuntimeError('Duplicate saved GDC file UUID')
            raw[hit['file_id']] = hit
    current_config = json.loads((ROOT / 'configs/preprocessing.json').read_text())
    rows = []
    for selected in selection['slides']:
        audited = normalize_file(raw[selected['file_id']])
        for key in ['file_id', 'md5sum', 'file_size', 'case_id', 'patient_id', 'project_id',
                    'slide_id', 'sample_id', 'sample_type', 'candidate_class', 'decision',
                    'preparation', 'preparation_provenance']:
            if audited[key] != selected[key]: raise RuntimeError(f'Specimen/label audit mismatch: {key}')
        if audited['decision'] != 'include': raise RuntimeError('Excluded pilot specimen')
        directory = ROOT / 'artifacts/slides' / selected['file_id']
        prep = json.loads((directory / 'preprocessing.json').read_text())
        emb, coords, meta = load_features(directory / 'embeddings.npz')
        emb_json = json.loads((directory / 'embeddings.json').read_text())
        if checksum(directory / 'embeddings.npz') != emb_json['npz_sha256']:
            raise RuntimeError('Embedding checksum mismatch')
        if prep['source_md5'] != selected['md5sum'] or meta['source_md5'] != selected['md5sum']:
            raise RuntimeError('Slide identity mismatch')
        if meta['encoder']['revision'] != revision or meta['encoder']['checkpoint_sha256'] != expected_weight:
            raise RuntimeError('Encoder provenance mismatch')
        if fingerprint(meta['encoder']) != meta['encoder_identifier']:
            raise RuntimeError('Encoder metadata fingerprint mismatch')
        if prep['config'] != current_config or meta['preprocessing_config'] != current_config:
            raise RuntimeError('Preprocessing configuration mismatch')
        expected_key = fingerprint({'preprocessing': prep['fingerprint'], 'encoder': meta['encoder_identifier'],
                                    'coordinates': fingerprint(coords.tolist()),
                                    'implementation': checksum(ROOT / 'lungcancer/features.py')})
        if expected_key != meta['fingerprint']: raise RuntimeError('Feature cache fingerprint mismatch')
        if emb.shape != (512, 1536): raise RuntimeError('Unexpected pilot embedding shape')
        with np.load(directory / 'coordinates.npz', allow_pickle=False) as saved:
            if not np.array_equal(coords, saved['coordinates']): raise RuntimeError('Coordinate-order mismatch')
        dimensions = np.asarray(prep['dimensions_level0'])
        footprint = np.asarray(prep['geometry']['footprint_level0'])
        if not ((coords >= 0).all() and (coords + footprint <= dimensions).all()):
            raise RuntimeError('Tile footprint exceeds level-0 bounds')
        if prep['accepted_count'] + prep['rejected_count'] != prep['candidate_count']:
            raise RuntimeError('Tile counts do not reconcile')
        for picture in [*directory.glob('*.jpg'), *directory.glob('*.png')]:
            with Image.open(picture) as image: image.verify()
        rows.append({'file_id': selected['file_id'], 'case_id': selected['case_id'],
                     'patient': selected['patient_id'], 'class': selected['candidate_class'],
                     'project': selected['project_id'], 'shape': list(emb.shape),
                     'finite': bool(np.isfinite(emb).all()), 'coordinates_aligned_and_bounded': True,
                     'specimen_label_provenance_reaudited': True, 'cache_fingerprint_valid': True})

    ledger = json.loads((ROOT / 'artifacts/download_ledger.json').read_text())
    if sum(a['transferred_bytes'] for a in ledger['attempts']) != ledger['transferred_bytes']:
        raise RuntimeError('Raw transfer ledger does not reconcile')
    panels = []
    for cls in ['non_tumor', 'adenocarcinoma', 'squamous']:
        picture = ROOT / 'artifacts/pilot_review' / f'{cls}_audit.jpg'
        with Image.open(picture) as image: image.verify()
        panels.append(str(picture))
    git = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    remote = json.loads(remote_report.read_text()) if remote_report and remote_report.exists() else None
    blockers = list(env['blockers'])
    blockers += [f'dependency_import_failed:{k}' for k, v in imports.items() if not v['import_ok']]
    if not checkpoint_present: blockers.append('uni2_checkpoint_not_cached')
    return {
        'verified_at_utc': utcnow(), 'status': 'review_ready_processing_blocked' if blockers else 'ready',
        'artifact_review_ready': True, 'slide_processing_prerequisites_ready': not blockers,
        'processing_blockers': blockers, 'environment_report': str(environment),
        'immutable_checkpoint': str(backup), 'restored_and_persistent_artifact_checksums_verified': len(files),
        'saved_gdc_files': len(raw), 'dependency_imports': imports, 'encoder': weight,
        'pilot_counts': {c: {'slides': sum(r['class'] == c for r in rows),
                            'patients': len({r['case_id'] for r in rows if r['class'] == c})}
                         for c in ['non_tumor', 'adenocarcinoma', 'squamous']},
        'total_patients': len({r['case_id'] for r in rows}), 'pilot_slides': rows,
        'raw_bytes_transferred': ledger['transferred_bytes'], 'raw_bytes_reserved': ledger['reserved_bytes'],
        'raw_budget_bytes': ledger['budget_bytes'], 'normal_projects': dict(Counter(
            r['project'] for r in rows if r['class'] == 'non_tumor')), 'panel_paths': panels,
        'local_git_repository_available': git.returncode == 0,
        'local_commit': git.stdout.strip() if git.returncode == 0 else None,
        'github_reference': remote, 'downloads_performed': False, 'dependencies_installed': False,
        'encoder_loaded': False, 'profiling_or_training_performed': False,
        'new_heldout_evaluation_or_inference_performed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', type=Path, required=True)
    parser.add_argument('--backup', type=Path, default=Path(
        '/content/drive/MyDrive/LungCancer_AC215/recovery/20261019T002107Z'))
    parser.add_argument('--remote-report', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.environment, args.backup, args.remote_report)
    atomic_json(args.output, result)
    print(json.dumps({k: result[k] for k in ['status', 'restored_and_persistent_artifact_checksums_verified',
        'pilot_counts', 'processing_blockers', 'local_git_repository_available']}, indent=2))
    print(args.output)
    return 0 if result['slide_processing_prerequisites_ready'] else 2


if __name__ == '__main__': raise SystemExit(main())
