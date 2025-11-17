# Task Master Backlog — analog_image_generator
Generated 1763315001952597592

## aeolian-v1

### aeolian-v1:1 — Implement Aeolian parameter schema and base field scaffolding [pending]
Create a reusable parameter dataclass + helper utilities that normalize all aeolian slider inputs, seed RNG deterministically, and prepare base grids shared by all dune styles.

Subtasks:
- 1.1 Draft AeolianParams schema and module layout (deps: None) — pending
- 1.2 Implement AeolianParams dataclass with PRD-backed validation and normalization (deps: 1) — pending
- 1.3 Provide deterministic RNG helper bound to AeolianParams (deps: 2) — pending
- 1.4 Implement base-field utilities for aeolian grids, rotation, and base noise (deps: 2, 3) — pending
- 1.5 Wire AeolianParams and helpers into GEOLOGIC_RULES and aeolian notebook anchors (deps: 1, 2, 4) — pending
- 1.6 Add pytest coverage for AeolianParams validation, RNG, and base-field utilities (deps: 2, 3, 4) — pending

### aeolian-v1:2 — Build Barchan dune generator with crest/slipface/interdune masks [pending]
Implement horned barchan synthesis driven by wind azimuth, including mask outputs for crest, slipface, stoss, and interdune plus migration metadata.

Subtasks:
- 2.1 Design barchan builder API and AeolianParams integration (deps: None) — pending
- 2.2 Implement aeolian_make_crests to seed horned barchan crests (deps: 1) — pending
- 2.3 Implement horn growth and downwind migration operations (deps: 2) — pending
- 2.4 Implement aeolian_add_slipfaces to project lee-side slipfaces (deps: 2, 3) — pending
- 2.5 Implement aeolian_interdune to carve interdune corridors (deps: 3, 4) — pending
- 2.6 Compose grayscale shading and masks dict aligned with palettes (deps: 1, 4, 5) — pending
- 2.7 Capture horn curvature and interdune fraction as generator metadata (deps: 3, 5, 6) — pending
- 2.8 Integrate barchan builder with generate_aeolian entry points (deps: 1, 6, 7) — pending
- 2.9 Add tests/test_barchan_generator.py for orientation and connectivity (deps: 2, 3, 5, 6, 7, 8) — pending

### aeolian-v1:3 — Implement Linear/Seif dune generator with ridge continuity controls [pending]
Generate linear dune fields that honor mean wind direction, secondary wind kinks, and target ridge continuity metrics.

Subtasks:
- 3.1 Define aeolian_linear_ridges builder API and scaffolding (deps: None) — pending
- 3.2 Implement parallel spine seeding aligned with wind direction and spacing (deps: 1) — pending
- 3.3 Add secondary wind kink perturbations based on research PDF (deps: 2) — pending
- 3.4 Construct crest mask and aeolian_ridge_continuity metric via components (deps: 2, 3) — pending
- 3.5 Implement interdune corridor carving and stoss/slipface mask differentiation (deps: 4) — pending
- 3.6 Apply defect_rate-driven crest breaking while preserving interpretable continuity (deps: 4, 5) — pending
- 3.7 Finalize aeolian_linear_ridges outputs compatible with stats.compute_metrics (deps: 1, 5, 6) — pending
- 3.8 Document and wire aeolian_ridge_continuity anchors in GEOLOGIC_RULES and notebook (deps: 4, 6, 7) — pending
- 3.9 Create linear dune generator tests for continuity, orientation, and defect effects (deps: 1, 2, 3, 4, 5, 6, 7) — pending

### aeolian-v1:4 — Implement Transverse dune generator with λ=f(H) spacing [pending]
Produce transverse dune fields whose crest spacing scales linearly with dune height and remain orthogonal to wind direction.

