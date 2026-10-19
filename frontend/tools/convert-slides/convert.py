# /// script
# requires-python = ">=3.9"
# dependencies = ["openslide-python>=1.3", "openslide-bin>=4.0", "pillow>=10"]
# ///
"""Convert whole-slide images (.svs) into Deep Zoom (DZI) pyramids for OpenSeadragon.

For each slide in the input directory this writes, under <out>/<slide-id>/:

    slide.dzi            Deep Zoom descriptor
    slide_files/<L>/<col>_<row>.jpeg
    thumbnail.jpg        ~512 px long side
    metadata.json        dimensions, MPP, objective power, pyramid parameters

and a manifest <out>/index.json listing every converted slide.

Usage (uv resolves the dependencies, including the OpenSlide C library):

    uv run tools/convert-slides/convert.py                     # defaults below
    uv run tools/convert-slides/convert.py IN_DIR OUT_DIR [--force] [--quality 85]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import openslide
from openslide.deepzoom import DeepZoomGenerator

ROOT = Path(__file__).resolve().parents[2]  # frontend/
DEFAULT_IN = ROOT / "sample-slides"
DEFAULT_OUT = ROOT / "public" / "slides"

TILE_SIZE = 254  # 254 + 2×1 overlap = 256 px tiles on the wire
OVERLAP = 1
FORMAT = "jpeg"
THUMB_SIZE = 512

# Worker state (one OpenSlide handle per process).
_dz: DeepZoomGenerator | None = None


def slide_id_for(path: Path) -> str:
    """TCGA barcodes → patient-level id (TCGA-91-8496); otherwise the file stem."""
    m = re.match(r"(TCGA-[A-Z0-9]{2}-[A-Z0-9]{4})", path.name)
    return m.group(1) if m else path.stem


def _init_worker(slide_path: str) -> None:
    global _dz
    _dz = DeepZoomGenerator(openslide.OpenSlide(slide_path), TILE_SIZE, OVERLAP, limit_bounds=False)


def _write_column(args: tuple[int, int, str, int]) -> int:
    level, col, level_dir, quality = args
    assert _dz is not None
    rows = _dz.level_tiles[level][1]
    for row in range(rows):
        tile = _dz.get_tile(level, (col, row))
        if tile.mode != "RGB":
            tile = tile.convert("RGB")
        tile.save(os.path.join(level_dir, f"{col}_{row}.{FORMAT}"), quality=quality)
    return rows


def _float(props: openslide._PropertyMap, key: str) -> float | None:
    try:
        return float(props[key])
    except (KeyError, ValueError):
        return None


def convert(slide_path: Path, out_root: Path, quality: int, force: bool) -> dict:
    sid = slide_id_for(slide_path)
    out_dir = out_root / sid
    meta_path = out_dir / "metadata.json"
    if meta_path.exists() and not force:
        print(f"  {sid}: already converted (use --force to redo)")
        return json.loads(meta_path.read_text())

    slide = openslide.OpenSlide(str(slide_path))
    dz = DeepZoomGenerator(slide, TILE_SIZE, OVERLAP, limit_bounds=False)
    files_dir = out_dir / "slide_files"
    files_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    total = 0
    with ProcessPoolExecutor(initializer=_init_worker, initargs=(str(slide_path),)) as pool:
        for level in range(dz.level_count):
            level_dir = files_dir / str(level)
            level_dir.mkdir(exist_ok=True)
            cols, rows = dz.level_tiles[level]
            jobs = [(level, c, str(level_dir), quality) for c in range(cols)]
            total += sum(pool.map(_write_column, jobs, chunksize=max(1, cols // 64)))
        # tiles are written; now the descriptor
    (out_dir / "slide.dzi").write_text(dz.get_dzi(FORMAT))

    thumb = slide.get_thumbnail((THUMB_SIZE, THUMB_SIZE)).convert("RGB")
    thumb.save(out_dir / "thumbnail.jpg", quality=88)

    props = slide.properties
    width, height = slide.dimensions
    meta = {
        "id": sid,
        "sourceFile": slide_path.name,
        "width": width,
        "height": height,
        "mppX": _float(props, openslide.PROPERTY_NAME_MPP_X),
        "mppY": _float(props, openslide.PROPERTY_NAME_MPP_Y),
        "objectivePower": _float(props, openslide.PROPERTY_NAME_OBJECTIVE_POWER),
        "vendor": props.get(openslide.PROPERTY_NAME_VENDOR),
        "dzi": f"/slides/{sid}/slide.dzi",
        "thumbnail": f"/slides/{sid}/thumbnail.jpg",
        "thumbnailWidth": thumb.width,
        "thumbnailHeight": thumb.height,
        "tileSize": TILE_SIZE,
        "overlap": OVERLAP,
        "format": FORMAT,
        "levels": dz.level_count,
        "tiles": total,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  {sid}: {width}×{height}, {total} tiles in {time.time() - started:.0f}s")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?", type=Path, default=DEFAULT_IN)
    ap.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--quality", type=int, default=85, help="JPEG quality (default 85)")
    ap.add_argument("--force", action="store_true", help="re-convert slides that already exist")
    args = ap.parse_args()

    slides = sorted(args.input.glob("*.svs"))
    if not slides:
        print(f"no .svs files in {args.input}", file=sys.stderr)
        return 1
    args.output.mkdir(parents=True, exist_ok=True)
    print(f"converting {len(slides)} slide(s) → {args.output}")
    metas = [convert(p, args.output, args.quality, args.force) for p in slides]
    manifest = [{k: m[k] for k in ("id", "width", "height", "mppX", "objectivePower", "dzi", "thumbnail")} for m in metas]
    (args.output / "index.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
