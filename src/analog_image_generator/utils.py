"""Shared utilities (grids, palettes, helpers).

Each helper maps back to a GEOLOGIC_RULES notebook anchor so generator modules
and reporting code share a single implementation surface. The anchors relevant
to this module live in ``docs/GEOLOGIC_RULES.md`` under the **Utilities**
section.
"""

from __future__ import annotations

from hashlib import blake2b
from typing import Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

Array = NDArray[np.float32]
RGBArray = NDArray[np.float32]

PaletteEntry = Mapping[str, str | Sequence[float] | Sequence[int]]

__all__ = [
    "seeded_rng",
    "rng_for_env",
    "make_field",
    "normalized_coords",
    "distance_to_mask",
    "signed_distance",
    "blend_masks",
    "boolean_stack_to_rgb",
    "mask_metadata",
    "palette_for_env",
    "PALETTES",
]


PALETTES: dict[str, list[dict[str, str]]] = {
    "fluvial": [
        {"facies": "channel", "color": "#0f3057"},
        {"facies": "pointbar", "color": "#d98943"},
        {"facies": "levee", "color": "#f2c335"},
        {"facies": "floodplain", "color": "#6b705c"},
        {"facies": "oxbow", "color": "#9a6d38"},
    ],
    "braided": [
        {"facies": "thread", "color": "#184e77"},
        {"facies": "bar", "color": "#f4a261"},
        {"facies": "chute", "color": "#c06c84"},
        {"facies": "floodplain", "color": "#6d6875"},
    ],
    "anastomosing": [
        {"facies": "channel", "color": "#264653"},
        {"facies": "levee", "color": "#a7c957"},
        {"facies": "marsh", "color": "#81b29a"},
        {"facies": "floodplain", "color": "#b08968"},
        {"facies": "fan", "color": "#e07a5f"},
    ],
    "aeolian": [
        {"facies": "crest", "color": "#d9ae61"},
        {"facies": "slipface", "color": "#a05c17"},
        {"facies": "stoss", "color": "#f2cc8f"},
        {"facies": "interdune", "color": "#6e6a5e"},
    ],
    "estuarine": [
        {"facies": "channel", "color": "#335c67"},
        {"facies": "bar", "color": "#f3a712"},
        {"facies": "mudflat", "color": "#93827f"},
        {"facies": "shoreline", "color": "#f4d58d"},
    ],
}


def seeded_rng(seed: int) -> np.random.Generator:
    """Return a deterministic ``numpy`` Generator (Utilities → RNG anchor)."""

    seed = int(seed) % (2**32)
    bitgen = np.random.PCG64(seed)
    return np.random.Generator(bitgen)


def rng_for_env(env: str, base_seed: int) -> np.random.Generator:
    """Derive a reproducible sub-seed for *env* (Utilities → env-rng anchor)."""

    label = env.strip().lower()
    digest = blake2b(f"{label}:{base_seed}".encode("utf-8"), digest_size=8).digest()
    derived_seed = int.from_bytes(digest, "little") % (2**32)
    return seeded_rng(derived_seed)


def make_field(height: int, width: int, fill: float = 0.0) -> Array:
    """Allocate an ``H×W`` float32 field filled with ``fill`` (utilities-grids)."""

    _validate_hw(height, width)
    return np.full((height, width), fill, dtype=np.float32)


def normalized_coords(
    height: int,
    width: int,
    *,
    space: str = "01",
) -> tuple[Array, Array]:
    """Return normalized coordinate grids (utilities-grids anchor)."""

    _validate_hw(height, width)
    scale = np.linspace(0.0, 1.0, height, dtype=np.float32)
    yy = np.repeat(scale[:, None], width, axis=1)
    scale_x = np.linspace(0.0, 1.0, width, dtype=np.float32)
    xx = np.repeat(scale_x[None, :], height, axis=0)
    if space == "-11":
        yy = yy * 2.0 - 1.0
        xx = xx * 2.0 - 1.0
    elif space != "01":
        raise ValueError("space must be '01' or '-11'")
    return yy.astype(np.float32), xx.astype(np.float32)


def distance_to_mask(mask: np.ndarray, *, sampling: Sequence[float] | float | None = None) -> Array:
    """Unsigned distance (px) to the nearest mask pixel (utilities-distance)."""

    mask_bool = _mask_bool(mask)
    distances = ndimage.distance_transform_edt(~mask_bool, sampling=sampling)
    return distances.astype(np.float32)


