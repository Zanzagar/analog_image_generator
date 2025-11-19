"""Stacked channel assembly utilities (GEOLOGIC_RULES stacked anchors)."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Literal, Sequence, TypedDict

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

from . import utils

Array = NDArray[np.float32]
FluvialStyle = Literal["meandering", "braided", "anastomosing"]

GeneratorFn = Callable[[dict, np.random.Generator], tuple[Array, dict[str, Array]]]


@dataclass(frozen=True)
class PackageSpec:
    """Parameters describing an individual stacked channel package."""

    style: FluvialStyle
    params: dict[str, Any] = field(default_factory=dict)
    thickness_px: float = 42.0
    relief_px: float = 18.0
    erosion_depth_px: float = 10.0
    seed: int | None = None
    package_id: int | None = None


class PackageMetadata(TypedDict):
    """Metadata returned for each stacked package."""

    package_id: int
    style: FluvialStyle
    thickness_px: float
    relief_px: float
    erosion_depth_px: float
    seed: int
    mask_means: dict[str, float]


@dataclass(frozen=True)
class SequenceResult:
    """Return structure for ``sequence_packages``."""

    composite: Array
    stack: Array
    package_id_map: Array
    masks: dict[str, Array]
    package_metadata: list[PackageMetadata]
    realization_payloads: list[dict]


STACK_PARAM_KEYS = {
    "mode",
    "package_count",
    "package_styles",
    "package_thickness_px",
    "package_relief_px",
    "package_erosion_depth_px",
    "package_params",
    "package_param_overrides",
    "stack_seed",
    "erosional_relief_px",
    "seed",
}


def build_stacked_fluvial(params: dict) -> tuple[Array, dict[str, Array]]:
    """Assemble stacked fluvial packages driven by a params dictionary."""

    params = params or {}
    package_count = max(1, int(params.get("package_count", 1)))
    mode = params.get("mode", "single").lower()
    if mode != "stacked":
        raise ValueError("build_stacked_fluvial is intended for stacked mode only")

    stack_seed = int(params.get("stack_seed", params.get("seed", 0)))
    base_rng = utils.seeded_rng(stack_seed)

    if package_count == 1:
        style = _normalize_style(params.get("style", "meandering"))
        generator = _get_generator_map()[style]
        single_params = _base_generator_params(params)
        single_params["style"] = style
        single_params["seed"] = int(params.get("seed", stack_seed))
        rng = utils.seeded_rng(int(single_params["seed"]))
        return generator(single_params, rng)

    specs = _build_package_specs(params, package_count)
    base_shape = (
        int(params.get("height", specs[0].params.get("height", 512))),
        int(params.get("width", specs[0].params.get("width", 512))),
    )
    result = sequence_packages(specs, base_shape, base_rng)

    masks = dict(result.masks)
    masks["package_id_map"] = result.package_id_map
    if "upper_surface_mask" not in masks:
        masks["upper_surface_mask"] = (result.package_id_map >= 0).astype(np.float32)

    stack_stats = {
        "package_count": len(specs),
        "package_mix": _package_mix(result.package_metadata),
        "total_relief_px": float(sum(meta["relief_px"] for meta in result.package_metadata)),
        "total_thickness_px": float(sum(meta["thickness_px"] for meta in result.package_metadata)),
    }
    stack_stats["min_gray"] = float(result.stack.min()) if result.stack.size else 0.0
    stack_stats["max_gray"] = float(result.stack.max()) if result.stack.size else 0.0

    realization = result.realization_payloads[-1].copy() if result.realization_payloads else {}
    realization["stacked_packages"] = {
        "packages": result.package_metadata,
        "stack_statistics": stack_stats,
    }
    masks["realization_metadata"] = realization
    return result.composite, masks


def _build_package_specs(params: dict, package_count: int) -> list[PackageSpec]:
    base_params = _base_generator_params(params)
    height = int(params.get("height", base_params.get("height", 512)))
    width = int(params.get("width", base_params.get("width", 512)))
    base_params["height"] = height
    base_params["width"] = width

    styles_raw = params.get("package_styles")
    if styles_raw is None:
        styles = [params.get("style", "meandering")] * package_count
    elif isinstance(styles_raw, str):
        styles = [styles_raw] * package_count
    else:
        styles_raw = list(styles_raw)
        styles = (styles_raw * ((package_count + len(styles_raw) - 1) // len(styles_raw)))[:package_count]

    style_sequence = [_normalize_style(style) for style in styles]
    thickness_values = _coerce_package_values(params.get("package_thickness_px"), package_count, 42.0)
    relief_values = _coerce_package_values(
        params.get("package_relief_px", params.get("erosional_relief_px", 18.0)),
        package_count,
        18.0,
    )
    erosion_values = _coerce_package_values(
        params.get("package_erosion_depth_px", [max(4.0, val * 0.75) for val in relief_values]),
        package_count,
        12.0,
    )

    overrides = params.get("package_param_overrides") or [{} for _ in range(package_count)]
    if isinstance(overrides, dict):
        overrides = [overrides]
    overrides = list(overrides)
    specs: list[PackageSpec] = []
    for idx in range(package_count):
        style = style_sequence[idx % len(style_sequence)]
        override = overrides[idx % len(overrides)] if overrides else {}
        package_params = dict(base_params)
        package_params.update(override or {})
        package_params["style"] = style
        specs.append(
            PackageSpec(
                style=style,
                params=package_params,
                thickness_px=float(thickness_values[idx]),
                relief_px=float(relief_values[idx]),
                erosion_depth_px=float(erosion_values[idx]),
                seed=int(package_params.get("seed", 0)) if "seed" in package_params else None,
                package_id=idx,
            )
        )
    return specs


def _coerce_package_values(value: Any, count: int, default: float) -> list[float]:
    if value is None:
        return [float(default) for _ in range(count)]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        seq = list(value)
        if not seq:
            return [float(default) for _ in range(count)]
        return [float(seq[i % len(seq)]) for i in range(count)]
    return [float(value) for _ in range(count)]


def _base_generator_params(params: dict) -> dict:
    return {k: v for k, v in params.items() if k not in STACK_PARAM_KEYS}


def sequence_packages(
    package_specs: Sequence[PackageSpec],
    base_grid_shape: tuple[int, int],
    rng: np.random.Generator,
) -> SequenceResult:
    """Generate stacked packages and metadata."""

    if not package_specs:
        raise ValueError("package_specs must contain at least one entry")
    height, width = base_grid_shape
    height = int(height)
    width = int(width)
    stacked_slices: list[Array] = []
    aggregated_masks: dict[str, Array] = {}
    package_metadata: list[PackageMetadata] = []
    realization_payloads: list[dict] = []
    package_ids: list[int] = []
    current_surface = np.zeros((height, width), dtype=np.float32)
    erosion_surface = np.zeros((height, width), dtype=np.float32)

    for idx, spec in enumerate(package_specs):
        generator = _get_generator_map()[spec.style]
        package_seed = spec.seed if spec.seed is not None else int(rng.integers(0, 1_000_000))
        package_rng = utils.seeded_rng(package_seed)
        params = dict(spec.params)
        params["height"] = height
        params["width"] = width
        params["seed"] = package_seed
        params["style"] = spec.style

        gray, masks = generator(params, package_rng)
        gray = gray.astype(np.float32)
        if stacked_slices:
            prev_stack = np.stack(stacked_slices, axis=0)
            trimmed_stack, erosion_mask = cut_erosional_surface(prev_stack, spec.erosion_depth_px, spec.style)
            stacked_slices = [trimmed_stack[i] for i in range(trimmed_stack.shape[0])]
            erosion_surface = np.maximum(erosion_surface, erosion_mask)
        relief_gray, current_surface = apply_relief_slice(
            gray,
            current_surface,
            spec.thickness_px,
            spec.relief_px,
            rng,
        )
        stacked_slices.append(relief_gray)
        _merge_masks(aggregated_masks, masks)
        if "realization_metadata" in masks and isinstance(masks["realization_metadata"], dict):
            realization_payloads.append(dict(masks["realization_metadata"]))
        package_id = spec.package_id if spec.package_id is not None else idx
        package_ids.append(package_id)
        mask_means = _mask_means(masks)
        package_metadata.append(
            PackageMetadata(
                package_id=package_id,
                style=spec.style,
                thickness_px=float(spec.thickness_px),
                relief_px=float(spec.relief_px),
                erosion_depth_px=float(spec.erosion_depth_px),
                seed=package_seed,
                mask_means=mask_means,
            )
        )

    stack = np.stack(stacked_slices, axis=0) if stacked_slices else np.zeros((0, height, width), dtype=np.float32)
    composite, package_id_map = _composite_from_stack(stack, package_ids)
    aggregated_masks["upper_surface_mask"] = composite > 0.0
    aggregated_masks["upper_surface_mask"] = aggregated_masks["upper_surface_mask"].astype(np.float32)
    aggregated_masks["erosion_surface_mask"] = np.clip(erosion_surface, 0.0, 1.0).astype(np.float32)
    return SequenceResult(
        composite=composite,
        stack=stack,
        package_id_map=package_id_map,
        masks=aggregated_masks,
        package_metadata=package_metadata,
        realization_payloads=realization_payloads,
    )


def apply_relief_slice(
    gray: Array,
    current_surface: Array,
    thickness_px: float,
    relief_px: float,
    rng: np.random.Generator,
) -> tuple[Array, Array]:
    """Apply a simple relief transform to a slice and update vertical surface."""

    relief_px = max(relief_px, 0.0)
    base = gray.astype(np.float32)
    relief_noise = rng.standard_normal(base.shape).astype(np.float32)
    sigma = max(1.0, relief_px / 8.0)
    relief_field = ndimage.gaussian_filter(relief_noise, sigma=sigma)
    if float(np.max(np.abs(relief_field))) > 0.0:
        relief_field /= float(np.max(np.abs(relief_field)))
    relief_field *= relief_px / max(float(base.shape[0]), float(base.shape[1]), 1.0)
    modulated = np.clip(base + relief_field * 0.15, 0.0, 1.0)
    updated_surface = np.clip(current_surface + thickness_px + relief_field, 0.0, None)
    return modulated.astype(np.float32), updated_surface.astype(np.float32)


def cut_erosional_surface(
    previous_stack: Array,
    relief_px: float,
    style: FluvialStyle,
) -> tuple[Array, Array]:
    """Apply a deterministic erosional trim to the previous stack."""

    if previous_stack.size == 0:
        shape = previous_stack.shape[1:] if previous_stack.ndim == 3 else (0, 0)
        return previous_stack, np.zeros(shape, dtype=np.float32)
    top_surface = previous_stack[-1]
    gradient = np.abs(ndimage.sobel(top_surface))
    if float(gradient.max()) > 0.0:
        gradient /= float(gradient.max())
    style_bias = {"braided": 0.25, "anastomosing": 0.15, "meandering": 0.1}.get(style, 0.12)
    threshold = np.clip(0.45 - style_bias + relief_px / 300.0, 0.05, 0.95)
    erosion_mask = (gradient > threshold).astype(np.float32)
    trimmed_stack = previous_stack.copy()
    trimmed_stack[-1] = np.where(erosion_mask > 0.5, trimmed_stack[-1] * 0.7, trimmed_stack[-1])
    return trimmed_stack, erosion_mask


def _composite_from_stack(stack: Array, package_ids: Sequence[int]) -> tuple[Array, Array]:
    if stack.size == 0:
        shape = (0, 0)
        return np.zeros(shape, dtype=np.float32), np.zeros(shape, dtype=np.float32)
    height, width = stack.shape[1], stack.shape[2]
    composite = np.zeros((height, width), dtype=np.float32)
    package_id_map = np.full((height, width), -1, dtype=np.int32)
    visible = np.zeros((height, width), dtype=bool)
    for idx in reversed(range(stack.shape[0])):
        slice_gray = stack[idx]
        mask = slice_gray > 1e-3
        fill = mask & (~visible)
        composite[fill] = slice_gray[fill]
        package_id_map[fill] = package_ids[idx]
        visible |= mask
    return composite.astype(np.float32), package_id_map.astype(np.float32)


def _merge_masks(store: dict[str, Array], masks: dict[str, Array]) -> None:
    for key, value in masks.items():
        if not isinstance(value, np.ndarray):
            continue
        arr = value.astype(np.float32)
        if key not in store:
            store[key] = arr
        else:
            store[key] = np.maximum(store[key], arr)


def _mask_means(masks: dict[str, Array]) -> dict[str, float]:
    stats: dict[str, float] = {}
    for key, value in masks.items():
        if isinstance(value, np.ndarray):
            stats[key] = float(value.mean())
    return stats


def _package_mix(metadata: Sequence[PackageMetadata]) -> dict[str, int]:
    mix: dict[str, int] = {}
    for meta in metadata:
        mix[meta["style"]] = mix.get(meta["style"], 0) + 1
    return mix


def _normalize_style(style: str) -> FluvialStyle:
    key = style.lower()
    if key.startswith("braid"):
        return "braided"
    if key.startswith("anasto"):
        return "anastomosing"
    return "meandering"


@lru_cache(maxsize=1)
def _get_generator_map() -> dict[FluvialStyle, GeneratorFn]:
    from . import geologic_generators as gg

    return {
        "meandering": gg.generate_meandering,
        "braided": gg.generate_braided,
        "anastomosing": gg.generate_anastomosing,
    }
