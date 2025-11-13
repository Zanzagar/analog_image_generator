"""Interactive widgets and preview orchestration."""

from __future__ import annotations

from collections.abc import Iterable


def build_sliders(env: str) -> dict[str, dict[str, float]]:
    """Return slider metadata for the requested environment.

    Each slider definition includes at least min, max, step, and default.
    """
    raise NotImplementedError("Interactive controls land with v20a implementation.")


def preview_sequence(env: str, params: dict[str, float], seeds: Iterable[int]) -> None:
    """Render sequential previews for the Codex/Cursor demo notebooks."""
    raise NotImplementedError("Preview pipeline will be implemented per Task Master subtasks.")