Subtasks:
- 4.1 Define build_transverse_field / aeolian_transverse_ridges API and stubs (deps: None) — pending
- 4.2 Implement λ = k * H spacing logic with slider guards and overrides (deps: 1) — pending
- 4.3 Generate crest-parallel ridges orthogonal to wind direction (deps: 1, 2) — pending
- 4.4 Derive slipface, stoss, and interdune masks from crest geometry and wind (deps: 3) — pending
- 4.5 Incorporate defect_rate to generate crest bifurcations and continuity metrics (deps: 3, 4) — pending
- 4.6 Compute crest orientation error and spacing residual metrics (deps: 2, 3, 5) — pending
- 4.7 Align masks, palettes, and GEOLOGIC_RULES / notebook anchors for transverse dunes (deps: 1, 4, 6) — pending
- 4.8 Add tests/test_transverse_generator.py for PSD, spacing, and continuity validation (deps: 2, 3, 5, 6, 7) — pending

### aeolian-v1:5 — Add aeolian sedimentary feature overlays and property trends [pending]
Implement overlays for cross-bedding, reactivation surfaces, inverse grading, grain rounding, surface textures, erosional events, impacts, and cementation metadata.

Subtasks:
- 5.1 Design aeolian sedimentary overlay schema and key conventions (deps: None) — pending
- 5.2 Implement aeolian_cross_bedding_masks helper with reactivation surfaces (deps: 1) — pending
- 5.3 Implement aeolian_inverse_grading_profile helper and grading metadata (deps: 1) — pending
- 5.4 Implement aeolian_grain_rounding helper and surface texture indices (deps: 1) — pending
- 5.5 Implement aeolian_surface_impacts helper for impact and erosional events (deps: 1) — pending
- 5.6 Implement aeolian_cementation helper and palette-based tinting (deps: 1) — pending
- 5.7 Compose apply_sedimentary_overlays entry point to call all helpers (deps: 2, 3, 4, 5, 6) — pending
- 5.8 Wire overlay metadata fields into masks_dict contract for downstream use (deps: 7) — pending
- 5.9 Update GEOLOGIC_RULES and aeolian notebook anchors for new overlays (deps: 2, 3, 4, 5, 6, 7, 8) — pending
- 5.10 Add tests/test_aeolian_overlays.py to validate overlay behaviors (deps: 2, 3, 4, 5, 6, 7, 8) — pending

### aeolian-v1:6 — Compose aeolian generator pipeline and masks export [pending]
Wire `generate_aeolian` to orchestrate morphology-specific builders, sedimentary overlays, palette application, and mask packaging for downstream stats/reporting.

Subtasks:
- 6.1 Design generate_aeolian API and parameter ingestion (deps: None) — pending
- 6.2 Implement Aeolian builder registry and env dispatch (deps: 1) — pending
- 6.3 Integrate base-field creation, builders, and overlays into pipeline (deps: 1, 2) — pending
- 6.4 Define sequential stage ordering and storage schema (deps: 3) — pending
- 6.5 Align masks, facies keys, and palette metadata with documentation (deps: 3, 4) — pending
- 6.6 Implement legend and palette metadata helpers for reporting (deps: 5) — pending
- 6.7 Update GEOLOGIC_RULES compose_aeolian row and documentation anchors (deps: 1, 3, 5, 6) — pending
- 6.8 Add tests and regression harness for generate_aeolian across envs (deps: 3, 4, 5, 6, 7) — pending

### aeolian-v1:7 — Implement aeolian sliders, previews, and batch exporter [pending]
Extend `interactive.py` to expose aeolian slider metadata, render sequential previews, and run batch parameter sweeps for N realizations.

Subtasks:
- 7.1 Review PRD/AGENTS and define Aeolian slider schema (deps: None) — pending
- 7.2 Implement build_sliders("aeolian") based on AeolianParams and PRD ranges (deps: 1) — pending
- 7.3 Implement aeolian preview_sequence with staged outputs (deps: 1, 2) — pending
- 7.4 Add aeolian batch-export helper for seeds and parameter sweeps (deps: 2, 3) — pending
- 7.5 Design reusable hooks for notebooks to consume aeolian previews and batches (deps: 2, 3, 4) — pending
- 7.6 Wire ipywidgets-based aeolian UI with responsive observers (deps: 2, 3, 5) — pending
- 7.7 Document aeolian sliders, preview order, and batch exporter in docs and notebooks (deps: 1, 2, 3, 4, 5, 6) — pending
- 7.8 Add tests for aeolian interactive sliders, previews, and batch export (deps: 2, 3, 4, 5, 6, 7) — pending

