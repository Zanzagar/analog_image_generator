"""Regression tests for documented defects in stats.py.

Covers:
1. compactness = 4*pi*A/P^2 (was area/perimeter)
2. new topology 'connectivity' field = 1 - EulerCharacteristic/A
3. anisotropy_ratio = max/min of directional variogram slopes (was PSD aspect)
4. two_segment_fit optimizes the breakpoint (was fixed midpoint split)
5. metadata_hash is a deterministic digest (was salted builtin hash())
6. public functions must not mutate caller arrays (psd_anisotropy subtracted
   the mean in place on an np.asarray alias of the input)
7. metadata_hash is insensitive to numpy scalar/array types (np.int64(0)
   previously serialized via default=str as "0" while native 0 was a number)
8. entropy is counts-based discrete Shannon entropy in [0, 6] bits for 64
   bins (was density-based: uniform gave 0.0 and concentrated histograms
   went negative)
9. two_segment_fit crossover h0 = exp((b2-b1)/(beta1-beta2)) diverges when
   the two segment slopes are nearly equal (observed h0 ~1e186 in GAN
   River-I 7/9-facies reference tables); pathological h0 is now capped to
   the fitted breakpoint lag and flagged via the additive h0_capped key,
   while sane fits stay byte-identical
10. the h0_capped flag from two_segment_fit was dropped by compute_metrics
    (only beta_seg1/beta_seg2/h0 were mapped into MetricResult), so
    flattened metric rows could not distinguish capped h0 values from
    coincidental ones; the flag now propagates as an additive h0_capped
    key in the flattened row, with every previously-emitted key unchanged
"""

from __future__ import annotations

import subprocess
import sys

import numpy as np
import pytest
from scipy import ndimage

from analog_image_generator import stats


def _circle_mask(size: int = 128, radius: int = 40) -> np.ndarray:
    yy, xx = np.mgrid[0:size, 0:size]
    cy = cx = size // 2
    return (((yy - cy) ** 2 + (xx - cx) ** 2) <= radius**2).astype(np.float32)


def _rect_mask(size: int = 128, h: int = 4, w: int = 100) -> np.ndarray:
    mask = np.zeros((size, size), dtype=np.float32)
    y0 = size // 2 - h // 2
    x0 = (size - w) // 2
    mask[y0 : y0 + h, x0 : x0 + w] = 1.0
    return mask


def _smoothed_noise(seed: int = 7, size: int = 96) -> np.ndarray:
    rng = np.random.default_rng(seed)
    field = rng.normal(size=(size, size)).astype(np.float32)
    field = ndimage.gaussian_filter(field, sigma=(1.0, 4.0))
    field -= field.min()
    field /= field.max() + 1e-9
    return field.astype(np.float32)


# ---------------------------------------------------------------------------
# Fix 1: compactness = 4*pi*A/P^2
# ---------------------------------------------------------------------------


def test_compactness_filled_circle_near_one():
    result = stats._area_compactness("channel", _circle_mask())
    assert result["channel_compactness"] == pytest.approx(1.0, abs=0.15)


def test_compactness_elongated_below_one_and_below_circle():
    circle = stats._area_compactness("channel", _circle_mask())["channel_compactness"]
    rect = stats._area_compactness("channel", _rect_mask())["channel_compactness"]
    assert rect < 1.0
    assert rect < circle


def test_compactness_empty_mask_guarded():
    empty = np.zeros((32, 32), dtype=np.float32)
    result = stats._area_compactness("channel", empty)
    assert result["channel_compactness"] == 0.0
    assert result["channel_area_fraction"] == 0.0


def test_compactness_area_fraction_unchanged():
    mask = _circle_mask(64, 20)
    result = stats._area_compactness("channel", mask)
    assert result["channel_area_fraction"] == pytest.approx(float(mask.mean()))


# ---------------------------------------------------------------------------
# Fix 2: connectivity = 1 - chi/A  (chi = Euler characteristic)
# ---------------------------------------------------------------------------


def test_connectivity_field_exists_alongside_legacy_fields():
    mask = _circle_mask(64, 20)
    result = stats._connectivity("channel", mask)
    assert "channel_connectivity" in result
    assert "channel_component_count" in result
    assert "channel_largest_component_ratio" in result


