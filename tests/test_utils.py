import numpy as np
import pytest

from analog_image_generator import utils


def test_seeded_rng_is_deterministic():
    rng_a = utils.seeded_rng(123)
    rng_b = utils.seeded_rng(123)
    assert np.allclose(rng_a.random(5), rng_b.random(5))


def test_rng_for_env_derives_distinct_streams():
    rng_fluvial = utils.rng_for_env("fluvial", base_seed=1)
    rng_aeolian = utils.rng_for_env("aeolian", base_seed=1)
    assert not np.allclose(rng_fluvial.random(3), rng_aeolian.random(3))


def test_make_field_and_normalized_coords_shapes():
    field = utils.make_field(2, 3, fill=0.25)
    assert field.shape == (2, 3)
    assert np.allclose(field, 0.25)
    yy, xx = utils.normalized_coords(2, 3, space="01")
    assert yy.min() == pytest.approx(0.0)
    assert yy.max() == pytest.approx(1.0)
    assert xx.shape == (2, 3)


def test_distance_helpers_behave():
    mask = np.zeros((3, 3), dtype=bool)
    mask[1, 1] = True
    dist = utils.distance_to_mask(mask)
    assert dist[1, 1] == pytest.approx(0.0)
    signed = utils.signed_distance(mask)
    assert signed[1, 1] <= 0.0
    assert signed[0, 0] > 0.0


def test_blend_masks_weighted():
    m1 = np.zeros((2, 2), dtype=np.float32)
    m2 = np.ones((2, 2), dtype=np.float32)
    blended = utils.blend_masks([m1, m2], weights=[1, 3])
    assert blended.min() >= 0.0
    assert blended.max() <= 1.0
    assert blended[0, 0] == pytest.approx(0.75)


def test_boolean_stack_to_rgb_and_metadata():
    masks = {
        "channel": np.ones((2, 2), dtype=bool),
        "floodplain": np.zeros((2, 2), dtype=bool),
    }
    palette = utils.palette_for_env("fluvial")
    rgb = utils.boolean_stack_to_rgb(masks, palette)
    assert rgb.shape == (2, 2, 3)
    metadata = utils.mask_metadata(masks["channel"])
    assert metadata == {"dtype": "float32", "height": 2, "width": 2}


def test_palette_for_env_unknown():
    with pytest.raises(ValueError):
        utils.palette_for_env("unknown")
