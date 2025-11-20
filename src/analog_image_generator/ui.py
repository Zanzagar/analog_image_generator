"""UI helpers to keep notebooks lean (interactive panel wiring)."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import ipywidgets as widgets
import pandas as pd
import numpy as np
from IPython.display import Markdown, display

from . import interactive


def _make_slider_widget(
    cfg: Mapping[str, object], *, description_width: str, slider_width: str
) -> tuple[widgets.Widget, widgets.Widget]:
    """Return (slider, row_with_info_icon)."""

    common = dict(
        description=cfg["label"],
        min=cfg["min"],
        max=cfg["max"],
        step=cfg["step"],
        value=cfg["default"],
        continuous_update=False,
        style={"description_width": description_width},
        layout=widgets.Layout(width=slider_width),
    )
    slider = widgets.IntSlider(**common) if cfg["dtype"] == "int" else widgets.FloatSlider(**common)
    slider.tooltip = cfg.get("description", "")  # hover text

    info_text = cfg.get("description", "")
    info_icon = widgets.HTML(
        value=(
            f'<span title="{info_text or "No description"}" '
            'style="font-size:13px; color:#555; cursor:help; white-space:nowrap;">&#9432;</span>'
        ),
        layout=widgets.Layout(width="22px", align_self="center", justify_content="center", padding="0 4px"),
    )
    row = widgets.HBox(
        [slider, info_icon],
        layout=widgets.Layout(align_items="center", width="100%"),
    )
    return slider, row


def build_live_fluvial_panel(
    *,
    slider_width: str = "320px",
    description_width: str = "160px",
    panel_width: str = "520px",
    auto_run: bool = False,
) -> dict[str, widgets.Widget]:
    """
    Build a style-aware fluvial interactive panel with optional auto-run previews.

    Returns useful widgets in a dict: ui, run_button, status, output_area, batch_output, etc.
    """

    slider_groups = interactive.build_sliders("fluvial")
    slider_widgets: dict[str, widgets.Widget] = {}
    group_boxes: dict[str, widgets.Widget] = {}
    group_order: list[str] = []

    for group_key, meta in slider_groups.items():
        header = widgets.HTML(f"<h4>{meta['label']}</h4>")
        children: list[widgets.Widget] = [header]
        for cfg in meta["sliders"].values():
            slider, row = _make_slider_widget(
                cfg, description_width=description_width, slider_width=slider_width
            )
            slider_widgets[cfg["key"]] = slider
            children.append(row)
        box = widgets.VBox(children)
        group_boxes[group_key] = box
        group_order.append(group_key)

    slider_box = widgets.VBox(
        [group_boxes[g] for g in group_order],
        layout=widgets.Layout(width=panel_width),
    )

    style_dropdown = widgets.Dropdown(
        options=[("Meandering", "meandering"), ("Braided", "braided"), ("Anastomosing", "anastomosing")],
        value="meandering",
        description="Style",
    )
    mode_toggle = widgets.ToggleButtons(
        options=[("Single", "single"), ("Stacked", "stacked")],
        value="single",
        description="Mode",
    )
    package_mix = widgets.SelectMultiple(
        options=["Meandering", "Braided", "Anastomosing"],
        value=("Meandering", "Braided"),
        description="Pkg mix",
        layout=widgets.Layout(display="none"),
    )
    seed_box = widgets.IntText(value=42, description="Seed")
    auto_run_toggle = widgets.Checkbox(value=auto_run, description="Auto-run on change")
    status = widgets.HTML("<em>Idle</em>")
    run_button = widgets.Button(description="Run preview", button_style="primary", icon="eye")
    output_area = widgets.Output()

    # Batch summary helpers
    batch_start_seed = widgets.IntText(value=42, description="Start seed")
    batch_count = widgets.IntText(value=3, description="Image count")
    batch_button = widgets.Button(description="Run batch summary", button_style="info", icon="table")
    batch_output = widgets.Output()
    batch_grid_output = widgets.Output()
    batch_grid_mode = widgets.Dropdown(
        options=[("Facies composite", "color"), ("Grayscale", "gray"), ("Channel mask", "channel")],
        value="color",
        description="Grid view",
    )
    batch_images_cache: dict[str, list[np.ndarray]] = {}
    batch_labels: list[str] = []

    style_groups_map = {
        "meandering": ["general", "meandering", "facies_overlays"],
        "braided": ["general", "braided", "facies_overlays"],
        "anastomosing": ["general", "anastomosing", "facies_overlays"],
    }

    state = {"running": False, "pending": False}

    def apply_visibility(*_):
        # Hide all groups first
        for box in group_boxes.values():
            box.layout.display = "none"
        style_key = style_dropdown.value
        groups = style_groups_map.get(style_key, ["general"])
        if mode_toggle.value == "stacked":
            groups = list(groups) + ["stacked"]
            package_mix.layout.display = "flex"
        else:
            package_mix.layout.display = "none"
        for g in groups:
            if g in group_boxes:
                group_boxes[g].layout.display = "block"

    def current_params() -> dict:
        params = {k: float(w.value) for k, w in slider_widgets.items()}
        params["style"] = style_dropdown.value
        params["mode"] = mode_toggle.value
        params["seed"] = seed_box.value
        if params["mode"] == "stacked":
            params["package_styles"] = [label.lower() for label in package_mix.value]
        return params

    def render_preview(*_):
        state["running"] = True
        status.value = "<b>Running…</b>"
        try:
            params = current_params()
            preview = interactive.preview_sequence("fluvial", params, seeds=[params["seed"]])
            with output_area:
                output_area.clear_output()
                display(
                    Markdown(
                        f"**Preview** — preset `{params.get('style')}`, "
                        f"seed `{params['seed']}`, mode `{params['mode']}`"
                    )
                )
                display(preview.layout)
                frames = preview.frames or []
                if frames:
                    metrics_df = pd.DataFrame([frames[0]["metrics"]])
                    display(metrics_df)
        finally:
            state["running"] = False
            status.value = "<b>Done</b>"
            if state.get("pending"):
                state["pending"] = False
                render_preview()

    def render_batch_grid(*_):
        with batch_grid_output:
            batch_grid_output.clear_output()
            arrays = batch_images_cache.get(batch_grid_mode.value, [])
            if not arrays:
                return
            grid = _image_grid_widget(arrays, batch_labels)
            if grid is not None:
                display(grid)

    def run_batch(_=None):
        seeds = [int(batch_start_seed.value) + i for i in range(int(batch_count.value))]
        params = current_params()
        rows = []
        images_color: list[np.ndarray] = []
        images_gray: list[np.ndarray] = []
        images_channel: list[np.ndarray] = []
        labels: list[str] = []
        generator = interactive._resolve_generator("fluvial")
        for seed in seeds:
            params_seed = dict(params)
            params_seed["seed"] = seed
            preview = interactive.preview_sequence("fluvial", params_seed, seeds=[seed])
            if not preview.frames:
                continue
            rows.append({"seed": seed, **preview.frames[0]["metrics"]})
            # Collect a color thumbnail for the grid
            analog, masks = generator(params_seed)
            color = interactive._colorize_masks("fluvial", masks, analog.shape)
            channel = masks.get("channel") or masks.get("branch_channel") or np.zeros_like(analog)
            images_color.append(color)
            images_gray.append(analog)
            images_channel.append(channel)
            labels.append(f"seed {seed}")
        batch_images_cache.clear()
        batch_images_cache["color"] = images_color
        batch_images_cache["gray"] = images_gray
        batch_images_cache["channel"] = images_channel
        batch_labels[:] = labels
        with batch_output:
            batch_output.clear_output()
            if rows:
                df = pd.DataFrame(rows)
                display(Markdown(f"**Batch preview summary** ({len(rows)} runs)"))
                display(df)
                # summary stats
                display(Markdown("**Summary statistics (selected metrics)**"))
                summarize = df.describe(include="all")
                display(summarize)
                # quick histograms for beta / entropy if present
                hist = _batch_hist_widget(df)
                if hist is not None:
                    display(hist)
                grid = _image_grid_widget(batch_images_cache.get(batch_grid_mode.value, []), labels)
                if grid is not None:
                    display(Markdown("**Batch composite grid**"))
                    display(grid)
            else:
                print("No batch frames produced.")
        render_batch_grid()

    def schedule_preview(change=None):
        if not auto_run_toggle.value:
            return
        if state["running"]:
            state["pending"] = True
            return
        render_preview()

    run_button.on_click(lambda _: render_preview())
    batch_button.on_click(run_batch)
    batch_grid_mode.observe(render_batch_grid, names="value")
    mode_toggle.observe(apply_visibility, names="value")
    style_dropdown.observe(apply_visibility, names="value")
    mode_toggle.observe(schedule_preview, names="value")
    style_dropdown.observe(schedule_preview, names="value")
    seed_box.observe(schedule_preview, names="value")
    for w in slider_widgets.values():
        w.observe(schedule_preview, names="value")

    core_controls = widgets.VBox(
        [
            style_dropdown,
            mode_toggle,
            package_mix,
            seed_box,
            auto_run_toggle,
            status,
            run_button,
        ]
    )
    batch_controls = widgets.VBox(
        [
            widgets.HTML("<b>Batch preview</b>"),
            batch_start_seed,
            batch_count,
            batch_button,
            batch_grid_mode,
            batch_grid_output,
            batch_output,
        ]
    )

    ui = widgets.HBox(
        [
            slider_box,
            widgets.VBox(
                [
                    core_controls,
                    output_area,
                    batch_controls,
                ],
                layout=widgets.Layout(width="100%"),
            ),
        ],
        layout=widgets.Layout(width="100%"),
    )
    status.value = "<em>Ready — click Run preview or enable Auto-run.</em>"
    apply_visibility()

    return {
        "ui": ui,
        "run_button": run_button,
        "status": status,
        "output_area": output_area,
        "batch_output": batch_output,
        "batch_button": batch_button,
        "auto_run": auto_run_toggle,
        "slider_widgets": slider_widgets,
    }


def _batch_hist_widget(df: pd.DataFrame):
    """Render histograms for key metrics in batch summary."""

    import io
    from matplotlib import pyplot as plt

    cols = [col for col in ("beta_iso", "fractal_dimension", "entropy_global") if col in df.columns]
    if not cols:
        return None
    n = len(cols)
    fig, axes = plt.subplots(1, n, figsize=(3 * n, 2.6), dpi=120)
    if n == 1:
        axes = [axes]
    for ax, col in zip(axes, cols):
        ax.hist(df[col].dropna(), bins=8, color="#99c2ff", edgecolor="#3b4c6b")
        ax.set_title(col, fontsize=9)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return widgets.Image(value=buf.read(), format="png", width=200 * n, height=180)


def _image_grid_widget(images: list[np.ndarray], labels: list[str]) -> widgets.Image | None:
    """Render a grid of color composites from batch runs."""

    if not images:
        return None
    import io
    from math import ceil, sqrt
    from matplotlib import pyplot as plt

    n = len(images)
    cols = int(ceil(sqrt(n)))
    rows = int(ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows), dpi=100)
    axes = np.array(axes).reshape(rows, cols)
    for idx, ax in enumerate(axes.flat):
        ax.axis("off")
        if idx >= n:
            continue
        ax.imshow(np.clip(images[idx], 0.0, 1.0))
        ax.set_title(labels[idx], fontsize=9)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return widgets.Image(value=buf.read(), format="png")
