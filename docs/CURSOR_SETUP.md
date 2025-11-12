# Cursor Setup

## Pre-commit & Dev Env
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pre-commit install
# Fallback (pinned wheels): pip install -r requirements.txt -r requirements-dev.txt
```

## Running checks locally
```bash
pre-commit run --all-files
pytest -q
python -m build  # optional sanity check for Hatchling config
```

## Using AI chat
- Cursor phase: author PRD(s), AGENTS.md, review docs.
- Codex phase: enable Task Master MCP; parse PRDs into tags; analyze/expand tasks; implement.

## WSL tips
- Non-interactive shells skip pyenv/nvm by default; export `FORCE_PYENV=1` if you need those toolchains for a single command.
- Use the project-local `.cursor/mcp.json` example in `docs/TASKMASTER_WSL_SETUP.md` when enabling the Task Master MCP.
