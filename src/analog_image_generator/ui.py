"""UI helpers to keep notebooks lean (interactive panel wiring)."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import ipywidgets as widgets
import pandas as pd
from IPython.display import Markdown, display

from . import interactive


def _make_slider_widget(cfg: Mapping[str, object], *, description_width: str, slider_width: str) -> widgets.Widget:
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
    if cfg["dtype"] == "int":
        return widgets.IntSlider(**common)
    return widgets.FloatSlider(**common)


def build_live_fluvial_panel(
    *,
    slider_width: str = "320px",
    description_width: str = "160px",
    panel_width: str = "460px",
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
            w = _make_slider_widget(cfg, description_width=description_width, slider_width=slider_width)
            slider_widgets[cfg["key"]] = w
            children.append(w)
        box = widgets.VBox(children)
        group_boxes[group_key] = box
        group_order.append(group_key)

    slider_box = widgets.VBox(
        [group_boxes[g] for g in group_order],
        layout=widgets.Layout(max_height="520px", overflow_y="auto", width=panel_width),
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
    )
    seed_box = widgets.IntText(value=42, description="Seed")
    auto_run_toggle = widgets.Checkbox(value=auto_run, description="Auto-run on change")
    status = widgets.HTML("<em>Idle</em>")
    run_button = widgets.Button(description="Run preview", button_style="primary", icon="eye")
    output_area = widgets.Output()

    # Batch summary helpers
    batch_seeds = widgets.Text(value="42,43,44", description="Seeds CSV")
    batch_button = widgets.Button(description="Run batch summary", button_style="info")
    batch_output = widgets.Output()

    style_groups_map = {
        "meandering": ["general", "meandering"],
        "braided": ["general", "braided"],
        "anastomosing": ["general", "anastomosing"],
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

    def run_batch(_=None):
        seeds = []
        for part in batch_seeds.value.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                seeds.append(int(part))
            except ValueError:
                continue
        if not seeds:
            with batch_output:
                batch_output.clear_output()
                print("No valid seeds.")
            return
        params = current_params()
        rows = []
        for seed in seeds:
            params_seed = dict(params)
            params_seed["seed"] = seed
            preview = interactive.preview_sequence("fluvial", params_seed, seeds=[seed])
            if not preview.frames:
                continue
            rows.append({"seed": seed, **preview.frames[0]["metrics"]})
        with batch_output:
            batch_output.clear_output()
            if rows:
                df = pd.DataFrame(rows)
                display(Markdown("**Batch preview summary**"))
                display(df)
            else:
                print("No batch frames produced.")

    def schedule_preview(change=None):
        if not auto_run_toggle.value:
            return
        if state["running"]:
            state["pending"] = True
            return
        render_preview()

    run_button.on_click(lambda _: render_preview())
    batch_button.on_click(run_batch)
    mode_toggle.observe(apply_visibility, names="value")
    style_dropdown.observe(apply_visibility, names="value")
    mode_toggle.observe(schedule_preview, names="value")
    style_dropdown.observe(schedule_preview, names="value")
    seed_box.observe(schedule_preview, names="value")
    for w in slider_widgets.values():
        w.observe(schedule_preview, names="value")

    controls = widgets.VBox(
        [
            style_dropdown,
            mode_toggle,
            package_mix,
            seed_box,
            auto_run_toggle,
            status,
            run_button,
            batch_seeds,
            batch_button,
            batch_output,
        ]
    )

    ui = widgets.HBox(
        [slider_box, widgets.VBox([controls, output_area], layout=widgets.Layout(width="100%"))],
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
