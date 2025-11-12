# Onboarding (Template)

## 1. Clone & Setup
```bash
git clone <repo-url> && cd __PROJECT_NAME__
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
- Read `docs/WORKFLOW.md` (Cursor → PRD/AGENTS → GitHub → Codex+Task Master → Release)

## 4. Make a Change
- Branch: `feature/<scope>` and follow Conventional Commits
- Update `docs/GEOLOGIC_RULES.md` and notebook anchors for rule changes

## 5. Open a PR
- Ensure CI is green and use the PR checklist