### aeolian-v1:8 — Extend stats engine with aeolian Phase1/Phase2 metrics [pending]
Implement Phase 1/2 metrics plus aeolian-specific metrics (orientation rose vs θ, ridge continuity, interdune connectivity, PSD residuals, property trend logging).

Subtasks:
- 8.1 Design env-aware compute_metrics API and aeolian dispatch (deps: None) — pending
- 8.2 Implement beta and anisotropy helpers for aeolian gray fields (deps: 1) — pending
- 8.3 Implement entropy and D/SFI-style fractal metrics (deps: 1) — pending
- 8.4 Implement PSD-based anisotropy and orientation metrics via FFT (deps: 1, 2) — pending
- 8.5 Implement topology and mask-based metrics for ridges and interdunes (deps: 1) — pending
- 8.6 Integrate aeolian overlays and metadata from Task 5 into metrics (deps: 1, 2, 3, 4, 5) — pending
- 8.7 Define stable aeolian metrics schema and naming for exports (deps: 1, 2, 3, 4, 5, 6) — pending
- 8.8 Integrate aeolian metrics with reporting and CSV/export pipeline (deps: 7, 6) — pending
- 8.9 Optimize aeolian metrics computation for batch and CI performance (deps: 2, 3, 4, 5, 6, 8) — pending
- 8.10 Add synthetic-pattern tests for aeolian metrics and schema stability (deps: 2, 3, 4, 5, 6, 7, 8, 9) — pending

### aeolian-v1:9 — Enhance reporting for aeolian CSV + PDF deliverables [pending]
Upgrade `reporting.py` to emit aeolian-aware CSV columns, per-style PDFs, and a master PDF containing thumbnails, legends, and property summaries.

Subtasks:
- 9.1 Review existing reporting, metrics, and artifact expectations (deps: None) — pending
- 9.2 Design Aeolian CSV schema and update TASKMASTER_TASKS_EXPORT documentation (deps: 1) — pending
- 9.3 Implement CSV writing helpers to emit Aeolian metrics with new schema (deps: 2) — pending
- 9.4 Extend build_reports signature and orchestration for Aeolian env metadata (deps: 3) — pending
- 9.5 Implement per-style Aeolian PDF templates with ReportLab (deps: 2, 3, 4) — pending
- 9.6 Integrate palette legends and cementation color keys from PALETTES.md (deps: 1, 5) — pending
- 9.7 Implement master Aeolian PDF assembly with legends and property summaries (deps: 5, 6) — pending
- 9.8 Align file naming and output directories with smoke tests and Task Master artifacts (deps: 3, 4, 5, 7) — pending
- 9.9 Add end-to-end Aeolian reporting tests and basic checksums (deps: 3, 5, 7, 8) — pending

### aeolian-v1:10 — Traceability, documentation, and QA automation for aeolian release [pending]
Update documentation/notebooks for new functions, ensure GEOLOGIC_RULES anchors align, and add QA smoke routines covering interactive + stats + reporting pipeline.

Subtasks:
- 10.1 Align GEOLOGIC_RULES anchors with Aeolian functions from Tasks 1–9 (deps: None) — pending
- 10.2 Document Aeolian workflow, sliders, and acceptance criteria in WORKFLOW, README, and PRD (deps: 1) — pending
- 10.3 Update `notebooks/aeolian.ipynb` anchors and add QA checklist per AGENTS (deps: 1, 2) — pending
- 10.4 Extend `scripts/smoke_test.py` to run Aeolian pipeline in dry-run mode (deps: 1, 3) — pending
- 10.5 Implement Aeolian metric and report threshold checks in smoke test (deps: 4) — pending
- 10.6 Integrate Aeolian docs and smoke checks into pre-commit and CI workflows (deps: 2, 3, 5) — pending
- 10.7 Write Aeolian release recap and Task Master usage in MEETING_RECAP (deps: 1, 2, 3, 4, 5, 6) — pending
- 10.8 Add `tests/test_smoke_aeolian.py` to validate Aeolian smoke pipeline (deps: 4, 5, 6, 3) — pending


