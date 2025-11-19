"""Core geologic generators with notebook/document anchors for traceability."""

from __future__ import annotations

from math import pi
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

from . import utils
from .stacked_channels import build_stacked_fluvial

Array = NDArray[np.float32]

_MEANDER_DEFAULTS: dict[str, float | int] = {
    "height": 512,
    "width": 512,
    "seed": 42,
    "n_control_points": 6,
    "amplitude_range": (0.08, 0.22),
    "drift_fraction": 0.08,
    "channel_width_min": 26.0,
    "channel_width_max": 46.0,
    "levee_iterations": 5,
    "scroll_lambda_px": 28.0,
    "oxbow_probability": 0.25,
    "floodplain_noise": 0.08,
}

_BRAIDED_DEFAULTS: dict[str, float | int] = {
    "height": 512,
    "width": 512,
    "seed": 42,
    "style": "braided",
    "thread_count": 5,
    "mean_thread_width": 18.0,
    "bar_spacing_factor": 4.2,
    "chute_frequency": 0.35,
    "floodplain_noise": 0.05,
}

_ANASTO_DEFAULTS: dict[str, float | int] = {
    "height": 512,
    "width": 512,
    "seed": 42,
    "style": "anastomosing",
    "branch_count": 3,
    "levee_width_px": 6.0,
    "levee_height_scale": 0.65,
    "marsh_fraction": 0.45,
    "fan_length_px": 35.0,
    "floodplain_noise": 0.04,
}


def generate_fluvial(params: dict) -> tuple[Array, dict[str, Array]]:
    """Return grayscale analog and masks for fluvial environments."""

    params = params or {}
    mode = params.get("mode", "single").lower()
    if mode == "stacked":
        return build_stacked_fluvial(params)

    style = params.get("style", "meandering").lower()
    if style == "braided":
        cfg = {**_BRAIDED_DEFAULTS, **params}
        rng = utils.seeded_rng(int(cfg.get("seed", 42)))
        return generate_braided(cfg, rng)
    if style == "anastomosing":
        cfg = {**_ANASTO_DEFAULTS, **params}
        rng = utils.seeded_rng(int(cfg.get("seed", 42)))
        return generate_anastomosing(cfg, rng)

    cfg = {**_MEANDER_DEFAULTS, **params}
    rng = utils.seeded_rng(int(cfg.get("seed", 42)))
    return generate_meandering(cfg, rng)


def generate_aeolian(params: dict) -> tuple[Array, dict[str, Array]]:
    """Return grayscale analog and masks for aeolian environments."""
    raise NotImplementedError("Implemented during aeolian-v1 milestone.")


def generate_estuarine(params: dict) -> tuple[Array, dict[str, Array]]:
    """Return grayscale analog and masks for estuarine environments."""
    raise NotImplementedError("Implemented during estuarine-v1 milestone.")


def generate_meandering(params: dict, rng: np.random.Generator) -> tuple[Array, Dict[str, Array]]:
    """Orchestrate the meandering pipeline (GEOLOGIC_RULES meandering anchors)."""

    height = int(params.get("height", _MEANDER_DEFAULTS["height"]))
    width = int(params.get("width", _MEANDER_DEFAULTS["width"]))
    amp_range = _as_pair(params.get("amplitude_range", _MEANDER_DEFAULTS["amplitude_range"]))
    drift_frac = float(params.get("drift_fraction", _MEANDER_DEFAULTS["drift_fraction"]))
    centerline = meander_centerline(
        height,
        width,
        int(params.get("n_control_points", 6)),
        amp_range,
        drift_frac,
        rng,
    )
    channel_mask = meander_variable_channel(
        centerline,
        (height, width),
        float(params.get("channel_width_min", 25.0)),
        float(params.get("channel_width_max", 45.0)),
        rng,
    )
    levee_mask = add_levees(channel_mask, int(params.get("levee_iterations", 5)))
    scroll_mask = add_scroll_bars(channel_mask, float(params.get("scroll_lambda_px", 28.0)))
    oxbow_mask = add_oxbow(
        centerline,
        (height, width),
        float(params.get("oxbow_probability", 0.25)),
        rng,
    )
    floodplain_mask = np.clip(1.0 - np.clip(channel_mask + oxbow_mask, 0.0, 1.0), 0.0, 1.0)

    masks: Dict[str, Array] = {
        "channel": channel_mask,
        "levee": levee_mask,
        "scroll_bar": scroll_mask,
        "oxbow": oxbow_mask,
        "floodplain": floodplain_mask,
    }

    base_gray = (
        channel_mask * 0.65
        + levee_mask * 0.2
        + scroll_mask * 0.1
        + oxbow_mask * 0.15
        + floodplain_mask * 0.35
    )
    analog, masks = compose_meandering(
        base_gray,
        masks,
        float(params.get("floodplain_noise", 0.08)),
        rng,
    )
    analog, masks = apply_sedimentary_overlays(analog, masks, rng, env="meandering")
    return analog, masks


