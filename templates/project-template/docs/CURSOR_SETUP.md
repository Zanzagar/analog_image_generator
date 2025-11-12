# Cursor Setup

## Pre-commit & Dev Env
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

## Running checks locally
```bash
pre-commit run --all-files
pytest -q
```

## Using AI chat
- Cursor phase: author PRD(s), AGENTS.md, review docs.
- Codex phase: enable Task Master MCP; parse PRDs into tags; analyze/expand tasks; implement.

