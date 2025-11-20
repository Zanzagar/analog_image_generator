#!/usr/bin/env python3
"""Sedimentary overlay smoke test.

Runs the fluvial generators (meandering, braided, anastomosing) and asserts
that the new sedimentary overlay masks plus realization metadata exist. Use as
a lightweight CI hook before committing larger runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np

from analog_image_generator import geologic_generators as gg, reporting, stats


REQUIRED_MASKS: tuple[str, ...] = (
    "channel_fill",
    "cross_bed",
    "ripple",
    "fining_upward",
    "overbank_mudstone",
    "realization_metadata",
)

STACKED_MASKS: tuple[str, ...] = (
    "upper_surface_mask",
    "erosion_surface_mask",
    "package_id_map",
)


def _run_smoke(style: str) -> dict:
    params = {"style": style, "seed": 123, "height": 128, "width": 128}
    analog, masks = gg.generate_fluvial(params)
    assert analog.shape == (128, 128)
    _assert_required_masks(masks, REQUIRED_MASKS)
    metrics = stats.compute_metrics(analog, masks, "fluvial")
    _assert_metric_keys(metrics)
    metrics["env"] = "fluvial"
    metrics["realization_id"] = f"{style}-seed123"
    metrics["seed"] = 123
    metrics["gray"] = analog
    metrics["color"] = _sample_color_stack(masks, analog.shape)
    metrics.setdefault("petrology_cement", "")
    metrics.setdefault("petrology_mineralogy", {})
    metrics.setdefault("stacked_package_count", 0)
    return metrics


def _run_stacked_smoke() -> dict:
    params = {
        "mode": "stacked",
        "package_count": 2,
        "package_styles": ["meandering", "braided"],
        "height": 128,
        "width": 128,
        "seed": 999,
        "stack_seed": 5,
    }
    analog, masks = gg.generate_fluvial(params)
    assert analog.shape == (128, 128)
    _assert_required_masks(masks, REQUIRED_MASKS + STACKED_MASKS)
    meta = masks["realization_metadata"]
    assert "stacked_packages" in meta
    metrics = stats.compute_metrics(analog, masks, "fluvial")
    _assert_metric_keys(metrics)
    metrics["env"] = "fluvial"
    metrics["realization_id"] = "stacked-seed999"
    metrics["seed"] = 999
    metrics["gray"] = analog
    metrics["color"] = _sample_color_stack(masks, analog.shape)
    metrics.setdefault("petrology_cement", "")
    metrics.setdefault("petrology_mineralogy", {})
    count = masks.get("package_id_map")
    metrics["stacked_package_count"] = int(masks["realization_metadata"]["stacked_packages"]["stack_statistics"]["package_count"]) if "realization_metadata" in masks else 0
    return metrics


def _assert_required_masks(masks: dict, keys: Iterable[str]) -> None:
    for key in keys:
        assert key in masks, f"missing mask {key}"
        value = masks[key]
        if isinstance(value, np.ndarray):
            assert value.size > 0 and value.dtype == np.float32
        else:
            assert isinstance(value, dict)


def _assert_metric_keys(metrics: dict) -> None:
    for key in ("beta_iso", "entropy_global", "fractal_dimension", "psd_aspect"):
        assert key in metrics, f"missing metric {key}"
        assert isinstance(metrics[key], float)


def _sample_color_stack(masks: dict, shape: tuple[int, int]) -> np.ndarray:
    palette = np.zeros(shape + (3,), dtype=np.float32)
    channel = masks.get("channel")
    if channel is None:
        channel = np.zeros(shape, dtype=np.float32)
    palette[..., 0] = channel
    palette[..., 1] = 0.5 * channel
    return palette


def main() -> int:
    rows = []
    for style in ("meandering", "braided", "anastomosing"):
        rows.append(_run_smoke(style))
        print(f"✓ smoke passed for style={style}")
    rows.append(_run_stacked_smoke())
    print("✓ smoke passed for stacked=2-packages")
    reporting.build_reports(rows, Path("outputs/smoke_report"))
    print("✓ reporting artifacts generated in outputs/smoke_report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
