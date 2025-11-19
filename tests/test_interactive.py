import ipywidgets as ipw
import numpy as np
import pytest

from analog_image_generator import interactive


def test_build_sliders_returns_expected_groups():
    library = interactive.build_sliders("fluvial")
    assert {"general", "meandering", "braided", "anastomosing", "stacked"}.issubset(library.keys())
    meander = library["meandering"]["sliders"]["n_control_points"]
    assert meander["min"] < meander["max"]
    assert meander["default"] == 6


def test_build_interactive_ui_constructs_panel():
    panel = interactive.build_interactive_ui("fluvial")
    assert isinstance(panel.layout, ipw.Widget)
    assert "seed" in panel.widgets
    assert panel.widgets["style"].value == "meandering"


def test_preview_sequence_returns_layout():
    params = {"style": "meandering", "height": 128, "width": 128}
    result = interactive.preview_sequence("fluvial", params, seeds=[3, 4])
    assert isinstance(result.layout, ipw.Widget)
    assert len(result.frames) == 2
    assert set(result.frames[0]["metrics"].keys()) == {"beta_iso", "fractal_dimension", "entropy_global"}


def test_run_param_batch(tmp_path):
    sliders = interactive.build_sliders("fluvial")
    sliders["general"]["sliders"]["height"]["default"] = 128
    sliders["general"]["sliders"]["width"]["default"] = 128
    saved = interactive.run_param_batch("fluvial", sliders, seeds=[7], output_dir=tmp_path)
    assert len(saved) == 1
    record = saved[0]
    assert record["analog"].exists()
    assert record["color"].exists()
