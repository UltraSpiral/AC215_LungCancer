"""Profile exactly one existing pilot SVS, without modifying pilot caches.

No acquisition is performed here. A local SVS path and the cached UNI2-h
checkpoint are required. Every CUDA measurement has explicit synchronization.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import time
from unittest.mock import patch
import numpy as np
from PIL import Image
from .common import ROOT, atomic_json, canonical, checksum, fingerprint, read_json, sync_artifacts, persist_file, utcnow
from . import preprocess
from .preprocess import TileConfig, read_tile, atomic_npz
from .safety import prepare_checked
from .features import load_features, validate_alignment


@contextmanager
def time_preprocessing_saves(counter):
    """Separate actual file encoding/writes from preprocessing CPU wall time."""
    def instrument(function):
        def wrapped(*args, **kwargs):
            start=time.perf_counter()
            try:
                return function(*args, **kwargs)
            finally:
                counter['seconds']+=time.perf_counter()-start
        return wrapped
    with patch.object(Image.Image,'save',instrument(Image.Image.save)), \
         patch.object(preprocess,'atomic_npz',instrument(preprocess.atomic_npz)), \
         patch.object(preprocess,'atomic_json',instrument(preprocess.atomic_json)):
        yield


def profile_slide(slide_path,file_id,batch_size=16,output=None,persist=True,warmup_batches=3):
    """Single serial pass over 512 selected real tiles; no mixed precision changes."""
    if not 1<=batch_size<=32: raise ValueError('profiling_batch_size_must_be_between_1_and_32')
    if warmup_batches<1: raise ValueError('profiling_requires_at_least_one_warmup_batch')
    slide_path=Path(slide_path)
    if not slide_path.is_file(): raise FileNotFoundError('raw_svs_missing; this command never downloads a slide')
    records=read_json(ROOT/'artifacts/pilot_selection.json')['slides']
    record=next((r for r in records if r['file_id']==file_id),None)
    if record is None: raise ValueError('profile_only_one_existing_selected_pilot_file')
    original_dir=ROOT/'artifacts/slides'/file_id
    protected={name:checksum(original_dir/name) for name in ['embeddings.npz','coordinates.npz','preprocessing.json']}
    cached_prep=read_json(original_dir/'preprocessing.json')
    cached_features,cached_coords,cached_meta=load_features(original_dir/'embeddings.npz')
    config=TileConfig(**cached_prep['config'])
    run_id=file_id+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output=Path(output) if output else ROOT/'artifacts/profiles'/run_id
    output.mkdir(parents=True,exist_ok=False)

    # Supported offline mode: the profiler must reuse the cached gated checkpoint.
    os.environ['HF_HUB_OFFLINE']='1'
    import torch
    import openslide
    from .encoder import UNI2Encoder
    torch.cuda.synchronize()
    start=time.perf_counter()
    encoder=UNI2Encoder(revision=cached_meta['encoder']['revision'],batch_size=batch_size)
    torch.cuda.synchronize()
    model_load_seconds=time.perf_counter()-start
    if encoder.identifier!=cached_meta['encoder_identifier']:
        raise ValueError('profiling_encoder_does_not_match_existing_pilot')

    saves={'seconds':0.0}
    start=time.perf_counter()
    with time_preprocessing_saves(saves):
        prep=prepare_checked(slide_path,output/'processing',config,file_id,record['md5sum'])
    preprocessing_wall=time.perf_counter()-start
    with np.load(output/'processing/coordinates.npz',allow_pickle=False) as data:
        coords=data['coordinates']
    if not np.array_equal(coords,cached_coords): raise ValueError('profiling_changed_tile_selection')

    # Real first-batch warm-up, measured separately. It is never called synthetic.
    start=time.perf_counter()
    with openslide.OpenSlide(str(slide_path)) as slide:
        warm_images=[read_tile(slide,c,prep['geometry'],config.tile_size) for c in coords[:batch_size]]
    warm_batch=torch.stack([encoder.transform(im) for im in warm_images]).to('cuda')
    with torch.inference_mode():
        for _ in range(warmup_batches):
            warm_output=encoder.model(warm_batch)
    torch.cuda.synchronize()
    del warm_output,warm_batch,warm_images
    warmup_seconds=time.perf_counter()-start
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    baseline_allocated=torch.cuda.memory_allocated()
    counters={name:0.0 for name in ['slide_region_reading','input_transforms_cpu','host_to_device',
                                   'uni2_forward_sync_wall','uni2_forward_cuda_events',
                                   'validation_and_device_to_host']}
    batches=[]; blocks=[]
    loop_start=time.perf_counter()
    open_start=time.perf_counter()
    with openslide.OpenSlide(str(slide_path)) as slide:
        counters['slide_region_reading']+=time.perf_counter()-open_start
        # The production extractor reads 32 regions, then evaluates batches of 16.
        for offset in range(0,len(coords),32):
            start=time.perf_counter()
            images=[read_tile(slide,c,prep['geometry'],config.tile_size) for c in coords[offset:offset+32]]
            counters['slide_region_reading']+=time.perf_counter()-start
            for inner in range(0,len(images),batch_size):
                start=time.perf_counter()
                batch=torch.stack([encoder.transform(im) for im in images[inner:inner+batch_size]])
                counters['input_transforms_cpu']+=time.perf_counter()-start
                torch.cuda.synchronize()
                start=time.perf_counter()
                batch=batch.to('cuda')
                torch.cuda.synchronize()
                counters['host_to_device']+=time.perf_counter()-start
                begin=torch.cuda.Event(enable_timing=True); end=torch.cuda.Event(enable_timing=True)
                torch.cuda.synchronize()
                start=time.perf_counter()
                begin.record()
                with torch.inference_mode():
                    prediction=encoder.model(batch)
                end.record()
                torch.cuda.synchronize()
                wall=time.perf_counter()-start
                device_seconds=begin.elapsed_time(end)/1000
                counters['uni2_forward_sync_wall']+=wall
                counters['uni2_forward_cuda_events']+=device_seconds
                start=time.perf_counter()
                if prediction.shape!=(len(batch),1536) or not bool(torch.isfinite(prediction).all().item()):
                    raise ValueError('nonfinite_or_unexpected_profile_embeddings')
                blocks.append(prediction.float().cpu().numpy())
                torch.cuda.synchronize()
                counters['validation_and_device_to_host']+=time.perf_counter()-start
                batches.append({'tiles':len(batch),'forward_sync_wall_seconds':wall,'forward_cuda_event_seconds':device_seconds})
                del batch,prediction
            print(f'Profiled {min(offset+32,len(coords))}/{len(coords)} tiles',flush=True)
    loop_wall=time.perf_counter()-loop_start
    peak_allocated=torch.cuda.max_memory_allocated()
    peak_reserved=torch.cuda.max_memory_reserved()
    start=time.perf_counter()
    features=np.concatenate(blocks).astype(np.float32)
    validate_alignment(features,coords)
    replay_max_abs_error=float(np.max(np.abs(features-cached_features)))
    cpu_finalization=time.perf_counter()-start

    start=time.perf_counter()
    profile_meta={**cached_meta,'profiling_output':True,'profiling_run_id':run_id}
    atomic_npz(output/'processing/embeddings.npz',embeddings=features,coordinates=coords,
               metadata_json=np.array(canonical(profile_meta)))
    atomic_json(output/'processing/embeddings.json',{**profile_meta,'npz_sha256':checksum(output/'processing/embeddings.npz')})
    feature_save_seconds=time.perf_counter()-start
    start=time.perf_counter()
    receipts=sync_artifacts(output,Path('artifacts/profiles')/output.name) if persist else []
    drive_persistence=time.perf_counter()-start if persist else 0.0
    steady_wall=preprocessing_wall+loop_wall+cpu_finalization+feature_save_seconds+drive_persistence
    counted_loop=sum(v for k,v in counters.items() if k!='uni2_forward_cuda_events')
    stages={
        'slide_reading_tiling_masking_sampling_and_checksums':preprocessing_wall-saves['seconds']+counters['slide_region_reading'],
        'input_transforms_cpu':counters['input_transforms_cpu'],
        'host_to_device':counters['host_to_device'],
        'uni2_forward_synchronized_wall':counters['uni2_forward_sync_wall'],
        'validation_device_to_host_and_cpu_finalization':counters['validation_and_device_to_host']+cpu_finalization,
        'local_artifact_encoding_and_saving':saves['seconds']+feature_save_seconds,
        'drive_copy_and_sha256_verification':drive_persistence,
        'loop_bookkeeping_other':loop_wall-counted_loop,
    }
    gpu_seconds=counters['uni2_forward_cuda_events']
    scenarios={str(speed):{'assumed_gpu_forward_speedup':speed,
                          'predicted_total_seconds':steady_wall-gpu_seconds+gpu_seconds/speed,
                          'predicted_total_speedup':steady_wall/(steady_wall-gpu_seconds+gpu_seconds/speed)}
               for speed in [2,3,5]}
    if any(checksum(original_dir/name)!=digest for name,digest in protected.items()):
        raise ValueError('original_pilot_cache_was_modified')
    report={
        'status':'success','profiled_at_utc':utcnow(),'profile_kind':'one_real_pilot_slide',
        'patient_id':record['patient_id'],'file_id':file_id,'source_path':str(slide_path),'source_md5':record['md5sum'],
        'representative_selection':'Median raw file size among the existing nine pilot slides; not a cohort-wide performance estimate.',
        'tiles':len(coords),'embedding_shape':list(features.shape),'all_finite':bool(np.isfinite(features).all()),
        'original_pilot_cache_unchanged':True,'replay_max_abs_embedding_difference':replay_max_abs_error,
        'gpu':torch.cuda.get_device_name(0),'total_gpu_memory_bytes':torch.cuda.get_device_properties(0).total_memory,
        'batch_size':batch_size,'batch_count':len(batches),'precision':'float32; no autocast',
        'float32_matmul_precision':torch.get_float32_matmul_precision(),
        'baseline_gpu_allocated_bytes':baseline_allocated,'peak_gpu_allocated_bytes':peak_allocated,
        'peak_gpu_reserved_bytes':peak_reserved,'model_load_seconds':model_load_seconds,
        'warmup_batches':warmup_batches,'warmup_seconds':warmup_seconds,
        'steady_slide_total_seconds':steady_wall,'stage_seconds':stages,
        'uni2_forward_cuda_event_seconds':gpu_seconds,'gpu_forward_fraction_of_total':gpu_seconds/steady_wall,
        'optimistic_total_speedup_if_gpu_forward_free':steady_wall/(steady_wall-gpu_seconds),
        'hypothetical_gpu_only_speedup_scenarios':scenarios,
        'timing_method':'perf_counter wall times; CUDA synchronize before and after GPU stages; CUDA events around model forward; peak stats reset after real-tile warm-up.',
        'limitations':['One slide, one measured pass; filesystem cache not flushed.',
                       'Model loading and warm-up reported separately from steady slide processing.',
                       'Report bookkeeping and any raw acquisition are excluded from processing stage times.',
                       'A100 scenarios are hypothetical, hold CPU/storage fixed, and are not A100 benchmarks.',
                       'No AMP, TF32, batch-size search, encoder change, or cohort reprocessing.'],
        'encoder':encoder.metadata,'batch_measurements':batches,'persistent_artifact_receipts':receipts,
    }
    atomic_json(output/'profile.json',report)
    lines=['# One-slide performance profile','',f'Profiled at {report["profiled_at_utc"]}.',
           '',f'Patient: **{record["patient_id"]}**; file `{file_id}`. Exactly one pilot slide; {len(coords)} real tiles.',
           '',f'GPU: **{report["gpu"]}**; fixed batch size **{batch_size}**; **float32**, no autocast.',
           '', '| Stage | Seconds | Share of steady slide time |','|---|---:|---:|']
    for name,value in stages.items(): lines.append(f'| {name} | {value:.4f} | {value/steady_wall:.1%} |')
    lines+=['',f'Steady slide total: **{steady_wall:.4f} s**. Model load: **{model_load_seconds:.4f} s**; '
            f'{warmup_batches} real-batch warm-ups: **{warmup_seconds:.4f} s**, reported separately.',
            '',f'CUDA-event model-forward time: **{gpu_seconds:.4f} s**. '
            'Synchronized wall timing is used for the forward stage above. Transfers are measured separately.',
            '',f'Peak allocated GPU memory: **{peak_allocated/2**30:.3f} GiB**; '
            f'peak reserved: **{peak_reserved/2**30:.3f} GiB**; model baseline: **{baseline_allocated/2**30:.3f} GiB**. '
            'These are PyTorch allocator measurements after warm-up, not total driver/NVML memory.',
            '',f'All embeddings finite: {report["all_finite"]}; maximum absolute difference from the original cached features: {replay_max_abs_error}. '
            'The original pilot caches were checksum-verified unchanged.',
            '', '## A100 assessment bounds','',
            f'Measured GPU-forward share: **{gpu_seconds/steady_wall:.1%}**. If forward time became zero, '
            f'the optimistic end-to-end upper bound would be **{report["optimistic_total_speedup_if_gpu_forward_free"]:.2f}×**.',
            '', '| Assumed GPU-only speedup | Predicted total seconds | Predicted total speedup |',
            '|---:|---:|---:|']
    for scenario in scenarios.values():
        lines.append(f'| {scenario["assumed_gpu_forward_speedup"]}× | {scenario["predicted_total_seconds"]:.4f} | {scenario["predicted_total_speedup"]:.2f}× |')
    lines+=['', 'These scenarios hold CPU/storage fixed and do not assert any measured A100 speedup. '
            'The current run uses float32; GPU capacity, memory bandwidth, and raw FP32 throughput are different constraints. '
            'NVIDIA lists L4 FP32 at 30.3 TFLOPS and 300 GB/s bandwidth, while A100 lists FP32 at 19.5 TFLOPS '
            'and substantially higher memory bandwidth. An A100 is not automatically faster for this exact FP32 path.',
            '', 'Sources: [L4 specifications](https://www.nvidia.com/en-us/data-center/l4/), '
            '[A100 specifications](https://www.nvidia.com/en-us/data-center/a100/).',
            '', '## Measurement limits','']
    lines.extend('- '+note for note in report['limitations'])
    (output/'profile.md').write_text('\n'.join(lines)+'\n')
    if persist:
        for name in ['profile.json','profile.md']:
            persist_file(output/name,Path('artifacts/profiles')/output.name/name)
    print(f'Profile saved: {output}/profile.md',flush=True)
    return report