def signed_distance(
    mask: np.ndarray,
    *,
    sampling: Sequence[float] | float | None = None,
    invert: bool = False,
) -> Array:
    """Signed EDT, negative inside the mask by default (utilities-distance)."""

    mask_bool = _mask_bool(mask)
    outside = ndimage.distance_transform_edt(~mask_bool, sampling=sampling)
    inside = ndimage.distance_transform_edt(mask_bool, sampling=sampling)
    signed = outside.astype(np.float32)
    signed[mask_bool] = -inside[mask_bool]
    if invert:
        signed = -signed
    return signed


def blend_masks(masks: Sequence[np.ndarray], weights: Sequence[float] | None = None) -> Array:
    """Weighted blend of masks (utilities-blend anchor)."""

    if not masks:
        raise ValueError("At least one mask must be provided")
    stack = np.stack([_ensure_float(mask) for mask in masks], axis=0)
    if weights is None:
        blended = stack.mean(axis=0)
    else:
        weight_arr = np.asarray(weights, dtype=np.float32)
        if weight_arr.shape[0] != stack.shape[0]:
            raise ValueError("weights length must match masks length")
        weight_arr = weight_arr[:, None, None]
        blended = np.sum(stack * weight_arr, axis=0)
        denom = float(weight_arr.sum())
        if denom != 0.0:
            blended /= denom
    return np.clip(blended, 0.0, 1.0).astype(np.float32)


def boolean_stack_to_rgb(
    masks: Mapping[str, np.ndarray],
    palette: Sequence[PaletteEntry],
) -> RGBArray:
    """Map boolean masks to RGB rasters (utilities-rgb anchor)."""

    if not masks:
        raise ValueError("masks must contain at least one entry")
    height, width = _infer_hw(masks.values())
    rgb = np.zeros((height, width, 3), dtype=np.float32)
    for entry in palette:
        facies = entry.get("facies")
        if facies is None or facies not in masks:
            continue
        mask = _ensure_float(masks[facies])
        color = np.asarray(_color_to_rgb(entry.get("color")), dtype=np.float32)
        rgb += mask[..., None] * color
    return np.clip(rgb, 0.0, 1.0)


def mask_metadata(mask: np.ndarray) -> dict[str, int | str]:
    """Return serialization metadata for mask arrays (utilities-rgb anchor)."""

    arr = _ensure_float(mask)
    height, width = arr.shape
    return {"dtype": str(arr.dtype), "height": height, "width": width}


def palette_for_env(env: str) -> list[dict[str, str]]:
    """Lookup the default palette declared in ``docs/PALETTES.md`` (utilities-palettes)."""

    env_key = env.strip().lower()
    if env_key not in PALETTES:
        raise ValueError(f"Unknown environment palette: {env}")
    return [dict(entry) for entry in PALETTES[env_key]]


def _validate_hw(height: int, width: int) -> None:
    if height <= 0 or width <= 0:
        raise ValueError("height and width must be positive")


def _ensure_float(array: np.ndarray) -> Array:
    arr = np.asarray(array, dtype=np.float32)
    if arr.ndim != 2:
        raise ValueError("mask arrays must be HxW")
    return arr


def _mask_bool(mask: np.ndarray) -> np.ndarray:
    arr = np.asarray(mask)
    if arr.ndim != 2:
        raise ValueError("mask must be HxW")
    return arr.astype(bool)


def _infer_hw(arrays: Iterable[np.ndarray]) -> tuple[int, int]:
    first_shape: tuple[int, int] | None = None
    for array in arrays:
        arr = np.asarray(array)
        if arr.ndim != 2:
            raise ValueError("mask arrays must be HxW")
        if first_shape is None:
            first_shape = arr.shape
        elif arr.shape != first_shape:
            raise ValueError("all mask arrays must share the same shape")
    if first_shape is None:
        raise ValueError("no arrays provided")
    return first_shape


def _color_to_rgb(
    color: str | Sequence[float] | Sequence[int] | None,
) -> tuple[float, float, float]:
    if color is None:
        return (1.0, 1.0, 1.0)
    if isinstance(color, str):
        value = color.lstrip("#")
        if len(value) != 6:
            raise ValueError(f"Unsupported color format: {color}")
        r = int(value[0:2], 16) / 255.0
        g = int(value[2:4], 16) / 255.0
        b = int(value[4:6], 16) / 255.0
        return (r, g, b)
    seq = list(color)
    if len(seq) != 3:
        raise ValueError("RGB colors must have three components")
    if max(seq) > 1.0:
        return tuple(float(c) / 255.0 for c in seq)
    return tuple(float(c) for c in seq)
