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
- Enable MCP (WSL wrapper), set `codex-cli` main model.
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
