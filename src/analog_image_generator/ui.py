"""UI helpers to keep notebooks lean (interactive panel wiring)."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import ipywidgets as widgets
import pandas as pd
from IPython.display import Markdown, display

from . import interactive


def build_live_fluvial_panel(
    *,
    slider_width: str = "320px",
    description_width: str = "160px",
    panel_width: str = "460px",
    debounce_ms: int = 250,
    auto_run: bool = False,
) -> dict[str, widgets.Widget]:
    """
    Build a fluvial interactive panel with optional auto-run previews.

    Returns a dict containing:
    - ui: the composed widget layout
    - run_button / status / output_area: useful for further customization
    """

    slider_groups = interactive.build_sliders("fluvial")
    slider_widgets: dict[str, widgets.Widget] = {}
    slider_children: list[widgets.Widget] = []

    for group in slider_groups.values():
        slider_children.append(widgets.HTML(f"<h4>{group['label']}</h4>"))
        for cfg in group["sliders"].values():
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
            w: widgets.Widget
            if cfg["dtype"] == "int":
                w = widgets.IntSlider(**common)
            else:
                w = widgets.FloatSlider(**common)
            slider_widgets[cfg["key"]] = w
            slider_children.append(w)

    slider_box = widgets.VBox(
        slider_children,
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

    state = {"running": False, "pending": False}

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

    def schedule_preview(_change=None):
        if not auto_run_toggle.value:
            return
        if state["running"]:
            state["pending"] = True
            return
        render_preview()

    run_button.on_click(lambda _: render_preview())
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
        ]
    )

    ui = widgets.HBox(
        [slider_box, widgets.VBox([controls, output_area], layout=widgets.Layout(width="100%"))],
        layout=widgets.Layout(width="100%"),
    )
    status.value = "<em>Ready — click Run preview or enable Auto-run.</em>"

    return {
        "ui": ui,
        "run_button": run_button,
        "status": status,
        "output_area": output_area,
        "auto_run": auto_run_toggle,
        "slider_widgets": slider_widgets,
    }
