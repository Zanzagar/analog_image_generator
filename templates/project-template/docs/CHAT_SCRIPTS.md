# Chat Scripts (Copy/Paste)

Use these verbatim in chat to standardize the workflow across projects.

## 1) Cursor Phase (author PRDs/AGENTS; no Task Master yet)

### Initialize repository hygiene
```
Create the repo scaffolding for a Python project:
- Add LICENSE (MIT), README.md
- Add .editorconfig, .gitattributes, .pre-commit-config.yaml
- Create requirements.txt and requirements-dev.txt with black, isort, ruff, pre-commit, pytest, nbstripout
- Add GitHub Actions CI to run pre-commit and tests
```

### Author PRDs and AGENTS
```
Help me draft PRDs in .taskmaster/docs/ for each domain and an AGENTS.md at the root.
Include: Acceptance by Metrics, Out of Scope, Glossary, and Sources referencing research docs.
```

### Verify docs and CI locally
```
What are the exact commands to install dev deps and run pre-commit and tests locally?
```

## 2) Switch to Codex (separate extension / CLI)

### Verify Codex CLI
```
Check if Codex CLI is installed and authenticated. If not, provide steps to install and login.
Then confirm `codex --version` and show where auth.json is stored.
```

### Set Task Master main model to Codex (document-only)
```
Show me how to set Task Master main model to gpt-5.1-codex-max for later: the exact command and where it writes config.
Do not run it now.
```

### Confirm MCP WSL wrapper (document-only)
```
Show me the minimal project-local .cursor/mcp.json for WSL with task-master-ai using tool mode 'standard'.
Do not enable it yet.
```

### Package-first restructure (execute right after switching; not during Cursor-only phase)
```
Create a Python package skeleton using Hatchling (src layout):
- Create src/__PACKAGE_NAME__/ with __init__.py (expose __version__) and modules: geologic_generators.py, interactive.py, stats.py, reporting.py, utils.py
- Update pyproject.toml to PEP 621 + Hatchling (build-system hatchling; [project] metadata)
- Update CI to build and install the package before tests (python -m build; pip install -e .)
- Ensure tests and notebooks import __PACKAGE_NAME__ (no relative imports)
```

## 3) Task Master Phase (after PRDs/AGENTS + GitHub are solid)

### Parse PRDs into tags
```
Parse these PRDs into tags (one PRD → one tag):
- .taskmaster/docs/prd_primary.txt → __PRIMARY_TAG__
- .taskmaster/docs/prd_secondary.txt → __SECONDARY_TAG__
- .taskmaster/docs/prd_tertiary.txt → __TERTIARY_TAG__
Stop after parsing; do not expand tasks yet.
```

### Analyze and expand
```
Analyze complexity for the current tag with research, then expand eligible tasks.
Use `standard` tool mode, and append subtasks to existing ones.
```

### Implement with logging
```
For subtask <id>, append an implementation plan: files to edit, function signatures, diffs, and risks.
Then mark the subtask in-progress and continue step-by-step, appending notes as we proceed.
```

### Status management
```
Set the status for tasks/subtasks according to progress and show a summary.
```