def test_connectivity_solid_blob_near_one():
    # One component, no holes: chi = 1, connectivity = 1 - 1/A ~ 1
    mask = _circle_mask(64, 20)
    area = float((mask > 0.2).sum())
    result = stats._connectivity("channel", mask)
    assert result["channel_connectivity"] == pytest.approx(1.0 - 1.0 / area, abs=1e-6)


def test_connectivity_blob_with_hole_exactly_one():
    # One component with one hole: chi = 1 - 1 = 0, connectivity = 1
    mask = _circle_mask(64, 20)
    yy, xx = np.mgrid[0:64, 0:64]
    hole = ((yy - 32) ** 2 + (xx - 32) ** 2) <= 5**2
    mask[hole] = 0.0
    result = stats._connectivity("channel", mask)
    assert result["channel_connectivity"] == pytest.approx(1.0, abs=1e-6)


def test_connectivity_scattered_pixels_low():
    # N isolated single pixels: chi = N, A = N -> connectivity = 0
    mask = np.zeros((32, 32), dtype=np.float32)
    mask[2::4, 2::4] = 1.0
    result = stats._connectivity("channel", mask)
    assert result["channel_connectivity"] == pytest.approx(0.0, abs=1e-6)


def test_connectivity_empty_mask_guarded():
    empty = np.zeros((16, 16), dtype=np.float32)
    result = stats._connectivity("channel", empty)
    assert result["channel_connectivity"] == 0.0


def test_compute_metrics_exposes_topology_connectivity():
    gray = _smoothed_noise()
    masks = {"channel": _circle_mask(96, 30), "floodplain": _rect_mask(96, 20, 60)}
    metrics = stats.compute_metrics(gray, masks, "fluvial")
    assert "topology_channel_connectivity" in metrics
    # legacy schema keys must survive
    assert "topology_channel_component_count" in metrics
    assert "topology_channel_largest_component_ratio" in metrics
    assert "topology_channel_compactness" in metrics


# ---------------------------------------------------------------------------
# Fix 3: anisotropy_ratio = max(beta_dir) / min(beta_dir)
# ---------------------------------------------------------------------------


def test_anisotropy_ratio_is_directional_beta_ratio():
    gray = _smoothed_noise()
    masks = {"channel": _circle_mask(96, 30)}
    metrics = stats.compute_metrics(gray, masks, "fluvial")
    betas = [v for k, v in metrics.items() if k.startswith("beta_dir_")]
    assert betas, "expected directional beta fields in metrics"
    expected = max(betas) / min(betas)
    assert metrics["anisotropy_ratio"] == pytest.approx(expected, rel=1e-6)


def test_psd_aspect_field_still_present_and_separate():
    gray = _smoothed_noise(seed=11)
    masks = {"channel": _circle_mask(96, 30)}
    metrics = stats.compute_metrics(gray, masks, "fluvial")
    assert "psd_aspect" in metrics
    assert isinstance(metrics["psd_aspect"], float)


# ---------------------------------------------------------------------------
# Fix 4: two_segment_fit optimized breakpoint
# ---------------------------------------------------------------------------


def test_two_segment_fit_recovers_breakpoint():
    # Continuous piecewise power law: slope 0.9 up to h=8, slope 0.2 after.
    lags = np.arange(1, 25, dtype=np.float32)
    b1, b2, h_break = 0.9, 0.2, 8.0
    gamma = np.where(
        lags <= h_break,
        lags**b1,
        (h_break**b1) * (lags / h_break) ** b2,
    ).astype(np.float32)
    seg = stats.two_segment_fit(lags, gamma)
    assert seg["beta_seg1"] == pytest.approx(b1, abs=0.05)
    assert seg["beta_seg2"] == pytest.approx(b2, abs=0.05)
    assert "breakpoint_lag" in seg
    assert abs(seg["breakpoint_lag"] - h_break) <= 2.0
    assert seg["h0"] == pytest.approx(h_break, rel=0.25)


