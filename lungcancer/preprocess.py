"""Region-based WSI tiling. All saved x,y coordinates are level-0 upper left."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json
import math
import os
from pathlib import Path
import tempfile
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from .common import atomic_json, checksum, fingerprint, read_json


@dataclass(frozen=True)
class TileConfig:
    target_mpp: float = 0.5
    tile_size: int = 224
    max_tiles: int = 512
    minimum_tissue_fraction: float = 0.5
    thumbnail_max: int = 4096
    saturation_min: float = 0.08
    value_min: float = 0.15
    value_max: float = 0.98
    mask_min_component_pixels: int = 16
    mask_closing_iterations: int = 1
    seed: int = 215

    def __post_init__(self):
        if self.target_mpp <= 0 or self.tile_size != 224 or self.max_tiles < 1:
            raise ValueError('invalid_tile_config: UNI2-h requires 224-pixel output tiles')
        if not 0 <= self.minimum_tissue_fraction <= 1:
            raise ValueError('invalid_tissue_threshold')


def atomic_npz(path, **arrays):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('wb',dir=path.parent,prefix='.writing-',delete=False) as f:
        np.savez_compressed(f,**arrays); f.flush(); os.fsync(f.fileno()); temporary=f.name
    os.replace(temporary,path)


def rgb_white(image):
    if image.mode=='RGBA':
        return Image.alpha_composite(Image.new('RGBA',image.size,'white'),image).convert('RGB')
    return image.convert('RGB')


def scale_metadata(properties):
    values=[]
    for key in ['openslide.mpp-x','openslide.mpp-y']:
        try: value=float(properties[key])
        except (KeyError,ValueError,TypeError):
            raise ValueError('missing_or_invalid_physical_scale: requires openslide.mpp-x and openslide.mpp-y') from None
        if not math.isfinite(value) or not 0.1<=value<=2.0:
            raise ValueError('implausible_physical_scale')
        values.append(value)
    if max(values)/min(values)>1.25:
        raise ValueError('implausibly_anisotropic_physical_scale')
    return tuple(values)


def extraction_geometry(dimensions,mpp,config,level_downsamples):
    mx,my=mpp
    w0=max(1,round(config.tile_size*config.target_mpp/mx))
    h0=max(1,round(config.tile_size*config.target_mpp/my))
    ideal=min(w0/config.tile_size,h0/config.tile_size)
    # Choose a level at least as fine as the output, avoiding a coarse-level upsample.
    eligible=[i for i,d in enumerate(level_downsamples) if d<=ideal*(1+1e-6)]
    level=max(eligible,key=lambda i:level_downsamples[i]) if eligible else 0
    ds=float(level_downsamples[level])
    return {'level':level,'level_downsample':ds,'footprint_level0':[w0,h0],
            'read_size_level':[math.ceil(w0/ds),math.ceil(h0/ds)],
            'crop_box_level':[0,0,w0/ds,h0/ds],
            'actual_output_mpp':[w0*mx/config.tile_size,h0*my/config.tile_size]}


def tissue_mask(thumbnail,config):
    hsv=np.asarray(thumbnail.convert('HSV'),dtype=np.float32)/255.0
    mask=(hsv[:,:,1]>=config.saturation_min)&(hsv[:,:,2]>=config.value_min)&(hsv[:,:,2]<=config.value_max)
    if config.mask_closing_iterations:
        mask=ndimage.binary_closing(mask,structure=ndimage.generate_binary_structure(2,1),
                                   iterations=config.mask_closing_iterations)
    labels,n=ndimage.label(mask)
    if n:
        sizes=np.bincount(labels.ravel()); keep=sizes>=config.mask_min_component_pixels; keep[0]=False
        mask=keep[labels]
    return mask


def mask_coverage(mask,coords,footprint,dimensions):
    """Conservative floor/ceil mapping using separate true X and Y ratios."""
    height,width=mask.shape; fullw,fullh=dimensions; w0,h0=footprint
    if np.any(coords<0) or np.any(coords[:,0]+w0>fullw) or np.any(coords[:,1]+h0>fullh):
        raise ValueError('tile_coordinates_out_of_bounds')
    x0=np.floor(coords[:,0]*width/fullw).astype(int)
    y0=np.floor(coords[:,1]*height/fullh).astype(int)
    x1=np.minimum(width,np.ceil((coords[:,0]+w0)*width/fullw).astype(int))
    y1=np.minimum(height,np.ceil((coords[:,1]+h0)*height/fullh).astype(int))
    integral=np.pad(mask.astype(np.int64),((1,0),(1,0))).cumsum(0).cumsum(1)
    sums=integral[y1,x1]-integral[y0,x1]-integral[y1,x0]+integral[y0,x0]
    return sums/((x1-x0)*(y1-y0))


def distributed_indices(coords,limit,seed):
    if len(coords)<=limit: return np.arange(len(coords),dtype=np.int64)
    # Deterministic farthest-point sampling covers separated tissue fragments.
    points=coords.astype(np.float64)
    points/=max(1,float(np.ptp(points,axis=0).max()))
    current=int(np.random.default_rng(seed).integers(len(points)))
    distance=np.full(len(points),np.inf)
    selected=[]
    for _ in range(limit):
        selected.append(current)
        distance=np.minimum(distance,np.sum((points-points[current])**2,axis=1))
        distance[selected]=-1
        current=int(np.argmax(distance))
    # Reading order is fixed row-major; features preserve this order exactly.
    return np.sort(np.asarray(selected,dtype=np.int64))


def read_tile(slide,coordinate,geometry,tile_size=224):
    image=rgb_white(slide.read_region(tuple(map(int,coordinate)),geometry['level'],tuple(geometry['read_size_level'])))
    return image.resize((tile_size,tile_size),resample=Image.Resampling.LANCZOS,box=tuple(geometry['crop_box_level']))


def draw_overlay(thumbnail,coords,footprint,dimensions):
    overlay=thumbnail.copy(); draw=ImageDraw.Draw(overlay)
    sx=overlay.width/dimensions[0]; sy=overlay.height/dimensions[1]
    for x,y in coords:
        draw.rectangle((x*sx,y*sy,(x+footprint[0])*sx,(y+footprint[1])*sy),outline=(255,20,20),width=2)
    return overlay


def prepare_slide(path,output,config=None,file_id=None,expected_md5=None):
    import openslide
    config=config or TileConfig(); path=Path(path); output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    source_md5=checksum(path,'md5')
    if expected_md5 and source_md5!=expected_md5: raise ValueError('source_md5_mismatch')
    key=fingerprint({'source_md5':source_md5,'config':asdict(config),
                     'implementation_sha256':checksum(__file__),'openslide_version':openslide.__library_version__})
    meta_path=output/'preprocessing.json'
    if meta_path.exists():
        previous=read_json(meta_path)
        if previous.get('fingerprint')==key and previous.get('status')=='success':
            if checksum(output/'coordinates.npz')==previous['coordinates_file_sha256']:
                print(f'Preprocessing cache verified: {path.name}',flush=True)
                return previous
    try:
        with openslide.OpenSlide(str(path)) as slide:
            mpp=scale_metadata(slide.properties)
            dims=tuple(slide.dimensions)
            levels=[float(x) for x in slide.level_downsamples]
            geometry=extraction_geometry(dims,mpp,config,levels)
            thumb=rgb_white(slide.get_thumbnail((config.thumbnail_max,config.thumbnail_max)))
            mask=tissue_mask(thumb,config)
            w0,h0=geometry['footprint_level0']
            xs=np.arange(0,dims[0]-w0+1,w0,dtype=np.int64)
            ys=np.arange(0,dims[1]-h0+1,h0,dtype=np.int64)
            xx,yy=np.meshgrid(xs,ys)
            candidates=np.column_stack([xx.ravel(),yy.ravel()])
            if not len(candidates): raise ValueError('slide_smaller_than_one_physical_tile')
            coverage=mask_coverage(mask,candidates,(w0,h0),dims)
            accepted=np.flatnonzero(coverage>=config.minimum_tissue_fraction)
            warnings=[]
            if len(accepted)==0: raise ValueError('no_usable_tiles_at_configured_tissue_threshold')
            chosen=accepted[distributed_indices(candidates[accepted],config.max_tiles,config.seed)]
            coords=candidates[chosen]
            if len(coords)<32: warnings.append('fewer_than_32_tiles')
            if len(accepted)/len(candidates)<0.05: warnings.append('low_fraction_of_grid_passes_tissue_threshold')
            if min(w0*thumb.width/dims[0],h0*thumb.height/dims[1])<4:
                warnings.append('thumbnail_mask_has_fewer_than_4_pixels_across_tile')
            if max(mpp)>config.target_mpp*1.05: warnings.append('native_resolution_coarser_than_requested_output')
            if abs(mpp[0]-mpp[1])>0.01*min(mpp): warnings.append('anisotropic_native_resolution_resampled_per_axis')
            if slide.color_profile is not None: warnings.append('embedded_icc_profile_present_not_applied')
            thumb.save(output/'thumbnail.jpg',quality=90)
            tinted=np.asarray(thumb).copy()
            tinted[mask]=(tinted[mask]*0.55+np.array([20,200,30])*0.45).astype(np.uint8)
            Image.fromarray(tinted).save(output/'tissue_mask_overlay.jpg',quality=90)
            Image.fromarray(mask.astype(np.uint8)*255).save(output/'tissue_mask.png')
            draw_overlay(thumb,coords,(w0,h0),dims).save(output/'selected_tiles_overlay.jpg',quality=90)
            representative=np.unique(np.linspace(0,len(coords)-1,min(24,len(coords))).astype(int))
            columns=6; rows=math.ceil(len(representative)/columns)
            sheet=Image.new('RGB',(224*columns,248*rows),'white'); draw=ImageDraw.Draw(sheet)
            for position,index in enumerate(representative):
                tile=read_tile(slide,coords[index],geometry,config.tile_size)
                px=(position%columns)*224; py=(position//columns)*248
                sheet.paste(tile,(px,py)); draw.text((px+3,py+225),f'i={index} tissue={coverage[chosen[index]]:.2f}',fill='black')
            sheet.save(output/'contact_sheet.jpg',quality=92)
            atomic_npz(output/'coordinates.npz',coordinates=coords,tissue_coverage=coverage[chosen])
            meta={'status':'success','fingerprint':key,'source_md5':source_md5,'file_id':file_id,
                  'config':asdict(config),'dimensions_level0':list(dims),
                  'level_dimensions':[list(x) for x in slide.level_dimensions],'level_downsamples':levels,
                  'mpp_level0':list(mpp),'mpp_provenance':['openslide.mpp-x','openslide.mpp-y'],
                  'objective_power_record_only':slide.properties.get('openslide.objective-power'),
                  'geometry':geometry,'coordinate_system':'level0_upper_left_xy_pixels',
                  'thumbnail_size':list(thumb.size),'thumbnail_to_level0_xy':[dims[0]/thumb.width,dims[1]/thumb.height],
                  'mask_method':'HSV S>=0.08, 0.15<=V<=0.98; 1 cross-structure binary closing; remove components <16 thumbnail pixels; retain airspaces',
                  'sampling_method':'deterministic farthest-point selection; stored row-major',
                  'candidate_count':len(candidates),'accepted_count':len(accepted),'selected_count':len(coords),
                  'rejected_count':len(candidates)-len(accepted),
                  'rejection_reasons':{'below_tissue_coverage_threshold':len(candidates)-len(accepted)},
                  'accepted_but_not_sampled':len(accepted)-len(coords),
                  'partial_edge_positions_excluded':math.ceil(dims[0]/w0)*math.ceil(dims[1]/h0)-len(candidates),
                  'coverage_threshold_counts':{str(t):int(np.sum(coverage>=t)) for t in [0.1,0.25,0.5,0.75]},
                  'coverage_histogram':np.histogram(coverage,bins=np.linspace(0,1,11))[0].tolist(),
                  'selected_coverage_min_median_max':[float(coverage[chosen].min()),float(np.median(coverage[chosen])),float(coverage[chosen].max())],
                  'mask_fraction_of_thumbnail':float(mask.mean()),'warnings':warnings,
                  'coordinates_file_sha256':checksum(output/'coordinates.npz')}
            atomic_json(meta_path,meta)
            return meta
    except Exception as exc:
        atomic_json(output/'processing_failure.json',{'status':'error','reason':str(exc),'source_md5':source_md5,'fingerprint':key})
        raise
