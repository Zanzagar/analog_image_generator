import numpy as np

from analog_image_generator import geologic_generators as gg
from analog_image_generator import stats


def test_compute_variogram_monotonic():
    gradient = np.tile(np.linspace(0, 1, 64, dtype=np.float32), (64, 1))
    series = stats.compute_variogram(gradient, {"dir_0": (0, 1)}, max_lag=10)
    iso = series["isotropic"]["semivariances"]
    assert np.all(np.diff(iso) >= -1e-5)


def test_psd_anisotropy_detects_direction():
    yy = np.linspace(-1, 1, 128, dtype=np.float32)
    xx = np.linspace(-1, 1, 128, dtype=np.float32)
    yy, xx = np.meshgrid(yy, xx, indexing="ij")
    field = np.exp(-((xx * 4) ** 2 + (yy) ** 2))
    metrics = stats.psd_anisotropy(field)
    assert metrics["aspect_ratio"] > 1.1


def test_compute_metrics_returns_required_keys():
    params = {"style": "meandering", "height": 96, "width": 96, "seed": 12}
    analog, masks = gg.generate_fluvial(params)
    metrics = stats.compute_metrics(analog, masks, "fluvial")
    required = {
        "beta_iso",
        "entropy_global",
        "fractal_dimension",
        "psd_aspect",
        "topology_channel_area_fraction",
        "qa_channel_area_warning",
    }
    assert required.issubset(metrics.keys())
    assert isinstance(metrics["beta_iso"], float)