def test_two_segment_fit_breakpoint_off_center():
    # Breakpoint far from the midpoint of 24 lags: the old fixed midpoint
    # split (index 12) could not recover slopes for a break at lag 5.
    lags = np.arange(1, 25, dtype=np.float32)
    b1, b2, h_break = 1.2, 0.1, 5.0
    gamma = np.where(
        lags <= h_break,
        lags**b1,
        (h_break**b1) * (lags / h_break) ** b2,
    ).astype(np.float32)
    seg = stats.two_segment_fit(lags, gamma)
    assert seg["beta_seg1"] == pytest.approx(b1, abs=0.05)
    assert seg["beta_seg2"] == pytest.approx(b2, abs=0.05)
    assert abs(seg["breakpoint_lag"] - h_break) <= 2.0


def test_two_segment_fit_single_power_law_equal_slopes():
    lags = np.arange(1, 21, dtype=np.float32)
    gamma = lags**0.7
    seg = stats.two_segment_fit(lags, gamma)
    assert seg["beta_seg1"] == pytest.approx(0.7, abs=0.05)
    assert seg["beta_seg2"] == pytest.approx(0.7, abs=0.05)


def test_two_segment_fit_short_series_fallback():
    lags = np.asarray([1.0, 2.0, 3.0], dtype=np.float32)
    gamma = lags**0.5
    seg = stats.two_segment_fit(lags, gamma)
    assert seg["beta_seg1"] == pytest.approx(seg["beta_seg2"])


# ---------------------------------------------------------------------------
# Fix 5: deterministic metadata_hash
# ---------------------------------------------------------------------------


def _metric_result() -> stats.MetricResult:
    return stats.MetricResult(
        beta_iso=0.5,
        beta_dir={"dir_0": 0.5, "dir_90": 0.6},
        beta_seg1=0.4,
        beta_seg2=0.6,
        h0=8.0,
        entropy_global=4.0,
        fractal_dimension=2.5,
        psd_aspect=1.3,
        psd_theta=10.0,
        anisotropy_ratio=1.2,
        topology={},
        qa_flags={},
    )


def test_metadata_hash_insensitive_to_insertion_order():
    meta_a = {"seed": 42, "style": "meandering", "width": 128}
    meta_b = {"width": 128, "seed": 42, "style": "meandering"}
    row_a = stats._flatten_metrics(_metric_result(), "fluvial", meta_a)
    row_b = stats._flatten_metrics(_metric_result(), "fluvial", meta_b)
    assert row_a["metadata_hash"] == row_b["metadata_hash"]


def test_metadata_hash_differs_for_different_content():
    row_a = stats._flatten_metrics(_metric_result(), "fluvial", {"seed": 42})
    row_b = stats._flatten_metrics(_metric_result(), "fluvial", {"seed": 43})
    assert row_a["metadata_hash"] != row_b["metadata_hash"]


# ---------------------------------------------------------------------------
# Fix 6: public functions must not mutate caller arrays
# ---------------------------------------------------------------------------


def test_psd_anisotropy_does_not_mutate_input():
    gray = _smoothed_noise(seed=3)  # float32, so np.asarray would alias it
    original = gray.copy()
    stats.psd_anisotropy(gray)
    assert gray.tobytes() == original.tobytes()


def test_compute_metrics_does_not_mutate_input():
    gray = _smoothed_noise(seed=5)
    masks = {"channel": _circle_mask(96, 30), "floodplain": _rect_mask(96, 20, 60)}
    original_gray = gray.tobytes()
    original_masks = {k: v.tobytes() for k, v in masks.items()}
    stats.compute_metrics(gray, masks, "fluvial")
    assert gray.tobytes() == original_gray
    for key, mask in masks.items():
        assert mask.tobytes() == original_masks[key]


@pytest.mark.parametrize(
    "func",
    [
        stats.entropy,
        lambda arr: stats.compute_variogram(arr, {"dir_0": (0, 1)}, max_lag=8),
        lambda arr: stats.preview_metrics(arr, {"channel": _circle_mask(96, 30)}, "fluvial"),
    ],
    ids=["entropy", "compute_variogram", "preview_metrics"],
)
def test_array_consuming_functions_do_not_mutate_input(func):
    gray = _smoothed_noise(seed=9)
    original = gray.tobytes()
    func(gray)
    assert gray.tobytes() == original


