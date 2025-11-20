# Fluvial Demo Notebook Inventory & Anchor Plan

Purpose: enumerate every fluvial-focused notebook and record the sections that must exist for tomorrow's professor-facing demo. Each section references the fully qualified code anchors listed in `docs/GEOLOGIC_RULES.md`. Current status reflects what is in the repo **today** (post-nbconvert execution); most notebooks only contain the anchor/checklist cells, so the required sections are still pending.

| Notebook | Target Sections (Anchors / Code References) | Current Status |
| --- | --- | --- |
| `notebooks/fluvial_meandering.ipynb` | 1) Intro markdown referencing `analog_image_generator.geologic_generators.generate_meandering` (`anchor-fluvial-meandering-overview`)<br>2) Parameter presets cell (`_MEANDER_DEFAULTS`, `_STACKED` overrides)<br>3) Single-belt run cell calling `geologic_generators.generate_fluvial({'style': 'meandering', ...})`<br>4) Stacked run cell calling `stacked_channels.build_stacked_fluvial`<br>5) Visualization cell (gray, masks, palette legend)<br>6) Metrics cell (`stats.compute_metrics` summary)<br>7) Reporting hook (link to `outputs/smoke_report`, snippet of CSV/PDF metadata)<br>8) Debug seed/package controls + checklist | **Missing** (only anchor/checklist cells present) |
| `notebooks/fluvial_braided.ipynb` | Same sections as above, but referencing braided defaults (`generate_braided`, braided anchors) and multi-thread presets | **Missing** |
| `notebooks/fluvial_anastomosing.ipynb` | Same sections referencing `generate_anastomosing`, marsh/fan presets | **Missing** |
| `notebooks/fluvial_sanity.ipynb` | Quick visual QA notebook showing side-by-side comparisons for all three styles + stacked boundary masks; include parameter table + seed override | **Exists** but lacks structured intro/checklist (needs refresh) |
| `notebooks/fluvial_stats.ipynb` | 1) Intro referencing `stats.compute_metrics` anchors<br>2) Cells running `stats.compute_metrics` on single + stacked realizations<br>3) PSD anisotropy visualization<br>4) QA flag discussion / table<br>5) Checklist | **Intro/checklist only; rest missing** |
| `notebooks/reporting.ipynb` | 1) Intro referencing `reporting.build_reports` anchors<br>2) Sample `metrics_rows` construction<br>3) Run `reporting.build_reports` (save to tmp folder)<br>4) Display resulting CSV/PDF thumbnails & metadata<br>5) Checklist | **Intro/checklist only** |
| `notebooks/v20a_interactive_rebuild.ipynb` | 1) Intro referencing `interactive.build_interactive_ui` and slider schema anchors<br>2) Cell displaying the control panel<br>3) Preview sequence demo (multiple seeds)<br>4) Batch export example<br>5) Debug notes (how to override slider configs)<br>6) Checklist | **Anchor/checklist only** |
| `notebooks/fluvial_stacked.ipynb` (new) | 1) Intro referencing `stacked_channels.sequence_packages` / `build_stacked_fluvial` anchors<br>2) Package spec presets (mix of styles)<br>3) Visualization of package_id map + boundary masks<br>4) Metadata/QA table<br>5) Checklist | **Not yet created** |

## Action Items from Inventory
1. Create the missing sections listed above, using the standard pattern (`### <Env> demo` headers, anchor references, and ✅/⬜ checklist cell).
2. Add/refresh GEOLOGIC_RULES entries for the new notebook anchors (`anchor-meandering-overview`, `anchor-braided-overview`, etc.).
3. After each notebook is updated, run:
   ```bash
   python scripts/validate_geo_anchors.py
   jupyter nbconvert --to notebook --inplace --execute <notebook>
   ```
   to keep anchors synchronized and capture outputs.
