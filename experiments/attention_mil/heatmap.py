"""Phase 4 (preview) / Phase 5 (final): attention heatmap for one slide.

Paints each analysed tile with its attention RANK within the slide, next to the
existing logistic-regression model's per-tile scores. Example, from the repo root:

    uv run --project experiments/attention_mil python -m experiments.attention_mil.heatmap \
        --bundle local_data/cpu_bundle --run local_outputs/attention/native-<UTC> \
        --svs local_data/cpu_bundle/sample/sample.svs \
        --file-id a2e48dce-1874-468d-a302-fd30b3107f4a --stage "native preview, not reported"
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw
from scipy.stats import rankdata, spearmanr

from lungcancer.common import CLASSES, checksum

from .data import Normalizer, load_slide
from .model import build_model

RAMP = ['#00F0FF', '#0090FF', '#1E46FF']        # low -> high
FILL_OPACITY = 0.55
THUMBNAIL_MAX = 2048
DISCLAIMER = 'Attention over a 512-tile sample of tissue; not a tumor segmentation.'


def hex_rgb(colour):
    return tuple(int(colour[i:i + 2], 16) for i in (1, 3, 5))


def rank_normalise(scores):
    """Within-slide percentile in (0, 1]. Softmax weights are mostly ~1/n with a few
    spikes, so min-max scaling would paint almost every tile the lowest colour."""
    return rankdata(scores, method='average') / len(scores)


def ramp_colour(value):
    """Linear interpolation along RAMP for value in [0, 1]."""
    stops = [np.array(hex_rgb(c), float) for c in RAMP]
    position = np.clip(value, 0, 1) * (len(stops) - 1)
    i = min(int(position), len(stops) - 2)
    return tuple(int(round(v)) for v in stops[i] + (position - i) * (stops[i + 1] - stops[i]))


def tile_box(coord, footprint, scale):
    """Level-0 tile rectangle -> thumbnail pixels (same mapping as backend create_overlay)."""
    (x, y), (w, h), (sx, sy) = coord, footprint, scale
    return (x * sx, y * sy, (x + w) * sx, (y + h) * sy)


def verify_source(svs, bundle, file_id):
    """The slide file must be the exact bytes the cached tiles came from."""
    expected = json.loads((bundle / 'slides' / file_id / 'embeddings.json').read_text())['source_md5']
    if checksum(svs, 'md5') != expected:
        raise ValueError('slide file md5 does not match the cached features; tiles would be misplaced')
    return expected


def paint(thumbnail, slide, values, scale):
    """Coloured tiles + thin grey outlines; tissue that was never sampled stays uncoloured."""
    layer = Image.new('RGBA', thumbnail.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for coord, value in zip(slide.coords, values):
        draw.rectangle(tile_box(coord, slide.footprint, scale),
                       fill=(*ramp_colour(value), int(255 * FILL_OPACITY)), outline=(110, 110, 110, 200))
    return Image.alpha_composite(thumbnail.convert('RGBA'), layer).convert('RGB')


def paint_top(thumbnail, slide, values, scale, fraction=0.10):
    """Easier-to-read view: fill only the top `fraction` of tiles; outline the rest faintly."""
    cutoff = np.quantile(values, 1 - fraction)
    layer = Image.new('RGBA', thumbnail.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for coord, value in zip(slide.coords, values):
        box = tile_box(coord, slide.footprint, scale)
        if value >= cutoff:
            draw.rectangle(box, fill=(*hex_rgb(RAMP[2]), 230), outline=(255, 255, 255, 255))
        else:
            draw.rectangle(box, outline=(120, 120, 120, 150))
    return Image.alpha_composite(thumbnail.convert('RGBA'), layer).convert('RGB')


@torch.no_grad()
def attention_for(run, seed, config, normalizer, slide):
    model = build_model(config['model'], seed)
    model.load_state_dict(torch.load(run / f'seed_{seed}' / 'model.pt', weights_only=True))
    model.eval()
    logits, alpha = model(torch.from_numpy(normalizer.transform(slide.features)))
    return torch.softmax(logits, 0).numpy().astype(float), alpha.numpy().astype(float)


def logistic_tile_scores(bundle, slide):
    """Existing model applied to EACH tile instead of the slide mean (read-only).
    Score = per-tile probability of the class that model predicts for the whole slide."""
    import joblib
    from lungcancer.modeling import named_probabilities
    meta = json.loads((bundle / 'run/model/model.json').read_text())
    path = bundle / 'run/model/classifier.joblib'
    if checksum(path) != meta['classifier_sha256']:
        raise ValueError('saved classifier checksum mismatch')
    model = joblib.load(path)
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):   # macOS Accelerate false flags
        slide_probs = named_probabilities(model, slide.features.mean(0, dtype=np.float64)[None])[0]
        tile_probs = named_probabilities(model, slide.features.astype(np.float64))
    if not (np.isfinite(slide_probs).all() and np.isfinite(tile_probs).all()):
        raise ValueError('non-finite logistic probabilities')
    predicted = int(np.argmax(slide_probs))
    return slide_probs, tile_probs[:, predicted], predicted


def figure(panels, title, caption, path):
    """Side-by-side panels with one shared rank legend."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    aspect = panels[0][0].height / panels[0][0].width
    width = 6.2 * len(panels)
    fig, axes = plt.subplots(1, len(panels), figsize=(width, 6.2 * aspect + 1.6), squeeze=False,
                             layout='constrained')
    for ax, (image, subtitle) in zip(axes[0], panels):
        ax.imshow(image); ax.set_title(subtitle, fontsize=10); ax.axis('off')
    cmap = LinearSegmentedColormap.from_list('ramp', RAMP)
    bar = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap), ax=axes[0].tolist(), orientation='horizontal',
                       fraction=0.05, shrink=0.35, ticks=[0, 1])
    bar.ax.set_xticklabels(['Low', 'High']); bar.set_label('Rank within slide (uncoloured tissue was not sampled)')
    fig.suptitle(title, fontsize=12)
    fig.supxlabel(caption, fontsize=8.5, wrap=True)
    fig.savefig(path, dpi=110, bbox_inches='tight'); plt.close(fig)