# ---------------------------------------------------------------------------
# Fix 7: metadata_hash insensitive to numpy scalar/array types
# ---------------------------------------------------------------------------


def test_metadata_hash_numpy_scalars_match_native_types():
    meta_np = {"seed": np.int64(42), "scale": np.float64(1.5), "flag": np.bool_(True)}
    meta_native = {"seed": 42, "scale": 1.5, "flag": True}
    row_np = stats._flatten_metrics(_metric_result(), "fluvial", meta_np)
    row_native = stats._flatten_metrics(_metric_result(), "fluvial", meta_native)
    assert row_np["metadata_hash"] == row_native["metadata_hash"]


def test_metadata_hash_numpy_types_in_nested_structures():
    meta_np = {
        "seed": np.int32(0),
        "nested": {"count": np.int64(7), "levels": [np.float64(0.25), np.float64(0.75)]},
        "shape": np.asarray([128, 128], dtype=np.int64),
    }
    meta_native = {
        "seed": 0,
        "nested": {"count": 7, "levels": [0.25, 0.75]},
        "shape": [128, 128],
    }
    row_np = stats._flatten_metrics(_metric_result(), "fluvial", meta_np)
    row_native = stats._flatten_metrics(_metric_result(), "fluvial", meta_native)
    assert row_np["metadata_hash"] == row_native["metadata_hash"]


def test_metadata_hash_still_differs_for_different_numpy_content():
    row_a = stats._flatten_metrics(_metric_result(), "fluvial", {"seed": np.int64(42)})
    row_b = stats._flatten_metrics(_metric_result(), "fluvial", {"seed": np.int64(43)})
    assert row_a["metadata_hash"] != row_b["metadata_hash"]


# ---------------------------------------------------------------------------
# Fix 8: entropy = counts-based discrete Shannon entropy, bounded [0, 6] bits
# ---------------------------------------------------------------------------


def test_entropy_uniform_image_near_six_bits():
    # A finite ramp over [0, 1) fills all 64 bins equally: H = log2(64) = 6.
    gray = np.linspace(0.0, 1.0, 64 * 64, endpoint=False, dtype=np.float32).reshape(64, 64)
    assert stats.entropy(gray) == pytest.approx(6.0, abs=0.1)


def test_entropy_large_uniform_sample_near_six_bits():
    rng = np.random.default_rng(42)
    gray = rng.uniform(0.0, 1.0, size=(256, 256)).astype(np.float32)
    assert stats.entropy(gray) == pytest.approx(6.0, abs=0.1)


def test_entropy_constant_image_exactly_zero():
    gray = np.full((64, 64), 0.5, dtype=np.float32)
    assert stats.entropy(gray) == 0.0


def test_entropy_two_value_image_one_bit():
    gray = np.full((64, 64), 0.1, dtype=np.float32)
    gray[:, 32:] = 0.9
    assert stats.entropy(gray) == pytest.approx(1.0, abs=1e-6)


@pytest.mark.parametrize("seed", [0, 1, 7, 123])
def test_entropy_bounded_zero_to_six_bits(seed):
    rng = np.random.default_rng(seed)
    candidates = [
        rng.uniform(0.0, 1.0, size=(64, 64)),
        np.clip(rng.normal(0.5, 0.01, size=(64, 64)), 0.0, 1.0 - 1e-6),
        np.clip(rng.beta(0.5, 0.5, size=(64, 64)), 0.0, 1.0 - 1e-6),
    ]
    for gray in candidates:
        value = stats.entropy(gray.astype(np.float32))
        assert 0.0 <= value <= 6.0
        assert value >= 0.0


def test_entropy_monotone_multi_level_at_least_constant():
    constant = np.full((64, 64), 0.3, dtype=np.float32)
    rng = np.random.default_rng(11)
    noisy = rng.choice([0.1, 0.35, 0.6, 0.85], size=(64, 64)).astype(np.float32)
    assert stats.entropy(noisy) >= stats.entropy(constant)
    assert stats.entropy(noisy) > 0.0


