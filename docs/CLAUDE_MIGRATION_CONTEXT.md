# Project Context (Analog Image Generator → Claude Code)

## Part A: Project Overview
1) Purpose, goals, current state  
- Purpose: Generate synthetic geologic analog images (fluvial focus) with interactive notebooks and reporting/QA.  
- Goals: Professor-facing demos; transparent rule↔code mapping; interactive UI with batch/export; metrics/QA; reporting artifacts.  
- Current state: Fluvial fully implemented (meandering, braided, anastomosing, stacked), interactive UI overhauled, palette/legends style-aware with optional overlays, batch grids. Tasks for advanced controls/QA remain open (tag `fluvial-v1`).

2) Architecture & Structure (key paths)  
- `src/analog_image_generator/`: core package  
  - `geologic_generators.py`: fluvial generators + overlays + stacked orchestration  
  - `stacked_channels.py`: stacked package assembly  
  - `interactive.py`: slider schema, preview/batch helpers, palette → color  
  - `ui.py`: notebook UI wiring (widgets, batch, grid, overlay toggle)  
  - `stats.py`: variogram/β/H/fractal/PSD/topology metrics  
  - `utils.py`: RNG, palettes, mask helpers (palette now includes per-style facies + overlays)  
- `notebooks/`: demos  
  - `v20a_interactive_rebuild.ipynb`: interactive panel + preview/batch  
  - `fluvial_rules_whiteboard.ipynb`: rule→code mapping with `inspect.getsource`  
  - other fluvial notebooks (meandering/braided/anasto/stats/reporting/etc.)  
- `docs/`: runbooks and recap  
  - `MEETING_RECAP_2025-11-21.md`: demo script, current state, gaps  
  - `CODEX_RUNBOOK.md`, `WORKFLOW.md`, `GEOLOGIC_RULES.md` (anchors)  
- `.taskmaster/`: Taskmaster config, tasks, reports

3) Workflows (common commands)  
- Tests/validation: `python -m pytest`; `python scripts/validate_geo_anchors.py`; `python scripts/smoke_test.py`  
- Interactive: run cells in `notebooks/v20a_interactive_rebuild.ipynb` to launch `ui.build_live_fluvial_panel(...)`  
- Batch demo artifacts: `outputs/batch_demo/<style>/<mode>/` (generated for seeds 1–10)  
- Taskmaster: `task-master list --tag <tag>`, `task-master show <id>`, `task-master expand --id=<id> --tag <tag>`, `task-master parse-prd ...`  
- Git: frequent small commits; notebooks refreshed when UI changes.

4) Custom instructions/prompts  
- GEOLOGIC_RULES anchors discipline (code ↔ notebook anchors).  
- Interactive legends style-specific; overlay toggle controls whether overlay facies appear.  
- Meeting recap/demos scripted in `MEETING_RECAP_2025-11-21.md`.

5) Key decisions & context  
- Code-first (package) with notebooks as “whiteboards.”  
- Style-specific palettes/legends with optional overlays to avoid washed-out composites.  
- Variogram plot now linear axes; still fits β/D.  
- Batch UI separated from single preview; grid view toggle (facies composite, gray, channel mask).  
- Tasks split by tag; fluvial-v1 covers advanced controls/QA still pending.

6) Dependencies & environment  
- Python, numpy, matplotlib, ipywidgets (8.1.8), nbconvert, scipy.  
- Node for Taskmaster CLI.  
- ENV: typical Python venv; ensure ipywidgets enabled in notebooks.  
- No sensitive files committed; notebooks tracked.

7) Ongoing work (fluvial-v1 tasks)  
- Task 11: Curvature-coupled width/scroll; discharge/slope-linked widths/threads; plumb through UI/batch; docs/QA.  
- Task 12: Bar amalgamation, per-facies thickness variance, crevasse-splay/clay-clast enhancements.  
- Task 13: Stronger QA bands/flags surfaced in UI/reporting; env-specific acceptance bands.

---

## Part B: Taskmaster System
8) Overview  
- Taskmaster manages tasks per tag using PRDs.  
- Tags present: `fluvial-v1`, `aeolian-v1`, `estuarine-v1`, `fluvial-v1-demo` (demo tag is done; main work now on `fluvial-v1`).  
- PRDs (in `.taskmaster/docs/`) drive task generation; parsed into tasks.json per tag.  
- Complexity reports (`.taskmaster/reports/task-complexity-report_<tag>.json`) guide subtask counts.  
- `state.json` tracks `currentTag` and optional branch mapping; switching tags changes active context.

9) Workflows  
- Switch tags: `task-master use-tag <tag>` or edit state.json.  
- Generate tasks: `task-master parse-prd <prdfile> --tag <tag> [--num-tasks N --research]`.  
- Expand tasks: `task-master expand --id=<id> --tag <tag>`; uses complexity to pick subtask count.  
- Common CLI: `task-master list/show/set-status/add-task/remove-task/expand/parse-prd`.  
- Keep tags clean: demo tag completed; new work to `fluvial-v1`.

10) Configuration (current → planned)  
- Current models (codex config): `model = "gpt-5.1-codex-max"`, reasoning `high` (set in `~/.codex/config.toml`).  
- Taskmaster `.taskmaster/config.json` currently references `codex-cli` provider; update to Claude Code:  
  - Main: Claude Opus 4.5  
  - Fallback: Claude Sonnet 4.5  
  - Adjust provider/modelId fields accordingly; rerun `task-master --version` and a dry-run `parse-prd` to verify.  
- Other provider options exist in Taskmaster (claudeCode, grokCli sections) if needed.

---

## Part C: Project-Specific Details
11) Domain knowledge  
- Fluvial facies: meandering (channel/pointbar/levee/floodplain/oxbow), braided (channel/bar/chute/floodplain), anastomosing (branch_channel/levee/marsh/fan/floodplain). Overlays: channel_fill, cross_bed, ripple, fining_upward, overbank_mudstone, lateral_accretion.  
- Algorithms: spline/perturbation for centerlines; sinusoidal modulations for threads; distance-based bands for scrolls/fining/ripples; dilation/filters for levees; stacked relief/erosion for packages. Metrics: variogram β/H/D, PSD anisotropy, topology.  
- UI: ipywidgets panel with style-aware sliders, overlay toggle, batch grid, style-filtered legends.

12) Gotchas & watch-outs  
- Palettes: color composites filter to primary facies unless overlay toggle is on.  
- Legends: style-specific; overlays included only when toggle is on.  
- Width bounds: channel_width_min/max guarded to avoid negative variance (fix applied).  
- Taskmaster: ensure model provider updated before expand/parse (codex “xhigh” unsupported; use “high” or Claude settings).  
- Environment: ipywidgets must be enabled; notebooks should be run in a venv with correct deps.  
- Do not commit secrets; notebooks are tracked, so clear heavy outputs before commit if needed.
