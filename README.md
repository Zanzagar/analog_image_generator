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

## CI & Repo Hygiene
- Pre-commit enforces formatting, lint, and notebook output stripping.
- GitHub Actions (ci.yml) runs lint and optional smoke tests.

## License
MIT