def figure_plain(panels, title, caption, path):
    """Panels without a colour legend (for the top-10% view)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    aspect = panels[0][0].height / panels[0][0].width
    fig, axes = plt.subplots(1, len(panels), figsize=(6.2 * len(panels), 6.2 * aspect + 1.0),
                             squeeze=False, layout='constrained')
    for ax, (image, subtitle) in zip(axes[0], panels):
        ax.imshow(image); ax.set_title(subtitle, fontsize=10); ax.axis('off')
    fig.suptitle(title, fontsize=12)
    fig.supxlabel(caption, fontsize=8.5, wrap=True)
    fig.savefig(path, dpi=110, bbox_inches='tight'); plt.close(fig)


def top_tiles(svs, slide, alpha, out, k=5):
    import openslide
    order = np.argsort(-alpha)[:k]
    crops = []
    with openslide.OpenSlide(str(svs)) as handle:
        for rank, i in enumerate(order, 1):
            x, y = map(int, slide.coords[i])
            crop = handle.read_region((x, y), 0, slide.footprint).convert('RGB').resize((224, 224))
            crop.save(out / f'top{rank}_tile{i}.png')
            crops.append({'rank': rank, 'tile_index': int(i), 'x': x, 'y': y, 'alpha': float(alpha[i]),
                          'file': f'top{rank}_tile{i}.png'})
    strip = Image.new('RGB', (224 * k + 8 * (k - 1), 224), 'white')
    for n, c in enumerate(crops):
        strip.paste(Image.open(out / c['file']), (n * 232, 0))
    strip.save(out / 'top_tiles.png')
    return crops


def main(argv=None):
    parser = argparse.ArgumentParser(description='Attention heatmap for one slide.')
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--run', type=Path, required=True, help='training output directory')
    parser.add_argument('--svs', type=Path, required=True)
    parser.add_argument('--file-id', required=True)
    parser.add_argument('--seed', type=int, help='default: native_preferred_seed in seed_search.json')
    parser.add_argument('--stage', required=True, help='label printed on the figure')
    parser.add_argument('--out', type=Path, help='default: <run>/heatmap_<file-id prefix>')
    parser.add_argument('--require-arm64', action='store_true')
    args = parser.parse_args(argv)
    import platform
    if args.require_arm64 and platform.machine().lower() not in {'aarch64', 'arm64'}:
        raise SystemExit(f'expected an arm64 machine, got {platform.machine()}')
    import openslide

    run_info = json.loads((args.run / 'run.json').read_text())
    search = json.loads((args.run / 'seed_search.json').read_text())
    seed = args.seed or search.get('chosen_seed') or search['native_preferred_seed']
    short = args.file_id[:8]
    out = args.out or args.run / f'heatmap_{short}'
    if out.exists():
        raise SystemExit(f'{out} already exists; refusing to overwrite')

    md5 = verify_source(args.svs, args.bundle, args.file_id)
    # Display only: the slide is scored for the picture, never used to change the model.
    slide, split = load_slide(args.bundle, args.file_id, allow_test=True)
    normalizer = Normalizer.load(args.run / 'normalization.npz')
    config = run_info['config']
    probs, alpha = attention_for(args.run, seed, config, normalizer, slide)
    all_seeds = {s: attention_for(args.run, s, config, normalizer, slide)[1] for s in config['seeds']}
    mean_rank = np.mean([rank_normalise(a) for a in all_seeds.values()], axis=0)
    lr_slide, lr_tiles, lr_class = logistic_tile_scores(args.bundle, slide)

    out.mkdir(parents=True)
    with openslide.OpenSlide(str(args.svs)) as handle:
        thumbnail = handle.get_thumbnail((THUMBNAIL_MAX, THUMBNAIL_MAX)).convert('RGB')
    scale = (thumbnail.width / slide.dimensions[0], thumbnail.height / slide.dimensions[1])
    rank = rank_normalise(alpha)
    attention_img = paint(thumbnail, slide, rank, scale)
    average_img = paint(thumbnail, slide, mean_rank, scale)
    lr_img = paint(thumbnail, slide, rank_normalise(lr_tiles), scale)
    attention_img.save(out / f'attention_overlay_{short}.png')
    lr_img.save(out / f'logistic_tiles_overlay_{short}.png')

    predicted = CLASSES[int(np.argmax(probs))]
    prob_text = ', '.join(f'{c} {p:.2f}' for c, p in zip(CLASSES, probs))
    title = (f'{args.stage} | slide {short} ({split} split, true: {slide.label_name}) | '
             f'attention seed {seed} predicts {predicted}')
    caption = (f'Attention probabilities: {prob_text}. Existing model predicts {CLASSES[lr_class]} '
               f'({lr_slide[lr_class]:.2f}). {len(slide.features)} of 1,205 tissue tiles analysed. '
               f'{DISCLAIMER} Colours are ranks within this slide, not probabilities.')
    figure([(thumbnail, 'Slide thumbnail'),
            (attention_img, f'Attention rank, seed {seed}'),
            (lr_img, f'Existing model, per-tile P({CLASSES[lr_class]}) rank')],
           title, caption, out / f'heatmap_{short}.png')
    top_caption = (f'Filled: the top 10% of analysed tiles ({int(np.ceil(0.1 * len(rank)))} of {len(rank)}). '
                   f'Grey outline: other analysed tiles. {DISCLAIMER}')
    figure_plain([(thumbnail, 'Slide thumbnail'),
                  (paint_top(thumbnail, slide, rank, scale), f'Attention top 10%, seed {seed}'),
                  (paint_top(thumbnail, slide, rank_normalise(lr_tiles), scale),
                   f'Existing model top 10%, per-tile P({CLASSES[lr_class]})')],
                 title, top_caption, out / f'top10_{short}.png')
    figure([(attention_img, f'Seed {seed} only'), (average_img, 'Mean rank over 5 seeds')],
           f'{args.stage} | single seed vs seed-averaged attention', DISCLAIMER, out / f'seed_average_{short}.png')
    crops = top_tiles(args.svs, slide, alpha, out)

    tiles = [{'x': int(c[0]), 'y': int(c[1]), 'w': int(slide.footprint[0]), 'h': int(slide.footprint[1]),
              'score': float(a), 'rank': float(r)} for c, a, r in zip(slide.coords, alpha, rank)]
    seed_agreement = {s: float(spearmanr(alpha, a).statistic) for s, a in all_seeds.items() if s != seed}
    summary = {
        'stage': args.stage, 'file_id': args.file_id, 'split': split, 'true_class': slide.label_name,
        'source_md5': md5, 'seed': seed, 'predicted_class': predicted,
        'class_probabilities': dict(zip(CLASSES, map(float, probs))),
        'logistic_slide_prediction': CLASSES[lr_class],
        'logistic_slide_probabilities': dict(zip(CLASSES, map(float, lr_slide))),
        'tiles_analysed': len(tiles), 'tissue_tiles_accepted': 1205,
        'colour_scale': 'within-slide rank of alpha (rankdata average / n); raw alpha kept as score',
        'alpha_max': float(alpha.max()), 'alpha_uniform': 1 / len(alpha),
        'top10_share_of_attention': float(np.sort(alpha)[-10:].sum()),
        'spearman_attention_vs_logistic_tile_score': float(spearmanr(alpha, lr_tiles).statistic),
        'spearman_chosen_seed_vs_other_seeds': seed_agreement,
        'top_tiles': crops, 'disclaimer': DISCLAIMER,
    }
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    (out / f'attention_{short}.json').write_text(json.dumps(tiles))
    print(json.dumps({k: v for k, v in summary.items() if k != 'top_tiles'}, indent=1))
    return summary


if __name__ == '__main__':
    main()