# ---------------------------------------------------------------------------
# Fix 9: two_segment_fit crossover h0 must not explode for near-equal slopes
# ---------------------------------------------------------------------------


def _piecewise_gamma(lags: np.ndarray, b1: float, b2: float, h_break: float) -> np.ndarray:
    return np.where(
        lags <= h_break,
        lags**b1,
        (h_break**b1) * (lags / h_break) ** b2,
    ).astype(np.float32)


def test_h0_capped_for_near_equal_slopes_single_power_law():
    # A pure power law forced through the two-segment path: both segment
    # slopes come out ~0.7, so the crossover exponent is 0/0-shaped garbage
    # (previously h0 = 0.043, far outside the lag range [1, 24]).
    lags = np.arange(1, 25, dtype=np.float32)
    gamma = (lags**0.7).astype(np.float32)
    seg = stats.two_segment_fit(lags, gamma)
    assert "h0_capped" in seg
    assert seg["h0_capped"] is True
    assert np.isfinite(seg["h0"])
    assert lags.min() <= seg["h0"] <= lags.max()
    # capped value is the fitted breakpoint lag
    assert seg["h0"] == seg["breakpoint_lag"]


def test_h0_unchanged_for_genuine_two_segment_series():
    # Reuses the Fix-4 breakpoint-recovery fixtures. Sane fits must be
    # byte-identical to pre-guard behavior (values pinned from the current
    # implementation: exp((b2-b1)/(beta1-beta2+1e-6)) in float64).
    lags = np.arange(1, 25, dtype=np.float32)

    seg = stats.two_segment_fit(lags, _piecewise_gamma(lags, 0.9, 0.2, 8.0))
    assert seg["h0"] == 7.999976586006721
    assert seg["h0_capped"] is False

    seg = stats.two_segment_fit(lags, _piecewise_gamma(lags, 1.2, 0.1, 5.0))
    assert seg["h0"] == 4.999992706459131
    assert seg["h0_capped"] is False


def test_h0_capped_key_present_in_short_series_fallback():
    lags = np.asarray([1.0, 2.0, 3.0], dtype=np.float32)
    gamma = (lags**0.5).astype(np.float32)
    seg = stats.two_segment_fit(lags, gamma)
    assert "h0_capped" in seg
    # finite fallback h0 (= exp(intercept)) is left untouched
    assert seg["h0_capped"] is False
    assert seg["h0"] == pytest.approx(1.0, abs=0.05)


@pytest.mark.parametrize("seed", range(20))
def test_h0_always_finite_and_within_lag_range(seed):
    # Battery of seeded random gamma curves, including near-flat and
    # noisy-single-slope families that previously drove h0 to ~1e186/inf.
    rng = np.random.default_rng(seed)
    lags = np.arange(1, 25, dtype=np.float32)
    amp = float(np.exp(rng.uniform(-3.0, 3.0)))
    beta = float(rng.uniform(0.0, 1.5))
    family = seed % 4
    if family == 0:
        gamma = amp * lags**beta
    elif family == 1:
        gamma = amp * lags**beta * np.exp(rng.normal(0.0, 0.05, size=lags.size))
    elif family == 2:
        gamma = amp * (1.0 + 0.01 * rng.uniform(-1.0, 1.0, size=lags.size))
    else:
        h_break = float(rng.uniform(3.0, 20.0))
        b2 = float(rng.uniform(0.0, 1.5))
        gamma = amp * _piecewise_gamma(lags, beta, b2, h_break)
    seg = stats.two_segment_fit(lags, gamma.astype(np.float32))
    assert np.isfinite(seg["h0"])
    assert lags.min() <= seg["h0"] <= lags.max()
    assert isinstance(seg["h0_capped"], bool)

