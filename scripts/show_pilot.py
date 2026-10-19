"""Display the three saved class audit panels inline; no downloads or models.

Colab: %run /content/LungCancer/scripts/show_pilot.py
Terminal validation: python scripts/show_pilot.py --check
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

CLASSES = ('non_tumor', 'adenocarcinoma', 'squamous')
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def panel_paths(artifact_root=None):
    roots = [Path(artifact_root)] if artifact_root else [
        PROJECT_ROOT / 'artifacts',
        Path('/content/drive/MyDrive/LungCancer_AC215/artifacts'),
    ]
    for root in roots:
        panels = [root / 'pilot_review' / f'{label}_audit.jpg' for label in CLASSES]
        if all(path.is_file() for path in panels):
            return root, panels
    raise FileNotFoundError('Three complete pilot panels were not found locally or in mounted Drive.')


def show_pilot(artifact_root=None, check_only=False):
    from PIL import Image as PILImage
    root, panels = panel_paths(artifact_root)
    summary = json.loads((root / 'pilot_review' / 'summary.json').read_text())
    for path in panels:
        with PILImage.open(path) as image:
            image.verify()
    if check_only:
        for label, path in zip(CLASSES, panels):
            print(f'{label}: {summary["counts"][label]} | {path}')
        return panels

    from IPython.display import Image, Markdown, display
    display(Markdown(
        '**Pilot review: three class panels covering all nine slides.** '
        'Each row is one slide; columns show thumbnail, tissue mask, '
        'analyzed tile locations, and representative tile contact sheet. '
        'Red boxes mark analyzed locations only.'
    ))
    for label, path in zip(CLASSES, panels):
        counts = summary['counts'][label]
        display(Markdown(f'**{label}: {counts["slides"]} slides, '
                         f'{counts["patients"]} independent patients**'))
        display(Image(filename=str(path), width=1600, embed=True))
    return panels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, help='Artifact directory; defaults to local, then Drive.')
    parser.add_argument('--check', action='store_true', help='Validate files without notebook display.')
    args = parser.parse_args()
    show_pilot(args.root, args.check)


if __name__ == '__main__':
    main()
