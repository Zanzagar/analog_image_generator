import numpy as np
import pytest

from analog_image_generator import geologic_generators as gg


def test_generate_anastomosing_shapes_and_masks():
    params = {
        "style": "anastomosing",
        "seed": 8,
        "height": 160,
        "width": 160,
        "branch_count": 3,
        "marsh_fraction": 0.4,
        "fan_length_px": 32.0,
    }
    analog, masks = gg.generate_fluvial(params)
    assert analog.shape == (160, 160)
    assert analog.dtype == np.float32
    expected_keys = {
        "branch_channel",
        "levee",
        "marsh",
        "fan",
        "overbank",
        "wetland_water",
        "channel_fill",
        "cross_bed",
        "ripple",
        "fining_upward",
        "overbank_mudstone",
        "realization_metadata",
        "_metadata_branch_stability",
    }
    assert expected_keys.issubset(set(masks.keys()))
    for key, value in masks.items():
        if isinstance(value, np.ndarray) and value.shape == analog.shape:
            assert value.dtype == np.float32
            assert 0.0 <= float(value.min()) <= float(value.max()) <= 1.0
    metadata = masks["realization_metadata"]
    assert pytest.approx(1.0, rel=1e-3) == sum(metadata["mineralogy"].values())


def test_marsh_fraction_respects_slider():
    params = {
        "style": "anastomosing",
        "seed": 4,
        "height": 200,
        "width": 200,
        "marsh_fraction": 0.55,
        "fan_length_px": 28.0,
    }
    _, masks = gg.generate_fluvial(params)
    ratio = float(masks["marsh"].mean())
    assert 0.45 <= ratio <= 0.65


def test_fan_length_validation():
    params = {
        "style": "anastomosing",
        "fan_length_px": 10.0,
    }
    with pytest.raises(ValueError):
        gg.generate_fluvial(params)
