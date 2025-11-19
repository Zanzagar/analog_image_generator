import numpy as np
import pytest

from analog_image_generator import geologic_generators as gg


def test_generate_fluvial_shapes_and_masks():
    params = {"height": 128, "width": 96, "seed": 7}
    analog, masks = gg.generate_fluvial(params)
    assert analog.shape == (128, 96)
    assert analog.dtype == np.float32
    required = {
        "channel",
        "levee",
        "scroll_bar",
        "oxbow",
        "floodplain",
        "channel_fill",
        "cross_bed",
        "ripple",
        "fining_upward",
        "overbank_mudstone",
        "realization_metadata",
    }
    assert required.issubset(set(masks.keys()))
    for key, mask in masks.items():
        if isinstance(mask, np.ndarray) and mask.shape == analog.shape:
            assert mask.dtype == np.float32
            assert 0.0 <= float(mask.min()) <= float(mask.max()) <= 1.0
    metadata = masks["realization_metadata"]
    assert isinstance(metadata, dict)
    assert pytest.approx(1.0, rel=1e-3) == sum(metadata["mineralogy"].values())


def test_generate_fluvial_is_deterministic():
    params = {"height": 128, "width": 96, "seed": 11}
    analog_a, masks_a = gg.generate_fluvial(params)
    analog_b, masks_b = gg.generate_fluvial(params)
    np.testing.assert_allclose(analog_a, analog_b)
    for key in masks_a:
        if isinstance(masks_a[key], np.ndarray):
            np.testing.assert_allclose(masks_a[key], masks_b[key])
        else:
            assert masks_a[key] == masks_b[key]
