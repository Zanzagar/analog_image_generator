"""Reporting pipeline: CSV, per-env PDFs, merged master PDF (REP anchors)."""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from PyPDF2 import PdfMerger
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from . import utils


@dataclass(frozen=True)
class MetricRow:
    env: str
    realization_id: str
    seed: int
    beta_iso: float
    beta_seg1: float
    beta_seg2: float
    h0: float
    entropy_global: float
    fractal_dimension: float
    psd_aspect: float
    psd_theta: float
    topology_channel_area_fraction: float
    topology_channel_compactness: float
    topology_channel_component_count: float
    topology_channel_largest_component_ratio: float
    qa_psd_anisotropy_warning: bool
    qa_channel_area_warning: bool
    petrology_cement: str | None = None
    petrology_mineralogy: dict[str, float] = field(default_factory=dict)
    stacked_package_count: int | None = None


CSV_COLUMNS = [
    "env",
    "realization_id",
    "seed",
    "beta_iso",
    "beta_seg1",
    "beta_seg2",
    "h0",
    "entropy_global",
    "fractal_dimension",
    "psd_aspect",
    "psd_theta",
    "topology_channel_area_fraction",
    "topology_channel_compactness",
    "topology_channel_component_count",
    "topology_channel_largest_component_ratio",
    "qa_psd_anisotropy_warning",
    "qa_channel_area_warning",
    "petrology_cement",
    "petrology_mineralogy",
    "stacked_package_count",
]


def build_reports(metrics_rows: Iterable[Mapping[str, object]], output_dir: Path | str) -> dict[str, Path]:
    """Create CSV + PDFs from the supplied metrics rows."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    materialized = list(metrics_rows)
    if not materialized:
        raise ValueError("metrics_rows must contain at least one entry")
    csv_path = _write_csv(materialized, output_path)
    mosaics = _generate_mosaics(materialized, output_path / "mosaics")
    env_pdfs = _build_env_pdfs(materialized, mosaics, output_path / "pdfs")
    master_pdf = _merge_master_pdf(env_pdfs, output_path / "master_report.pdf")
    return {"csv": csv_path, "env_pdfs": env_pdfs, "master_pdf": master_pdf}


def _write_csv(rows: list[Mapping[str, object]], output_dir: Path) -> Path:
    frame = pd.DataFrame(rows)
    missing = [col for col in CSV_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError(f"metrics_rows missing required columns: {missing}")
    frame = frame[CSV_COLUMNS]
    csv_path = output_dir / "metrics.csv"
    output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False)
    return csv_path


def _generate_mosaics(rows: list[Mapping[str, object]], output_dir: Path) -> dict[str, dict[str, Path]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    env_groups: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        env_groups.setdefault(row["env"], []).append(row)
    mosaics: dict[str, dict[str, Path]] = {}
    for env, env_rows in env_groups.items():
        sample = env_rows[0]
        gray = sample.get("gray")
        color = sample.get("color")
        if gray is None or color is None:
            continue
        gray_path = output_dir / f"{env}_gray.png"
        color_path = output_dir / f"{env}_facies.png"
        _save_image(gray, gray_path, cmap="gray")
        _save_image(color, color_path, cmap=None)
        mosaics[env] = {"gray": gray_path, "color": color_path}
    return mosaics


def _build_env_pdfs(
    rows: list[Mapping[str, object]],
    mosaics: Mapping[str, Mapping[str, Path]],
    output_dir: Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    env_groups: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        env_groups.setdefault(row["env"], []).append(row)
    env_pdfs: list[Path] = []
    for env, env_rows in env_groups.items():
        pdf_path = output_dir / f"{env}_report.pdf"
        _render_env_pdf(env, env_rows, mosaics.get(env, {}), pdf_path)
        env_pdfs.append(pdf_path)
    return env_pdfs


def _render_env_pdf(
    env: str,
    rows: list[Mapping[str, object]],
    mosaic_paths: Mapping[str, Path],
    pdf_path: Path,
) -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(36, height - 36, f"{env.title()} Report")
    y = height - 72
    if mosaic_paths.get("gray"):
        c.drawImage(ImageReader(mosaic_paths["gray"]), 36, y - 256, width=256, height=256)
    if mosaic_paths.get("color"):
        c.drawImage(ImageReader(mosaic_paths["color"]), 320, y - 256, width=256, height=256)
    beta_hist = _histogram(rows, "beta_iso")
    entropy_hist = _histogram(rows, "entropy_global")
    if beta_hist:
        c.drawImage(ImageReader(beta_hist), 36, y - 512, width=256, height=180)
    if entropy_hist:
        c.drawImage(ImageReader(entropy_hist), 320, y - 512, width=256, height=180)
    table_y = 120
    _draw_summary_table(c, rows, table_y)
    c.showPage()
    c.save()


def _histogram(rows: Sequence[Mapping[str, object]], field: str) -> io.BytesIO | None:
    values = [float(row[field]) for row in rows if row.get(field) is not None]
    if not values:
        return None
    buf = io.BytesIO()
    plt.figure(figsize=(2.5, 2.5))
    plt.hist(values, bins=10, color="#264653")
    plt.title(field)
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf


def _draw_summary_table(canvas_obj: canvas.Canvas, rows: Sequence[Mapping[str, object]], y: float) -> None:
    canvas_obj.setFont("Helvetica", 9)
    headers = ["Realization", "β_iso", "D", "PSD_AR", "QA Flags"]
    canvas_obj.drawString(36, y + 16, "Summary")
    data = [headers]
    for row in rows[:8]:
        flags = ", ".join([name.replace("qa_", "") for name, value in row.items() if name.startswith("qa_") and value])
        data.append(
            [
                str(row.get("realization_id", "")),
                f"{row.get('beta_iso', 0):.3f}",
                f"{row.get('fractal_dimension', 0):.3f}",
                f"{row.get('psd_aspect', 0):.2f}",
                flags or "—",
            ]
        )
    col_width = 120
    for r_idx, row in enumerate(data):
        x = 36
        for value in row:
            canvas_obj.drawString(x, y - 12 * r_idx, value)
            x += col_width


def _merge_master_pdf(env_pdfs: Sequence[Path], output_path: Path) -> Path:
    merger = PdfMerger()
    for pdf in env_pdfs:
        merger.append(str(pdf))
    with output_path.open("wb") as fh:
        merger.write(fh)
    return output_path


def _save_image(array: np.ndarray, path: Path, *, cmap: str | None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.imsave(path, np.clip(array, 0.0, 1.0), cmap=cmap, vmin=0.0, vmax=1.0)
