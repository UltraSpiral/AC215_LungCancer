"""Restartable, budgeted real-data baseline run; preserves the original pilot."""
from pathlib import Path
import argparse
import contextlib
import fcntl
import os
import sys
import time
import traceback
import threading

import numpy as np

from .common import (CLASSES, DEFAULT_PERSISTENT, ROOT, atomic_json, checksum,
                     fingerprint, persist_file, read_json, sync_artifacts, utcnow)

LOG_LOCK=threading.RLock()


def process_with_prefetch(records,process,download,is_cached):
    """One acquisition worker overlaps exactly one serial extraction worker.

    A current raw file is verified before the next download starts. Only the
    background worker mutates the download ledger while extraction runs.
    Caller separates development and test phases, preventing pre-test tuning.
    """
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1,thread_name_prefix='one-slide-download') as pool:
        pending=None
        for index,record in enumerate(records):
            if pending is not None:
                pending.result()
            elif not is_cached(record):
                download(record)
            pending=None
            if index+1<len(records) and not is_cached(records[index+1]):
                pending=pool.submit(download,records[index+1])
            process(record)


def verify_cache(record, directory, config, encoder):
    """A completed cache is reusable only with matching bytes and configuration."""
    import openslide
    from . import features, preprocess
    from .features import load_features
    directory = Path(directory)
    embeddings, coords, meta = load_features(directory / 'embeddings.npz')
    prep = read_json(directory / 'preprocessing.json')
    from .safety import preprocessing_fingerprint
    prep_key = preprocessing_fingerprint(record['md5sum'], config.__dict__, prep)
    encoder_id=encoder if isinstance(encoder,str) else encoder.identifier
    expected = fingerprint({'preprocessing': prep_key, 'encoder': encoder_id,
                            'coordinates': fingerprint(coords.tolist()),
                            'implementation': checksum(features.__file__)})
    if (prep['status'] != 'success' or prep['fingerprint'] != prep_key or
            meta['fingerprint'] != expected or meta['file_id'] != record['file_id'] or
            meta['source_md5'] != record['md5sum']):
        raise ValueError('incompatible_cache: preserve existing artifacts and investigate')
    if checksum(directory / 'coordinates.npz') != prep['coordinates_file_sha256']:
        raise ValueError('coordinate_file_checksum_mismatch')
    if checksum(directory / 'embeddings.npz') != read_json(directory / 'embeddings.json')['npz_sha256']:
        raise ValueError('embedding_file_checksum_mismatch')
    with np.load(directory / 'coordinates.npz', allow_pickle=False) as data:
        if not np.array_equal(coords, data['coordinates']):
            raise ValueError('embedding_coordinate_order_mismatch')
    w, h = prep['dimensions_level0']; tw, th = prep['geometry']['footprint_level0']
    if np.any(coords < 0) or np.any(coords[:, 0] + tw > w) or np.any(coords[:, 1] + th > h):
        raise ValueError('coordinates_out_of_bounds')
    return prep, meta


