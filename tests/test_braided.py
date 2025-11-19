import numpy as np
import pytest

from analog_image_generator import geologic_generators as gg


def test_generate_braided_shapes_and_masks():
    params = {
        "style": "braided",
        "seed": 7,
        "height": 160,
        "width": 120,
        "thread_count": 4,
        "mean_thread_width": 20.0,
    }
    analog, masks = gg.generate_fluvial(params)
    assert analog.shape == (160, 120)
    assert analog.dtype == np.float32
    required = {
        "channel",
        "bar",
        "chute",
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
    assert pytest.approx(1.0, rel=1e-3) == sum(metadata["mineralogy"].values())


def test_generate_braided_is_deterministic():
    params = {
        "style": "braided",
        "seed": 11,
        "thread_count": 5,
        "mean_thread_width": 18.0,
    }
    analog_a, masks_a = gg.generate_fluvial(params)
    analog_b, masks_b = gg.generate_fluvial(params)
    np.testing.assert_allclose(analog_a, analog_b)
    for key in masks_a:
        if isinstance(masks_a[key], np.ndarray):
            np.testing.assert_allclose(masks_a[key], masks_b[key])
        else:
            assert masks_a[key] == masks_b[key]


def test_braided_parameter_validation():
    params = {"style": "braided", "thread_count": 2, "mean_thread_width": 18.0}
    try:
        gg.generate_fluvial(params)
    except ValueError:
        pass
    else:
        raise AssertionError("thread_count validation not enforced")

    params = {"style": "braided", "thread_count": 4, "mean_thread_width": 8.0}
    try:
        gg.generate_fluvial(params)
    except ValueError:
        pass
    else:
        raise AssertionError("mean_thread_width validation not enforced")