## estuarine-v1

### estuarine-v1:1 — Define estuarine parameter schema & slider metadata [pending]
Introduce a strongly typed estuarine parameter schema plus slider metadata so downstream generators and UI can consume a single source of truth for ranges, defaults, and documentation links from the PRD.

Subtasks:
- 1.1 Extract estuarine parameters and ranges from PRD (deps: None) — pending
- 1.2 Define strongly typed `EstuarineParams` schema (deps: 1) — pending
- 1.3 Implement `PARAM_METADATA["estuarine"]` slider metadata (deps: 1) — pending
- 1.4 Add `clamp_estuarine_params` normalization and validation helper (deps: 2, 3) — pending
- 1.5 Integrate estuarine schema and metadata with `build_sliders` (deps: 2, 3, 4) — pending

### estuarine-v1:2 — Implement tide-dominated estuarine primitives & masks [pending]
Add tide-dominated generation helpers that synthesize ebb/flood channels, elongate tidal bars, and mudflat masks with the geometric constraints from the PRD.

Subtasks:
- 2.1 Implement `tide_channel_network` with bimodal orientations and controlled sinuosity (deps: None) — pending
- 2.2 Implement `tide_bars` for elongate tidal bar masks and length/width statistics (deps: 1) — pending
- 2.3 Implement `mudflat_mask` and integrate tide helpers into a cohesive tide primitives API (deps: 1, 2) — pending

### estuarine-v1:3 — Implement wave-dominated estuarine primitives & shoreline extraction [pending]
Create wave-dominated helpers for shoreface-parallel bars, distributary mouth bars, and shoreline curvature derived from delta-front angle φ.

Subtasks:
- 3.1 Implement `wave_shoreface_bars(params, shape)` with shoreline-aligned bar masks (deps: 1) — pending
- 3.2 Implement `mouth_bar_field(channel_entries, params)` with Gaussian fans and QC metadata (deps: 1) — pending
- 3.3 Implement `extract_shoreline(gray_base)` and integrate wave shoreline pipeline with curvature QC (deps: 1) — pending

### estuarine-v1:4 — Blend regimes inside `generate_estuarine` and emit sequential masks [pending]
Implement the public `generate_estuarine` orchestrator that mixes tide/wave primitives via the dominance slider δ, produces grayscale + mask dict, and records sequential preview stages.

Subtasks:
- 4.1 Implement tidal–wave mask blending logic in `generate_estuarine` (deps: 1, 2, 3) — pending
- 4.2 Compose ordered sequential preview rasters from blended components (deps: 1, 2, 3) — pending
- 4.3 Finalize `generate_estuarine` return signature, metadata sidecar, and exports (deps: 1, 2, 3) — pending

### estuarine-v1:5 — Wire interactive sliders & preview pipeline for estuarine v20a [pending]
Implement the interactive layer so estuarine sliders use the shared metadata and preview sequences update in real time with quick metrics.

Subtasks:
- 5.1 Extend estuarine slider metadata in `build_sliders` (deps: None) — pending
- 5.2 Implement `preview_sequence` for estuarine with quick metrics (deps: None) — pending
- 5.3 Wire estuarine sliders, debounced callbacks, and quick metrics preview (deps: None) — pending

### estuarine-v1:6 — Implement Phase 1 metrics within `stats.compute_metrics` [pending]
Extend the statistics module to compute the baseline Phase 1 metrics (β_iso, β_dir*, anisotropy ratio, two-segment parameters) for estuarine outputs so quick metrics and reporting have consistent values.