def initialize_run(draft, run_root):
    """Freeze the approved cohort and patient assignments before acquisition."""
    from .modeling import create_splits, check_patient_separation
    run_root = Path(run_root)
    cohort_path, split_path = run_root / 'cohort.json', run_root / 'splits.json'
    draft = read_json(draft)
    rows = draft['slides']
    if len(rows) != 45 or len({r['case_id'] for r in rows}) != 45:
        raise ValueError('approved_run_requires_45_independent_patients')
    if any(sum(r['candidate_class'] == c for r in rows) != 15 for c in CLASSES):
        raise ValueError('approved_run_requires_15_slides_per_class')
    audited = {r['file_id']: r for r in read_json(ROOT / 'artifacts/discovery/manifest.json')}
    for row in rows:
        if audited.get(row['file_id']) != row or row['decision'] != 'include':
            raise ValueError('cohort_does_not_match_saved_specimen_audit')
    if draft['cumulative_raw_budget_bytes'] != 10_000_000_000:
        raise ValueError('approved_budget_is_10GB_cumulative')
    if not cohort_path.exists():
        approved = {**draft, 'created_at': utcnow(), 'draft_only': False,
                    'download_authorized': True, 'training_authorized': True,
                    'authorization': 'User: go ahead and start; proposed 45-slide modeling run',
                    'pilot_patients_development_only': read_json('artifacts/pilot_selection.json')['pilot_patients_development_only']}
        atomic_json(cohort_path, approved)
    else:
        if read_json(cohort_path)['slides'] != rows:
            raise ValueError('existing_cohort_differs; refusing_to_overwrite')
    if not split_path.exists():
        create_splits(cohort_path, split_path, seed=215, pilot_selection='artifacts/pilot_selection.json')
    split = read_json(split_path)
    if split['cohort_sha256'] != checksum(cohort_path):
        raise ValueError('frozen_cohort_checksum_changed')
    check_patient_separation(split['slides'])
    for path in (cohort_path, split_path):
        persist_file(path, path.relative_to(ROOT))
    return read_json(cohort_path), split


