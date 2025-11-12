"""Statistics stack (Phase 1 & 2 metrics)."""

from __future__ import annotations

from typing import Dict, Tuple


def compute_metrics(gray: Tuple, masks: Dict[str, Tuple], env: str) -> Dict[str, float]:
    """Compute Phase 1/2 metrics for a single realization."""
    raise NotImplementedError("Metrics implementation arrives with STAT milestone.")
