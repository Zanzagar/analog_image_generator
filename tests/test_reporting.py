from pathlib import Path

import numpy as np

from analog_image_generator import reporting


def _sample_row(env: str, idx: int):
    return {
        "env": env,
        "realization_id": f"{env}-{idx}",
        "seed": idx,
        "beta_iso": 0.6,
        "beta_seg1": 0.4,
        "beta_seg2": 0.8,
        "h0": 10.0,
        "entropy_global": 4.2,
        "fractal_dimension": 2.4,
        "psd_aspect": 1.3,
        "psd_theta": 45.0,
        "topology_channel_area_fraction": 0.3,
        "topology_channel_compactness": 0.1,
        "topology_channel_component_count": 2.0,
        "topology_channel_largest_component_ratio": 0.7,
        "qa_psd_anisotropy_warning": False,
        "qa_channel_area_warning": False,
        "petrology_cement": "calcite",
        "petrology_mineralogy": {"quartz": 0.5},
        "stacked_package_count": 2,
        "gray": np.random.rand(64, 64).astype("float32"),
        "color": np.random.rand(64, 64, 3).astype("float32"),
    }


def test_build_reports_creates_files(tmp_path: Path):
    rows = [_sample_row("fluvial", i) for i in range(2)]
    artifact_map = reporting.build_reports(rows, tmp_path)
    assert artifact_map["csv"].exists()
    for pdf in artifact_map["env_pdfs"]:
        assert pdf.exists()
    assert artifact_map["master_pdf"].exists()
