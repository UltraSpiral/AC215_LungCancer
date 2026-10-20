"""Resource guard: never let OpenSlide's thumbnail helper decode a huge level."""
from pathlib import Path
import math
from .common import atomic_json
from .preprocess import prepare_slide,TileConfig
from .common import checksum,fingerprint,read_json


def preprocessing_fingerprint(source_md5,config,metadata=None):
    """Preserve identical legacy preprocessing; separately version the new fallback."""
    import openslide
    from . import preprocess
    base=fingerprint({'source_md5':source_md5,'config':config,
                      'implementation_sha256':checksum(preprocess.__file__),
                      'openslide_version':openslide.__library_version__})
    policy=(metadata or {}).get('thumbnail_policy')
    if policy is None:
        return base
    if policy.get('method')!='bounded_coarser_pyramid_v1' or policy.get('implementation_sha256')!=checksum(__file__):
        raise ValueError('thumbnail_policy_implementation_mismatch')
    return fingerprint({'base_preprocessing_fingerprint':base,'thumbnail_policy':policy})


def prepare_checked(path,output,config=None,file_id=None,expected_md5=None):
    import openslide
    config=config or TileConfig()
    try:
        with openslide.OpenSlide(str(path)) as slide:
            ideal=max(slide.dimensions)/config.thumbnail_max
            candidates=[i for i,d in enumerate(slide.level_downsamples) if d<=ideal]
            level=max(candidates,key=lambda i:slide.level_downsamples[i]) if candidates else 0
            width,height=slide.level_dimensions[level]
            fallback=None
            if width*height>64_000_000:
                smaller=[i for i,d in enumerate(slide.level_downsamples)
                         if d>slide.level_downsamples[level] and
                         math.prod(slide.level_dimensions[i])<=64_000_000]
                if not smaller:
                    raise ValueError('no_memory_safe_thumbnail_pyramid_level: refusing_large_region_decode')
                fallback=min(smaller,key=lambda i:slide.level_downsamples[i])
        if fallback is not None:
            from unittest.mock import patch
            from PIL import Image
            original=openslide.OpenSlide
            class BoundedThumbnailSlide:
                def __init__(self,*args,**kwargs): self.slide=original(*args,**kwargs)
                def __getattr__(self,name): return getattr(self.slide,name)
                def __enter__(self): return self
                def __exit__(self,*args): self.slide.close()
                def get_thumbnail(self,size):
                    # Read one bounded existing pyramid level, never full-resolution.
                    region=self.slide.read_region((0,0),fallback,self.slide.level_dimensions[fallback])
                    background='#'+self.slide.properties.get('openslide.background-color','ffffff')
                    image=Image.new('RGB',region.size,background)
                    image.paste(region,mask=region.getchannel('A'))
                    image.thumbnail(size,Image.Resampling.LANCZOS)
                    return image
            with patch.object(openslide,'OpenSlide',BoundedThumbnailSlide):
                result=prepare_slide(path,output,config,file_id,expected_md5)
            result['thumbnail_policy']={'method':'bounded_coarser_pyramid_v1',
                                        'implementation_sha256':checksum(__file__),
                                        'pyramid_level':fallback,
                                        'reason':'default_thumbnail_level_exceeds_64000000_pixels'}
            result['fingerprint']=preprocessing_fingerprint(result['source_md5'],result['config'],result)
            result['warnings'].append('thumbnail_uses_bounded_coarser_pyramid_level')
            atomic_json(Path(output)/'preprocessing.json',result)
            return result
        return prepare_slide(path,output,config,file_id,expected_md5)
    except Exception as exc:
        atomic_json(Path(output)/'processing_failure.json',{'status':'error','reason':str(exc)})
        raise
