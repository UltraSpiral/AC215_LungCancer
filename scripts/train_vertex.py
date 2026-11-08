"""Train the slide classifier on cached UNI2 features, log each run to Vertex AI Experiments, and save the best model."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lungcancer.common import CLASSES, checksum, fingerprint, read_json  # noqa: E402
from lungcancer.modeling import (  # noqa: E402
    check_patient_separation,
    fit_classifier,
    metric_report,
    named_probabilities,
    pooled_dataset,
)
from track_training_vertex import SEARCH, log_run  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', default='/gcs/ac215-lungcancer-data/app/cpu_bundle_audit2')
    parser.add_argument('--output', required=True, help='folder for the model and its report')
    parser.add_argument('--project', default='ac215-lungcancer')
    parser.add_argument('--location', default='us-central1')
    parser.add_argument('--experiment', default='lungcancer-training')
    parser.add_argument('--code-version', default='unknown', help='git commit the image was built from')
    parser.add_argument('--no-tracking', action='store_true', help='train without logging to Vertex AI')
    args = parser.parse_args()

    aiplatform = None
    if not args.no_tracking:
        from google.cloud import aiplatform
        aiplatform.init(project=args.project, location=args.location, experiment=args.experiment,
                        experiment_description='Slide classifier trained as a Vertex AI custom job',
                        experiment_tensorboard=False)

    bundle = Path(args.bundle)
    split_path = bundle / 'run' / 'splits.json'
    split = read_json(split_path)
    records = split['slides']
    check_patient_separation(records)
    X, y, metas = pooled_dataset([r for r in records if r['split'] == 'train'], bundle / 'slides')
    Xv, yv, _ = pooled_dataset([r for r in records if r['split'] == 'validation'], bundle / 'slides')
    print(f'Loaded {len(X)} training and {len(Xv)} validation slides, {X.shape[1]} features each.', flush=True)

    shared = {
        'pooling': 'mean_of_tile_embeddings',
        'scaler': 'StandardScaler fit on training slides only',
        'model': 'LogisticRegression(penalty=l2, solver=lbfgs, max_iter=3000, random_state=215)',
        'encoder_identifier': metas[0]['encoder_identifier'],
        'preprocessing_fingerprint': fingerprint(metas[0]['preprocessing_config']),
        'split_identifier': split['split_identifier'][:16],
        'split_file_sha256': checksum(split_path)[:16],
        'bundle_manifest_sha256': checksum(bundle / 'manifest.json')[:16],
        'n_train_slides': int(len(X)),
        'n_validation_slides': int(len(Xv)),
        'n_features': int(X.shape[1]),
        'git_commit': args.code_version,
        'runner': 'vertex_custom_job',
    }
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dt%H%M%S')

    results = []
    for C in SEARCH:
        pipeline = fit_classifier(X, y, C)
        metrics = metric_report(yv, named_probabilities(pipeline, Xv))
        results.append((C, metrics, pipeline))
        print(f'C={C}: validation macro F1 = {metrics["macro_f1"]:.3f}', flush=True)
        if aiplatform:
            log_run(aiplatform, f"job-c{str(C).replace('.', 'p')}-{stamp}", {**shared, 'C': C}, metrics)

    best_f1 = max(m['macro_f1'] for _, m, _ in results)
    best_C, best_metrics, best_pipeline = next(r for r in results if r[1]['macro_f1'] == best_f1)

    import joblib
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, output / 'classifier.joblib')
    saved = read_json(bundle / 'run' / 'model' / 'model.json')
    report = {
        'trained_at': stamp,
        'selected_C': best_C,
        'selection_metric': 'validation macro F1, first C on ties',
        'search': [{'C': C, 'validation_macro_f1': m['macro_f1']} for C, m, _ in results],
        'validation': best_metrics,
        'classes': list(CLASSES),
        'parameters': shared,
        'classifier_sha256': checksum(output / 'classifier.joblib'),
        'matches_bundle_model': best_C == saved['C']
        and abs(best_f1 - saved['validation']['macro_f1']) < 1e-9,
    }
    (output / 'training_report.json').write_text(json.dumps(report, indent=2))
    print(f'Selected C={best_C} (validation macro F1 {best_f1:.3f}). '
          f'Matches bundle model: {report["matches_bundle_model"]}. Saved to {output}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
