import numpy as np
import pytest

from experiments.attention_mil.data import LockedTestSplit, load_slide
from experiments.attention_mil.heatmap import (
    RAMP, hex_rgb, ramp_colour, rank_normalise, tile_box, verify_source)

SAMPLE_ID = 'a2e48dce-1874-468d-a302-fd30b3107f4a'


def test_rank_normalise_keeps_order_and_spreads_softmax_like_weights():
    alpha = np.array([0.001, 0.002, 0.0015, 0.9, 0.0955])   # one spike, the rest tiny
    r = rank_normalise(alpha)
    assert list(np.argsort(r)) == list(np.argsort(alpha))
    assert r.max() == 1 and r.min() > 0
    minmax = (alpha - alpha.min()) / (alpha.max() - alpha.min())
    assert (minmax < 0.11).sum() == 4 and (r < 0.11).sum() == 0   # why min-max is not used


def test_rank_normalise_gives_ties_the_same_value():
    assert rank_normalise(np.array([0.2, 0.2, 0.6]))[0] == rank_normalise(np.array([0.2, 0.2, 0.6]))[1]


def test_colour_ramp_endpoints_and_midpoint():
    assert ramp_colour(0) == hex_rgb(RAMP[0])
    assert ramp_colour(0.5) == hex_rgb(RAMP[1])
    assert ramp_colour(1) == hex_rgb(RAMP[2])


def test_tile_box_matches_backend_overlay_mapping():
    # backend create_overlay: (x*sx, y*sy, (x+tile_w)*sx, (y+tile_h)*sy)
    assert tile_box((2230, 446), (223, 223), (0.05, 0.1)) == (111.5, 44.6, 122.65, 66.9)


def test_wrong_slide_file_is_rejected(bundle, tmp_path):
    fake = tmp_path / 'other.svs'
    fake.write_bytes(b'not the slide')
    with pytest.raises(ValueError, match='md5 does not match'):
        verify_source(fake, bundle, SAMPLE_ID)


def test_single_slide_loading_keeps_the_test_lock(bundle):
    with pytest.raises(LockedTestSplit):
        load_slide(bundle, SAMPLE_ID)
    slide, split = load_slide(bundle, SAMPLE_ID, allow_test=True)
    assert split == 'test' and slide.footprint == (223, 223) and len(slide.features) == 512
