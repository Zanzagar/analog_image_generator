"""Sanity-check preview helpers.

This module keeps the preview workflow inside the package so both notebooks and
CLI tooling can rely on the exact same code paths. It intentionally degrades to
placeholder noise until the actual geologic generators come online.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

import numpy as np

from . import geologic_generators

Environment = Literal["fluvial", "aeolian", "estuarine"]
ENVIRONMENTS: tuple[Environment, ...] = ("fluvial", "aeolian", "estuarine")


@dataclass(frozen=True)
class PreviewArtifacts:
    """Paths to rendered artifacts produced by :func:`save_preview`."""

    analog_path: Path
    mask_paths: dict[str, Path]
    metadata_path: Path


def generate_preview(
    env: Environment,
    *,
    width: int = 512,
    height: int = 512,
    seed: int = 0,
    params: dict | None = None,
) -> tuple[np.ndarray, dict[str, np.ndarray], dict]:
    """Render or synthesize a preview for *env*.

    The returned analog array is normalized to ``[0, 1]`` for easier plotting.
    Masks (if any) are normalized the same way. ``metadata`` records whether the
    result came from a real generator or the placeholder fallback.
    """

    generator = _resolve_generator(env)
    merged_params = {"seed": seed}
    if params:
        merged_params.update(params)
    merged_params.setdefault("width", width)
    merged_params.setdefault("height", height)

    note: str | None = None
    source = "generator"
    try:
        analog, masks = generator(merged_params)
    except NotImplementedError as exc:
        analog = _placeholder_preview(width, height, seed)
        masks = {}
        note = str(exc)
        source = "placeholder"

    analog_array = _normalize_array(analog)
    mask_arrays = {name: _normalize_array(mask) for name, mask in masks.items()}

    metadata = {
        "env": env,
        "width": int(width),
        "height": int(height),
        "seed": int(seed),
        "params": merged_params,
        "mask_names": sorted(mask_arrays.keys()),
        "source": source,
        "note": note,
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    return analog_array, mask_arrays, metadata


def save_preview(
    analog: np.ndarray,
    masks: dict[str, np.ndarray],
    metadata: dict,
    *,
    output_dir: Path | str,
    slug: str | None = None,
) -> PreviewArtifacts:
    """Persist preview outputs to *output_dir* and return their paths."""

    from matplotlib import pyplot as plt  # Imported lazily to avoid global side effects

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = metadata["generated_at"].replace(":", "")
    slug = slug or f"{metadata['env']}-{metadata['seed']}-{timestamp}"
    analog_path = output_dir / f"{slug}.png"
    metadata_path = output_dir / f"{slug}.json"

    plt.imsave(analog_path, analog, cmap="gray", vmin=0.0, vmax=1.0)

    mask_paths: dict[str, Path] = {}
    for name, array in masks.items():
        safe_name = name.replace(" ", "-")
        mask_path = output_dir / f"{slug}__{safe_name}.png"
        plt.imsave(mask_path, array, cmap="gray", vmin=0.0, vmax=1.0)
        mask_paths[name] = mask_path

    metadata = dict(metadata)
    metadata["artifacts"] = {
        "analog": analog_path.name,
        "masks": {name: path.name for name, path in mask_paths.items()},
    }
    metadata_path.write_text(_json_dumps(metadata))

    return PreviewArtifacts(
        analog_path=analog_path,
        mask_paths=mask_paths,
        metadata_path=metadata_path,
    )


def _resolve_generator(env: Environment):
    mapping = {
        "fluvial": geologic_generators.generate_fluvial,
        "aeolian": geologic_generators.generate_aeolian,
        "estuarine": geologic_generators.generate_estuarine,
    }
    return mapping[env]


def _placeholder_preview(width: int, height: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    gradient = np.linspace(0.1, 0.9, width, dtype=np.float32)
    gradient = np.tile(gradient, (height, 1))
    noise = rng.normal(0.0, 0.15, size=(height, width)).astype(np.float32)
    belts = np.sin(np.linspace(0, np.pi, height, dtype=np.float32)[:, None] * 3.0)
    belts = (belts + 1.0) * 0.2
    return _normalize_array(gradient + belts + noise)


def _normalize_array(array) -> np.ndarray:
    arr = np.asarray(array, dtype=np.float32)
    if arr.ndim == 3 and arr.shape[-1] == 1:
        arr = arr[..., 0]
    if arr.ndim != 2:
        raise ValueError("Preview expects 2D arrays")
    arr = np.nan_to_num(arr)
    arr_min = float(arr.min())
    arr_max = float(arr.max())
    if arr_max - arr_min <= 1e-8:
        return np.zeros_like(arr)
    return (arr - arr_min) / (arr_max - arr_min)


def _json_dumps(payload: dict) -> str:
    import json

    return json.dumps(payload, indent=2, sort_keys=True)