Subtasks:
- 6.1 Implement core variogram and anisotropy utilities for Phase 1 metrics (deps: None) — pending
- 6.2 Extend `stats.compute_metrics` to compute Phase 1 variogram-based metrics for `env="estuarine"` (deps: None) — pending
- 6.3 Add two-segment fit, provenance caching, and quick-metrics downsampling in `compute_metrics` (deps: None) — pending

### estuarine-v1:7 — Add Phase 2 + estuarine-specific QC metrics and acceptance flags [pending]
Augment `compute_metrics` (or helper routines) with entropy, D/SFI, PSD anisotropy, topology per facies, and the estuarine-specific acceptance checks defined in the PRD.

Subtasks:
- 7.1 Implement Phase 2 estuarine metric calculations in compute_metrics (deps: None) — pending
- 7.2 Add estuarine-specific QC metrics and acceptance flags (deps: None) — pending
- 7.3 Integrate Phase 2 metrics, QC outputs, and metadata reuse into estuarine workflow (deps: None) — pending

### estuarine-v1:8 — Extend reporting (CSV + PDFs + master summary) for estuarine metrics [pending]
Upgrade `analog_image_generator.reporting.build_reports` to emit CSV rows, per-style PDFs, and the master PDF/legend bundle that include the new estuarine-specific metrics and QC flags.

Subtasks:
- 8.1 Extend CSV schema and row construction for estuarine metrics (deps: None) — pending
- 8.2 Implement per-style estuarine PDF report generation (tide, wave, mixed) (deps: None) — pending
- 8.3 Assemble master estuarine summary PDF and integrate CLI/smoke test behavior (deps: None) — pending

### estuarine-v1:9 — Document estuarine rules, anchors, and workflow updates [pending]
Update documentation and notebook anchors so every new estuarine principle/function is traceable per AGENTS.md guidelines.

Subtasks:
- 9.1 Extend GEOLOGIC_RULES for estuarine helper functions and anchors (deps: 4, 7, 8) — pending
- 9.2 Create and align estuarine notebook anchors for principles and sliders (deps: 4, 7, 8) — pending
- 9.3 Update estuarine PRD, workflow, and reporting docs for new schema and outputs (deps: 4, 7, 8) — pending

### estuarine-v1:10 — Add automated tests & smoke coverage for estuarine pipeline [pending]
Create comprehensive pytest suites and smoke scripts that cover generator outputs, slider plumbing, metrics, and reporting to prevent regressions before CI/Task Master handoff.

Subtasks:
- 10.1 Create estuarine pytest modules for generators, metrics, and reporting (deps: None) — pending
- 10.2 Extend smoke_test.py to cover estuarine mini-pipeline (deps: None) — pending
- 10.3 Optimize estuarine tests for speed, CI wiring, and coverage tracking (deps: None) — pending


## fluvial-v1

### fluvial-v1:1 — Implement shared rasterization + RNG utilities [pending]
Build `analog_image_generator.utils` helpers needed by all generators (grids, seeded RNG, palette/mask helpers).

Subtasks:
- 1.1 Design and implement `seeded_rng` and env-specific RNG wrappers (deps: None) — pending
- 1.2 Add grid utilities: `make_field`, `normalized_coords`, and EDT helpers (deps: 1) — pending
- 1.3 Implement mask utilities: `blend_masks` and `boolean_stack_to_rgb` (deps: 2) — pending
- 1.4 Introduce centralized palette lookup aligned with `docs/PALETTES.md` (deps: 3) — pending
- 1.5 Create `tests/test_utils.py` covering RNG, grids, masks, and palettes (deps: 1, 2, 3, 4) — pending
- 1.6 Update GEOLOGIC_RULES and notebook anchors for new utils (deps: 1, 2, 3, 4, 5) — pending

### fluvial-v1:2 — Implement meandering generator sequencing [pending]
Fill `generate_fluvial` path for meandering belts with named sub-functions and masks following PRD hierarchy.

