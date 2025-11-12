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
- Confirm CI green.

3) Switch to Codex + Task Master
- Enable MCP (WSL wrapper), set `codex-cli` main model.
- Tag per PRD (one PRD → one tag).
- Parse PRD → analyze complexity → expand tasks.

  Package-first restructure (execute immediately after switching; do not do during Cursor-only phase)
  - Create `src/__PACKAGE_NAME__/` package and modules.
  - Update `pyproject.toml` to PEP 621 + Hatchling.
  - Amend CI to build and install the package before tests.
  - Ensure tests/notebooks import the package.

4) Implement
- Work by `next` task. Append subtask notes; keep anchors and rules in sync.

5) QA & Release
- Run smoke tests; update CHANGELOG; open PR with artifacts; merge when green.

