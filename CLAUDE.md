# Analog Image Generator

@AGENTS.md

## Project Overview

Generate synthetic geologic analog images (fluvial focus) with interactive notebooks and reporting/QA. Designed for professor-facing demos with transparent rule↔code mapping, interactive UI with batch/export, metrics/QA, and reporting artifacts.

**Current State**: Fluvial fully implemented (meandering, braided, anastomosing, stacked), interactive UI overhauled, palette/legends style-aware with optional overlays, batch grids. Tasks for advanced controls/QA remain open (tag `fluvial-v1`).

## Architecture & Key Files

```
src/analog_image_generator/
├── geologic_generators.py  # Fluvial generators + overlays + stacked orchestration
├── stacked_channels.py     # Stacked package assembly
├── interactive.py          # Slider schema, preview/batch helpers, palette → color
├── ui.py                   # Notebook UI wiring (widgets, batch, grid, overlay toggle)
├── stats.py                # Variogram/β/H/fractal/PSD/topology metrics
└── utils.py                # RNG, palettes, mask helpers

notebooks/
├── v20a_interactive_rebuild.ipynb  # Interactive panel + preview/batch (main demo)
├── fluvial_rules_whiteboard.ipynb  # Rule→code mapping with inspect.getsource
└── [other fluvial notebooks]       # Meandering/braided/anasto/stats/reporting

scripts/
├── validate_geo_anchors.py  # Verify GEOLOGIC_RULES anchors match code
├── smoke_test.py            # Quick validation
└── render_preview.py        # CLI preview rendering

outputs/batch_demo/          # Generated artifacts by style/mode for seeds 1-10
```

## Common Commands

```bash
# Run tests
python -m pytest

# Validate geologic anchors (rule↔code mapping)
python scripts/validate_geo_anchors.py

# Smoke test
python scripts/smoke_test.py

# Interactive demo (in Jupyter)
# Run cells in notebooks/v20a_interactive_rebuild.ipynb
# Launches ui.build_live_fluvial_panel(...)
```

## Task Tracking

Task-master is retired. Pending tasks were exported to `tasks.md` at the repo root (grouped by tag); `.taskmaster/` remains as an inert archive.

**Active Tags**:
- `fluvial-realism-v2` (current) - Physics-based fluvial realism (research-enabled)
- `fluvial-v1` - Advanced controls/QA work
- `fluvial-v1-demo` (completed) - Demo preparation
- `aeolian-v1`, `estuarine-v1` - Future environments

## Domain Knowledge

### Fluvial Facies
- **Meandering**: channel, pointbar, levee, floodplain, oxbow
- **Braided**: channel, bar, chute, floodplain
- **Anastomosing**: branch_channel, levee, marsh, fan, floodplain

### Overlay Facies
channel_fill, cross_bed, ripple, fining_upward, overbank_mudstone, lateral_accretion

### Key Algorithms
- Spline/perturbation for centerlines
- Sinusoidal modulations for threads
- Distance-based bands for scrolls/fining/ripples
- Dilation/filters for levees
- Stacked relief/erosion for packages

### Metrics
Variogram β/H/D, PSD anisotropy, topology analysis

## Key Decisions & Constraints

### Code Organization
- **Package-first**: Core code in `src/analog_image_generator/`, notebooks are for demo/lecture
- **Anchor discipline**: Every principle in code is referenced in notebook markdown AND `docs/GEOLOGIC_RULES.md`
- Anchor IDs follow `anchor-<env>-<principle>` (lowercase kebab case)

### Palette & Legend Rules
- Style-specific palettes/legends with optional overlays
- Color composites filter to primary facies unless overlay toggle is on
- Legends include overlays only when toggle is on

### UI Architecture
- ipywidgets panel with style-aware sliders
- Overlay toggle controls visibility
- Batch grid separate from single preview
- Grid view modes: facies composite, gray, channel mask

## Gotchas & Watch-outs

- **Width bounds**: `channel_width_min/max` guarded to avoid negative variance
- **Variogram plot**: Now uses linear axes; still fits β/D
- **ipywidgets**: Must be enabled in notebooks (version 8.1.8)
- **Notebooks tracked**: Clear heavy outputs before commit if needed

## Ongoing Work (fluvial-v1)

- **Task 11**: Curvature-coupled width/scroll; discharge/slope-linked widths/threads
- **Task 12**: Bar amalgamation, per-facies thickness variance, crevasse-splay/clay-clast
- **Task 13**: Stronger QA bands/flags in UI/reporting; env-specific acceptance bands

## Definition of Done (per Agent Role)

| Role | Criteria |
|------|----------|
| **GEO** | Rules mapped in GEOLOGIC_RULES.md and notebook anchors; visual realism checks passed |
| **GEN** | Generators return (gray, masks_dict); masks align with palettes; parameters documented |
| **UX** | Sliders/preview responsive; metrics update; batch export button works |
| **STAT** | compute_metrics covers Phase 1 & 2; CSV schema stable; unit tests where feasible |
| **REP** | CSV + per-env PDFs + master PDF generated; legends consistent with PALETTES.md |
| **QA** | Smoke passes; checklist at top of notebooks fully ticked; no regressions vs previous tag |
| **DOC** | README/WORKFLOW updated; GEOLOGIC_RULES + anchors in sync; meeting recap saved |

## Development Workflow

### Daily Loop
1. Edit PRDs; update GEOLOGIC_RULES anchors
2. Pre-commit run; small PR
3. Work the next pending task in `tasks.md`

### Release Loop
1. Smoke + CI green; CHANGELOG entry added
2. PR with artifacts (CSV/PDF/figures) and PRD references
3. Review + merge; tag release if applicable

## AI Assistant Instructions

Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.

## Related Documentation

- `docs/CLAUDE_MIGRATION_CONTEXT.md` - Full project context (migrated from Codex)
- `docs/GEOLOGIC_RULES.md` - Rule↔code anchor mappings
- `docs/WORKFLOW.md` - Development workflow
- `docs/MEETING_RECAP_2025-11-21.md` - Demo script and current state
- `docs/MCP_SETUP.md` - MCP server setup (Task Master, Context7, GitHub)
- `docs/rules/` - Git workflow, Python standards, self-improvement rules
- `docs/legacy/AGENTS-codex-taskmaster-2025.md` - (Legacy) Codex CLI + Task Master setup guide, retained for reference; `AGENTS.md` now carries the harness standing rules