def test_metadata_hash_stable_across_processes():
    meta = {"seed": 42, "style": "meandering", "nested": {"b": 2, "a": 1}}
    local = stats._flatten_metrics(_metric_result(), "fluvial", meta)["metadata_hash"]
    script = (
        "from analog_image_generator import stats\n"
        "m = stats.MetricResult(beta_iso=0.5, beta_dir={'dir_0': 0.5, 'dir_90': 0.6},\n"
        "    beta_seg1=0.4, beta_seg2=0.6, h0=8.0, entropy_global=4.0,\n"
        "    fractal_dimension=2.5, psd_aspect=1.3, psd_theta=10.0,\n"
        "    anisotropy_ratio=1.2, topology={}, qa_flags={})\n"
        "meta = {'nested': {'a': 1, 'b': 2}, 'style': 'meandering', 'seed': 42}\n"
        "print(stats._flatten_metrics(m, 'fluvial', meta)['metadata_hash'])\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stdout.strip() == local


# ---------------------------------------------------------------------------
# Fix 10: h0_capped propagates through compute_metrics into flattened rows
# ---------------------------------------------------------------------------


def _white_noise(seed: int = 1, size: int = 96) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(0.0, 1.0, size=(size, size)).astype(np.float32)


def _topology_masks(size: int = 96) -> dict[str, np.ndarray]:
    return {"channel": _circle_mask(size, 30), "floodplain": _rect_mask(size, 20, 60)}


def _isotropic_seg(gray: np.ndarray) -> dict:
    variogram = stats.compute_variogram(gray, stats._DIRECTIONS)["isotropic"]
    return stats.two_segment_fit(variogram["lags"], variogram["semivariances"])


def test_flattened_row_h0_capped_true_for_pathological_series():
    # White noise: near-flat variogram, near-equal segment slopes, so the
    # crossover h0 is pathological and two_segment_fit caps it. The flag
    # must survive into the flattened compute_metrics row.
    gray = _white_noise(seed=1)
    assert _isotropic_seg(gray)["h0_capped"] is True  # fixture sanity
    row = stats.compute_metrics(gray, _topology_masks(), "fluvial")
    assert "h0_capped" in row
    assert row["h0_capped"] is True


def test_flattened_row_h0_capped_false_for_sane_series():
    gray = _smoothed_noise(seed=7)
    assert _isotropic_seg(gray)["h0_capped"] is False  # fixture sanity
    row = stats.compute_metrics(gray, _topology_masks(), "fluvial")
    assert "h0_capped" in row
    assert row["h0_capped"] is False


def test_flattened_row_h0_capped_is_python_bool():
    # CSV/JSON serialization must see a native bool, not np.bool_.
    for gray in (_white_noise(seed=1), _smoothed_noise(seed=7)):
        row = stats.compute_metrics(gray, _topology_masks(), "fluvial")
        assert isinstance(row["h0_capped"], bool)


def test_flattened_row_previous_keys_and_values_unchanged():
    # The flag is strictly additive: the flattened row keeps exactly the
    # previously-emitted key set plus h0_capped, and the seg-fit values
    # match the direct two_segment_fit output bit-for-bit.
    gray = _smoothed_noise(seed=7)
    row = stats.compute_metrics(gray, _topology_masks(), "fluvial", metadata={"seed": 7})
    seg = _isotropic_seg(gray)
    assert row["beta_seg1"] == seg["beta_seg1"]
    assert row["beta_seg2"] == seg["beta_seg2"]
    assert row["h0"] == seg["h0"]

    baseline_keys = {
        "env",
        "beta_iso",
        "entropy_global",
        "fractal_dimension",
        "beta_seg1",
        "beta_seg2",
        "h0",
        "psd_aspect",
        "psd_theta",
        "anisotropy_ratio",
        "metadata_hash",
    }
    baseline_keys |= {f"beta_dir_{angle}" for angle in (0, 45, 90, 135)}
    baseline_keys |= {
        f"topology_{label}_{field}"
        for label in ("channel", "floodplain", "levee")
        for field in (
            "area_fraction",
            "compactness",
            "component_count",
            "largest_component_ratio",
            "connectivity",
        )
    }
    baseline_keys |= {"qa_psd_anisotropy_warning", "qa_channel_area_warning"}
    assert set(row) == baseline_keys | {"h0_capped"}


def test_flatten_metrics_defaults_h0_capped_false():
    # MetricResult constructors that predate the flag (no h0_capped argument)
    # must still flatten, with the additive key defaulting to False.
    row = stats._flatten_metrics(_metric_result(), "fluvial", {})
    assert row["h0_capped"] is False
