# convert-slides

Turns the `.svs` whole-slide images in `frontend/sample-slides/` into Deep Zoom pyramids that the
OpenSeadragon viewer can stream:

```
frontend/public/slides/
├── index.json                    manifest of converted slides
└── TCGA-91-8496/
    ├── slide.dzi                 Deep Zoom descriptor (254 px tiles, 1 px overlap, JPEG q85)
    ├── slide_files/<level>/<col>_<row>.jpeg
    ├── thumbnail.jpg             ≤512 px, used by the minimap and sample picker
    └── metadata.json             width, height, mppX/Y, objectivePower, vendor, pyramid params
```

Run from `frontend/` (needs [uv](https://docs.astral.sh/uv/); it installs `openslide-python` and the
bundled OpenSlide library from `openslide-bin`, no Homebrew needed):

```sh
uv run tools/convert-slides/convert.py           # sample-slides/ → public/slides/
uv run tools/convert-slides/convert.py --force   # re-convert
```

Slide ids are the TCGA patient barcode (`TCGA-91-8496`). Tiles use `limit_bounds=False`, so DZI level-0
pixel coordinates equal the original slide's level-0 coordinates (useful later for tile overlays from the
model). Both the `.svs` files and the generated tiles are git-ignored.