def generate_braided(params: dict, rng: np.random.Generator) -> tuple[Array, Dict[str, Array]]:
    """Orchestrate braided belt generation (GEOLOGIC_RULES braided anchors)."""

    height = int(params.get("height", _BRAIDED_DEFAULTS["height"]))
    width = int(params.get("width", _BRAIDED_DEFAULTS["width"]))
    thread_count = int(params.get("thread_count", _BRAIDED_DEFAULTS["thread_count"]))
    mean_width = float(params.get("mean_thread_width", _BRAIDED_DEFAULTS["mean_thread_width"]))
    bar_spacing = float(params.get("bar_spacing_factor", _BRAIDED_DEFAULTS["bar_spacing_factor"]))
    chute_freq = float(params.get("chute_frequency", _BRAIDED_DEFAULTS["chute_frequency"]))

    thread_masks, thread_info, centerlines = braided_threads(
        height, width, thread_count, mean_width, rng
    )
    channel_mask = np.clip(np.sum(thread_masks, axis=0), 0.0, 1.0)
    bar_mask = seed_bars(thread_masks, thread_info, bar_spacing, rng, (height, width))
    chute_mask = add_chutes(centerlines, thread_info, chute_freq, rng, (height, width))
    floodplain_mask = np.clip(
        1.0 - np.clip(channel_mask + bar_mask + chute_mask, 0.0, 1.0), 0.0, 1.0
    )

    masks: Dict[str, Array] = {
        "channel": channel_mask,
        "bar": bar_mask,
        "chute": chute_mask,
        "floodplain": floodplain_mask,
    }
    gray = channel_mask * 0.6 + bar_mask * 0.25 + chute_mask * 0.15 + floodplain_mask * 0.45
    analog, masks = compose_braided(
        gray,
        masks,
        float(params.get("floodplain_noise", _BRAIDED_DEFAULTS["floodplain_noise"])),
        rng,
    )
    analog, masks = apply_sedimentary_overlays(analog, masks, rng, env="braided")
    return analog, masks


def generate_anastomosing(params: dict, rng: np.random.Generator) -> tuple[Array, Dict[str, Array]]:
    """Build anastomosing belts (GEOLOGIC_RULES anastomosing anchors)."""

    height = int(params.get("height", _ANASTO_DEFAULTS["height"]))
    width = int(params.get("width", _ANASTO_DEFAULTS["width"]))
    branch_count = int(params.get("branch_count", _ANASTO_DEFAULTS["branch_count"]))
    levee_width = float(params.get("levee_width_px", _ANASTO_DEFAULTS["levee_width_px"]))
    levee_scale = float(params.get("levee_height_scale", _ANASTO_DEFAULTS["levee_height_scale"]))
    marsh_fraction = float(params.get("marsh_fraction", _ANASTO_DEFAULTS["marsh_fraction"]))
    fan_length = float(params.get("fan_length_px", _ANASTO_DEFAULTS["fan_length_px"]))

    branch_mask, centerlines, branch_info = anasto_paths(height, width, branch_count, rng)
    levee_mask = add_levees_narrow(branch_mask, levee_width, levee_scale)
    marsh_mask, overbank_mask, wetland_water = make_marsh(
        branch_mask, marsh_fraction, rng, (height, width)
    )
    breach_points = _select_breach_points(branch_mask, rng)
    fan_mask, fan_intensity = seed_fans(breach_points, fan_length, rng, (height, width))

    masks: Dict[str, Array] = {
        "branch_channel": branch_mask,
        "levee": levee_mask,
        "marsh": marsh_mask,
        "fan": fan_mask,
        "overbank": overbank_mask,
        "wetland_water": wetland_water,
    }
    gray = (
        branch_mask * 0.55
        + levee_mask * 0.35
        + fan_intensity * 0.4
        + marsh_mask * 0.25
        + overbank_mask * 0.2
    )
    analog, masks = compose_anasto(
        gray,
        masks,
        float(params.get("floodplain_noise", _ANASTO_DEFAULTS["floodplain_noise"])),
        rng,
    )
    masks["_metadata_branch_stability"] = np.array([1.0 / max(branch_count, 1)], dtype=np.float32)
    analog, masks = apply_sedimentary_overlays(analog, masks, rng, env="anastomosing")
    return analog, masks