def run(draft, run_root, batch_size=32):
    import torch
    from .download import download_slide, remove_managed_raw
    from .encoder import UNI2Encoder
    from .features import extract_features
    from .inference import predict
    from .modeling import train, evaluate
    from .preprocess import TileConfig
    from .safety import prepare_checked

    run_root = Path(run_root).resolve()
    if not run_root.is_relative_to(ROOT / 'artifacts/modeling'):
        raise ValueError('run_directory_must_be_under_artifacts/modeling')
    run_root.mkdir(parents=True, exist_ok=True)
    # A crashed process releases this lock automatically. No parallel ledger writers.
    lock = (run_root / '.run.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    started = time.monotonic()
    cohort, split = initialize_run(draft, run_root)
    state_path = run_root / 'progress.json'
    state = read_json(state_path) if state_path.exists() else {
        'started_at': utcnow(), 'status': 'running', 'slides': {}, 'events': []}
    if state.get('status')=='error':
        state['events'].append({'event':'resuming_after_error','at':utcnow(),'reason':state.get('reason')})
    state.update(status='running',reason=None)
    pilot = read_json('artifacts/pilot_selection.json')
    original_pilot_ids = {r['file_id'] for r in pilot['slides']}
    protected_paths = [Path('artifacts/pilot_results.json'), Path('artifacts/pilot_selection.json')]
    protected_paths += list(Path('artifacts/slides').glob('*/embeddings.npz'))
    protected = {str(p): checksum(p) for p in protected_paths if p.is_file()}
    atomic_json(run_root / 'protected_input_checksums.json', protected)

    def save():
        state['updated_at'] = utcnow()
        atomic_json(state_path, state)
        # Prevent a download completion message changing the log during SHA256 copy.
        with LOG_LOCK:
            sync_artifacts(run_root, run_root.relative_to(ROOT))

    try:
        torch.set_num_threads(8)
        config = TileConfig(**read_json('configs/preprocessing.json'))
        smoke = read_json('artifacts/encoder_smoke.json')
        encoder = UNI2Encoder(revision=smoke['encoder']['revision'], batch_size=batch_size)
        if encoder.identifier != smoke['encoder_identifier']:
            raise ValueError('encoder_identity_differs_from_verified_pilot')
        atomic_json(run_root / 'encoder.json', {
            'verified_at': utcnow(), 'encoder': encoder.metadata, 'encoder_identifier': encoder.identifier,
            'gpu': torch.cuda.get_device_name(0), 'requested_batch_size': batch_size,
            'parameters_frozen': all(not p.requires_grad for p in encoder.model.parameters()),
            'model_in_evaluation_mode': not encoder.model.training})
        test_rows = [r for r in split['slides'] if r['split'] == 'test']
        # Pick the retained demonstration slide by identity before looking at test images or metrics.
        heldout = min(test_rows, key=lambda r: fingerprint([215, r['file_id']]))
        state['heldout_inference_file_id'] = heldout['file_id']
        save()

        def process(record):
            file_id = record['file_id']; begin = time.monotonic()
            directory = ROOT / 'artifacts/slides' / file_id
            print(f"SLIDE {len(state['slides']) + 1}/45 {record['split']} {record['candidate_class']} {file_id}", flush=True)
            raw = None
            cached = (directory / 'embeddings.npz').exists()
            if cached:
                prep, meta = verify_cache(record, directory, config, encoder)
                print('Compatible finite embedding cache verified; no raw download', flush=True)
            else:
                if file_id in original_pilot_ids:
                    raise ValueError('original_pilot_cache_missing; refusing_unplanned_redownload')
                raw = download_slide(record, budget=cohort['cumulative_raw_budget_bytes'])
                prep = prepare_checked(raw, directory, config, file_id, record['md5sum'])
                meta = extract_features(raw, directory, encoder)
                verify_cache(record, directory, config, encoder)
            receipts = sync_artifacts(directory, Path('artifacts/slides') / file_id)
            keep = file_id == heldout['file_id']
            if raw is not None and not keep:
                remove_managed_raw(raw, record, receipts)
            state['slides'][file_id] = {
                'status': 'success', 'class': record['candidate_class'], 'split': record['split'],
                'patient_id': record['patient_id'], 'cached': cached, 'embedding_shape': meta['shape'],
                'all_embeddings_finite': True, 'tiles': prep['selected_count'],
                'candidate_count': prep['candidate_count'], 'accepted_count': prep['accepted_count'],
                'rejected_count': prep['rejected_count'], 'warnings': prep['warnings'],
                'elapsed_seconds_this_attempt': time.monotonic() - begin,
                'raw_retained_for_inference': keep, 'persistent_receipts': receipts}
            save()
            print(f"PERSISTED {len(state['slides'])}/45 elapsed={time.monotonic()-started:.1f}s", flush=True)

        # Test patients are processed only after training/validation choices are fixed.
        def download(record):
            return download_slide(record,budget=cohort['cumulative_raw_budget_bytes'])
        def cached(record):
            return (ROOT/'artifacts/slides'/record['file_id']/'embeddings.npz').exists()
        development=[record for record in split['slides'] if record['split']!='test']
        process_with_prefetch(development,process,download,cached)
        model_root = run_root / 'model'
        if not (model_root / 'model.json').exists():
            state['stage'] = 'fitting_logistic_regression'; save()
            model = train(run_root / 'splits.json', ROOT / 'artifacts/slides', model_root)
            state['events'].append({'event': 'model_frozen_before_test_processing', 'at': utcnow(),
                                    'model_identifier': model['model_identifier']})
            save()
        state['stage'] = 'heldout_processing'; save()
        process_with_prefetch(test_rows,process,download,cached)
        for name in ('validation', 'test'):
            output = run_root / f'evaluation_{name}'
            if not (output / 'metrics.json').exists():
                evaluate(run_root / 'splits.json', ROOT / 'artifacts/slides', model_root, name, output)
                save()
        state['stage'] = 'renamed_heldout_inference'; save()
        del encoder
        torch.cuda.empty_cache()
        prediction_root = run_root / 'inference_arbitrary_filename'
        if not (prediction_root / 'prediction.json').exists():
            source = Path('/tmp/lungcancer-raw') / f"{heldout['file_id']}.svs"
            if not source.exists() or checksum(source, 'md5') != heldout['md5sum']:
                raise ValueError('heldout_raw_missing_or_changed; no_automatic_redownload')
            arbitrary = Path('/tmp/lungcancer-inference/unknown_slide.svs')
            arbitrary.parent.mkdir(parents=True, exist_ok=True)
            if arbitrary.exists():
                if checksum(arbitrary, 'md5') != heldout['md5sum']:
                    raise ValueError('existing_arbitrary_path_differs; preserving')
            else:
                os.link(source, arbitrary)
            prediction = predict(arbitrary, model_root, prediction_root)
            if prediction['status'] != 'success':
                save()
                raise RuntimeError('real_inference_failed: ' + prediction['reason'])
        prediction = read_json(prediction_root / 'prediction.json')
        expected = next(p for p in read_json(run_root / 'evaluation_test/predictions.json')
                        if p['file_id'] == heldout['file_id'])
        maximum_delta = max(abs(prediction['class_probabilities'][c] - expected['class_probabilities'][c]) for c in CLASSES)
        if prediction.get('status') != 'success' or prediction['predicted_class'] != expected['predicted_class'] or maximum_delta > 1e-4:
            raise ValueError('renamed_inference_disagrees_with_heldout_prediction')
        if prediction['source_md5'] != heldout['md5sum']:
            raise ValueError('renamed_inference_source_checksum_mismatch')
        atomic_json(run_root / 'inference_verification.json', {
            'status': 'success', 'actual_input_path': '/tmp/lungcancer-inference/unknown_slide.svs',
            'source_file_id': heldout['file_id'], 'source_md5': heldout['md5sum'], 'split': 'test',
            'no_filename_or_diagnosis_inputs': True, 'agrees_with_test_prediction': True,
            'maximum_probability_difference': maximum_delta, 'float32_comparison_tolerance': 1e-4})
        for path, digest in protected.items():
            if checksum(path) != digest:
                raise ValueError('original_pilot_artifact_changed')
        state.update(status='success', stage='complete', finished_at=utcnow(),
                     elapsed_seconds_this_attempt=time.monotonic()-started,
                     download_ledger=read_json('artifacts/download_ledger.json'))
        from datetime import datetime
        state['elapsed_seconds_total']=(datetime.fromisoformat(state['finished_at'])-
                                        datetime.fromisoformat(state['started_at'])).total_seconds()
        save()
        # Derived inference and source features have now both been persisted and reread.
        raw = Path('/tmp/lungcancer-raw') / f"{heldout['file_id']}.svs"
        if raw.exists():
            receipts = state['slides'][heldout['file_id']]['persistent_receipts']
            remove_managed_raw(raw, heldout, receipts)
        arbitrary = Path('/tmp/lungcancer-inference/unknown_slide.svs')
        if arbitrary.exists() and checksum(arbitrary, 'md5') == heldout['md5sum']:
            arbitrary.unlink()
        state['retained_raw_deleted_after_verified_inference_persistence'] = True
        save()
        print(f'REAL MODELING RUN COMPLETE: {run_root}', flush=True)
        return state
    except Exception as exc:
        state.update(status='error', reason=str(exc), stage=state.get('stage', 'processing'))
        save()
        raise
    finally:
        lock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', required=True)
    parser.add_argument('--run-root', required=True)
    parser.add_argument('--batch-size', type=int, default=32, choices=range(1, 33))
    args = parser.parse_args()
    root = Path(args.run_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    class Tee:
        def __init__(self, console, log):
            self.console, self.log = console, log
        def write(self, value):
            with LOG_LOCK:
                self.console.write(value); self.log.write(value); self.log.flush()
            return len(value)
        def flush(self):
            with LOG_LOCK:
                self.console.flush(); self.log.flush()
        def isatty(self):
            return False
    with (root / 'run.log').open('a', buffering=1) as log:
        with contextlib.redirect_stdout(Tee(sys.stdout, log)), contextlib.redirect_stderr(Tee(sys.stderr, log)):
            try:
                run(args.draft, root, args.batch_size)
            except Exception:
                traceback.print_exc()
                raise SystemExit(1)
            finally:
                log.flush()
                persist_file(root / 'run.log', (root / 'run.log').relative_to(ROOT))


if __name__ == '__main__':
    main()