Subtasks:
- 2.1 Standardize NDArray types and shared fluvial mask structures (deps: None) — pending
- 2.2 Implement meander_centerline(H, W, n_ctrl, amp_range, drift_frac) geometry (deps: 1) — pending
- 2.3 Implement variable bankfull width logic using params and seeded RNG (deps: 1, 2) — pending
- 2.4 Rasterize centerline and width into channel/belt masks (deps: 2, 3) — pending
- 2.5 Implement levee, scroll-bar, and oxbow morphology helpers (deps: 4) — pending
- 2.6 Compose grayscale float32 field from channel, levees, scroll bars, and floodplain noise (deps: 1, 4, 5) — pending
- 2.7 Define masks dict schema and metadata (sinuosity, levee thickness, labels) (deps: 1, 4, 5, 6) — pending
- 2.8 Integrate generate_meandering into generate_fluvial dispatcher with parameter validation (deps: 2, 3, 4, 5, 6, 7) — pending
- 2.9 Create tests/test_meandering.py and smoke fixtures for coverage, oxbow frequency, and anchors (deps: 1, 2, 3, 4, 5, 6, 7, 8) — pending

### fluvial-v1:3 — Implement braided generator sequencing [pending]
Create braided belt pipeline (threads, bars, chutes, floodplain masks) under `generate_fluvial` path for `env="braided"`.

Subtasks:
- 3.1 Define braided NDArray types and channel/mask conventions (deps: None) — pending
- 3.2 Implement braided_threads(H, W, thread_count, mean_width) with PRD validation (deps: 1) — pending
- 3.3 Implement seed_bars and place_mid_channel_bars with spacing control (deps: 2) — pending
- 3.4 Implement add_chutes(...) to route cross-cutting chutes over bars (deps: 2, 3) — pending
- 3.5 Compose braided grayscale field with correct intensity ordering (deps: 2, 3, 4) — pending
- 3.6 Construct braided masks dict and per-thread metadata structure (deps: 2, 3, 4, 5) — pending
- 3.7 Implement generate_braided(params, rng) and hook into generate_fluvial dispatcher (deps: 1, 2, 3, 4, 5, 6) — pending
- 3.8 Write tests/test_braided.py for geometry, spacing, and RNG determinism (deps: 2, 3, 4, 5, 6, 7) — pending
- 3.9 Update GEOLOGIC_RULES.md and braided notebook anchors (deps: 2, 3, 4, 5, 6, 7) — pending

### fluvial-v1:4 — Implement anastomosing generator sequencing [pending]
Build stable/narrow channel generator with levees, wetlands, and crevasse fans, honoring slider table ranges.

Subtasks:
- 4.1 Design and implement `anasto_paths(H, W, branch_count)` for narrow stable branches (deps: None) — pending
- 4.2 Implement `add_levees_narrow` to generate levees around anastomosing channels (deps: 1) — pending
- 4.3 Implement `make_marsh(chan, base, quantile)` using distance/base quantiles (deps: 1) — pending
- 4.4 Implement `seed_fans(...)` to draw radial crevasse fans with controllable length (deps: 1) — pending
- 4.5 Compose anastomosing environment masks with palette-aligned semantics (deps: 1, 2, 3, 4) — pending
- 4.6 Compose grayscale anastomosing fields with layered contrasts (deps: 2, 3, 4, 5) — pending
- 4.7 Implement `generate_anastomosing(params, rng)` and integrate into `generate_fluvial` (deps: 1, 2, 3, 4, 5, 6) — pending
- 4.8 Add `tests/test_anastomosing.py` covering masks, fractions, and determinism (deps: 1, 2, 3, 4, 5, 6, 7) — pending
- 4.9 Update GEOLOGIC_RULES.md and notebooks with anastomosing anchors and documentation (deps: 1, 2, 3, 4, 5, 6, 7, 8) — pending

### fluvial-v1:5 — Add sedimentary structures & petrology overlays [pending]
Layer fining-upward textures, cross-bedding, ripple bands, channel-fill sandstone masks, and mineralogical metadata across all fluvial generators.

