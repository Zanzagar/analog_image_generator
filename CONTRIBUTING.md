# Contributing

## Branching & Commits
- Branches: `feature/<scope>`, `fix/<scope>`, `docs/<scope>`
- Commits follow Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`

### Examples
- `feat(stats): add PSD anisotropy metrics`
- `fix(ux): prevent slider from submitting twice`
- `docs(rules): map meander_variable_channel in GEOLOGIC_RULES`

## PRs
- Link the relevant PRD section
- Note the professor/Codex review gate approval (include approver + date) in the PR body
- Include screenshots or artifact paths (CSV/PDF) if applicable
- Ensure pre-commit passes locally

## Anchors Discipline
- When code or function names change, update GEOLOGIC_RULES.md and the matching notebook markdown anchors in the same PR.

## Local Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pre-commit install
pytest -q
pre-commit run --all-files
python -m build  # optional sanity check
```
