# Standard Workflow: Cursor → PRD/AGENTS → GitHub → Task Master in Codex

## Overview
Use Cursor to author PRDs and AGENTS.md first, set up GitHub hygiene (CI, templates, pre-commit), then switch to Codex + Task Master for task orchestration and iterative implementation.

## Phases
1) Cursor (no Task Master)
- Author PRD(s) in `.taskmaster/docs/` and `AGENTS.md`.
- Keep Sources citing `research-documents/`.
- Ensure docs/GEOLOGIC_RULES.md anchors map principles → functions.

2) GitHub hygiene
- Commit/push.
- Enable branch protection: require CI + 1 review; block direct pushes to main.
- Confirm CI green.

3) Switch to Codex + Task Master *(after professor + Codex review gate)*
- Enable MCP (WSL wrapper), set `codex-cli` main model to `gpt-5.1-codex-max`.
- Tag per PRD (e.g., `fluvial-v1`, `aeolian-v1`, `estuarine-v1`).
- Record approval (date + reviewer) in each PRD, run `task-master init --rules codex,cursor --yes` (first-time only), confirm `.taskmaster/config.json` shows `codex-cli` as main, then parse PRD → analyze complexity → expand tasks.
- If a PRD changes post-parse, pause implementation, rerun the gate, and re-parse before expanding.

  Package-first restructure (execute immediately after switching; do not do during Cursor-only phase)
  - Create `src/analog_image_generator/` package with module skeletons (`__init__.py`, `geologic_generators.py`, `interactive.py`, `stats.py`, `reporting.py`, `utils.py`).
  - Update `pyproject.toml` to PEP 621 + Hatchling (`build-system` hatchling; `[project]` metadata; runtime deps).
  - Amend CI to build and install the package before tests (`python -m build`; `pip install -e .`).
  - Ensure tests and notebooks import `analog_image_generator` (no relative-path hacks). Notebooks serve as demos only.

4) Implement
- Work by `next` task.
- Append subtask notes; keep notebook anchors and GEOLOGIC_RULES in lockstep.
- Use `scripts/render_preview.py` (paired with `notebooks/fluvial_sanity.ipynb`) for quick visual sanity checks before wiring generators into UX/stats pipelines.
- Before running `task-master next`, run `task-master list --with-subtasks --status pending` and ensure the current task and all of its subtasks show `done`; if anything remains, finish or explicitly defer it before advancing so dependencies stay accurate.

### Stacked channel controls
- Toggle stacked sequencing by setting `params["mode"] = "stacked"` on fluvial calls; `package_count == 1` maps back to the single-belt path for parity.
- Sliders feed `package_styles`, `package_thickness_px`, `package_relief_px`, and `package_erosion_depth_px`; pass lists to mix packages or scalars to broadcast.
- `stack_seed` derives deterministic sub-seeds for each package while still allowing per-package overrides in `package_param_overrides`.
- Downstream stats/reporting expect the new masks (`upper_surface_mask`, `erosion_surface_mask`, `package_id_map`) plus the metadata attached to `realization_metadata["stacked_packages"]`.

### Interactive previews (v20a)
- Use `analog_image_generator.interactive.build_sliders("fluvial")` to pull PRD-aligned slider configs (min/max/step/default with citations) before constructing widgets.
- `build_interactive_ui("fluvial")` returns an `InteractivePanel` dataclass bundling the slider VBox, style dropdown, stacked toggle, and preview button for notebooks or Task Master chat.
- Call `preview_sequence("fluvial", params, seeds)` to render gray/color/channel previews per seed and get placeholder β/D/H metrics until the stats pipeline lands.
- `run_param_batch("fluvial", slider_configs, seeds, output_dir, style="meandering")` emits PNGs for QA attachments or batch artifact exports; reuse the same slider configs the UI exposes so docs/tests remain in sync.

### Phase 1 & 2 metrics
- All generators/stacks feed `analog_image_generator.stats.compute_metrics` which handles variograms (β_iso, β_dir, β_seg, h0), entropy/fractal dimension, PSD anisotropy, topology, and QA flags.
- Use `stats.preview_metrics` for quick β/D/H readouts inside notebooks without rerunning the full pipeline; smoke tests already call the full metrics function so CI catches regressions.
- Add notebook anchors in `notebooks/fluvial_stats.ipynb` whenever metric formulas change to keep GEOLOGIC_RULES/PRDs aligned.

### Reporting exports
- Reporting rows combine `compute_metrics` output with realization metadata (env, realization_id, seed, petrology tags, stacked package counts) before calling `analog_image_generator.reporting.build_reports`.
- The helper writes the canonical CSV, per-env PDFs (mosaic thumbnails + β/D histograms + summary table), and a merged `master_report.pdf`. Palettes reference `docs/PALETTES.md` and QA flags are surfaced in the summary table on each PDF.
- `scripts/smoke_test.py` already exercises the pipeline and writes artifacts to `outputs/smoke_report/`; replicate that flow for milestone deliverables (batch run → metrics → build_reports → attach CSV/PDFs to PR).

5) QA & Release
- Run smoke tests.
- Update CHANGELOG.
- Open PR with artifacts; merge when green.
- Capture a recap using `docs/MEETING_RECAP_TEMPLATE.md` when closing each milestone.

## Conventions
- One PRD → one Tag; keep `master` for epics.
- Conventional Commits; branches `feature/<scope>`.
- Pre-commit: black, isort, ruff, nbstripout.

## References
- TASKMASTER_WSL_SETUP.md
- CURSOR_SETUP.md