Subtasks:
- 5.1 Design sedimentary overlay API and mask/metadata schema (deps: None) — pending
- 5.2 Implement channel_fill_sandstone with erosional bases and infill textures (deps: 1) — pending
- 5.3 Implement cross-bedding, ripple textures, and lateral accretion overlays (deps: 1, 2) — pending
- 5.4 Add fining-upward and overbank mudstone masks with grayscale modulation (deps: 1, 2, 3) — pending
- 5.5 Define petrology metadata schema and attach mineralogy, cement, and mud clast flags (deps: 1, 2, 3, 4) — pending
- 5.6 Integrate sedimentary overlays into meandering, braided, and anastomosing pipelines (deps: 2, 3, 4, 5) — pending
- 5.7 Update PALETTES and GEOLOGIC_RULES with new facies and overlay principles (deps: 1, 2, 3, 4, 5, 6) — pending
- 5.8 Extend unit tests for fluvial generators and shared sedimentary overlays (deps: 2, 3, 4, 5, 6) — pending
- 5.9 Add sedimentary overlay smoke tests to scripts/smoke_test.py (deps: 6, 8) — pending
- 5.10 Document approximations, limitations, and notebook anchors for sedimentary overlays (deps: 6, 7, 8, 9) — pending

### fluvial-v1:6 — Implement stacked channel package builder [pending]
Create `stacked_channels.py` that composes multi-package stratigraphy with relief controls and boundary masks for stats/reporting.

Subtasks:
- 6.1 Design stacked channel package spec and metadata structures (deps: None) — pending
- 6.2 Define generator dispatch map for fluvial styles in stacked_channels (deps: 1) — pending
- 6.3 Implement sequence_packages to build 3D gray stack and per-package masks (deps: 1, 2) — pending
- 6.4 Design and implement apply_relief functions for vertical stacking (deps: 1, 3) — pending
- 6.5 Implement cut_erosional_surface and integrate with stacking loop (deps: 3, 4) — pending
- 6.6 Export boundary masks and package_id_map for stats and reporting (deps: 3, 4, 5) — pending
- 6.7 Implement build_stacked_fluvial API and single vs stacked mode toggle (deps: 2, 3, 4, 5, 6) — pending
- 6.8 Wire stacked mode into generate_fluvial and parameter plumbing (deps: 7) — pending
- 6.9 Create unit tests for stacked_channels behaviors and invariants (deps: 3, 4, 5, 6, 7, 8) — pending
- 6.10 Extend smoke tests and documentation for stacked workflows and anchors (deps: 7, 8, 9) — pending

### fluvial-v1:7 — Build ipywidgets sliders, previews, and param batch (Interactive v20a) [pending]
Implement `interactive.py` to expose slider schemas per env, render sequential previews, show live β/D/H, and save lightweight param batches.

Subtasks:
- 7.1 Design slider schema and implement build_sliders(env) in interactive.py (deps: None) — pending
- 7.2 Implement ipywidgets-based UI factory using slider configs (deps: 1) — pending
- 7.3 Implement preview_sequence(env, params, seeds) with generator/stacked integration (deps: 1, 2) — pending
- 7.4 Add lightweight β/D/H metrics adapter for previews (deps: 3) — pending
- 7.5 Implement run_param_batch(env, slider_configs, seeds, output_dir) for PNG and metadata export (deps: 1, 3, 4) — pending
- 7.6 Validate slider ranges/defaults against PRD and research documents and attach citation metadata (deps: 1) — pending
- 7.7 Add tests for interactive slider data, preview plumbing, and batch execution (deps: 1, 2, 3, 4, 5, 6) — pending
- 7.8 Update v20a interactive notebook anchors and GEOLOGIC_RULES documentation for interactive.py (deps: 1, 2, 3, 4, 5, 6, 7) — pending

### fluvial-v1:8 — Implement full Phase 1 & 2 metrics pipeline [pending]
Fill `stats.py` compute_metrics covering variograms, entropy, fractal dimension, PSD anisotropy, topology, and property metadata hooks.

