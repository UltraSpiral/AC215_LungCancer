"""Log the classifier C search on cached UNI2 features to Vertex AI Experiments."""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lungcancer.common import CLASSES, checksum, fingerprint, read_json  # noqa: E402
from lungcancer.modeling import (  # noqa: E402
    check_patient_separation,
    fit_classifier,
    metric_report,
    named_probabilities,
    pooled_dataset,
)

SEARCH = [0.01, 0.1, 1.0]


def git_commit() -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except Exception:
        return 'unknown'


def log_run(aiplatform, name: str, params: dict, metrics: dict) -> None:
    aiplatform.start_run(name)
    aiplatform.log_params(params)
    scores = {
        'validation_macro_f1': float(metrics['macro_f1']),
        'validation_balanced_accuracy': float(metrics['balanced_accuracy']),
    }
    for c in CLASSES:
        f1 = metrics['per_class'][c]['f1']
        auc = metrics['one_vs_rest_auroc'][c]
        if f1 is not None:
            scores[f'validation_f1_{c}'] = float(f1)
        if auc is not None:
            scores[f'validation_auroc_{c}'] = float(auc)
    aiplatform.log_metrics(scores)
    aiplatform.log_classification_metrics(
        labels=list(CLASSES),
        matrix=[[int(v) for v in row] for row in metrics['confusion_matrix']],
        display_name='validation-confusion-matrix',
    )
    aiplatform.end_run()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', default='local_data/cpu_bundle')
    parser.add_argument('--project', default='ac215-lungcancer')
    parser.add_argument('--location', default='us-central1')
    parser.add_argument('--experiment', default='lungcancer-c-search')
    parser.add_argument('--dry-run', action='store_true', help='train and report without logging')
    args = parser.parse_args()

    aiplatform = None
    if not args.dry_run:
        from google.cloud import aiplatform
        aiplatform.init(
            project=args.project,
            location=args.location,
            experiment=args.experiment,
            experiment_description='Logistic regression C search on cached UNI2 features',
            experiment_tensorboard=False,
        )

    bundle = Path(args.bundle)
    split_path = bundle / 'run' / 'splits.json'
    split = read_json(split_path)
    saved = read_json(bundle / 'run' / 'model' / 'model.json')
    records = split['slides']
    check_patient_separation(records)

    X, y, metas = pooled_dataset([r for r in records if r['split'] == 'train'], bundle / 'slides')
    Xv, yv, _ = pooled_dataset([r for r in records if r['split'] == 'validation'], bundle / 'slides')
    print(f'Loaded {len(X)} training and {len(Xv)} validation slides, {X.shape[1]} features each.')

    shared = {
        'pooling': 'mean_of_tile_embeddings',
        'scaler': 'StandardScaler fit on training slides only',
        'model': 'LogisticRegression(penalty=l2, solver=lbfgs, max_iter=3000, random_state=215)',
        'encoder_identifier': metas[0]['encoder_identifier'],
        'preprocessing_fingerprint': fingerprint(metas[0]['preprocessing_config']),
        'split_identifier': split['split_identifier'][:16],
        'split_file_sha256': checksum(split_path)[:16],
        'n_train_slides': int(len(X)),
        'n_validation_slides': int(len(Xv)),
        'n_features': int(X.shape[1]),
        'git_commit': git_commit(),
    }
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dt%H%M%S')

    results = []
    for C in SEARCH:
        metrics = metric_report(yv, named_probabilities(fit_classifier(X, y, C), Xv))
        results.append((C, metrics['macro_f1']))
        print(f'C={C}: validation macro F1 = {metrics["macro_f1"]:.3f}')
        if aiplatform:
            log_run(aiplatform, f"logreg-c{str(C).replace('.', 'p')}-{stamp}", {**shared, 'C': C}, metrics)

    from sklearn.dummy import DummyClassifier
    baseline = DummyClassifier(strategy='most_frequent').fit(X, y)
    base_metrics = metric_report(yv, named_probabilities(baseline, Xv))
    print(f'Majority baseline: validation macro F1 = {base_metrics["macro_f1"]:.3f}')
    if aiplatform:
        log_run(aiplatform, f'majority-baseline-{stamp}',
                {**shared, 'model': 'DummyClassifier(most_frequent)'}, base_metrics)

    best_f1 = max(f1 for _, f1 in results)
    best_C = next(C for C, f1 in results if f1 == best_f1)
    matches = best_C == saved['C'] and abs(best_f1 - saved['validation']['macro_f1']) < 1e-9
    print(f'Picked C={best_C} (F1 {best_f1:.3f}). Saved model: C={saved["C"]} '
          f'(F1 {saved["validation"]["macro_f1"]:.3f}). Match: {matches}')
    if aiplatform:
        print(f'Logged to experiment {args.experiment}: '
              f'https://console.cloud.google.com/vertex-ai/experiments?project={args.project}')
    return 0 if matches else 1


if __name__ == '__main__':
    raise SystemExit(main())
