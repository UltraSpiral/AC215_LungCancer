"""Select new frozen slides for the Milestone 3 cohort from a GDC discovery manifest."""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lungcancer.common import CLASSES, atomic_json, checksum, fingerprint, read_json, utcnow  # noqa: E402

PREPARATION = 'frozen'
RULES = ('Included, frozen, at most max_file_size bytes; patients from earlier cohorts and the pilot excluded; '
         'one slide per patient across all classes; distinct MD5s; classes filled in turn; ranked by explicit '
         'preparation metadata, sites shared by all classes, unused sites within the class, then seeded hash order.')


def used_patients(cohort_path: Path, pilot_path: Path | None) -> set[str]:
    patients = {r['case_id'] for r in read_json(cohort_path)['slides']}
    if pilot_path:
        pilot = read_json(pilot_path)
        patients |= set(pilot.get('pilot_patients_development_only') or [r['case_id'] for r in pilot['slides']])
    return patients


def candidates(manifest: list[dict], excluded: set[str], max_size: int) -> list[dict]:
    return [r for r in manifest
            if r['decision'] == 'include'
            and r['preparation'] == PREPARATION
            and int(r['file_size']) <= max_size
            and r['case_id'] not in excluded]


def select(pool: list[dict], per_class: int, seed: int) -> list[dict]:
    sites = [{r['source_site'] for r in pool if r['candidate_class'] == c and r['source_site']} for c in CLASSES]
    shared = set.intersection(*sites) if all(sites) else set()
    chosen, patients, md5s = [], set(), set()
    for _ in range(per_class):
        for cls in CLASSES:
            used_sites = {r['source_site'] for r in chosen if r['candidate_class'] == cls}
            eligible = [r for r in pool if r['candidate_class'] == cls
                        and r['case_id'] not in patients and r['md5sum'] not in md5s]
            if not eligible:
                continue
            eligible.sort(key=lambda r: (r['preparation_provenance'] != 'explicit_metadata',
                                         r['source_site'] not in shared,
                                         r['source_site'] in used_sites,
                                         fingerprint([seed, r['case_id'], r['file_id']])))
            pick = eligible[0]
            chosen.append(pick)
            patients.add(pick['case_id'])
            md5s.add(pick['md5sum'])
    return chosen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='artifacts/discovery_ms3/manifest.json')
    parser.add_argument('--previous-cohort', default='configs/modeling_snapshot_45.json')
    parser.add_argument('--pilot', help='pilot_selection.json whose patients are also excluded')
    parser.add_argument('--per-class', type=int, default=20)
    parser.add_argument('--max-file-size', type=int, default=300_000_000)
    parser.add_argument('--seed', type=int, default=215)
    parser.add_argument('--output', default='artifacts/ms3_cohort/selection.json')
    args = parser.parse_args()

    manifest_path, cohort_path = Path(args.manifest), Path(args.previous_cohort)
    pilot_path = Path(args.pilot) if args.pilot else None
    excluded = used_patients(cohort_path, pilot_path)
    pool = candidates(read_json(manifest_path), excluded, args.max_file_size)
    chosen = select(pool, args.per_class, args.seed)

    counts = Counter(r['candidate_class'] for r in chosen)
    total = sum(int(r['file_size']) for r in chosen)
    report = {
        'created_at': utcnow(),
        'draft_only': True,
        'seed': args.seed,
        'preparation': PREPARATION,
        'target_per_class': args.per_class,
        'max_file_size_bytes': args.max_file_size,
        'rules': RULES,
        'inputs': {
            'manifest_sha256': checksum(manifest_path),
            'previous_cohort_sha256': checksum(cohort_path),
            'pilot_sha256': checksum(pilot_path) if pilot_path else None,
        },
        'excluded_patients': len(excluded),
        'eligible_slides': dict(Counter(r['candidate_class'] for r in pool)),
        'counts': {c: counts.get(c, 0) for c in CLASSES},
        'selected_bytes': total,
        'source_sites': len({r['source_site'] for r in chosen}),
        'complete_target': all(counts.get(c, 0) == args.per_class for c in CLASSES),
        'slides': chosen,
    }
    atomic_json(Path(args.output), report)

    print(f'Excluded {len(excluded)} patients from earlier cohorts.')
    print(f'Eligible frozen slides: {report["eligible_slides"]}')
    print(f'Selected: {report["counts"]} from {report["source_sites"]} sites, {total / 1e9:.2f} GB')
    print(f'Complete: {report["complete_target"]}. Saved {args.output}')
    return 0 if report['complete_target'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
