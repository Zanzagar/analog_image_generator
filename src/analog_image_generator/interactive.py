"""Notebook-friendly interactive controls and preview orchestration (UX anchors)."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Mapping, Sequence, TypedDict

import ipywidgets as ipw
import numpy as np

from . import geologic_generators, stats, utils

EnvKey = Literal["fluvial"]
SliderType = Literal["float", "int"]


class SliderConfig(TypedDict):
    """Typed dictionary describing a single slider control."""

    key: str
    label: str
    min: float
    max: float
    step: float
    default: float
    units: str
    source: str
    citation_ids: list[str]
    dtype: SliderType
    description: str


class SliderGroup(TypedDict):
    """Grouping metadata so sliders can be rendered in logical sections."""

    label: str
    sliders: dict[str, SliderConfig]


@dataclass
class InteractivePanel:
    """Return type for :func:`build_interactive_ui`."""

    env: EnvKey
    slider_groups: dict[str, SliderGroup]
    widgets: dict[str, ipw.Widget]
    layout: ipw.VBox
    slider_box: ipw.VBox
    preview_button: ipw.Button


class PreviewFrame(TypedDict):
    """Metadata captured for each preview seed."""

    seed: int
    params: dict[str, float]
    metrics: dict[str, float]


@dataclass
class PreviewResult:
    """Return container for :func:`preview_sequence`."""

    layout: ipw.VBox
    frames: list[PreviewFrame]


_FLUVIAL_SLIDER_LIBRARY: "OrderedDict[str, SliderGroup]" = OrderedDict(
    [
        (
            "general",
            {
                "label": "General (fluvial)",
                "sliders": OrderedDict(
                    [
                        (
                            "height",
                            {
                                "key": "height",
                                "label": "Height (px)",
                                "min": 128,
                                "max": 768,
                                "step": 32,
                                "default": 384,
                                "units": "px",
                                "source": "PRD fluvial layout defaults",
                                "citation_ids": ["prd-fluvial-table1"],
                                "dtype": "int",
                                "description": "Grid height. Lower for faster previews.",
                            },
                        ),
                        (
                            "width",
                            {
                                "key": "width",
                                "label": "Width (px)",
                                "min": 128,
                                "max": 768,
                                "step": 32,
                                "default": 384,
                                "units": "px",
                                "source": "PRD fluvial layout defaults",
                                "citation_ids": ["prd-fluvial-table1"],
                                "dtype": "int",
                                "description": "Grid width. Matches height when square belts are desired.",
                            },
                        ),
                        (
                            "floodplain_noise",
                            {
                                "key": "floodplain_noise",
                                "label": "Floodplain noise",
                                "min": 0.02,
                                "max": 0.25,
                                "step": 0.01,
                                "default": 0.08,
                                "units": "σ",
                                "source": "Nicholas & Fisher 2023 table 2",
                                "citation_ids": ["research-fluvial-noise"],
                                "dtype": "float",
                                "description": "Gaussian noise amplitude for background floodplain texture.",
                            },
                        ),
                    ]
                ),
            },
        ),
        (
            "meandering",
            {
                "label": "Meandering controls",
                "sliders": OrderedDict(
                    [
                        (
                            "n_control_points",
                            {
                                "key": "n_control_points",
                                "label": "Centerline control points",
                                "min": 3,
                                "max": 12,
                                "step": 1,
                                "default": 6,
                                "units": "count",
                                "source": "AGENTS.md fluvial mandates",
                                "citation_ids": ["prd-fluvial-table1"],
                                "dtype": "int",
                                "description": "Number of centerline control points used when solving the spline.",
                            },
                        ),
                        (
                            "amplitude_min",
                            {
                                "key": "amplitude_min",
                                "label": "Amplitude min (fraction of width)",
                                "min": 0.05,
                                "max": 0.2,
                                "step": 0.01,
                                "default": 0.08,
                                "units": "W",
                                "source": "Leopold & Wolman sinuosity bounds",
                                "citation_ids": ["research-meander-amp"],
                                "dtype": "float",
                                "description": "Lower bound for the random amplitude range controlling belt wiggle.",
                            },
                        ),
                        (
                            "amplitude_max",
                            {
                                "key": "amplitude_max",
                                "label": "Amplitude max (fraction of width)",
                                "min": 0.15,
                                "max": 0.35,
                                "step": 0.01,
                                "default": 0.22,
                                "units": "W",
                                "source": "Leopold & Wolman sinuosity bounds",
                                "citation_ids": ["research-meander-amp"],
                                "dtype": "float",
                                "description": "Upper bound for the amplitude range.",
                            },
                        ),
                        (
                            "channel_width_min",
                            {
                                "key": "channel_width_min",
                                "label": "Channel width min (px)",
                                "min": 12,
                                "max": 48,
                                "step": 2,
                                "default": 26,
                                "units": "px",
                                "source": "Bridge 2003 fluvial width summary",
                                "citation_ids": ["research-meander-width"],
                                "dtype": "int",
                                "description": "Lower bound for bankfull width along the belt.",
                            },
                        ),
                        (
                            "channel_width_max",
                            {
                                "key": "channel_width_max",
                                "label": "Channel width max (px)",
                                "min": 24,
                                "max": 72,
                                "step": 2,
                                "default": 46,
                                "units": "px",
                                "source": "Bridge 2003 fluvial width summary",
                                "citation_ids": ["research-meander-width"],
                                "dtype": "int",
                                "description": "Upper bound for the variable bankfull width curve.",
                            },
                        ),
                        (
                            "drift_fraction",
                            {
                                "key": "drift_fraction",
                                "label": "Centerline drift fraction",
                                "min": 0.02,
                                "max": 0.25,
                                "step": 0.01,
                                "default": 0.08,
                                "units": "fraction",
                                "source": "Task Master PRD table (fluvial)",
                                "citation_ids": ["prd-fluvial-table1"],
                                "dtype": "float",
                                "description": "Controls the amount of random walk applied to the spline.",
                            },
                        ),
                    ]
                ),
            },
        ),
        (
            "braided",
            {
                "label": "Braided controls",
                "sliders": OrderedDict(
                    [
                        (
                            "thread_count",
                            {
                                "key": "thread_count",
                                "label": "Thread count",
                                "min": 2,
                                "max": 10,
                                "step": 1,
                                "default": 5,
                                "units": "count",
                                "source": "Brice 1964 multi-thread observations",
                                "citation_ids": ["research-braided-thread"],
                                "dtype": "int",
                                "description": "Number of active threads in the braid plain.",
                            },
                        ),
                        (
                            "mean_thread_width",
                            {
                                "key": "mean_thread_width",
                                "label": "Mean thread width (px)",
                                "min": 10,
                                "max": 40,
                                "step": 2,
                                "default": 18,
                                "units": "px",
                                "source": "Brice 1964 multi-thread observations",
                                "citation_ids": ["research-braided-thread"],
                                "dtype": "int",
                                "description": "Nominal width for each braided thread.",
                            },
                        ),
                        (
                            "bar_spacing_factor",
                            {
                                "key": "bar_spacing_factor",
                                "label": "Bar spacing factor",
                                "min": 2.0,
                                "max": 6.0,
                                "step": 0.2,
                                "default": 4.2,
                                "units": "×width",
                                "source": "Church & Jones 1982 bar spacing ratio",
                                "citation_ids": ["research-braided-bar"],
                                "dtype": "float",
                                "description": "Spacing multiplier between compound bars.",
                            },
                        ),
                    ]
                ),
            },
        ),
        (
            "anastomosing",
            {
                "label": "Anastomosing controls",
                "sliders": OrderedDict(
                    [
                        (
                            "branch_count",
                            {
                                "key": "branch_count",
                                "label": "Branch count",
                                "min": 2,
                                "max": 6,
                                "step": 1,
                                "default": 3,
                                "units": "count",
                                "source": "Makaske 2001 marsh-dominated belts",
                                "citation_ids": ["research-anasto-branch"],
                                "dtype": "int",
                                "description": "Number of active anabranches.",
                            },
                        ),
                        (
                            "levee_width_px",
                            {
                                "key": "levee_width_px",
                                "label": "Levee width (px)",
                                "min": 3,
                                "max": 12,
                                "step": 1,
                                "default": 6,
                                "units": "px",
                                "source": "Makaske 2001 marsh-dominated belts",
                                "citation_ids": ["research-anasto-levee"],
                                "dtype": "int",
                                "description": "Morphologic levee width for narrow channels.",
                            },
                        ),
                        (
                            "marsh_fraction",
                            {
                                "key": "marsh_fraction",
                                "label": "Marsh fraction",
                                "min": 0.1,
                                "max": 0.75,
                                "step": 0.05,
                                "default": 0.45,
                                "units": "fraction",
                                "source": "Makaske 2001 marsh-dominated belts",
                                "citation_ids": ["research-anasto-marsh"],
                                "dtype": "float",
                                "description": "Fraction of floodplain treated as wetland marsh.",
                            },
                        ),
                    ]
                ),
            },
        ),
        (
            "stacked",
            {
                "label": "Stacked package controls",
                "sliders": OrderedDict(
                    [
                        (
                            "package_count",
                            {
                                "key": "package_count",
                                "label": "Package count",
                                "min": 1,
                                "max": 5,
                                "step": 1,
                                "default": 2,
                                "units": "count",
                                "source": "AGENTS stacked channel mandate",
                                "citation_ids": ["agents-stacked"],
                                "dtype": "int",
                                "description": "Number of vertically stacked packages to assemble.",
                            },
                        ),
                        (
                            "package_relief_px",
                            {
                                "key": "package_relief_px",
                                "label": "Relief per package (px)",
                                "min": 4,
                                "max": 64,
                                "step": 2,
                                "default": 18,
                                "units": "px",
                                "source": "AGENTS stacked channel mandate",
                                "citation_ids": ["agents-stacked"],
                                "dtype": "int",
                                "description": "Erosional relief applied when stacking belts.",
                            },
                        ),
                        (
                            "package_erosion_depth_px",
                            {
                                "key": "package_erosion_depth_px",
                                "label": "Erosion depth (px)",
                                "min": 2,
                                "max": 48,
                                "step": 2,
                                "default": 12,
                                "units": "px",
                                "source": "AGENTS stacked channel mandate",
                                "citation_ids": ["agents-stacked"],
                                "dtype": "int",
                                "description": "Depth removed from the previous package before depositing the next.",
                            },
                        ),
                    ]
                ),
            },
        ),
    ]
)

_FACIES_TO_MASK = {
    "channel": "channel",
    "pointbar": "scroll_bar",
    "levee": "levee",
    "floodplain": "floodplain",
    "oxbow": "oxbow",
    "thread": "channel",
    "bar": "bar",
    "chute": "chute",
    "marsh": "marsh",
}

_PACKAGE_STYLE_OPTIONS = ("meandering", "braided", "anastomosing")


def build_sliders(env: str) -> dict[str, SliderGroup]:
    """Return slider definitions for *env* (task anchor: UX sliders)."""

    env_key = env.strip().lower()
    if env_key != "fluvial":
        raise NotImplementedError("Interactive sliders currently available for fluvial env only.")
    # Defensive copy so notebooks/tests can tweak defaults without mutating module state.
    import copy

    return copy.deepcopy(_FLUVIAL_SLIDER_LIBRARY)


def build_interactive_ui(env: str) -> InteractivePanel:
    """Create an ipywidgets-based control panel for *env*."""

    slider_groups = build_sliders(env)
    slider_widgets: dict[str, ipw.Widget] = {}
    slider_children: list[ipw.Widget] = []

    for group in slider_groups.values():
        slider_children.append(ipw.HTML(f"<h4>{group['label']}</h4>"))
        for config in group["sliders"].values():
            widget = _slider_widget(config)
            slider_widgets[config["key"]] = widget
            slider_children.append(widget)

    slider_box = ipw.VBox(slider_children)
    slider_box.layout.width = "420px"
    slider_box.layout.overflow_y = "auto"
    slider_box.layout.max_height = "620px"

    style_dropdown = ipw.Dropdown(
        options=[("Meandering", "meandering"), ("Braided", "braided"), ("Anastomosing", "anastomosing")],
        value="meandering",
        description="Style",
    )
    seed_input = ipw.IntText(value=42, description="Seed")
    mode_toggle = ipw.ToggleButtons(
        options=[("Single belt", "single"), ("Stacked", "stacked")],
        value="single",
        description="Mode",
        button_style="",
    )
    package_mix = ipw.SelectMultiple(
        options=[opt.title() for opt in _PACKAGE_STYLE_OPTIONS],
        value=("Meandering", "Braided"),
        description="Package mix",
    )
    preview_button = ipw.Button(description="Preview", button_style="primary", icon="eye")
    status_html = ipw.HTML("<em>Adjust sliders, then press Preview.</em>")

    extra_box = ipw.VBox(
        [
            style_dropdown,
            seed_input,
            mode_toggle,
            package_mix,
            preview_button,
            status_html,
        ],
        layout=ipw.Layout(width="320px"),
    )

    widgets = {
        **slider_widgets,
        "style": style_dropdown,
        "seed": seed_input,
        "mode": mode_toggle,
        "package_mix": package_mix,
        "status": status_html,
    }
    layout = ipw.HBox([slider_box, extra_box], layout=ipw.Layout(width="100%"))
    return InteractivePanel(
        env="fluvial",
        slider_groups=slider_groups,
        widgets=widgets,
        layout=ipw.VBox([layout]),
        slider_box=slider_box,
        preview_button=preview_button,
    )


def preview_sequence(env: str, params: Mapping[str, float] | None, seeds: Iterable[int]) -> PreviewResult:
    """Return a widget layout that stacks preview frames for each seed."""

    env_key = env.strip().lower()
    generator = _resolve_generator(env_key)
    params = dict(params or {})
    seeds = list(seeds)
    frames: list[PreviewFrame] = []
    rows: list[ipw.Widget] = []
    height = int(params.get("height", 256))
    width = int(params.get("width", 256))

    for seed in seeds:
        merged_params = dict(params)
        merged_params.setdefault("style", "meandering")
        merged_params["seed"] = int(seed)
        analog, masks = generator(merged_params)
        color = _colorize_masks(env_key, masks, analog.shape)
        channel = masks.get("channel")
        if channel is None:
            channel = masks.get("branch_channel")
        if channel is None:
            channel = np.zeros_like(analog)
        preview = stats.preview_metrics(analog, masks, env_key)
        metrics = {key: round(float(val), 4) for key, val in preview.items()}
        frames.append({"seed": int(seed), "params": merged_params, "metrics": metrics})
        row = _make_preview_row(analog, color, channel, metrics, height=height, width=width)
        rows.append(row)

    return PreviewResult(layout=ipw.VBox(rows, layout=ipw.Layout(width="100%")), frames=frames)


def run_param_batch(
    env: str,
    slider_configs: Mapping[str, SliderGroup | SliderConfig | float],
    seeds: Sequence[int],
    output_dir: str | Path,
    *,
    style: str = "meandering",
    mode: str = "single",
    extra_params: Mapping[str, float] | None = None,
) -> list[dict]:
    """Render a batch of realizations for the supplied seeds and write PNGs."""

    env_key = env.strip().lower()
    if not seeds:
        return []
    generator = _resolve_generator(env_key)
    defaults = _extract_slider_defaults(slider_configs)
    saved: list[dict] = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for seed in seeds:
        params = dict(defaults)
        params.update(extra_params or {})
        params["seed"] = int(seed)
        params["style"] = style
        params["mode"] = mode
        analog, masks = generator(params)
        color = _colorize_masks(env_key, masks, analog.shape)
        slug = f"{env_key}-{style}-{seed:03d}"
        analog_path = output_path / f"{slug}-gray.png"
        color_path = output_path / f"{slug}-color.png"
        _save_png(analog, analog_path, cmap="gray")
        _save_png(color, color_path, cmap=None)
        saved.append({"seed": int(seed), "analog": analog_path, "color": color_path})
    return saved


def _slider_widget(config: SliderConfig) -> ipw.Widget:
    common = {
        "description": config["label"],
        "min": config["min"],
        "max": config["max"],
        "step": config["step"],
        "value": config["default"],
        "continuous_update": False,
        "readout_format": ".2f" if config["dtype"] == "float" else "d",
        "tooltip": f"{config['description']} — {config['source']}",
    }
    if config["dtype"] == "int":
        return ipw.IntSlider(**common)
    return ipw.FloatSlider(**common)


def _resolve_generator(env: str):
    if env == "fluvial":
        return geologic_generators.generate_fluvial
    raise NotImplementedError(f"Interactive workflow not implemented for env={env!r}")


def _extract_slider_defaults(
    slider_configs: Mapping[str, SliderGroup | SliderConfig | float],
) -> dict[str, float]:
    defaults: dict[str, float] = {}
    for key, value in slider_configs.items():
        if isinstance(value, dict) and "sliders" in value:
            for inner_key, config in value["sliders"].items():
                defaults[inner_key] = float(config["default"])
        elif isinstance(value, dict) and "default" in value:
            defaults[value.get("key", key)] = float(value["default"])
        else:
            defaults[key] = float(value)
    return defaults


def _colorize_masks(env: str, masks: Mapping[str, np.ndarray], shape: tuple[int, int]):
    palette = utils.palette_for_env("fluvial")
    channel_masks: dict[str, np.ndarray] = {}
    for entry in palette:
        facies = entry["facies"]
        mask_key = _FACIES_TO_MASK.get(facies, facies)
        mask = masks.get(mask_key)
        if mask is None:
            continue
        channel_masks[facies] = mask.astype(np.float32)
    if not channel_masks:
        channel_masks["channel"] = np.zeros(shape, dtype=np.float32)
    return utils.boolean_stack_to_rgb(channel_masks, palette)


def _make_preview_row(
    analog: np.ndarray,
    color: np.ndarray,
    channel_mask: np.ndarray,
    metrics: Mapping[str, float],
    *,
    height: int,
    width: int,
) -> ipw.Widget:
    analog_img = _array_to_image_widget(analog, cmap="gray", width=width, height=height)
    color_img = _array_to_image_widget(color, cmap=None, width=width, height=height)
    channel_img = _array_to_image_widget(channel_mask, cmap="gray", width=width, height=height)
    metrics_html = ipw.HTML(
        "<br>".join(
            f"<b>{name}</b>: {value:.4f}"
            for name, value in metrics.items()
        )
    )
    return ipw.HBox([analog_img, color_img, channel_img, metrics_html])


def _array_to_image_widget(
    array: np.ndarray,
    *,
    cmap: str | None,
    width: int,
    height: int,
) -> ipw.Image:
    png_bytes = _array_to_png_bytes(array, cmap=cmap)
    return ipw.Image(value=png_bytes, format="png", width=width // 2, height=height // 2)


def _array_to_png_bytes(array: np.ndarray, *, cmap: str | None) -> bytes:
    import io
    from matplotlib import pyplot as plt

    buf = io.BytesIO()
    clipped = np.clip(array, 0.0, 1.0)
    plt.imsave(buf, clipped, cmap=cmap, vmin=0.0, vmax=1.0)
    buf.seek(0)
    return buf.read()


def _save_png(array: np.ndarray, path: Path, *, cmap: str | None) -> None:
    from matplotlib import pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(array, 0.0, 1.0)
    if cmap:
        plt.imsave(path, clipped, cmap=cmap, vmin=0.0, vmax=1.0)
    else:
        plt.imsave(path, clipped, vmin=0.0, vmax=1.0)
