vb# Codex Runbook — End‑to‑End Copy/Paste Scripts

Use these verbatim with the standalone Codex CLI and your WSL terminal. Keep this order.

0) Prereqs (one time)
- Codex CLI installed and authenticated (auth.json present).
- Do not enable Task Master or parse PRDs until professor approves PRDs + Codex review findings.

1) Initialize GitHub repository (terminal)
- GitHub CLI:
```bash
gh repo create <OWNER>/<REPO> --public --source=. --remote=origin --push
git branch -M main
git push -u origin main
```
- Manual UI:
```bash
git init
git add -A
git commit -m "chore: initial commit"
git branch -M main
git remote add origin git@github.com:<OWNER>/<REPO>.git
git push -u origin main
```

2) Pre‑meeting checks (terminal)
```bash
pre-commit run --all-files
pytest -q
```

3) Codex CLI review gate (read‑only prompts; paste these into Codex)
- Workflow & repo hygiene
```
Please review the following files for completeness and clarity. Propose concrete improvements with exact diffs (unified format) and filename headers.
Files:
- README.md
- docs/WORKFLOW.md
- docs/CURSOR_SETUP.md
- docs/TASKMASTER_WSL_SETUP.md
- docs/CHAT_SCRIPTS.md
- CONTRIBUTING.md
- .github/workflows/ci.yml
- .pre-commit-config.yaml
- .editorconfig
- .gitattributes
- .github/PULL_REQUEST_TEMPLATE.md
- .github/ISSUE_TEMPLATE/bug_report.md
- .github/ISSUE_TEMPLATE/feature_request.md
- .github/CODEOWNERS
```
- PRDs + research provenance
```
Review PRDs for rigor and structure. Validate Acceptance by Metrics, slider ranges/defaults, Glossary, and Sources. Propose diffs by file.
Files:
- .taskmaster/docs/prd.txt
- .taskmaster/docs/prd_aeolian.txt
- .taskmaster/docs/prd_estuarine.txt
- research-documents/README.md
Then cross-check PRD slider ranges vs the research index; propose corrected ranges with citations where needed.
```
- Rules & anchors discipline
```
Review docs/GEOLOGIC_RULES.md and AGENTS.md for Principle→Code anchors and anchors discipline. Propose standardized anchor names and exact function signatures. Provide unified diffs by file.
```

4) Apply professor feedback + Codex suggestions (terminal)
```bash
git checkout -b docs/incorporate-professor-feedback
# apply agreed edits from meeting + Codex review
git add -A
git commit -m "docs: incorporate professor feedback into PRDs and docs"
git push -u origin docs/incorporate-professor-feedback
gh pr create --fill
```

5) Switch to Task Master: parse PRDs into tags (terminal; post‑approval)
```bash
# One PRD → one tag
task-master parse-prd .taskmaster/docs/prd.txt --tag fluvial-v1
task-master parse-prd .taskmaster/docs/prd_aeolian.txt --tag aeolian-v1
task-master parse-prd .taskmaster/docs/prd_estuarine.txt --tag estuarine-v1
```

6) Analyze complexity and expand (terminal; per tag)
```bash
task-master analyze-complexity --tag fluvial-v1 --research
task-master expand --all --tag fluvial-v1

task-master analyze-complexity --tag aeolian-v1 --research
task-master expand --all --tag aeolian-v1

task-master analyze-complexity --tag estuarine-v1 --research
task-master expand --all --tag estuarine-v1
```

7) Package‑first restructure (immediately after switching; not earlier) (terminal)
```bash
# create package skeleton
mkdir -p src/analog_image_generator
touch src/analog_image_generator/__init__.py \
      src/analog_image_generator/geologic_generators.py \
      src/analog_image_generator/interactive.py \
      src/analog_image_generator/stats.py \
      src/analog_image_generator/reporting.py \
      src/analog_image_generator/utils.py

# install & verify build
pip install -e .
python -m build
pytest -q
```

8) Begin executing tasks (Task Master + Codex)
```bash
task-master use-tag fluvial-v1
task-master next
task-master show <id>
```
- Implementation loop:
```
In Codex:
“For subtask <id>, draft an implementation plan with files, functions, unified diffs, risks.”
```
```bash
# apply changes; then log and mark
pytest -q
pre-commit run --all-files
task-master update-subtask --id <id> --prompt "Implemented X; tests pass; notes: ..."
task-master set-status --id <id> --status=done
git add -A && git commit -m "feat(module): implement <subtask title>" && git push
```

9) New project bootstrap from template (terminal)
```bash
cp -R templates/project-template ../__NEW_PROJECT__
cd ../__NEW_PROJECT__
# replace: __PROJECT_NAME__, __PACKAGE_NAME__, __OWNER__, __REPO__, etc.
pre-commit install
git init && git add -A && git commit -m "chore: scaffold from template"
```

Notes
- Do not run Task Master until PRDs are approved (professor + Codex review gate).
- Update README badge to real <OWNER>/<REPO> before first push.
