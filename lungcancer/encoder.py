"""Official UNI2-h architecture, pinned Hub revision, evaluation transforms."""
from pathlib import Path
import time
import numpy as np
from .common import atomic_json, fingerprint, utcnow

REPOSITORY = 'MahmoodLab/UNI2-h'
DIMENSION = 1536


class UNI2Encoder:
    def __init__(self, revision=None, batch_size=16):
        import torch
        import timm
        from huggingface_hub import HfApi, hf_hub_download
        from timm.data import resolve_data_config, create_transform

        if not torch.cuda.is_available():
            raise RuntimeError('cuda_unavailable: UNI2-h requires the approved GPU process')
        self.torch = torch
        self.batch_size = batch_size
        revision = revision or HfApi().model_info(REPOSITORY).sha
        self.revision = revision
        # This is the architecture in the official model card, with strict pretrained loading.
        kwargs = dict(img_size=224, patch_size=14, depth=24, num_heads=24,
                      init_values=1e-5, embed_dim=1536, mlp_ratio=2.66667*2,
                      num_classes=0, no_embed_class=True,
                      mlp_layer=timm.layers.SwiGLUPacked, act_layer=torch.nn.SiLU,
                      reg_tokens=8, dynamic_img_size=True)
        print(f'Loading {REPOSITORY} revision {revision}', flush=True)
        self.model = timm.create_model(f'hf-hub:{REPOSITORY}@{revision}', pretrained=True, **kwargs)
        self.data_config = resolve_data_config(self.model.pretrained_cfg, model=self.model)
        self.transform = create_transform(**self.data_config, is_training=False)
        self.model.requires_grad_(False).eval().to('cuda')
        checkpoint = Path(hf_hub_download(REPOSITORY, 'pytorch_model.bin', revision=revision))
        # Hub cache blob identity is revision-pinned; capture checkpoint bytes SHA256 once.
        from .common import checksum
        self.metadata = {
            'repository': REPOSITORY, 'revision': revision,
            'checkpoint_sha256': checksum(checkpoint), 'embedding_dimension': DIMENSION,
            'architecture': {**{k:v for k,v in kwargs.items() if k not in {'mlp_layer','act_layer'}},
                             'mlp_layer':'timm.layers.SwiGLUPacked', 'act_layer':'torch.nn.SiLU'},
            'data_config': self.data_config, 'transform': repr(self.transform),
            'inference_precision': 'float32', 'timm_version': timm.__version__,
            'torch_version': torch.__version__, 'frozen': True, 'evaluation_mode': True,
        }
        self.identifier = fingerprint(self.metadata)

    def encode(self, images):
        torch = self.torch
        result = []
        offset = 0
        while offset < len(images):
            count = min(self.batch_size, len(images)-offset)
            try:
                batch = torch.stack([self.transform(im) for im in images[offset:offset+count]]).to('cuda')
                with torch.inference_mode():
                    output = self.model(batch)
                if output.ndim != 2 or output.shape != (count, DIMENSION) or not torch.isfinite(output).all():
                    raise RuntimeError('invalid_uni2_embedding_shape_or_nonfinite_values')
                result.append(output.float().cpu().numpy())
                del batch, output
                offset += count
            except torch.cuda.OutOfMemoryError:
                if count == 1:
                    raise RuntimeError('gpu_memory_insufficient_for_one_uni2_tile') from None
                self.batch_size = max(1, count//2)
                if 'batch' in locals():
                    del batch
                torch.cuda.empty_cache()
                print(f'CUDA memory pressure: reducing batch size to {self.batch_size}', flush=True)
        return np.concatenate(result) if result else np.empty((0, DIMENSION), dtype=np.float32)


def smoke_test(output, revision=None):
    from PIL import Image
    start = time.monotonic()
    encoder = UNI2Encoder(revision=revision, batch_size=2)
    rng = np.random.default_rng(215)
    # Deliberately synthetic inputs validate tensor plumbing only, never tissue performance.
    images = [Image.fromarray(rng.integers(0, 256, (224,224,3), dtype=np.uint8)) for _ in range(2)]
    features = encoder.encode(images)
    torch = encoder.torch
    report = {'status':'success', 'test_kind':'synthetic_encoder_smoke_only',
              'timestamp':utcnow(), 'shape':list(features.shape), 'all_finite':bool(np.isfinite(features).all()),
              'gpu':torch.cuda.get_device_name(0),
              'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated(),
              'elapsed_seconds':time.monotonic()-start, 'encoder':encoder.metadata,
              'encoder_identifier':encoder.identifier}
    atomic_json(output, report)
    print(f'Synthetic UNI2-h smoke passed: {features.shape}, finite={report["all_finite"]}', flush=True)
    return report
