"""Phase 1 & 2 statistics for analog realizations (STAT anchors)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

Array = NDArray[np.float32]

VariogramSeries = dict[str, dict[str, Array]]


@dataclass
class MetricResult:
    """Container to keep code intent readable."""

    beta_iso: float
    beta_dir: dict[str, float]
    beta_seg1: float
    beta_seg2: float
    h0: float
    entropy_global: float
    fractal_dimension: float
    psd_aspect: float
    psd_theta: float
    anisotropy_ratio: float
    topology: dict[str, float]
    qa_flags: dict[str, bool]


_DIRECTIONS = {
    "dir_0": (0, 1),
    "dir_45": (-1, 1),
    "dir_90": (1, 0),
    "dir_135": (1, 1),
}


def compute_metrics(
    gray: Array,
    masks: Mapping[str, Array | dict],
    env: str,
    *,
    metadata: Mapping | None = None,
) -> dict[str, float | int | str]:
    """Compute PRD-required Phase 1/2 metrics for the requested environment."""

    env_key = env.strip().lower()
    gray = np.asarray(gray, dtype=np.float32)
    meta_payload = metadata or masks.get("realization_metadata") or {}

    variograms = compute_variogram(gray, _DIRECTIONS)
    iso = variograms["isotropic"]
    beta_iso, _ = fit_power_law(iso["lags"], iso["semivariances"])
    beta_dir = {}
    for key, series in variograms.items():
        if key == "isotropic":
            continue
        beta, _ = fit_power_law(series["lags"], series["semivariances"])
        beta_dir[key] = beta

    seg = two_segment_fit(iso["lags"], iso["semivariances"])
    entropy_val = entropy(gray)
    fractal = fractal_dimension(beta_iso)
    psd = psd_anisotropy(gray)
    topology = topology_metrics(masks)
    qa_flags = _qa_flags(env_key, psd, topology)

    metrics = MetricResult(
        beta_iso=beta_iso,
        beta_dir=beta_dir,
        beta_seg1=seg["beta_seg1"],
        beta_seg2=seg["beta_seg2"],
        h0=seg["h0"],
        entropy_global=entropy_val,
        fractal_dimension=fractal,
        psd_aspect=psd["aspect_ratio"],
        psd_theta=psd["theta_deg"],
        anisotropy_ratio=psd["aspect_ratio"],
        topology=topology,
        qa_flags=qa_flags,
    )

    result = _flatten_metrics(metrics, env_key, meta_payload)
    return result


def preview_metrics(gray: Array, masks: Mapping[str, Array], env: str) -> dict[str, float]:
    """Lightweight subset used for interactive previews (β/D/H placeholders)."""

    gray = np.asarray(gray, dtype=np.float32)
    variogram = compute_variogram(gray, {"dir_0": (0, 1)}, max_lag=8)["isotropic"]
    beta_iso, _ = fit_power_law(variogram["lags"], variogram["semivariances"])
    entropy_val = entropy(gray)
    return {
        "beta_iso": float(beta_iso),
        "fractal_dimension": float(fractal_dimension(beta_iso)),
        "entropy_global": float(entropy_val),
    }


def compute_variogram(
    gray: Array,
    directions: Mapping[str, tuple[int, int]],
    *,
    max_lag: int = 24,
) -> VariogramSeries:
    """Return directional and isotropic semi-variograms."""

    gray = np.asarray(gray, dtype=np.float32)
    height, width = gray.shape
    series: VariogramSeries = {}
    iso_lags: list[float] = []
    iso_semivariance: list[float] = []

    for name, (dy, dx) in directions.items():
        lags: list[float] = []
        gamma: list[float] = []
        for lag in range(1, max_lag + 1):
            shift_y = dy * lag
            shift_x = dx * lag
            src = gray[max(0, shift_y) : height + min(0, shift_y), max(0, shift_x) : width + min(0, shift_x)]
            dst = gray[max(0, -shift_y) : height - max(0, shift_y), max(0, -shift_x) : width - max(0, shift_x)]
            if src.size == 0 or dst.size == 0:
                break
            diff = src - dst
            semivar = 0.5 * float(np.mean(diff * diff))
            lags.append(float(np.hypot(shift_y, shift_x)))
            gamma.append(semivar)
        if not lags:
            continue
        series[name] = {
            "lags": np.asarray(lags, dtype=np.float32),
            "semivariances": np.asarray(gamma, dtype=np.float32),
        }
        iso_lags.extend(lags)
        iso_semivariance.extend(gamma)

    if not iso_lags:
        iso_lags = [1.0]
        iso_semivariance = [0.0]
    iso_sorted = np.argsort(iso_lags)
    iso_lags_arr = np.asarray(iso_lags, dtype=np.float32)[iso_sorted]
    iso_gamma_arr = np.asarray(iso_semivariance, dtype=np.float32)[iso_sorted]
    series["isotropic"] = {"lags": iso_lags_arr, "semivariances": iso_gamma_arr}
    return series


def fit_power_law(lags: Array, gamma: Array) -> tuple[float, float]:
    """Fit log γ = a + β log h; returns β and intercept."""

    lags = np.asarray(lags, dtype=np.float32)
    gamma = np.asarray(gamma, dtype=np.float32)
    mask = (lags > 0) & (gamma > 0)
    if mask.sum() < 2:
        return 0.0, 0.0
    x = np.log(lags[mask])
    y = np.log(gamma[mask])
    slope, intercept = np.polyfit(x, y, 1)
    return float(slope), float(intercept)


def two_segment_fit(lags: Array, gamma: Array) -> dict[str, float]:
    """Fit two linear segments to the log-log variogram."""

    lags = np.asarray(lags, dtype=np.float32)
    gamma = np.asarray(gamma, dtype=np.float32)
    mask = (lags > 0) & (gamma > 0)
    if mask.sum() < 4:
        beta, intercept = fit_power_law(lags, gamma)
        return {"beta_seg1": beta, "beta_seg2": beta, "h0": np.exp(intercept)}
    lags = lags[mask]
    gamma = gamma[mask]
    split = len(lags) // 2
    beta1, b1 = fit_power_law(lags[:split], gamma[:split])
    beta2, b2 = fit_power_law(lags[split:], gamma[split:])
    h0 = np.exp((b2 - b1) / (beta1 - beta2 + 1e-6))
    return {"beta_seg1": beta1, "beta_seg2": beta2, "h0": float(h0)}


def entropy(gray: Array) -> float:
    """Global Shannon entropy of grayscale values."""

    arr = np.asarray(gray, dtype=np.float32)
    hist, _ = np.histogram(arr, bins=64, range=(0.0, 1.0), density=True)
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist + 1e-12)))


def fractal_dimension(beta: float) -> float:
    """Approximate fractal dimension from variogram slope."""

    beta = float(beta)
    dimension = 3.0 - beta / 2.0
    return float(np.clip(dimension, 2.0, 3.0))


def psd_anisotropy(gray: Array) -> dict[str, float]:
    """Estimate PSD anisotropy via second-moment ellipse in frequency space."""

    arr = np.asarray(gray, dtype=np.float32)
    arr -= float(arr.mean())
    spectrum = np.fft.fftshift(np.abs(np.fft.fft2(arr)) ** 2)
    height, width = spectrum.shape
    yy = np.linspace(-0.5, 0.5, height, dtype=np.float32)
    xx = np.linspace(-0.5, 0.5, width, dtype=np.float32)
    yy, xx = np.meshgrid(yy, xx, indexing="ij")
    weight = spectrum / (spectrum.sum() + 1e-9)
    m_xx = float((weight * xx * xx).sum())
    m_yy = float((weight * yy * yy).sum())
    m_xy = float((weight * xx * yy).sum())
    trace = m_xx + m_yy
    det = m_xx * m_yy - m_xy * m_xy
    eig_term = max(trace ** 2 / 4.0 - det, 0.0)
    lambda1 = trace / 2.0 + np.sqrt(eig_term)
    lambda2 = trace / 2.0 - np.sqrt(eig_term)
    ratio = float(np.sqrt((lambda1 + 1e-9) / (lambda2 + 1e-9)))
    theta = 0.5 * np.degrees(np.arctan2(2 * m_xy, (m_xx - m_yy + 1e-9)))
    return {"aspect_ratio": ratio, "theta_deg": float(theta)}


def topology_metrics(masks: Mapping[str, Array | dict]) -> dict[str, float]:
    """Compute area/compactness/connectivity metrics for relevant masks."""

    channel = _get_mask(masks, ("channel", "branch_channel"))
    floodplain = _get_mask(masks, ("floodplain", "overbank"))
    levee = _get_mask(masks, ("levee",))
    result = {}
    for label, mask in {
        "channel": channel,
        "floodplain": floodplain,
        "levee": levee,
    }.items():
        result.update(_area_compactness(label, mask))
        result.update(_connectivity(label, mask))
    return result


def _flatten_metrics(metrics: MetricResult, env: str, metadata: Mapping) -> dict:
    result: dict[str, float | int | str | bool] = {
        "env": env,
        "beta_iso": metrics.beta_iso,
        "entropy_global": metrics.entropy_global,
        "fractal_dimension": metrics.fractal_dimension,
        "beta_seg1": metrics.beta_seg1,
        "beta_seg2": metrics.beta_seg2,
        "h0": metrics.h0,
        "psd_aspect": metrics.psd_aspect,
        "psd_theta": metrics.psd_theta,
        "anisotropy_ratio": metrics.anisotropy_ratio,
    }
    for name, value in metrics.beta_dir.items():
        result[f"beta_{name}"] = value
    result.update({f"topology_{k}": v for k, v in metrics.topology.items()})
    result.update({f"qa_{k}": v for k, v in metrics.qa_flags.items()})
    if metadata:
        result["metadata_hash"] = hash(str(sorted(metadata.items())))
        if "stacked_packages" in metadata:
            result["stacked_package_count"] = metadata["stacked_packages"]["stack_statistics"]["package_count"]
    return result


def _qa_flags(env: str, psd: dict[str, float], topology: dict[str, float]) -> dict[str, bool]:
    flags = {
        "psd_anisotropy_warning": False,
        "channel_area_warning": False,
    }
    if env == "braided" and psd["aspect_ratio"] > 2.0:
        flags["psd_anisotropy_warning"] = True
    channel_area = topology.get("channel_area_fraction", 0.0)
    if channel_area < 0.05 or channel_area > 0.8:
        flags["channel_area_warning"] = True
    return flags


def _get_mask(masks: Mapping[str, Array | dict], keys: Sequence[str]) -> Array:
    for key in keys:
        arr = masks.get(key)
        if isinstance(arr, np.ndarray):
            return arr.astype(np.float32)
    first = next(iter(masks.values()))
    if isinstance(first, np.ndarray):
        return np.zeros_like(first, dtype=np.float32)
    raise ValueError("Cannot infer mask shape for topology metrics.")


def _area_compactness(label: str, mask: Array) -> dict[str, float]:
    area = float(mask.mean())
    grad_y = np.abs(np.diff(mask, axis=0, prepend=0.0))
    grad_x = np.abs(np.diff(mask, axis=1, prepend=0.0))
    perimeter = float((grad_x + grad_y).sum()) + 1e-6
    compactness = float(area / perimeter)
    return {
        f"{label}_area_fraction": area,
        f"{label}_compactness": compactness,
    }


def _connectivity(label: str, mask: Array) -> dict[str, float]:
    struct = np.ones((3, 3))
    labeled, count = ndimage.label(mask > 0.2, structure=struct)
    largest = np.max(ndimage.sum(mask, labeled, index=range(1, count + 1))) if count else 0.0
    ratio = float(largest / (mask.sum() + 1e-6))
    return {
        f"{label}_component_count": float(count),
        f"{label}_largest_component_ratio": ratio,
    }