def meander_centerline(
    height: int,
    width: int,
    n_ctrl: int,
    amp_range: Tuple[float, float],
    drift_frac: float,
    rng: np.random.Generator,
) -> Array:
    """Sinuous belt centerline from control points (anchor-fluvial-meander-centerline)."""

    n_ctrl = max(3, n_ctrl)
    ctrl_x = np.linspace(0, width - 1, n_ctrl)
    base_y = np.full(n_ctrl, height / 2.0, dtype=np.float32)
    drift_scale = drift_frac * height * 0.5
    drift = rng.normal(0.0, drift_scale, size=n_ctrl)
    base_y = np.clip(base_y + np.cumsum(drift), height * 0.2, height * 0.8)
    amp_low, amp_high = sorted((float(amp_range[0]), float(amp_range[1])))
    amps = rng.uniform(amp_low, amp_high, size=n_ctrl) * height
    phase = rng.uniform(0, 2 * pi)
    modulation = np.sin(np.linspace(0, 2 * pi, n_ctrl) + phase) * amps
    ctrl_y = np.clip(base_y + modulation, 0, height - 1)
    samples = np.arange(width)
    centerline = np.interp(samples, ctrl_x, ctrl_y)
    return centerline.astype(np.float32)


def meander_variable_channel(
    centerline: Array,
    shape: Tuple[int, int] | Array,
    width_min: float,
    width_max: float,
    rng: Optional[np.random.Generator] = None,
) -> Array:
    """Variable bankfull width along belt (anchor-fluvial-variable-width)."""

    rng = rng or utils.seeded_rng(31415)
    if isinstance(shape, np.ndarray):
        height, width = shape.shape
    else:
        height, width = shape
    columns = np.linspace(0.0, 1.0, width)
    width_profile = np.interp(
        columns,
        [0.0, 0.3, 0.7, 1.0],
        [width_min, width_max, width_min * 1.1, width_max * 0.9],
    )
    width_profile += rng.normal(0.0, (width_max - width_min) * 0.1, size=width)
    width_profile = np.clip(width_profile, width_min, width_max)
    rows = np.arange(height, dtype=np.float32)[:, None]
    center = centerline[None, :]
    half_width = (width_profile / 2.0).astype(np.float32)[None, :]
    mask = (np.abs(rows - center) <= half_width).astype(np.float32)
    return mask


def add_levees(chan: Array, iterations: int) -> Array:
    """Simulate levee rims as a dilation/gaussian rim (anchor-fluvial-levees)."""

    iterations = max(1, iterations)
    dilated = ndimage.grey_dilation(chan, size=(iterations, iterations))
    blurred = ndimage.gaussian_filter(dilated, sigma=max(1.0, iterations / 2.0))
    levees = np.clip(blurred - chan, 0.0, 1.0)
    return levees.astype(np.float32)


def add_scroll_bars(chan: Array, lambda_px: float) -> Array:
    """Apply cosine banding tied to channel distance (anchor-fluvial-scroll-bars)."""

    if lambda_px <= 0:
        return np.zeros_like(chan)
    dist = utils.distance_to_mask(chan >= 0.5)
    scroll = 0.5 * (np.cos((2 * pi * dist) / max(lambda_px, 1.0)) + 1.0)
    scroll *= (chan >= 0.2).astype(np.float32)
    return np.clip(scroll, 0.0, 1.0).astype(np.float32)


