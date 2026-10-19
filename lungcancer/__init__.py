"""Reproducible TCGA lung slide engineering prototype."""
from pathlib import Path
import sys

# Project-local OpenSlide wheels; never replaces Colab's PyTorch/CUDA packages.
_vendor = Path(__file__).resolve().parents[1] / '.vendor'
if _vendor.is_dir():
    sys.path.insert(0, str(_vendor))

__version__ = '0.1.0'
