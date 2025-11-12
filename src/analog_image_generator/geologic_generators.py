"""Core geologic generators.

These functions intentionally act as placeholders until Task Master subtasks
drive concrete implementations. They provide stable import paths for notebooks
and upcoming modules.
"""

from __future__ import annotations

from typing import Dict, Tuple

Array = Tuple  # TODO: replace with numpy.typing.NDArray when implemented


def generate_fluvial(params: Dict) -> Tuple[Array, Dict[str, Array]]:
    """Return grayscale analog and masks for fluvial environments."""
    raise NotImplementedError("Implemented during fluvial-v1 milestone.")


def generate_aeolian(params: Dict) -> Tuple[Array, Dict[str, Array]]:
    """Return grayscale analog and masks for aeolian environments."""
    raise NotImplementedError("Implemented during aeolian-v1 milestone.")


def generate_estuarine(params: Dict) -> Tuple[Array, Dict[str, Array]]:
    """Return grayscale analog and masks for estuarine environments."""
    raise NotImplementedError("Implemented during estuarine-v1 milestone.")
