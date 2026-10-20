"""One Colab cell: %run /content/LungCancer/scripts/show_modeling.py

Reads completed artifacts only; never trains, extracts, or downloads.
"""
from pathlib import Path
import json
from IPython.display import Image, Markdown, display

RUN = Path('/content/LungCancer/artifacts/modeling/20261020T0220Z-audit2')
if not (RUN/'verified_results.json').exists():
    RUN = Path('/content/drive/MyDrive/LungCancer_AC215/artifacts/modeling/20261020T0220Z-audit2')
if not (RUN/'verified_results.json').exists():
    raise RuntimeError('Verified modeling report is not complete; check progress.json first.')
result=json.loads((RUN/'verified_results.json').read_text())
display(Markdown((RUN/'RESULTS.md').read_text()))
display(Image(filename=str(RUN/'test_confusion_matrix.png'),width=650))
display(Markdown('**Analyzed locations on an arbitrarily named held-out slide. This is not a tumor heatmap.**'))
display(Image(filename=str(RUN/'inference_arbitrary_filename/analyzed_tiles_overlay.jpg'),width=900))
