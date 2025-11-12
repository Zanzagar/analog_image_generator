# Professor Meeting: Workflow Demo & Feedback Plan (Template)

## Objectives
- Demonstrate Cursor-first docs → GitHub hygiene → (future) Codex+Task Master handoff.
- Validate rigor (PRDs, rules, metrics) and engineering process (CI, review).
- Collect decisions on acceptance metrics, slider ranges, reporting, priorities.

## What to Show
- README.md, docs/WORKFLOW.md, docs/CHAT_SCRIPTS.md
- .taskmaster/docs/prd_*.txt
- docs/GEOLOGIC_RULES.md, AGENTS.md, research-documents/README.md
- CI (.github/workflows/ci.yml), pre-commit, templates

## Live Demo Flow
1) README.md → badges/links
2) WORKFLOW.md → 5 phases
3) PRDs → sliders + Acceptance by Metrics
4) GEOLOGIC_RULES.md → anchors discipline
5) AGENTS.md → DoD per role
6) Local checks (no Task Master): pre-commit run --all-files; pytest -q
7) CHAT_SCRIPTS.md → exact prompts

## Codex CLI Review Gate
- Run 4 read-only reviews (workflow/hygiene, PRDs, rules/anchors, research provenance)
- Paste findings into docs/MEETING_RECAP_TEMPLATE.md → “Codex Review Findings”

## After Meeting (no execution during meeting)
- Apply approved edits to PRDs/AGENTS/rules; commit.
- Move to Codex+Task Master → parse → analyze → expand.

## Package-first (after switch to Codex+Task Master)
- Create src/__PACKAGE_NAME__/ skeleton; update pyproject to Hatchling; CI builds & installs; notebooks import package.

## To-dos
- [ ] Codex review gate complete
- [ ] Package-first restructure after switch

