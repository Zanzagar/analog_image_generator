# __PROJECT_NAME__

![CI](https://github.com/__OWNER__/__REPO__/actions/workflows/ci.yml/badge.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)

Standard workflow: see `docs/WORKFLOW.md`, `docs/CURSOR_SETUP.md`, `docs/TASKMASTER_WSL_SETUP.md`.

## Quick Start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

## Documents
- `.taskmaster/docs/prd_primary.txt`
- `.taskmaster/docs/prd_secondary.txt`
- `.taskmaster/docs/prd_tertiary.txt`
- `docs/GEOLOGIC_RULES.md`
- `docs/PALETTES.md`
- `docs/MEETING_RECAP_TEMPLATE.md`

## Working in Cursor + Codex + Task Master
- Keep tasks isolated by domain tags (one PRD → one tag).
- Parse the appropriate PRD into its tag only when actively working in Codex+Task Master.

## Install (editable) after package-first step
```bash
pip install -e .
```

## License
MIT