Subtasks:
- 8.1 Design metrics result schema and QA flag structure (deps: None) — pending
- 8.2 Implement compute_variogram(gray, directions) and lag binning helpers (deps: 1) — pending
- 8.3 Implement power-law and two-segment variogram slope fitting helpers (deps: 2) — pending
- 8.4 Implement entropy(gray) and fractal_dimension(beta) calculations (deps: 2, 3) — pending
- 8.5 Implement psd_anisotropy(gray) using FFT-based PSD analysis (deps: 1, 2) — pending
- 8.6 Implement topology_metrics(mask) for area, compactness, connectivity, and SFI (deps: 1) — pending
- 8.7 Implement compute_metrics(gray, masks, env, metadata=None) orchestration (deps: 1, 2, 3, 4, 5, 6) — pending
- 8.8 Add lightweight β/D/H adapter for interactive preview mode (deps: 3, 4, 7) — pending
- 8.9 Create tests/test_stats.py with synthetic fields and regression fixtures (deps: 2, 3, 4, 5, 6, 7, 8) — pending
- 8.10 Integrate compute_metrics into smoke tests and geologic documentation (deps: 7, 8, 9) — pending

### fluvial-v1:9 — Implement reporting pipeline (CSV, per-env PDFs, master PDF) [pending]
Complete `reporting.py` to output metrics CSV, mosaics, per-environment PDF pages with histograms + tables, and master PDF with overview + appended reports.

Subtasks:
- 9.1 Define metrics_rows schema and CSV column mapping (deps: None) — pending
- 9.2 Implement deterministic CSV export in build_reports using pandas (deps: 1) — pending
- 9.3 Implement mosaic generation helpers for grayscale, facies, legends, and stacked overlays (deps: 1) — pending
- 9.4 Implement per-environment PDF page generation with mosaics, histograms, and summary tables (deps: 2, 3) — pending
- 9.5 Implement master PDF assembly with global summary cover and appended env PDFs (deps: 4) — pending
- 9.6 Integrate QA flagging logic for metric deviations and sed/petrology compliance (deps: 1, 2, 3, 4) — pending
- 9.7 Design deterministic output directory structure and naming conventions for reporting artifacts (deps: 2, 3, 4, 5, 6) — pending
- 9.8 Create tests/test_reporting.py for CSV, PDFs, mosaics, and QA flags (deps: 2, 3, 4, 5, 6, 7) — pending
- 9.9 Extend smoke tests and documentation to cover reporting pipeline usage and CI integration (deps: 2, 3, 4, 5, 6, 7, 8) — pending

### fluvial-v1:10 — Ensure traceability, automation, and Task Master gating [pending]
Wire documentation, notebooks, and CI/smoke automation so every principle maps to code and Task Master enforces non-regression.

Subtasks:
- 10.1 Inventory new generator/stacked/stats/reporting functions for GEOLOGIC_RULES mapping (deps: None) — pending
- 10.2 Update docs/GEOLOGIC_RULES.md with rows and code/notebook anchors for all new functions (deps: 1) — pending
- 10.3 Align notebook markdown anchors in v20 notebooks with GEOLOGIC_RULES conventions (deps: 2) — pending
- 10.4 Implement doc-anchor validation script for GEOLOGIC_RULES and notebooks (deps: 2, 3) — pending
- 10.5 Extend scripts/smoke_test.py with mini end-to-end run and anchor/report checks (deps: 4) — pending
- 10.6 Integrate doc-anchor validation and smoke test into pytest or a dedicated CLI (deps: 4, 5) — pending
- 10.7 Update GitHub Actions workflows to enforce unit, doc-anchor, and smoke gates (deps: 6) — pending
- 10.8 Refresh README and workflow docs for stacked/interactive/stats/reporting and Task Master usage (deps: 7, 10, 11) — pending
- 10.9 Add programmatic non-regression checklist cells to v20 notebooks (deps: 3) — pending
- 10.10 Configure Task Master tags, tasks, and milestones for gating (deps: 6) — pending
- 10.11 Verify Task Master MCP connectivity on WSL and document WSL-specific adjustments (deps: 10) — pending
- 10.12 Perform final traceability alignment across GEOLOGIC_RULES, notebooks, code, CI, and Task Master (deps: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) — pending
