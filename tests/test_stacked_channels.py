import numpy as np

from analog_image_generator import geologic_generators as gg
from analog_image_generator import stacked_channels as sc


def test_build_stacked_respects_package_count_and_masks():
    params = {
        "mode": "stacked",
        "package_count": 3,
        "package_styles": ["meandering", "braided", "anastomosing"],
        "height": 96,
        "width": 96,
        "seed": 321,
        "stack_seed": 222,
    }
    analog, masks = sc.build_stacked_fluvial(params)
    assert analog.shape == (96, 96)
    assert analog.dtype == np.float32
    upper = masks["upper_surface_mask"]
    assert upper.shape == analog.shape
    package_map = masks["package_id_map"]
    assert package_map.shape == analog.shape
    metadata = masks["realization_metadata"]["stacked_packages"]["packages"]
    assert len(metadata) == 3
    assert {entry["style"] for entry in metadata} == {"meandering", "braided", "anastomosing"}
    assert np.all((package_map >= -1) & (package_map <= 2))


def test_erosion_depth_controls_surface_mask():
    base = {
        "mode": "stacked",
        "package_count": 2,
        "height": 128,
        "width": 128,
        "stack_seed": 77,
        "package_styles": ["meandering", "braided"],
    }
    _, shallow_masks = sc.build_stacked_fluvial({**base, "package_erosion_depth_px": 3.0})
    _, deep_masks = sc.build_stacked_fluvial({**base, "package_erosion_depth_px": 28.0})
    shallow_ratio = _first_package_ratio(shallow_masks["package_id_map"])
    deep_ratio = _first_package_ratio(deep_masks["package_id_map"])
    assert deep_ratio >= shallow_ratio


def test_single_package_matches_single_belt_output():
    params = {
        "mode": "stacked",
        "package_count": 1,
        "style": "braided",
        "height": 72,
        "width": 72,
        "seed": 15,
    }
    analog_stacked, masks_stacked = sc.build_stacked_fluvial(params)
    analog_single, masks_single = gg.generate_fluvial(
        {"style": "braided", "height": 72, "width": 72, "seed": 15}
    )
    np.testing.assert_allclose(analog_stacked, analog_single)
    assert masks_stacked.keys() == masks_single.keys()
    for key in masks_single:
        if isinstance(masks_single[key], np.ndarray):
            np.testing.assert_allclose(masks_stacked[key], masks_single[key])
        else:
            assert masks_stacked[key] == masks_single[key]


def test_generate_fluvial_routes_to_stacked_mode():
    params = {
        "mode": "stacked",
        "package_count": 2,
        "package_styles": ["meandering", "anastomosing"],
        "height": 128,
        "width": 128,
        "seed": 101,
    }
    analog, masks = gg.generate_fluvial(params)
    assert analog.shape == (128, 128)
    meta = masks["realization_metadata"]
    assert "stacked_packages" in meta
    assert meta["stacked_packages"]["stack_statistics"]["package_count"] == 2


def _first_package_ratio(package_map: np.ndarray) -> float:
    depositional = package_map >= 0
    if not np.any(depositional):
        return 0.0
    first = np.isclose(package_map, 0.0)
    return float(np.count_nonzero(first & depositional)) / float(np.count_nonzero(depositional))
