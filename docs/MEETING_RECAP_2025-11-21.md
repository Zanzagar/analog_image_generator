# Professor Demo – Fluvial Interactive (2025-11-21)

## Agenda / Live Script
- Open interactive demo: `notebooks/v20a_interactive_rebuild.ipynb`
  - Run the intro cells; launch panel via:
    ```python
    from analog_image_generator import ui
    panel = ui.build_live_fluvial_panel(
        slider_width="320px", description_width="160px", panel_width="520px", auto_run=False
    )
    display(panel["ui"])
    ```
  - Explain controls: style (meandering/braided/anasto), single/stacked toggle, package mix (only in stacked), seed, overlay toggle (shows facies overlays), batch controls (start seed + image count, grid view dropdown).
- Single preview:
  - Pick a style (start with meandering), mode single → click “Run preview”.
  - Show panels: grayscale analog, facies composite (style-specific legend in accordion; overlays optional via checkbox), channel mask, variogram plot with β/D fit, metrics table.
  - Switch style to braided/anasto; rerun to show style-specific masks/colors.
- Stacked preview:
  - Mode stacked, set package_count=2 (default), run preview; show package_id_map in masks, stacked appearance, metadata in preview table.
- Multi-style quick compare:
  - Run the “Multi-style single vs stacked preview” cell appended to the notebook to show all 3 styles in single + stacked for seed 42.
- Batch summary:
  - Set start seed and image count; run batch summary.
  - Show batch table, describe stats, histograms (β_iso, fractal_dimension, entropy), and grid view (dropdown: facies composite, grayscale, channel mask).
- Whiteboard notebook:
  - Open `notebooks/fluvial_rules_whiteboard.ipynb` to show rule→code mapping. Use it as a “how code implements geology” reference (sections for meander/braided/anasto/stacked/overlays/metrics, each with geologic intent + logic + improvement notes and code via `inspect.getsource`).

## What’s implemented (fluvial)
- Style-specific generators and facies: meandering (channel/pointbar/levee/floodplain/oxbow), braided (channel/bar/chute/floodplain), anastomosing (branch_channel/levee/marsh/fan/floodplain), stacked packages with relief/erosion, sedimentary overlays (channel_fill, cross_bed, ripple, fining_upward, overbank_mudstone, lateral_accretion).
- Interactive UI: style-aware sliders, stacked package controls, batch grid, overlay toggle, style-filtered legends, variogram plot for β/D, metrics table.
- Palette/legend now includes full facies set; color composites default to primary facies per style, with optional overlays via checkbox.
- QA/metrics: variogram β/H/fractal, PSD anisotropy, topology, entropy; batch stats + histograms.
- Docs: `fluvial_rules_whiteboard.ipynb` for rule↔code traceability; GEOLOGIC_RULES anchors aligned with UI/helpers.

## Known gaps / improvements
- Advanced controls not yet implemented (tasks queued under fluvial-v1):
  - Curvature-coupled width/scroll wavelength; discharge/slope-linked widths/thread counts (Task 11).
  - Bar amalgamation probability; per-facies thickness variance; crevasse-splay/clay-clast overbank enhancements (Task 12).
  - Stronger QA bands/flags and reporting hooks surfaced in UI/notebooks (Task 13).
- Legends/composites currently filter overlays by default; keep the overlay toggle on if professor wants to see textures.
- Aeolian/estuarine generators remain stubs; facies palettes and rules exist but not implemented.

## Quick commands (validation loop)
```
python -m pytest
python scripts/validate_geo_anchors.py
python scripts/smoke_test.py
```

## Feedback log
- Professor requests/notes:
  - [ ] …
  - [ ] …

## Next actions (after meeting)
- Collect feedback, map to fluvial-v1 tasks:
  - Expand palette/legend/overlays if needed.
  - Implement Tasks 11–13 subtasks (advanced controls, facies thickness/amalgamation, QA bands/reporting).
- Add similar rule↔code notebook once aeolian/estuarine are implemented.
