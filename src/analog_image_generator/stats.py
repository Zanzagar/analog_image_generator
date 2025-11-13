"""Statistics stack (Phase 1 & 2 metrics)."""

from __future__ import annotations


def compute_metrics(gray: tuple, masks: dict[str, tuple], env: str) -> dict[str, float]:
    """Compute Phase 1/2 metrics for a single realization."""
    raise NotImplementedError("Metrics implementation arrives with STAT milestone.")
