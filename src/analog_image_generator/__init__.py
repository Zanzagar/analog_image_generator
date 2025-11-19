"""Public package interface for analog_image_generator."""

from importlib import metadata

from . import preview

__all__ = ["__version__", "preview"]


try:
    __version__ = metadata.version("analog-image-generator")
except metadata.PackageNotFoundError:  # pragma: no cover - during local dev
    __version__ = "0.0.0"
