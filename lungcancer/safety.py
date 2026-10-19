"""Resource guard: never let OpenSlide's thumbnail helper decode a huge level."""
from pathlib import Path
import math
from .common import atomic_json
from .preprocess import prepare_slide,TileConfig


def prepare_checked(path,output,config=None,file_id=None,expected_md5=None):
    import openslide
    config=config or TileConfig()
    try:
        with openslide.OpenSlide(str(path)) as slide:
            ideal=max(slide.dimensions)/config.thumbnail_max
            candidates=[i for i,d in enumerate(slide.level_downsamples) if d<=ideal]
            level=max(candidates,key=lambda i:slide.level_downsamples[i]) if candidates else 0
            width,height=slide.level_dimensions[level]
            if width*height>64_000_000:
                raise ValueError('no_memory_safe_thumbnail_pyramid_level: refusing_large_region_decode')
        return prepare_slide(path,output,config,file_id,expected_md5)
    except Exception as exc:
        atomic_json(Path(output)/'processing_failure.json',{'status':'error','reason':str(exc)})
        raise