def add_oxbow(
    centerline: Array,
    shape: Tuple[int, int] | Array,
    neck_tol: float,
    rng: Optional[np.random.Generator] = None,
) -> Array:
    """Seed oxbow scars adjacent to neck cutoffs (anchor-fluvial-oxbow)."""

    rng = rng or utils.seeded_rng(2718)
    if isinstance(shape, np.ndarray):
        height, width = shape.shape
    else:
        height, width = shape
    mask = np.zeros((height, width), dtype=np.float32)
    step = max(10, width // 32)
    probability = np.clip(neck_tol, 0.0, 1.0)
    for col in range(step, width - step, step):
        if rng.random() > probability:
            continue
        row = int(np.clip(centerline[col] + rng.normal(0.0, height * 0.05), 0, height - 1))
        radius = int(max(4, rng.uniform(6, min(height, width) * 0.08)))
        yy, xx = np.ogrid[:height, :width]
        circle = ((yy - row) ** 2 + (xx - col) ** 2) <= radius**2
        mask[circle] = 1.0
    return mask


def compose_meandering(
    gray: Array,
    masks: Dict[str, Array],
    noise_scale: float = 0.05,
    rng: Optional[np.random.Generator] = None,
) -> tuple[Array, Dict[str, Array]]:
    """Compose grayscale + masks payload (anchor-fluvial-compose)."""

    rng = rng or utils.seeded_rng(4242)
    noise = rng.normal(0.0, noise_scale, size=gray.shape).astype(np.float32)
    blended = np.clip(gray + noise, 0.0, None)
    analog = _normalize(blended)
    normalized_masks = {
        name: np.clip(mask, 0.0, 1.0).astype(np.float32) for name, mask in masks.items()
    }
    return analog, normalized_masks


def compose_braided(
    gray: Array,
    masks: Dict[str, Array],
    noise_scale: float = 0.03,
    rng: Optional[np.random.Generator] = None,
) -> tuple[Array, Dict[str, Array]]:
    """Compose braided grayscale + masks (anchor-fluvial-braided-compose)."""

    rng = rng or utils.seeded_rng(5151)
    noise = rng.normal(0.0, noise_scale, size=gray.shape).astype(np.float32)
    blended = np.clip(gray + noise, 0.0, None)
    analog = _normalize(blended)
    normalized_masks = {
        name: np.clip(mask, 0.0, 1.0).astype(np.float32) for name, mask in masks.items()
    }
    return analog, normalized_masks


def _normalize(field: Array) -> Array:
    arr = field.astype(np.float32)
    min_val = float(arr.min())
    max_val = float(arr.max())
    if max_val - min_val <= 1e-6:
        return np.zeros_like(arr)
    return (arr - min_val) / (max_val - min_val)


def _as_pair(value) -> Tuple[float, float]:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return float(value[0]), float(value[1])
    return (0.1, 0.2)


def braided_threads(
    height: int,
    width: int,
    thread_count: int,
    mean_width: float,
    rng: np.random.Generator,
) -> tuple[list[Array], list[dict], list[Array]]:
    """Generate braided threads (anchor-fluvial-braided-threads)."""

    if not 3 <= thread_count <= 9:
        raise ValueError("thread_count must be between 3 and 9 for braided belts")
    if not 12.0 <= mean_width <= 28.0:
        raise ValueError("mean_thread_width must be between 12 and 28 pixels")

    base_rows = np.linspace(height * 0.2, height * 0.8, thread_count)
    xs = np.linspace(0.0, 1.0, width)
    thread_masks: list[Array] = []
    thread_info: list[dict] = []
    centerlines: list[Array] = []
    phases = rng.uniform(0, 2 * pi, size=thread_count)
    freqs = rng.uniform(1.0, 2.0, size=thread_count)
    for idx in range(thread_count):
        amp = rng.uniform(0.04, 0.18) * height
        center = base_rows[idx] + amp * np.sin(freqs[idx] * 2 * pi * xs + phases[idx])
        center = np.clip(center, 2.0, height - 3.0)
        width_px = float(np.clip(rng.normal(mean_width, mean_width * 0.2), 12.0, 28.0))
        mask = _centerline_mask(center, height, width, width_px)
        thread_masks.append(mask)
        centerlines.append(center.astype(np.float32))
        thread_info.append({"width_px": width_px, "drift_px": float(amp)})
    return thread_masks, thread_info, centerlines


def seed_bars(
    thread_masks: Sequence[Array],
    metadata: Sequence[dict],
    bar_spacing_factor: float,
    rng: np.random.Generator,
    shape: Tuple[int, int],
) -> Array:
    """Place mid-channel bar masks (anchor-fluvial-bar-spacing)."""

    if not 3.5 <= bar_spacing_factor <= 5.5:
        raise ValueError("bar_spacing_factor must be between 3.5 and 5.5")
    height, width = shape
    bars = np.zeros(shape, dtype=np.float32)
    y_idx = np.arange(height, dtype=np.float32)[:, None]
    for mask, info in zip(thread_masks, metadata):
        if np.count_nonzero(mask) == 0:
            continue
        col_sum = mask.sum(axis=0) + 1e-5
        row_positions = (mask * y_idx).sum(axis=0) / col_sum
        width_px = float(info["width_px"])
        spacing = max(4.0, bar_spacing_factor * width_px)
        for column in np.arange(0, width, spacing):
            col_idx = int(np.clip(column, 0, width - 1))
            row_idx = int(np.clip(row_positions[col_idx], 0, height - 1))
            bar = _ellipse_patch(row_idx, col_idx, height, width, width_px * 0.6, spacing * 0.3)
            bars = np.maximum(bars, bar * (mask > 0.1))
    return np.clip(bars, 0.0, 1.0)


def add_chutes(
    centerlines: Sequence[Array],
    metadata: Sequence[dict],
    chute_frequency: float,
    rng: np.random.Generator,
    shape: Tuple[int, int],
) -> Array:
    """Create chute masks (anchor-fluvial-chutes)."""

    height, width = shape
    chute_frequency = float(np.clip(chute_frequency, 0.0, 1.0))
    chutes = np.zeros(shape, dtype=np.float32)
    if not centerlines:
        return chutes
    n_chutes = max(1, int(chute_frequency * len(centerlines) * 2))
    for _ in range(n_chutes):
        start_idx = rng.integers(0, len(centerlines))
        end_idx = (start_idx + rng.integers(1, len(centerlines))) % len(centerlines)
        start_col = int(rng.uniform(0, width * 0.3))
        end_col = int(rng.uniform(width * 0.7, width - 1))
        cols = np.linspace(start_col, end_col, num=max(2, end_col - start_col))
        width_px = float(np.clip(rng.normal(metadata[start_idx]["width_px"] * 0.4, 2.0), 4.0, 12.0))
        rows = np.linspace(
            centerlines[start_idx][start_col],
            centerlines[end_idx][end_col],
            num=cols.shape[0],
        )
        for col, row in zip(cols.astype(int), rows.astype(int)):
            r0 = max(0, row - int(width_px // 2))
            r1 = min(height, row + int(width_px // 2) + 1)
            c0 = max(0, col - int(width_px // 4))
            c1 = min(width, col + int(width_px // 4) + 1)
            chutes[r0:r1, c0:c1] = 1.0
    return np.clip(chutes, 0.0, 1.0)


def _centerline_mask(centerline: Array, height: int, width: int, width_px: float) -> Array:
    rows = np.arange(height, dtype=np.float32)[:, None]
    center = centerline[None, :]
    half_width = width_px / 2.0
    return (np.abs(rows - center) <= half_width).astype(np.float32)


def _ellipse_patch(
    row: int,
    col: int,
    height: int,
    width: int,
    half_height: float,
    half_width: float,
) -> Array:
    r0 = max(0, int(row - half_height))
    r1 = min(height, int(row + half_height + 1))
    c0 = max(0, int(col - half_width))
    c1 = min(width, int(col + half_width + 1))
    yy, xx = np.ogrid[r0:r1, c0:c1]
    ellipse = (
        ((yy - row) / max(half_height, 1.0)) ** 2 + ((xx - col) / max(half_width, 1.0)) ** 2
    ) <= 1.0
    patch = np.zeros((height, width), dtype=np.float32)
    patch[r0:r1, c0:c1] = ellipse.astype(np.float32)
    return patch


def anasto_paths(
    height: int,
    width: int,
    branch_count: int,
    rng: np.random.Generator,
) -> tuple[Array, list[Array], list[dict]]:
    """Create narrow, low-sinuosity branches (anchor-fluvial-anasto-paths)."""

    if not 2 <= branch_count <= 6:
        raise ValueError("branch_count must be between 2 and 6 for anastomosing belts")

    combined = np.zeros((height, width), dtype=np.float32)
    base_rows = np.linspace(height * 0.35, height * 0.65, branch_count)
    centerlines: list[Array] = []
    branch_info: list[dict] = []
    for idx, base in enumerate(base_rows):
        drift = rng.normal(0.0, height * 0.01, size=width)
        smooth = ndimage.gaussian_filter1d(drift, sigma=max(1, width // 80))
        center = base + np.cumsum(smooth) * 0.05
        center += rng.normal(0.0, height * 0.01)
        center = np.clip(center, 3.0, height - 3.0)
        width_px = float(np.clip(rng.uniform(8.0, 14.0), 6.0, 16.0))
        mask = _centerline_mask(center, height, width, width_px)
        combined = np.maximum(combined, mask)
        centerlines.append(center.astype(np.float32))
        branch_info.append({"width_px": width_px})
    return np.clip(combined, 0.0, 1.0), centerlines, branch_info


def add_levees_narrow(branch_channel: Array, width_px: float, height_scale: float) -> Array:
    """Thin levees hugging anastomosing channels (anchor-fluvial-anasto-levees)."""

    width_px = max(width_px, 1.0)
    height_scale = float(np.clip(height_scale, 0.2, 1.0))
    dist = utils.distance_to_mask(branch_channel >= 0.5)
    levee = np.exp(-dist / width_px) * height_scale
    levee = np.clip(levee - 0.2, 0.0, 1.0)
    levee = levee * (branch_channel < 0.3)
    return levee.astype(np.float32)


def make_marsh(
    branch_channel: Array,
    marsh_fraction: float,
    rng: np.random.Generator,
    shape: Tuple[int, int],
) -> tuple[Array, Array, Array]:
    """Derive marsh and overbank masks (anchor-fluvial-anasto-marsh)."""

    height, width = shape
    marsh_fraction = float(np.clip(marsh_fraction, 0.2, 0.7))
    dist = utils.distance_to_mask(branch_channel >= 0.5)
    yy, xx = utils.normalized_coords(height, width)
    base = 0.4 * yy + 0.3 * xx + 0.3 * rng.normal(0.0, 0.05, size=(height, width))
    score = np.clip(dist / (dist.max() + 1e-5), 0.0, 1.0) * 0.6 + base
    thresh = np.quantile(score, 1.0 - marsh_fraction)
    marsh = (score >= thresh).astype(np.float32)
    marsh = np.clip(marsh * (branch_channel < 0.2), 0.0, 1.0)
    overbank = np.clip((1.0 - marsh) * (branch_channel < 0.3), 0.0, 1.0)
    wetland = np.clip(score / (score.max() + 1e-5), 0.0, 1.0) * marsh
    return marsh.astype(np.float32), overbank.astype(np.float32), wetland.astype(np.float32)


def seed_fans(
    breach_points: Sequence[tuple[int, int]],
    fan_length_px: float,
    rng: np.random.Generator,
    shape: Tuple[int, int],
) -> tuple[Array, Array]:
    """Emit crevasse fans (anchor-fluvial-anasto-fans)."""

    if not 15.0 <= fan_length_px <= 60.0:
        raise ValueError("fan_length_px must be between 15 and 60")
    height, width = shape
    fan_values = np.zeros(shape, dtype=np.float32)
    if not breach_points:
        return np.zeros(shape, dtype=np.float32), fan_values
    yy, xx = np.ogrid[:height, :width]
    fan_count = max(1, int(len(breach_points) * 0.2))
    for _ in range(fan_count):
        row, col = breach_points[rng.integers(0, len(breach_points))]
        length = float(np.clip(rng.normal(fan_length_px, fan_length_px * 0.15), 10.0, 80.0))
        spread = np.deg2rad(rng.uniform(15.0, 35.0))
        angle = rng.uniform(-np.pi / 3, np.pi / 3)
        distance = np.sqrt((yy - row) ** 2 + (xx - col) ** 2)
        theta = np.arctan2(yy - row, xx - col)
        angle_mask = np.abs(_angle_diff(theta, angle)) <= spread
        cone = (distance <= length) & angle_mask
        if not np.any(cone):
            continue
        intensity = float(np.clip(rng.normal(0.6, 0.05), 0.3, 0.9))
        decay = np.clip(1.0 - distance / length, 0.0, 1.0)
        fan_values = np.maximum(fan_values, intensity * decay * cone)
    fan_mask = (fan_values > 0.05).astype(np.float32)
    return fan_mask, fan_values


def compose_anasto(
    gray: Array,
    masks: Dict[str, Array],
    noise_scale: float = 0.03,
    rng: Optional[np.random.Generator] = None,
) -> tuple[Array, Dict[str, Array]]:
    """Compose anastomosing grayscale + masks (anchor-fluvial-anasto-compose)."""

    rng = rng or utils.seeded_rng(6060)
    noise = rng.normal(0.0, noise_scale, size=gray.shape).astype(np.float32)
    analog = _normalize(np.clip(gray + noise, 0.0, None))
    normalized_masks = {
        name: np.clip(mask, 0.0, 1.0).astype(np.float32) for name, mask in masks.items()
    }
    return analog, normalized_masks


def _select_breach_points(branch_mask: Array, rng: np.random.Generator) -> list[tuple[int, int]]:
    edge = branch_mask > 0.2
    edge = edge & ~ndimage.binary_erosion(edge)
    coords = np.argwhere(edge)
    if coords.size == 0:
        return []
    rng.shuffle(coords)
    count = max(1, min(len(coords), len(coords) // 20 + 1))
    return [(int(r), int(c)) for r, c in coords[:count]]


def _angle_diff(angle_a: Array, angle_b: float) -> Array:
    return np.arctan2(np.sin(angle_a - angle_b), np.cos(angle_a - angle_b))


def _first_available(masks: Dict[str, Array], *keys: str) -> Optional[Array]:
    for key in keys:
        value = masks.get(key)
        if value is not None:
            return value
    return None


def channel_fill_sandstone(
    gray: Array,
    masks: Dict[str, Array],
    rng: np.random.Generator,
    strength: float = 0.5,
) -> tuple[Array, Dict[str, Array]]:
    """Apply channel-fill textures (anchor-fluvial-channel-fill)."""

    channel = _first_available(masks, "channel", "branch_channel")
    if channel is None:
        return gray, masks
    channel_mask = channel.astype(bool)
    if not np.any(channel_mask):
        masks.setdefault("channel_fill", np.zeros_like(gray))
        return gray, masks
    base_noise = rng.normal(0.0, 1.0, size=gray.shape).astype(np.float32)
    base_noise = ndimage.gaussian_filter(base_noise, sigma=5)
    distance = utils.distance_to_mask(~channel_mask)
    distance = distance / (distance.max() + 1e-5)
    fill = np.clip((1.0 - distance) * 0.7 + base_noise * 0.3, 0.0, 1.0)
    updated = gray.copy()
    updated[channel_mask] = np.clip(
        gray[channel_mask] * (1 - strength) + fill[channel_mask] * strength,
        0.0,
        1.0,
    )
    masks["channel_fill"] = channel_mask.astype(np.float32)
    return updated, masks


def apply_cross_bedding(
    mask: Optional[Array],
    style: str,
    rng: np.random.Generator,
) -> Array:
    """Apply oriented cross-bedding bands (anchor-fluvial-cross-bedding)."""

    if mask is None:
        return np.zeros((), dtype=np.float32)
    if mask.ndim != 2:
        return np.zeros_like(mask, dtype=np.float32)
    height, width = mask.shape
    yy, xx = np.mgrid[0:height, 0:width]
    orientation = rng.uniform(-np.pi / 4, np.pi / 4)
    frequency = 0.25 if style == "planar" else 0.4
    phase = rng.uniform(0, 2 * np.pi)
    bands = 0.5 * (
        1
        + np.sin(
            frequency * (xx * np.cos(orientation) + yy * np.sin(orientation)) * 2 * np.pi + phase
        )
    )
    overlay = np.clip(bands * mask, 0.0, 1.0).astype(np.float32)
    return overlay


def ripple_mark_texture(overbank_mask: Optional[Array], rng: np.random.Generator) -> Array:
    """Create ripple textures on overbank areas (anchor-fluvial-ripple-marks)."""

    if overbank_mask is None:
        return np.zeros((), dtype=np.float32)
    if overbank_mask.ndim != 2:
        return np.zeros_like(overbank_mask, dtype=np.float32)
    height, width = overbank_mask.shape
    yy, xx = np.mgrid[0:height, 0:width]
    wavelength = rng.uniform(8.0, 14.0)
    ripple = 0.5 * (1 + np.sin((yy / wavelength + xx / (wavelength * 0.7)) * 2 * np.pi))
    ripple = ndimage.gaussian_filter(ripple, sigma=1.0)
    return np.clip(ripple * overbank_mask, 0.0, 1.0).astype(np.float32)


def lateral_accretion_surface(channel_mask: Optional[Array], rng: np.random.Generator) -> Array:
    """Approximate lateral accretion surfaces (anchor-fluvial-lateral-accretion)."""

    if channel_mask is None:
        return np.zeros((), dtype=np.float32)
    dist = utils.distance_to_mask(channel_mask >= 0.5)
    band = np.clip(1.0 - dist / (dist.max() + 1e-5), 0.0, 1.0)
    gradient = ndimage.sobel(band)
    overlay = np.clip(np.abs(gradient) * channel_mask, 0.0, 1.0)
    jitter = rng.normal(0.0, 0.05, size=channel_mask.shape).astype(np.float32)
    return np.clip(overlay + jitter, 0.0, 1.0)


def fining_upward_and_mudstone(
    channel_mask: Optional[Array],
    floodplain_mask: Optional[Array],
    rng: np.random.Generator,
) -> tuple[Array, Array]:
    """Generate fining-upward and overbank mudstone masks."""

    if channel_mask is None:
        shape = floodplain_mask.shape if isinstance(floodplain_mask, np.ndarray) else (0,)
        return np.zeros(shape, dtype=np.float32), np.zeros(shape, dtype=np.float32)
    dist = utils.distance_to_mask(channel_mask >= 0.5)
    fining = np.clip(1.0 - dist / (dist.max() + 1e-5), 0.0, 1.0)
    fining = ndimage.gaussian_filter(fining, sigma=2.0)
    fining_mask = np.clip(fining * channel_mask, 0.0, 1.0)
    if floodplain_mask is None:
        mud = np.zeros_like(fining_mask)
    else:
        base = ndimage.gaussian_filter(floodplain_mask, sigma=3.0)
        mud = np.clip(base + rng.normal(0.0, 0.05, size=base.shape), 0.0, 1.0)
    return fining_mask.astype(np.float32), mud.astype(np.float32)


def apply_sedimentary_overlays(
    gray: Array,
    masks: Dict[str, Array],
    rng: np.random.Generator,
    env: str,
) -> tuple[Array, Dict[str, Array]]:
    """Apply sedimentary overlays and metadata across fluvial environments."""

    updated, masks = channel_fill_sandstone(gray, masks, rng)
    cross_target = masks.get("channel_fill")
    cross_overlay = apply_cross_bedding(
        cross_target, "trough" if env == "braided" else "planar", rng
    )
    if cross_overlay.size != 1:
        updated = np.clip(updated + cross_overlay * 0.1, 0.0, 1.0)
        masks["cross_bed"] = cross_overlay
        ripple_base = _first_available(masks, "overbank", "floodplain")
        ripple_overlay = ripple_mark_texture(ripple_base, rng)
    if ripple_overlay.size != 1:
        updated = np.clip(updated + ripple_overlay * 0.05, 0.0, 1.0)
        masks["ripple"] = ripple_overlay
    channel_base = _first_available(masks, "channel", "branch_channel")
    accretion = lateral_accretion_surface(channel_base, rng)
    if accretion.size != 1:
        masks["lateral_accretion"] = np.clip(accretion, 0.0, 1.0)
    floodplain_base = _first_available(masks, "overbank", "floodplain")
    fining_mask, mudstone_mask = fining_upward_and_mudstone(
        channel_base,
        floodplain_base,
        rng,
    )
    if fining_mask.size != 1:
        masks["fining_upward"] = fining_mask
    if mudstone_mask.size != 1:
        masks["overbank_mudstone"] = mudstone_mask
    masks["realization_metadata"] = _petrology_metadata(masks)
    return updated, masks


def _petrology_metadata(masks: Dict[str, Array]) -> dict:
    channel_fill = float(masks.get("channel_fill", np.zeros(1)).mean())
    overbank_arr = _first_available(masks, "overbank", "floodplain")
    if overbank_arr is None:
        overbank_arr = np.zeros(1)
    overbank = float(overbank_arr.mean())
    marsh = float(masks.get("marsh", np.zeros(1)).mean())
    total = channel_fill + overbank + marsh + 1e-6
    feldspar = np.clip(channel_fill / total, 0.2, 0.7)
    clay = np.clip((overbank + marsh) / total * 0.5, 0.1, 0.6)
    quartz = max(0.0, 1.0 - feldspar - clay)
    norm = feldspar + clay + quartz + 1e-9
    mineralogy = {
        "feldspar": round(feldspar / norm, 3),
        "quartz": round(quartz / norm, 3),
        "clay": round(clay / norm, 3),
    }
    cement = "kaolinite" if marsh > 0.2 else "calcite"
    mud_clasts = bool(overbank > 0.1)
    return {
        "mineralogy": mineralogy,
        "cement_signature": cement,
        "mud_clasts_bool": mud_clasts,
    }
