# AGENTS.md — analog_image_generator (geologic analog research tooling; adoption matrix §1 "RESEARCH")

Standing rules every session (Claude, Codex, human) loads. The harness standard is
`~/projects/claude-harness` (https://github.com/Zanzagar/claude-harness): `docs/git-hygiene.md` is the
git standard, `docs/adr/0001-verification-precedence.md` the workflow precedence, `docs/adoption-matrix.md`
this project's row. Adopted here 2026-09-24 from branch `gate/grilling-trailers` (unmerged at adoption;
re-sync when it lands).
The Codex + Task Master guide that used to be this file is `docs/legacy/AGENTS-codex-taskmaster-2025.md`,
reference only: task-master is retired and pending tasks live in `tasks.md`.

## Project standard (harness adoption matrix §1)

- domain-modeling formalizes the home-grown rule↔code anchor pattern (`docs/GEOLOGIC_RULES.md` +
  `scripts/validate_geo_anchors.py`); a `CONTEXT.md` pointing at GEOLOGIC_RULES.md is the missing piece.
  Grill the PRD phase of a new environment (aeolian, estuarine) before generating tasks for it.
- `.cursor/`, `.codex/`, `.taskmaster/` and `docs/CODEX_RUNBOOK.md` are inert archive, not instructions.

## Workflow precedence (harness ADR 0001)

1. **Pocock's skills are the default workflow**: grill / grill-with-docs before creative or scope-changing
   work, domain-modeling for `CONTEXT.md` and ADRs, tdd for code that must stay correct,
   verification-before-completion before any "done", handoff saved in-repo (`docs/handoffs/`). Invoked on
   judgment, except where a gate says otherwise.
2. **Codex adversarial review is the check on any diff that matters** (`/codex:adversarial-review`,
   `/code-review`): flag-only, on demand; findings are claims to verify, never auto-applied. The stop-time
   review gate stays disabled.
3. **A fan-out wave is the last resort**, for one job neither of the above can do: breaking a claim about a
   measurement, an artifact or an archive that no test pins and no diff review reaches.

## Multi-agent runs

- **One wave at a time, never concurrent.**
- **At most 6 questions and at most 6 verifiers per wave**; the entry-point / decision-critical claim is
  verified first; the tail is logged as unverified, not silently covered.
- **Say what the wave will spawn before launching it**, in the reply the owner reads.
- Run waves through `.claude/workflows/question-fanout-audit.js` (the hard-capped harness copy). An inline
  `Workflow` script that exceeds the caps is a rule violation, not a tooling gap.
- Ultracode ON does not reopen the caps (owner, 2026-09-02).
- Verifiers write nothing; premises in a brief are hypotheses (harness `docs/multi-agent-field-rules.md`).

## Git

- Follow claude-harness `docs/git-hygiene.md` rules 1–13: feature branches named `<track>/<subject>`,
  atomic imperative commits, `Co-Authored-By` on agent commits, push feature branches after every commit,
  `main` moves only through a merged pull request and a human merges. The checked-in
  `.claude/settings.json` carries the deny/ask rules.
- **Grilling gate:** rule 14 (`Decided:` / class trailers) is NOT adopted here. Adoption matrix §1a: "not adopted." To adopt: `~/projects/claude-harness/adopt.sh ~/projects/analog_image_generator`, then the owner runs `git config core.hooksPath .githooks`; adopt.sh replaces this line with its pointer. <!-- grill-gate:pointer -->
