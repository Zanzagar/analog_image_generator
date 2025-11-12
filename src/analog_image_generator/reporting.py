"""Reporting utilities (CSV + PDF generation)."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


def build_reports(metrics_rows: List[Dict[str, float]], output_dir: Path) -> None:
    """Create CSV and PDF artifacts for the provided metrics."""
    raise NotImplementedError("Reporting implementation lands with REP milestone.")
