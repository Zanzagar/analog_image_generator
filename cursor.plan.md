# Professor Meeting: Workflow Demo & Feedback Plan

## Objectives
- Demonstrate end-to-end workflow: Cursor-first docs → GitHub hygiene → (future) Codex+Task Master handoff.
- Validate geologic rigor (PRDs, rules, metrics) and engineering process (CI, review discipline).
- Collect decisions on acceptance metrics, slider ranges, reporting layout, and next-feature priorities.

## What to Show (files & where)
- Repository overview (2 min)
  - README.md (badges, quick start, workflow links)
  - docs/WORKFLOW.md (canonical process)
  - docs/CHAT_SCRIPTS.md (copy/paste scripts for Cursor, Codex, Task Master)
- Geologic & planning docs (6–8 min)
  - PRDs: .taskmaster/docs/prd.txt, prd_aeolian.txt, prd_estuarine.txt (show Acceptance by Metrics, Out of Scope, Glossary, Sources)
  - docs/GEOLOGIC_RULES.md (Principle → Code anchors)
  - AGENTS.md (Definition of Done, Daily/Release loops, anchors discipline)
  - research-documents/README.md (parameter ranges; provenance)
- Repo hygiene & CI (3–4 min)
  - .github/workflows/ci.yml (pre-commit + tests + smoke)
  - .pre-commit-config.yaml (black, isort, ruff, nbstripout)
  - Templates: PR/Issue, CODEOWNERS
- Handoff preview (2–3 min, document-only)
  - docs/TASKMASTER_WSL_SETUP.md (WSL MCP setup)
  - docs/CURSOR_SETUP.md (local dev and checks)
  - Tag-by-PRD convention; no execution during meeting.

## Live Demo Flow (15–20 min)
1. README.md → show badges and links.
2. docs/WORKFLOW.md → 5-phase overview.
3. Walk PRDs (fluvial → aeolian → estuarine): highlight slider ranges & Acceptance by Metrics.
4. docs/GEOLOGIC_RULES.md anchors and notebook-anchor discipline.
5. AGENTS.md → Definition of Done per role.
6. CI & pre-commit: run locally (no Task Master):
   - pre-commit run --all-files
   - pytest -q
7. docs/CHAT_SCRIPTS.md → exact chat prompts later for parsing PRDs into tags and proceeding.

## Codex CLI Review Gate (before switching to Task Master)
- Run four read-only reviews with standalone Codex CLI and paste findings into docs/MEETING_RECAP_TEMPLATE.md under “Codex Review Findings”:
  1) Workflow & repo hygiene: README, WORKFLOW, CURSOR_SETUP, TASKMASTER_WSL_SETUP, CHAT_SCRIPTS, CONTRIBUTING, CI, pre-commit, templates, CODEOWNERS
  2) PRDs (fluvial/aeolian/estuarine): acceptance bands, slider ranges, glossary, sources
  3) Rules & anchors: GEOLOGIC_RULES, AGENTS — naming and traceability
  4) Research provenance: parameter ranges vs PRD sliders using research-documents/README.md
- Do not edit files yet; consolidate findings to review with professor.

## After the Meeting (no execution yet during meeting)
- Apply professor’s changes to PRDs/AGENTS/GEOLOGIC_RULES (and any adopted Codex findings).
- Re-run local checks; commit and open a PR titled `docs: incorporate professor feedback`.
- When approved: move to Codex+Task Master phase using docs/CHAT_SCRIPTS.md (parse → analyze → expand).

## Package-first restructure (executed immediately after switching to Codex + Task Master)
- Create `src/analog_image_generator` package skeleton; update pyproject to PEP 621 + Hatchling; update CI to build & install before tests; ensure notebooks import the package.

## Sign-off Criteria
- Professor approves Acceptance by Metrics and slider ranges per domain.
- Professor approves reporting contents and overall process.
- Codex review findings considered; accepted items reflected in docs.
- All requested textual edits captured in PRDs/AGENTS and committed.

## To-dos
- [x] Augment PRDs with Acceptance by Metrics, Out of Scope, Glossary per domain
- [x] Add Definition of Done + Daily/Release loops to AGENTS.md
- [x] Create docs/WORKFLOW.md and TASKMASTER_WSL_SETUP.md, CURSOR_SETUP.md
- [x] Create research-documents/README.md index with parameter ranges & cites
- [x] Add pip cache and clarify smoke gating in .github/workflows/ci.yml
- [x] Update CONTRIBUTING with Conventional Commits & anchors discipline
- [x] Update README with workflow banner and links to PRDs & WORKFLOW.md
- [ ] Codex review gate: run 4 prompts and paste findings into meeting recap (pre-switch)
- [ ] Package-first restructure at start of Codex + Task Master phase (post-approval)
