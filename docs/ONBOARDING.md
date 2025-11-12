# Onboarding

## 1. Clone & Setup
```bash
git clone <repo-url> && cd analog_image_generator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

## 2. Verify locally
```bash
pre-commit run --all-files
pytest -q
```

## 3. Learn the Workflow
- Read `docs/WORKFLOW.md` for the Cursor → PRD/AGENTS → GitHub → Codex+Task Master process.
- Review `docs/CURSOR_SETUP.md` and `docs/TASKMASTER_WSL_SETUP.md`.

## 4. Make a Change
- Branch: `feature/<scope>`
- Follow Conventional Commits in `CONTRIBUTING.md`.
- If changing geologic functions, update `docs/GEOLOGIC_RULES.md` and notebook anchors.

## 5. Open a PR
- Ensure CI is green.
- Attach artifacts/screenshots as needed.
- Use PR template checklist.
