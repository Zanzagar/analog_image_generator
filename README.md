# Analog Image Generator

![CI](https://github.com/cjh5690/analog_image_generator/actions/workflows/ci.yml/badge.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)

Fluvial analogs with interactive exploration, statistics, and reporting, extended to aeolian and estuarine systems. Built to work with Task Master (MCP) and Codex in Cursor.

> Standard Workflow: see `docs/WORKFLOW.md`, `docs/CURSOR_SETUP.md`, `docs/TASKMASTER_WSL_SETUP.md`.

## Quick Start
```bash
# Create virtual env (example)
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pre-commit install
pytest -q
```

## Package install shortcuts
- `pip install -r requirements.txt -r requirements-dev.txt` remains available for pinned/air-gapped installs.
- Run `python -m build` before publishing to validate the Hatchling config.

## Documents
- `.taskmaster/docs/prd.txt` (Fluvial)
- `.taskmaster/docs/prd_aeolian.txt`
- `.taskmaster/docs/prd_estuarine.txt`
- `docs/GEOLOGIC_RULES.md`
- `docs/PALETTES.md`
- `docs/MEETING_RECAP_TEMPLATE.md`

## Review Gate & Task Master Sequence
- Capture PRD/AGENTS edits inside Cursor, then run `pre-commit` + `pytest` locally.
- Record professor approval in each PRD and run the Codex CLI review prompts in `docs/CODEX_RUNBOOK.md`.
- Only after approvals, create the domain tags (`fluvial-v1`, `aeolian-v1`, `estuarine-v1`) and run `task-master parse-prd`, `analyze`, and `expand` within Codex.

## Working in Cursor + Codex + Task Master
- Keep tasks isolated by domain tags (create when ready).
- Parse the appropriate PRD into its tag only when actively working in Codex and after the review gate.

## Interactive Demos
- `analog_image_generator.interactive.build_sliders("fluvial")` exposes the PRD-aligned slider schema (min/max/step/default plus citations) for PR/notebook use.
- `build_interactive_ui("fluvial")` returns the ipywidgets panel (style dropdown, stacked toggle, package mix) so notebooks and Cursor share the same UX.
- `preview_sequence("fluvial", params, seeds)` renders mini-previews plus placeholder β/D/H metrics, while `run_param_batch` writes PNGs for QA artifacts.

## Phase 1/2 Metrics
- `analog_image_generator.stats.compute_metrics(gray, masks, env)` now returns the PRD-required fields (β_iso, β_dir_*, β_seg*, entropy, PSD anisotropy, topology, QA flags, stacked metadata hashes).
- Lighter adapters such as `stats.preview_metrics` power the interactive panel without recomputing the full stack.
- Scripts (e.g., `scripts/smoke_test.py`) call these helpers so CI ensures the metrics surface stays healthy alongside generators and stacked workflows.

## Reporting
- `analog_image_generator.reporting.build_reports(metrics_rows, output_dir)` writes the metrics CSV, per-environment PDFs (mosaics + histograms + tables), and merges a master PDF.
- Reporting rows combine stats output with realization metadata (env/seed IDs, petrology flags, stacked package counts). See `scripts/smoke_test.py` for an end-to-end example that drops artifacts into `outputs/smoke_report/`.
- Palettes/legends follow `docs/PALETTES.md`; QA flags from stats are surfaced in the summary tables and master cover.

## Stacked Channel Packages
- Fluvial calls now accept `mode="stacked"` plus `package_count`, `package_styles`, and per-package thickness/relief/erosion parameters to sequence mixed belts.
- `stacked_channels.build_stacked_fluvial` composes stacked packages, and `generate_fluvial` routes to it automatically in stacked mode (falls back to single-belt when `package_count == 1`).
- Downstream consumers should read the new masks (`upper_surface_mask`, `erosion_surface_mask`, `package_id_map`) and metadata stored under `masks["realization_metadata"]["stacked_packages"]`.
- Use `package_param_overrides` for per-package tweaks (e.g., levee width for package 2) while `stack_seed` guarantees deterministic sub-seeds for the package sequence.

## CI & Repo Hygiene
- Pre-commit enforces formatting, lint, and notebook output stripping.
- GitHub Actions (ci.yml) runs lint and optional smoke tests.

## License
MIT
