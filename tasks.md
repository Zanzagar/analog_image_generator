# Task Backlog

> Exported from `.taskmaster/tasks/tasks.json` on 2026-08-31 (task-master is retired; `.taskmaster/` is kept as an inert archive).
> Pending/unstarted tasks only — completed tasks were not exported.
> Mark items done by annotating inline or moving them to a tasks-archive.md.

---

## Tag: fluvial-v1 (advanced controls/QA — 3 of 13 tasks still pending)

## 11. Add curvature- and discharge-linked fluvial controls [high]

Expose advanced controls: curvature-coupled channel width & scroll wavelength; bank erodibility factor; discharge/slope-linked thread count and width; ensure UI sliders and generators respect bounds.

**Subtasks:**
- [ ] 1. Define and expose new fluvial control sliders
- [ ] 2. Couple meandering width and scroll wavelength to curvature
- [ ] 3. Link braided threads to discharge and slope controls
- [ ] 4. Plumb new controls through preview, stacked builder, and batch paths
- [ ] 5. Refresh documentation, anchors, and QC coverage

## 12. Add bar amalgamation & facies thickness variance controls [high]

Implement bar amalgamation probability, per-facies thickness variance (channel_fill vs overbank), and overbank enhancements (crevasse-splay lenses, clay-clast scars). Wire sliders, generator logic, and UI defaults.

## 13. Strengthen QA thresholds and reporting hooks [medium]

Define environment-specific acceptance bands for β/H/PSD/topology; surface QA flags in UI; add reporting notebook hooks/cells that show report generation/links directly from interactive runs.

**Subtasks:**
- [ ] 1. Audit current QA logic, metrics, and anchors
- [ ] 2. Define env-specific QA acceptance bands and flag derivation
- [ ] 3. Expose QA flags and bands in interactive preview UI
- [ ] 4. Propagate QA bands into reporting outputs
- [ ] 5. Add notebook hooks for QA-aware reporting workflows

---

## Tag: aeolian-v1 (unstarted environment)

## 1. Implement Aeolian parameter schema and base field scaffolding [medium]

Create a reusable parameter dataclass + helper utilities that normalize all aeolian slider inputs, seed RNG deterministically, and prepare base grids shared by all dune styles.

Define `AeolianParams` (env, theta_deg, q, H, lambda_px, f_interdune, defect_rate, seed, invert_gradation, cement_type, event_schedule) in `geologic_generators.py` or a new `aeolian_params.py`, enforcing PRD ranges and citing research PDFs in docstrings. Add helper functions for rotating coordinate grids, sampling base noise, and gating sequential steps. Wire `docs/GEOLOGIC_RULES.md` and `notebooks/aeolian.ipynb#anchor-aeolian-params` to the new class.
Pseudo-code:
```
@dataclass
class AeolianParams:
    env: Literal["barchan","linear","transverse"]
    theta_deg: float = clamp(theta, 0, 180)
    ...
    def rng(self) -> np.random.Generator:
        return np.random.default_rng(self.seed)

def make_base_field(params):
    grid = gaussian_noise(params)
    return rotate(grid, params.theta_deg)
```
Update `docs/WORKFLOW.md` to mention Aeolian slider defaults and link associated notebook anchors.

**Subtasks:**
- [ ] 1. Draft AeolianParams schema and module layout
- [ ] 2. Implement AeolianParams dataclass with PRD-backed validation and normalization
- [ ] 3. Provide deterministic RNG helper bound to AeolianParams
- [ ] 4. Implement base-field utilities for aeolian grids, rotation, and base noise
- [ ] 5. Wire AeolianParams and helpers into GEOLOGIC_RULES and aeolian notebook anchors
- [ ] 6. Add pytest coverage for AeolianParams validation, RNG, and base-field utilities

**Test strategy:** Add `tests/test_aeolian_params.py` with pytest cases that (a) clamp each slider to PRD ranges, (b) verify seeds yield identical grids, and (c) ensure invalid env names raise `ValueError`. Use hypothesis-style parametrization across ranges.

## 2. Build Barchan dune generator with crest/slipface/interdune masks [medium]

Implement horned barchan synthesis driven by wind azimuth, including mask outputs for crest, slipface, stoss, and interdune plus migration metadata.

**Depends on:** 1

Add helpers (`aeolian_make_crests`, `aeolian_add_slipfaces`, `aeolian_interdune`) that construct horn seeds, advect dunes downwind, and carve interdune lows via distance transforms using params from Task 1. Compose masks dict with grayscale shading and palette keys per `docs/PALETTES.md`. Capture horn curvature vs. θ and record interdune fraction for metrics.
Pseudo-code:
```
def build_barchan_field(params):
    centerline = bezier(seed_points(params.seed))
    horns = dilate(centerline, horn_width(theta))
    slipface = project_downwind(horns, params.theta_deg)
    interdune = threshold(base_field, params.f_interdune)
    return {
        "gray": blend_layers(...),
        "masks": {"crest": crest_mask, "slipface": slipface, ...}
    }
```
Annotate GEOLOGIC_RULES rows for crest/slipface/interdune anchors once implemented.

**Subtasks:**
- [ ] 1. Design barchan builder API and AeolianParams integration
- [ ] 2. Implement aeolian_make_crests to seed horned barchan crests
- [ ] 3. Implement horn growth and downwind migration operations
- [ ] 4. Implement aeolian_add_slipfaces to project lee-side slipfaces
- [ ] 5. Implement aeolian_interdune to carve interdune corridors
- [ ] 6. Compose grayscale shading and masks dict aligned with palettes
- [ ] 7. Capture horn curvature and interdune fraction as generator metadata
- [ ] 8. Integrate barchan builder with generate_aeolian entry points
- [ ] 9. Add tests/test_barchan_generator.py for orientation and connectivity

**Test strategy:** Create `tests/test_barchan_generator.py` to assert (a) crest orientation aligns with θ within 15°, (b) ridge continuity index falls in 0.3–0.5 band, and (c) interdune connectivity stays between 0.2–0.6. Use seeded params and measure via numpy morphology helpers.

## 3. Implement Linear/Seif dune generator with ridge continuity controls [medium]

Generate linear dune fields that honor mean wind direction, secondary wind kinks, and target ridge continuity metrics.

**Depends on:** 1

Add `aeolian_linear_ridges` to extrude sinusoidal ridges along θ_wind, apply secondary wind perturbations, and cut interdune corridors. Compute ridge continuity metric (largest crest component / total crest pixels) and expose it for stats. Respect defect rate ρ by randomly removing segments. Update masks to include ridge/stoss/slipface states, storing continuity metadata.
Pseudo-code:
```
def build_linear_field(params):
    spines = seed_parallel_lines(theta=params.theta_deg, spacing=params.lambda_px)
    spines = add_secondary_kinks(spines, secondary_theta=params.theta_deg+30*q)
    crest_mask = enforce_continuity(spines, rho=params.defect_rate)
    metrics = {"ridge_continuity": largest_component(crest_mask)}
    return crest_mask, metrics
```
Document anchor `aeolian_ridge_continuity` and note default ranges from linear-dune PDF.

**Subtasks:**
- [ ] 1. Define aeolian_linear_ridges builder API and scaffolding
- [ ] 2. Implement parallel spine seeding aligned with wind direction and spacing
- [ ] 3. Add secondary wind kink perturbations based on research PDF
- [ ] 4. Construct crest mask and aeolian_ridge_continuity metric via components
- [ ] 5. Implement interdune corridor carving and stoss/slipface mask differentiation
- [ ] 6. Apply defect_rate-driven crest breaking while preserving interpretable continuity
- [ ] 7. Finalize aeolian_linear_ridges outputs compatible with stats.compute_metrics
- [ ] 8. Document and wire aeolian_ridge_continuity anchors in GEOLOGIC_RULES and notebook
- [ ] 9. Create linear dune generator tests for continuity, orientation, and defect effects

**Test strategy:** Unit tests should (a) compute ridge continuity ≥0.7 for default q, (b) drop into 0.5–0.6 when ρ≈0.25, and (c) confirm PSD orientation difference ≤10°. Use mocked params to compare measured orientation via FFT vs. θ.

## 4. Implement Transverse dune generator with λ=f(H) spacing [medium]

Produce transverse dune fields whose crest spacing scales linearly with dune height and remain orthogonal to wind direction.

**Depends on:** 1

Create `aeolian_transverse_ridges` that builds crest-parallel ridges via repeated morphological bands aligned perpendicular to θ. Derive spacing λ = k*H (fit from PRD citation) with guard rails for the slider range. Include defect rate adaptation for crest bifurcations and ensure mask labeling for crest/stoss/slipface/interdune. Track crest orientation error vs. θ and spacing residual for stats.
Pseudo-code:
```
def build_transverse_field(params):
    spacing = params.lambda_px or alpha*params.H
    crest_mask = draw_parallel_ridges(spacing, orientation=theta+90)
    slipface = downwind_projection(crest_mask)
    return crest_mask, slipface, build_gray(...)
```
Update GEOLOGIC_RULES anchors referencing `aeolian_make_crests` usage in transverse context.

**Subtasks:**
- [ ] 1. Define build_transverse_field / aeolian_transverse_ridges API and stubs
- [ ] 2. Implement λ = k * H spacing logic with slider guards and overrides
- [ ] 3. Generate crest-parallel ridges orthogonal to wind direction
- [ ] 4. Derive slipface, stoss, and interdune masks from crest geometry and wind
- [ ] 5. Incorporate defect_rate to generate crest bifurcations and continuity metrics
- [ ] 6. Compute crest orientation error and spacing residual metrics
- [ ] 7. Align masks, palettes, and GEOLOGIC_RULES / notebook anchors for transverse dunes
- [ ] 8. Add tests/test_transverse_generator.py for PSD, spacing, and continuity validation

**Test strategy:** Add pytest cases verifying (a) |θ_PSD − θ_wind| ≤ 15° median across seeds, (b) measured spacing falls within ±10% of λ input, and (c) ridge continuity sits between 0.4–0.6 as specified.

## 5. Add aeolian sedimentary feature overlays and property trends [medium]

Implement overlays for cross-bedding, reactivation surfaces, inverse grading, grain rounding, surface textures, erosional events, impacts, and cementation metadata.

**Depends on:** 2, 3, 4

Create helpers listed in `docs/GEOLOGIC_RULES.md` rows 57–65 (`aeolian_cross_bedding_masks`, `aeolian_inverse_grading_profile`, `aeolian_grain_rounding`, `aeolian_surface_impacts`, `aeolian_cementation`). Integrate them with mask outputs from Tasks 2–4, ensuring overlays add channels for dip azimuth histograms, gradation direction, roundedness index, surface roughness, event counts, and cement type tags for reporting. Link to palette entries to tint cemented regions red-orange.
Pseudo-code:
```
def apply_sedimentary_overlays(masks, params):
    cross_sets = synthesize_cross_beds(masks["slipface"], dip=params.theta_deg)
    rounding = compute_rounding(params.q, transport_distance(masks))
    impacts = sprinkle_impacts(masks["crest"], intensity=params.defect_rate)
    cement = aeolian_cementation(masks, params.cement_type)
    return {**masks, **cross_sets, "rounding": rounding, ...}
```
Update notebook anchors and PRD references to reflect implemented controls.

**Subtasks:**
- [ ] 1. Design aeolian sedimentary overlay schema and key conventions
- [ ] 2. Implement aeolian_cross_bedding_masks helper with reactivation surfaces
- [ ] 3. Implement aeolian_inverse_grading_profile helper and grading metadata
- [ ] 4. Implement aeolian_grain_rounding helper and surface texture indices
- [ ] 5. Implement aeolian_surface_impacts helper for impact and erosional events
- [ ] 6. Implement aeolian_cementation helper and palette-based tinting
- [ ] 7. Compose apply_sedimentary_overlays entry point to call all helpers
- [ ] 8. Wire overlay metadata fields into masks_dict contract for downstream use
- [ ] 9. Update GEOLOGIC_RULES and aeolian notebook anchors for new overlays
- [ ] 10. Add tests/test_aeolian_overlays.py to validate overlay behaviors

**Test strategy:** Expand pytest suite to verify (a) at least one cross-bed set >20° dip exists per realization, (b) roundedness index stays within 0.6–0.9 for default params, (c) gradation metadata flips sign when invert toggle changes, and (d) event counts increase when simulating wind shifts.

## 6. Compose aeolian generator pipeline and masks export [medium]

Wire `generate_aeolian` to orchestrate morphology-specific builders, sedimentary overlays, palette application, and mask packaging for downstream stats/reporting.

**Depends on:** 2, 3, 4, 5

Implement dispatcher that selects Barchan/Linear/Transverse builders, applies Task 5 overlays, blends grayscale shading, and returns `(gray, masks_dict)` conforming to existing API. Ensure sequential layering order (base → ridges → slipfaces → interdunes → final gray → facies RGB) is emitted for preview and batch export. Write palette legend metadata aligned with `docs/PALETTES.md` and ensure mask keys align with reporting schema. Update docstrings with citations and keep GEOLOGIC_RULES compose row in sync.
Pseudo-code:
```
def generate_aeolian(params_dict):
    params = AeolianParams.from_dict(params_dict)
    base = make_base_field(params)
    builder = BUILDERS[params.env]
    gray, masks = builder(base, params)
    masks = apply_sedimentary_overlays(masks, params)
    legend = build_palette_metadata(masks)
    return gray, {**masks, "legend": legend}
```
Add CLI hook or utility to drive new generator for smoke tests.

**Subtasks:**
- [ ] 1. Design generate_aeolian API and parameter ingestion
- [ ] 2. Implement Aeolian builder registry and env dispatch
- [ ] 3. Integrate base-field creation, builders, and overlays into pipeline
- [ ] 4. Define sequential stage ordering and storage schema
- [ ] 5. Align masks, facies keys, and palette metadata with documentation
- [ ] 6. Implement legend and palette metadata helpers for reporting
- [ ] 7. Update GEOLOGIC_RULES compose_aeolian row and documentation anchors
- [ ] 8. Add tests and regression harness for generate_aeolian across envs

**Test strategy:** Create `tests/test_generate_aeolian.py` to run each env with fixed seed, asserting mask keys, grayscale ranges, sequential snapshot counts, and validating that overlays exist. Include regression fixtures (npz) for CI tolerance within ±1e-6.

## 7. Implement aeolian sliders, previews, and batch exporter [medium]

Extend `interactive.py` to expose aeolian slider metadata, render sequential previews, and run batch parameter sweeps for N realizations.

**Depends on:** 1, 6

Populate `build_sliders("aeolian")` returning slider definitions using PRD ranges/defaults and cite sources in docstrings. For `preview_sequence`, call `generate_aeolian` for each intermediate stage (base/ridges/slipfaces/interdunes/gray/facies), capturing matplotlib frames or ipywidgets outputs. Add a batch-export helper to iterate seeds/param combos, storing metrics snapshots in `outputs/aeolian/<timestamp>/`. Ensure UI reacts immediately when sliders change (ipywidgets observe) and integrate into notebooks.
Pseudo-code:
```
def build_sliders(env):
    if env == "aeolian":
        return {
            "theta_deg": {"min":0,"max":180,"step":5,"default":60},
            ...
        }

def preview_sequence(env, params, seeds):
    for seed in seeds:
        frames = compute_stages(generate_aeolian({...}))
        show(frames)
```
Document sequential preview order per PRD and ensure `docs/WORKFLOW.md` references new batch exporter toggle.

**Subtasks:**
- [ ] 1. Review PRD/AGENTS and define Aeolian slider schema
- [ ] 2. Implement build_sliders("aeolian") based on AeolianParams and PRD ranges
- [ ] 3. Implement aeolian preview_sequence with staged outputs
- [ ] 4. Add aeolian batch-export helper for seeds and parameter sweeps
- [ ] 5. Design reusable hooks for notebooks to consume aeolian previews and batches
- [ ] 6. Wire ipywidgets-based aeolian UI with responsive observers
- [ ] 7. Document aeolian sliders, preview order, and batch exporter in docs and notebooks
- [ ] 8. Add tests for aeolian interactive sliders, previews, and batch export

**Test strategy:** Write widget/unit tests using `ipywidgets` test utilities verifying slider defaults match PRD table, preview call order matches stage list, and batch exporter writes expected number of realizations with distinct seeds. Smoke-test via `scripts/smoke_test.py` extension for aeolian env.

## 8. Extend stats engine with aeolian Phase1/Phase2 metrics [medium]

Implement Phase 1/2 metrics plus aeolian-specific metrics (orientation rose vs θ, ridge continuity, interdune connectivity, PSD residuals, property trend logging).

**Depends on:** 6

In `stats.py`, expand `compute_metrics` to detect env == "aeolian" and compute β_iso, β_dir_{0,45,90,135}, anisotropy ratio, two-segment fits, entropy, D/SFI, PSD anisotropy/aspect/θ, topology counts per mask using numpy/scipy. Incorporate Task 5 metadata for cross-bedding histograms, roundedness, texture variance, inversions, event counts, and crater frequencies. Return dict ready for CSV/export. Provide helper functions for PSD orientation residual vs θ_wind.
Pseudo-code:
```
def compute_metrics(gray, masks, env):
    if env == "aeolian":
        beta = calc_beta(gray)
        psd = fft2(gray)
        ridge = masks["ridge"]
        metrics = {
            "beta_iso": beta.iso,
            "ridge_continuity": ridge_continuity(ridge),
            ...
        }
        return metrics
    ...
```
Update docstrings referencing research PDFs and acceptance thresholds.

**Subtasks:**
- [ ] 1. Design env-aware compute_metrics API and aeolian dispatch
- [ ] 2. Implement beta and anisotropy helpers for aeolian gray fields
- [ ] 3. Implement entropy and D/SFI-style fractal metrics
- [ ] 4. Implement PSD-based anisotropy and orientation metrics via FFT
- [ ] 5. Implement topology and mask-based metrics for ridges and interdunes
- [ ] 6. Integrate aeolian overlays and metadata from Task 5 into metrics
- [ ] 7. Define stable aeolian metrics schema and naming for exports
- [ ] 8. Integrate aeolian metrics with reporting and CSV/export pipeline
- [ ] 9. Optimize aeolian metrics computation for batch and CI performance
- [ ] 10. Add synthetic-pattern tests for aeolian metrics and schema stability

**Test strategy:** Add `tests/test_aeolian_metrics.py` generating small synthetic masks to verify (a) PSD orientation residual within ±10° for aligned inputs, (b) ridge continuity matches Task 3 output, (c) interdune connectivity calculation equals 1−χ/A, and (d) cross-bedding hist hist counts include >0 entries. Use fixtures to assert metrics schema stability.

## 9. Enhance reporting for aeolian CSV + PDF deliverables [medium]

Upgrade `reporting.py` to emit aeolian-aware CSV columns, per-style PDFs, and a master PDF containing thumbnails, legends, and property summaries.

**Depends on:** 8

Modify `build_reports` to accept env metadata, add Aeolian metrics columns (ridge continuity, PSD residual, rounding index, gradation sign, cement type, event counts). Use ReportLab to create templates for barchan/linear/transverse PDFs with slider summaries, sequential preview frames, and acceptance-band annotations. Generate a master PDF combining all runs plus legends from docs/PALETTES.md, ensuring cement tags appear in legends. Save CSV schema reference in `docs/TASKMASTER_TASKS_EXPORT.md`.
Pseudo-code:
```
def build_reports(metrics_rows, output_dir):
    csv_path = write_csv(metrics_rows, aeolian_schema)
    for style in {"barchan","linear","transverse"}:
        style_rows = filter_rows(metrics_rows, style)
        pdf = build_style_pdf(style_rows)
    build_master_pdf(metrics_rows)
```
Ensure outputs integrate with Task Master artifacts per acceptance criteria.

**Subtasks:**
- [ ] 1. Review existing reporting, metrics, and artifact expectations
- [ ] 2. Design Aeolian CSV schema and update TASKMASTER_TASKS_EXPORT documentation
- [ ] 3. Implement CSV writing helpers to emit Aeolian metrics with new schema
- [ ] 4. Extend build_reports signature and orchestration for Aeolian env metadata
- [ ] 5. Implement per-style Aeolian PDF templates with ReportLab
- [ ] 6. Integrate palette legends and cementation color keys from PALETTES.md
- [ ] 7. Implement master Aeolian PDF assembly with legends and property summaries
- [ ] 8. Align file naming and output directories with smoke tests and Task Master artifacts
- [ ] 9. Add end-to-end Aeolian reporting tests and basic checksums

**Test strategy:** Add `tests/test_reporting_aeolian.py` to (a) write sample metrics and assert CSV headers match schema, (b) verify per-style PDFs exist and contain expected text via PyPDF2, and (c) confirm master PDF includes thumbnails count equal to realizations. Include golden-file checksum checks for CI.

## 10. Traceability, documentation, and QA automation for aeolian release [medium]

Update documentation/notebooks for new functions, ensure GEOLOGIC_RULES anchors align, and add QA smoke routines covering interactive + stats + reporting pipeline.

**Depends on:** 2, 3, 4, 5, 6, 7, 8, 9

Refresh `docs/GEOLOGIC_RULES.md`, `docs/WORKFLOW.md`, PRD appendix, and `notebooks/aeolian.ipynb` anchors for every function added in Tasks 1–9. Create QA checklist in notebooks (per AGENTS instructions) confirming acceptance metrics hits. Extend `scripts/smoke_test.py` to run `generate_aeolian` for each env, compute metrics, and write reports, flagging threshold violations. Capture recap in `docs/MEETING_RECAP_2025-11-12.md` and add Task Master updates. Ensure `README` highlights Aeolian support and prerequisites.

**Subtasks:**
- [ ] 1. Align GEOLOGIC_RULES anchors with Aeolian functions from Tasks 1–9
- [ ] 2. Document Aeolian workflow, sliders, and acceptance criteria in WORKFLOW, README, and PRD
- [ ] 3. Update `notebooks/aeolian.ipynb` anchors and add QA checklist per AGENTS
- [ ] 4. Extend `scripts/smoke_test.py` to run Aeolian pipeline in dry-run mode
- [ ] 5. Implement Aeolian metric and report threshold checks in smoke test
- [ ] 6. Integrate Aeolian docs and smoke checks into pre-commit and CI workflows
- [ ] 7. Write Aeolian release recap and Task Master usage in MEETING_RECAP
- [ ] 8. Add `tests/test_smoke_aeolian.py` to validate Aeolian smoke pipeline

**Test strategy:** Add `tests/test_smoke_aeolian.py` invoking the smoke script in dry-run mode, asserting it produces metrics + PDF placeholders and that checklists tick through. Validate docs via markdown lint (pre-commit) and ensure notebooks store anchors referencing updated code names.

---

## Tag: estuarine-v1 (unstarted environment)

## 1. Define estuarine parameter schema & slider metadata [medium]

Introduce a strongly typed estuarine parameter schema plus slider metadata so downstream generators and UI can consume a single source of truth for ranges, defaults, and documentation links from the PRD.

- Create `EstuarineParams` (e.g., dataclass or TypedDict) under `analog_image_generator.geologic_generators` capturing tidal prism, wave energy index, channel/bar wavelengths (px), mud fraction, delta-front angle φ, dominance δ, interlayer type enum, and RNG seed.
- Keep values normalized to slider ranges from `.taskmaster/docs/prd_estuarine.txt`; compute derived values such as km using the 5 m/px scale only inside helper properties.
- Expose metadata (min, max, step, default, tooltip text citing the correct PDF section) via `analog_image_generator.interactive.build_sliders` so UI consumers read from `PARAM_METADATA["estuarine"]` instead of hardcoding.
- Provide helper `clamp_estuarine_params(raw: Mapping[str, Any]) -> EstuarineParams` that enforces ranges and converts enums/angles.
- Pseudocode:
```
@dataclass
class EstuarineParams:
    tidal_prism: float = 0.5
    ...

PARAM_METADATA = {
  "estuarine": {
      "tidal_prism": {"min": 0.1, "max": 1.0, "step": 0.05, "default": 0.5,
                        "source": "depositional_system_estuarian_tide-dominated.pdf §3"},
      ...
  }
}
```
- Update `docs/GEOLOGIC_RULES.md` later to point to the new helper once implemented (tracked in a later task).

**Subtasks:**
- [ ] 1. Extract estuarine parameters and ranges from PRD
- [ ] 2. Define strongly typed `EstuarineParams` schema
- [ ] 3. Implement `PARAM_METADATA["estuarine"]` slider metadata
- [ ] 4. Add `clamp_estuarine_params` normalization and validation helper
- [ ] 5. Integrate estuarine schema and metadata with `build_sliders`

**Test strategy:** - Add unit tests that instantiate `EstuarineParams` with defaults and boundary values, asserting clamping honors PRD limits and enum normalization (pytest target `tests/test_params.py`).
- Validate `build_sliders("estuarine")` returns metadata for every slider with expected min/max/default and citation text.
- Include a regression test that feeds invalid values (e.g., δ>1) through `clamp_estuarine_params` and asserts the corrected value stays within range.

## 2. Implement tide-dominated estuarine primitives & masks [medium]

Add tide-dominated generation helpers that synthesize ebb/flood channels, elongate tidal bars, and mudflat masks with the geometric constraints from the PRD.

**Depends on:** 1

- Under `analog_image_generator.geologic_generators`, add functions like `tide_channel_network(params: EstuarineParams, shape: tuple[int, int]) -> NDArray` that create two forked centerlines rotated ±θ relative to shoreline to achieve bimodal peaks separated by ≥25°; use filtered noise + cubic splines and enforce channel sinuosity S within [1.0, 1.8].
- Implement `tide_bars(channel_mask, params) -> NDArray` that dilates along-flow segments to create elongate tidal bars with length:width ratios 3–15× and λ_b spacing between 20–150 px; modulate amplitude using tidal prism.
- Add `mudflat_mask(channel_mask, params)` that thresholds distance transforms + mud fraction m to carve intertidal flats.
- Ensure each helper returns boolean masks plus summary stats (length/width per bar) for later QC metrics.
- Pseudocode sketch:
```
def tide_channel_network(params, shape):
    dirs = [+φ_shift, -φ_shift]
    channels = []
    for theta in dirs:
        curve = spline_seed(seed=params.seed, sinuosity=params.channel_sinuosity)
        curve = rotate(curve, theta)
        channels.append(draw_tube(curve, width=base_width(params)))
    chan_mask = union(channels)
    return chan_mask, measure_orientations(channels)
```
- Use numpy/scipy interpolation and `scipy.ndimage.morphology` to dilate/distance operations; keep RNG seeded.

**Subtasks:**
- [ ] 1. Implement `tide_channel_network` with bimodal orientations and controlled sinuosity
- [ ] 2. Implement `tide_bars` for elongate tidal bar masks and length/width statistics
- [ ] 3. Implement `mudflat_mask` and integrate tide helpers into a cohesive tide primitives API

**Test strategy:** - Write targeted tests (e.g., `tests/test_estuarine_tide.py`) that call the helper with fixed seeds and assert: (a) measured orientation histogram has two peaks with |Δθ| ≥ 25°, (b) computed sinuosity falls within the slider range, (c) bar length/width ratios stay within 3–15×, (d) mudflat mask area fraction matches mud fraction ±5%.
- Add quick metric assertions that orientation stats captured in helper metadata feed into later QC calculations (serialized dict fields).

## 3. Implement wave-dominated estuarine primitives & shoreline extraction [medium]

Create wave-dominated helpers for shoreface-parallel bars, distributary mouth bars, and shoreline curvature derived from delta-front angle φ.

**Depends on:** 1

- Add `wave_shoreface_bars(params, shape)` that generates parallel bars aligned with shoreline azimuth derived from φ, using band-pass filtered noise in the alongshore direction to keep wavelengths λ_b=20–150 px and mouth-bar aspect ratios 2.0–4.0.
- Build `mouth_bar_field(channel_entries, params)` that seeds fans at channel termini with Gaussian envelopes whose major/minor axes satisfy the PRD ranges; mix in wave energy index to control taper.
- Implement `extract_shoreline(gray_base) -> (polyline, curvature_stats)` using marching squares on shoreline mask plus smoothing; compute curvature std dev and ensure δ≈1 cases fall below 0.25 rad/pixel by adjusting smoothing strength.
- Return masks for bars, shoreline, and metadata (curvature std, aspect ratios) for QC.
- Pseudocode snippet:
```
def wave_shoreline(params, shape):
    theta = np.deg2rad(params.delta_front_angle)
    shoreline = build_base_curve(theta)
    bars = stack_parallel_offset(shoreline, spacing=params.bar_wavelength)
    return bars_mask, shoreline_poly
```
- Keep RNG deterministic via `params.seed` offsets so mixed-energy blending remains reproducible.

**Subtasks:**
- [ ] 1. Implement `wave_shoreface_bars(params, shape)` with shoreline-aligned bar masks
- [ ] 2. Implement `mouth_bar_field(channel_entries, params)` with Gaussian fans and QC metadata
- [ ] 3. Implement `extract_shoreline(gray_base)` and integrate wave shoreline pipeline with curvature QC

**Test strategy:** - Unit tests verifying (a) mouth-bar aspect ratio distributions fall within 2.0–4.0 when wave energy index >0.7, (b) shoreline curvature std dev <0.25 for mixed-energy presets, (c) δ→1 scenarios produce PSD aspect ratios >2.0 when evaluated later (record metadata for Task 7).
- Compare extracted shoreline polylines against analytic arcs to ensure curvature computation is accurate within ±0.02 rad/pixel.
- Validate mask coverage percentages sum to expected area budgets (channels + bars + flats + shoreline edge).

## 4. Blend regimes inside `generate_estuarine` and emit sequential masks [medium]

Implement the public `generate_estuarine` orchestrator that mixes tide/wave primitives via the dominance slider δ, produces grayscale + mask dict, and records sequential preview stages.

**Depends on:** 1, 2, 3

- Inside `analog_image_generator.geologic_generators.generate_estuarine`, call the tide and wave helpers with shared params, then linearly or sigmoid-blend masks using δ (0 = fully tide, 1 = fully wave) while ensuring mud fraction scaling and shoreline curvature targets.
- Compose intermediate rasters: base topography, combined channels, bars, flats, shoreline, grayscale, and facies RGB (using `docs/PALETTES.md`), storing them in an ordered list for previews.
- Normalize outputs to `Array` alias (later NDArray) and ensure `masks_dict` exposes keys `channel`, `bar`, `mudflat`, `shoreline`, `dominance_tide`, `dominance_wave`, plus stats bundles for downstream metrics.
- Include quick metrics (length/width histograms, orientation peaks) in a sidecar metadata object returned with masks to avoid recomputation.
- Pseudocode skeleton:
```
def generate_estuarine(params_dict):
    params = clamp_estuarine_params(params_dict)
    tide_masks = tide_channel_network(...)
    wave_masks = wave_shoreface_bars(...)
    blended = blend_masks(tide_masks, wave_masks, params.dominance)
    sequential = [base_gray, blended['channel'], ..., facies_rgb]
    return final_gray, {**blended, "sequence": sequential}
```
- Update `__all__` / module exports if needed so notebooks can import the new helpers.

**Subtasks:**
- [ ] 1. Implement tidal–wave mask blending logic in `generate_estuarine`
- [ ] 2. Compose ordered sequential preview rasters from blended components
- [ ] 3. Finalize `generate_estuarine` return signature, metadata sidecar, and exports

**Test strategy:** - Integration test creating canonical parameter sets (δ=0, 0.5, 1) and asserting returned tuple contains a grayscale array with expected shape plus mask keys; verify sequential list contains the prescribed stages in order.
- Snapshot-test histograms/metrics stored in metadata to detect regressions (pytest + numpy testing utilities).
- Run smoke test via `scripts/smoke_test.py` to ensure generator executes within budgeted time (<1s for 512×512) and respects RNG reproducibility by comparing checksums for identical seeds.

## 5. Wire interactive sliders & preview pipeline for estuarine v20a [medium]

Implement the interactive layer so estuarine sliders use the shared metadata and preview sequences update in real time with quick metrics.

**Depends on:** 1, 4

- Extend `analog_image_generator.interactive.build_sliders` to return slider descriptors for `env="estuarine"`, building UI metadata (label, range, default, tooltip) directly from `PARAM_METADATA` to prevent drift; include interlayer type dropdown and RNG seed control.
- Implement `preview_sequence(env, params, seeds)` to repeatedly call `generate_estuarine`, capturing the sequential frames plus quick metrics (β_iso, anisotropy ratio) and wiring them into whichever widget stack (ipywidgets or CLI) consumes them.
- Provide hooks for quick metrics panel updates by computing a lightweight subset of `stats.compute_metrics` (Phase 1 fields) synchronously and caching them with the preview.
- Ensure slider callbacks throttle updates (e.g., via debouncing) so adjusting φ or δ doesn’t block UI.
- Pseudocode snippet:
```
def preview_sequence("estuarine", params, seeds):
    seq = []
    for seed in seeds:
        gray, masks = generate_estuarine({**params, "seed": seed})
        quick = compute_metrics(gray, masks, env="estuarine", fields=["beta_iso", ...])
        seq.append({"seed": seed, "frames": masks["sequence"], "metrics": quick})
    return seq
```
- Document slider order and stage descriptions for notebooks/demo scripts.

**Subtasks:**
- [ ] 1. Extend estuarine slider metadata in `build_sliders`
- [ ] 2. Implement `preview_sequence` for estuarine with quick metrics
- [ ] 3. Wire estuarine sliders, debounced callbacks, and quick metrics preview

**Test strategy:** - Widget-level unit tests (can use ipywidgets `interaction` stubs) verifying slider config structure and that callbacks feed sanitized params into the generator.
- Functional test running `preview_sequence("estuarine", default_params, seeds=[42])` asserts the sequential frames list matches the expected stage order and quick metrics dictionary contains beta values.
- Manual smoke test in notebook (recorded in QA checklist) verifying slider adjustments propagate to preview within <150 ms and quick metrics refresh accordingly.

## 6. Implement Phase 1 metrics within `stats.compute_metrics` [medium]

Extend the statistics module to compute the baseline Phase 1 metrics (β_iso, β_dir*, anisotropy ratio, two-segment parameters) for estuarine outputs so quick metrics and reporting have consistent values.

**Depends on:** 4

- In `analog_image_generator.stats.compute_metrics`, add FFT/variogram utilities that take grayscale/masks and compute isotropic variograms `β_iso`, directional variograms at 0/45/90/135°, anisotropy ratio, and two-line fit parameters `(β₁, β₂, h₀)`.
- Accept an `env` argument and branch for `"estuarine"` to include channel/bar masks in weighting.
- Cache metrics inside the returned dict along with provenance (window size, lag step) for reproducibility.
- Provide helper functions (e.g., `_variogram(field, theta_deg)`) to keep compute_metrics readable.
- Pseudocode outline:
```
def compute_metrics(gray, masks, env):
    metrics = {}
    beta_iso = variogram(gray)
    beta_dirs = {theta: variogram(gray, theta) for theta in [0,45,90,135]}
    metrics.update({...})
    metrics.update(two_segment_fit(beta_iso))
    return metrics
```
- Ensure metrics can run on downsampled frames for speed when called from quick metrics mode (Task 5).

**Subtasks:**
- [ ] 1. Implement core variogram and anisotropy utilities for Phase 1 metrics
- [ ] 2. Extend `stats.compute_metrics` to compute Phase 1 variogram-based metrics for `env="estuarine"`
- [ ] 3. Add two-segment fit, provenance caching, and quick-metrics downsampling in `compute_metrics`

**Test strategy:** - Unit tests using analytic fields (e.g., linear gradients, sinusoidal textures) where expected variogram/anisotropy values are known, verifying results within tolerance.
- Regression tests to ensure compute time stays within limits (pytest mark for performance) and that repeated calls with identical inputs yield identical metrics.
- Validate quick-metric subset agrees with the full compute by comparing truncated and full runs in tests.

## 7. Add Phase 2 + estuarine-specific QC metrics and acceptance flags [medium]

Augment `compute_metrics` (or helper routines) with entropy, D/SFI, PSD anisotropy, topology per facies, and the estuarine-specific acceptance checks defined in the PRD.

**Depends on:** 6

- Implement PSD-based anisotropy (aspect ratio and orientation θ) via 2D FFT of the bar/channel masks; ensure δ→0 cases yield aspect 1.3–1.8 and δ→1 exceed 2.0, recording deviations as QC flags.
- Compute Shannon entropy H, D/SFI, and per-facies topology stats (connected-component counts, Euler number) leveraging `scipy.ndimage` labelers.
- Add specialized metrics: ebb/flood orientation separation (difference between tide helper peaks), mouth-bar aspect ratio distribution (should fall within target ranges), shoreline curvature std dev, interlayer thickness histograms compared with required proportions, and LU_T / LU_F thickness + porosity proxies (derive using mask thickness fields + parameterized thickness distributions respecting Jiwei et al. 2025 values).
- Emit QC booleans and messages (e.g., `qc_psd_aspect_pass`, `qc_mouth_bar_ratio_pass`, `qc_interlayer_distribution_pass`) into the metrics dict so reporting can highlight rerun requirements.
- Pseudocode:
```
metrics["ebb_flood_delta_theta"] = abs(theta_ebb - theta_flood)
metrics["qc_ebb_flood"] = metrics["ebb_flood_delta_theta"] >= 25
...
```
- Ensure calculations reuse metadata captured in Tasks 2–4 to avoid recomputation.

**Subtasks:**
- [ ] 1. Implement Phase 2 estuarine metric calculations in compute_metrics
- [ ] 2. Add estuarine-specific QC metrics and acceptance flags
- [ ] 3. Integrate Phase 2 metrics, QC outputs, and metadata reuse into estuarine workflow

**Test strategy:** - Synthetic tests constructing known masks (e.g., ellipses with specified aspect ratios) verifying QC flags toggle at the documented thresholds.
- Add randomized property-based tests to ensure mouth-bar histograms remain within expected bounds for δ extremes.
- Write regression tests comparing computed PSD aspect vs dominance slider for δ in {0, 0.5, 1} to guarantee monotonic behavior.

## 8. Extend reporting (CSV + PDFs + master summary) for estuarine metrics [medium]

Upgrade `analog_image_generator.reporting.build_reports` to emit CSV rows, per-style PDFs, and the master PDF/legend bundle that include the new estuarine-specific metrics and QC flags.

**Depends on:** 7

- Expand CSV schema to cover Phase 1/2 metrics plus estuarine-specific values (orientation split, mouth-bar ratios, shoreline curvature std, PSD aspect, interlayer stats) with stable column ordering; document schema in README/docs.
- Generate per-style PDF reports (tide, wave, mixed) using ReportLab: include slider inputs, representative thumbnails from sequential frames, QC flag badges, and legends referencing `docs/PALETTES.md`.
- Assemble a master PDF that summarises all runs per environment with tables and aggregated charts (e.g., histogram overlays) plus a cover page referencing sources.
- Ensure PDF generation respects WSL pathing and writes to `dist/reports/<timestamp>`; support CLI invocation by returning output paths.
- Update `scripts/smoke_test.py` to call `build_reports` with sample metrics_rows produced by generator/stats to verify the pipeline end-to-end.
- Pseudocode:
```
def build_reports(metrics_rows, output_dir):
    csv_path = output_dir / "estuarine_metrics.csv"
    pd.DataFrame(metrics_rows).to_csv(...)
    for style, rows in groupby_tag(metrics_rows):
        pdf = ReportLabCanvas(...)
        ... draw legend, thumbnails, QC table ...
    merge_pdfs(per_style, master_path)
```

**Subtasks:**
- [ ] 1. Extend CSV schema and row construction for estuarine metrics
- [ ] 2. Implement per-style estuarine PDF report generation (tide, wave, mixed)
- [ ] 3. Assemble master estuarine summary PDF and integrate CLI/smoke test behavior

**Test strategy:** - Unit tests verifying CSV headers match the documented schema and QC flags serialize as booleans/strings.
- Regression tests that generate sample PDFs then inspect metadata (page count, presence of legend text) using PyPDF2; compare file hashes to golden fixtures when feasible.
- Smoke test ensuring `build_reports` handles empty metrics list gracefully and raises informative errors when thumbnails missing.

## 9. Document estuarine rules, anchors, and workflow updates [medium]

Update documentation and notebook anchors so every new estuarine principle/function is traceable per AGENTS.md guidelines.

**Depends on:** 4, 7, 8

- Extend `docs/GEOLOGIC_RULES.md` with entries for the new helper functions (`tide_channel_network`, `wave_shoreface_bars`, `generate_estuarine`, etc.) linking to notebook anchors such as `notebooks/estuarine.ipynb#anchor-estuarine-tide-channels`.
- Create or update `notebooks/estuarine.ipynb` markdown cells to include anchors describing each implemented principle and slider, referencing Jiwei et al. 2025 figures.
- Update `.taskmaster/docs/prd_estuarine.txt` and README/WORKFLOW sections if parameter naming or acceptance logic changed during implementation, keeping the tables in sync.
- Document the new CSV schema and PDF outputs in `docs/WORKFLOW.md` or a dedicated reporting section to help QA/REP roles.
- Summarize changes in `docs/MEETING_RECAP_*.md` or changelog entries referencing the acceptance criteria being satisfied.

**Subtasks:**
- [ ] 1. Extend GEOLOGIC_RULES for estuarine helper functions and anchors
- [ ] 2. Create and align estuarine notebook anchors for principles and sliders
- [ ] 3. Update estuarine PRD, workflow, and reporting docs for new schema and outputs

**Test strategy:** - Manual doc review checklist ensuring every code anchor appears both in GEOLOGIC_RULES and the notebook anchor column (per AGENTS instructions).
- Automated Markdown tests (e.g., custom pytest that parses GEOLOGIC_RULES) verifying anchors reference valid notebook IDs and function names exist in code.
- Spell-check/markdown-lint passes via pre-commit to catch link or formatting regressions.

## 10. Add automated tests & smoke coverage for estuarine pipeline [medium]

Create comprehensive pytest suites and smoke scripts that cover generator outputs, slider plumbing, metrics, and reporting to prevent regressions before CI/Task Master handoff.

**Depends on:** 4, 5, 7, 8

- Add new test modules (`tests/test_estuarine_generator.py`, `tests/test_estuarine_metrics.py`, `tests/test_reporting_estuarine.py`) exercising default, tide-heavy, and wave-heavy scenarios; assert RNG reproducibility, mask coverage, QC flags, and reporting artifacts.
- Expand `scripts/smoke_test.py` to run a mini pipeline: generate two realizations, compute metrics, and build CSV/PDF outputs, printing summary statuses for QA.
- Ensure tests run quickly by downsampling arrays where possible and mocking heavy PDF generation in unit tests (while leaving one integration test for real file I/O using tmp_path).
- Wire the new tests into CI (pytest collection picks up automatically) and document how to run them locally (`pytest tests/test_estuarine_*`).
- Collect coverage data for generator/interactive/stats/reporting to ensure critical branches are exercised; update QA checklist accordingly.

**Subtasks:**
- [ ] 1. Create estuarine pytest modules for generators, metrics, and reporting
- [ ] 2. Extend smoke_test.py to cover estuarine mini-pipeline
- [ ] 3. Optimize estuarine tests for speed, CI wiring, and coverage tracking

**Test strategy:** - Pytest suites verifying deterministic outputs, slider validation, QC flag boundaries, reporting file creation, and smoke pipeline success.
- Use hypothesis/property tests for parameter clamping edge cases.
- Add CI badge/update if coverage thresholds met; ensure `pre-commit run --all-files` stays clean after new notebooks/docstrings are included.

---

## Tag: fluvial-realism-v1 (superseded planning pass, all tasks pending)

## 1. Implement Geometric Helper Functions for Physics-Based Generation [high]

Create a new module or extend utils.py with geometric computation helpers required by physics-based fluvial generators: local curvature calculation, circular arc generation, wavelength/sinuosity measurement, and neck distance detection.

Create `src/analog_image_generator/geometry_helpers.py` with the following functions:

1. `compute_local_curvature(centerline: NDArray) -> NDArray`
   - Use finite differences: κ = (x'y'' - y'x'') / (x'² + y'²)^(3/2)
   - Apply Gaussian smoothing (σ=3-5) before differentiation to reduce noise
   - Return signed curvature array same length as centerline

2. `generate_circular_arc(center: tuple, radius: float, arc_angle: float, start_angle: float, n_points: int) -> NDArray`
   - Generate points along a circular arc
   - Return shape (n_points, 2) with (x, y) coordinates

3. `compute_arc_angle(wavelength: float, radius: float) -> float`
   - From geometry: arc_angle ≈ 2 * arcsin(wavelength / (4 * radius))
   - Clamp to valid range [0, π]

4. `measure_wavelength(centerline: NDArray) -> float`
   - Detect zero-crossings of curvature
   - Wavelength = 2× mean distance between successive same-sign extrema

5. `measure_sinuosity(centerline: NDArray, total_length: int) -> float`
   - S = path_length / straight_line_distance
   - path_length from cumulative Euclidean distances

6. `measure_radius_of_curvature(centerline: NDArray) -> NDArray`
   - R_c = 1 / |κ| where κ is curvature
   - Return R_c at bend apexes (local curvature maxima)

7. `detect_neck_cutoff_candidates(centerline: NDArray, channel_width: float, search_range: tuple) -> list[tuple[int, int]]`
   - Find pairs (x1, x2) where |y(x1) - y(x2)| < channel_width
   - Constrain x2 - x1 to be within 3-20× channel_width

All functions should operate on numpy arrays and be fully vectorized where possible.

**Subtasks:**
- [ ] 1. Implement Curvature Computation with Gaussian Smoothing and Finite Differences
- [ ] 2. Implement Circular Arc Generation and Arc Angle Calculation
- [ ] 3. Implement Wavelength and Sinuosity Measurement Functions
- [ ] 4. Implement Neck Cutoff Detection Algorithm

**Test strategy:** Unit tests in `tests/test_geometry_helpers.py`:
1. Test `compute_local_curvature` with known curves (circle → constant κ, straight line → κ=0)
2. Test `generate_circular_arc` produces points equidistant from center
3. Test `measure_wavelength` with synthetic sinusoid of known period
4. Test `measure_sinuosity` with known path (S=1 for straight line, S=π/2 for semicircle)
5. Test `detect_neck_cutoff_candidates` with synthetic centerline containing deliberate neck

## 2. Rewrite Meander Centerline with Physics-Based Arc Geometry [high]

Replace the current sinusoidal `meander_centerline()` with `meander_centerline_physics()` that generates proper circular arc-based meander bends with wavelength λ = 10-14×W and radius of curvature R_c = 2-3×W.

**Depends on:** 1

Replace `meander_centerline()` in `geologic_generators.py` with:

```python
def meander_centerline_physics(
    height: int,
    width: int,
    channel_width: float,
    rng: np.random.Generator,
    wavelength_factor: tuple[float, float] = (10.0, 14.0),
    curvature_factor: tuple[float, float] = (2.0, 3.0),
) -> Array:
    """Generate physics-based meander centerline (anchor-fluvial-meander-centerline-physics).
    
    Constraints from research:
    - G1: λ = k × W where k ∈ [10, 14]
    - G2: R_c = m × W where m ∈ [2, 3]
    - G4: Sinuosity S ∈ [1.5, 3.0]
    - G5: Bends are circular arcs, not sinusoids
    """
    wavelength = rng.uniform(*wavelength_factor) * channel_width
    base_radius = rng.uniform(*curvature_factor) * channel_width
    
    n_bends = int(width / (wavelength / 2))
    centerline = []
    current_pos = np.array([0.0, height / 2.0])
    current_direction = 0.0  # radians, 0 = downstream (+x)
    
    for i in range(n_bends):
        # Vary radius slightly per bend for naturalism
        R = base_radius * rng.uniform(0.85, 1.15)
        arc_angle = compute_arc_angle(wavelength, R)
        sign = 1 if i % 2 == 0 else -1  # Alternate left/right
        
        # Generate circular arc points
        arc_center = current_pos + sign * R * np.array([
            -np.sin(current_direction),
            np.cos(current_direction)
        ])
        arc_points = generate_circular_arc(
            arc_center, R, arc_angle * sign,
            current_direction - sign * np.pi/2,
            n_points=max(10, int(arc_angle * R / 2))
        )
        centerline.extend(arc_points)
        
        # Update for next bend
        current_pos = arc_points[-1]
        current_direction += sign * arc_angle
    
    # Resample to width points and clip to bounds
    centerline = np.array(centerline)
    x_samples = np.arange(width)
    y_interp = np.interp(x_samples, centerline[:, 0], centerline[:, 1])
    y_interp = np.clip(y_interp, height * 0.1, height * 0.9)
    
    return y_interp.astype(np.float32)
```

Update `generate_meandering()` to call `meander_centerline_physics()` instead of `meander_centerline()`.

Add validation at generation time:
```python
measured_wavelength = measure_wavelength(centerline)
measured_sinuosity = measure_sinuosity(centerline, width)
assert 10 * channel_width <= measured_wavelength <= 14 * channel_width
assert 1.5 <= measured_sinuosity <= 3.0
```

**Subtasks:**
- [ ] 1. Implement circular arc generation algorithm with downstream direction tracking
- [ ] 2. Implement wavelength constraint enforcement (λ = 10-14×W)
- [ ] 3. Implement radius of curvature constraint (R_c = 2-3×W)
- [ ] 4. Add sinuosity validation (S ∈ [1.5, 3.0]) with measurement
- [ ] 5. Integrate with generate_meandering() and add visual comparison tests

**Test strategy:** 1. Generate 100 centerlines with different seeds and channel widths
2. Verify measured wavelength is within 10-14× channel_width for >95% of samples
3. Verify measured R_c at bend apexes is within 2-3× channel_width for >90% of bends
4. Verify sinuosity is within [1.5, 3.0] for all samples
5. Visual inspection: centerlines should show clear rounded bends, not pointed sinusoids
6. Regression test: ensure API compatibility (same return type as before)

## 3. Implement Point Bar Generation (New Feature) [high]

Create `add_point_bars()` function to generate point bar deposits exclusively on the inner bank of meander bends, using curvature-based detection. This is currently missing from the implementation entirely.

**Depends on:** 1, 2

Add new function to `geologic_generators.py`:

```python
def add_point_bars(
    centerline: Array,
    channel_mask: Array,
    channel_width: float,
    rng: np.random.Generator,
    extent_factor: tuple[float, float] = (1.5, 2.0),
) -> Array:
    """Create point bar deposits on inner bank of bends (anchor-fluvial-point-bars).
    
    Constraints from research:
    - P1: Point bars form ONLY on inner bank of meander bends
    - P2: Extent = 1.5-2× channel width from inner bank
    - Outer bank = cutbank (erosion, no deposition)
    """
    height, width = channel_mask.shape
    point_bar_mask = np.zeros((height, width), dtype=np.float32)
    
    # Compute curvature to identify bends and their direction
    curvature = compute_local_curvature(centerline)
    curvature_threshold = 0.01 / channel_width  # Minimum bend curvature
    
    for x in range(width):
        if abs(curvature[x]) < curvature_threshold:
            continue  # Straight section - no point bar
        
        # Inner side is OPPOSITE to curvature direction
        # Positive curvature = bending up (y increasing) = inner bank is down
        inner_side = -np.sign(curvature[x])
        
        # Point bar extent scales with curvature magnitude
        curvature_normalized = min(1.0, abs(curvature[x]) * channel_width * 2)
        bar_extent = rng.uniform(*extent_factor) * channel_width * (0.7 + 0.3 * curvature_normalized)
        
        y_center = centerline[x]
        for y in range(height):
            offset = (y - y_center) * inner_side
            # Only deposit on inner side (offset > 0)
            if 0 < offset < bar_extent:
                # Intensity decreases away from channel
                intensity = 1.0 - (offset / bar_extent) ** 0.5
                # Modulate by curvature (stronger bars in tighter bends)
                intensity *= curvature_normalized
                point_bar_mask[y, x] = max(point_bar_mask[y, x], intensity)
    
    # Exclude channel itself
    point_bar_mask = point_bar_mask * (channel_mask < 0.3)
    return np.clip(point_bar_mask, 0.0, 1.0).astype(np.float32)
```

Update `generate_meandering()` to:
1. Call `add_point_bars()` after channel generation
2. Add 'pointbar' to masks dictionary
3. Include point bars in grayscale composition
4. Update `compose_meandering()` weights

Update `PALETTES` in utils.py to ensure 'pointbar' facies has a distinct color (already exists: '#d98943').

**Subtasks:**
- [ ] 1. Implement curvature-based inner bank detection
- [ ] 2. Calculate point bar extent with curvature-modulated intensity
- [ ] 3. Generate point bar mask excluding channel overlap
- [ ] 4. Integrate point bars into generate_meandering() pipeline

**Test strategy:** 1. Generate meandering rivers with varying channel widths and seeds
2. Verify point bar mask is non-zero ONLY where curvature is non-zero
3. Verify point bar material is ONLY on inner bends (side opposite to curvature direction)
4. Verify no point bar pixels overlap with channel mask
5. Verify point bar extent is approximately 1.5-2× channel width
6. Visual inspection: point bars should appear on inside of meander bends only

## 4. Rewrite Scroll Bars for Point Bar Regions Only [high]

Replace the current `add_scroll_bars()` with `add_scroll_bars_physics()` that confines scroll bar patterns exclusively to point bar regions with arcuate patterns following bend curvature.

**Depends on:** 1, 3

Replace `add_scroll_bars()` in `geologic_generators.py`:

```python
def add_scroll_bars_physics(
    centerline: Array,
    point_bar_mask: Array,
    channel_width: float,
    rng: np.random.Generator,
    spacing_factor: tuple[float, float] = (0.05, 0.15),
) -> Array:
    """Create scroll bar ridges within point bars (anchor-fluvial-scroll-bars-physics).
    
    Constraints from research:
    - P3: Scroll bars are arcuate ridges marking successive point bar growth
    - Concentric arcs following bend shape
    - Confined ONLY to point bar regions
    """
    height, width = point_bar_mask.shape
    scroll_mask = np.zeros((height, width), dtype=np.float32)
    
    # Only process where point bars exist
    if point_bar_mask.max() < 0.1:
        return scroll_mask
    
    curvature = compute_local_curvature(centerline)
    
    # Scroll spacing scales with channel width
    scroll_spacing = rng.uniform(*spacing_factor) * channel_width
    
    # Distance from channel edge (within point bar)
    from . import utils
    channel_edge = point_bar_mask > 0.5
    dist_from_edge = utils.distance_to_mask(channel_edge)
    
    # Create arcuate bands that follow curvature
    # The key insight: scroll bars are PARALLEL to the channel, not concentric circles
    for x in range(width):
        if point_bar_mask[:, x].max() < 0.1:
            continue
        
        # Phase offset based on local curvature creates arcuate pattern
        curvature_phase = np.cumsum(np.abs(curvature[:x+1])) if x > 0 else 0
        phase_offset = curvature_phase * scroll_spacing * 0.1
        
        for y in range(height):
            if point_bar_mask[y, x] < 0.1:
                continue
            
            dist = dist_from_edge[y, x]
            scroll_phase = ((dist + phase_offset) / scroll_spacing) % 1.0
            scroll_intensity = 0.5 * (np.cos(2 * np.pi * scroll_phase) + 1.0)
            
            # Modulate by point bar intensity
            scroll_mask[y, x] = scroll_intensity * point_bar_mask[y, x]
    
    return np.clip(scroll_mask, 0.0, 1.0).astype(np.float32)
```

Key changes from original:
1. Takes `point_bar_mask` as input instead of `channel_mask`
2. Scroll bars ONLY appear within point bar regions
3. Pattern follows curvature for arcuate appearance
4. No scroll bars on outer bends or floodplain

Update `generate_meandering()` to pass point_bar_mask to this function.

**Subtasks:**
- [ ] 1. Modify add_scroll_bars to accept point_bar_mask input
- [ ] 2. Implement arcuate curvature-following pattern generation
- [ ] 3. Apply point bar intensity modulation and update compose_meandering weights

**Test strategy:** 1. Verify scroll_mask is zero everywhere point_bar_mask is zero
2. Verify scroll pattern intensity modulated by point bar mask
3. Generate images with different curvatures and verify scroll pattern follows bend shape
4. Visual inspection: scroll bars should appear as arcuate ridges within point bars only
5. Regression test: ensure scroll_bar key still present in masks dictionary

## 5. Rewrite Oxbow Generation with Neck Cutoff Criterion [high]

Replace `add_oxbow()` with `add_oxbow_physics()` that uses deterministic neck cutoff detection (neck_distance < channel_width) and preserves meander loop shapes instead of random circles.

**Depends on:** 1, 2

Replace `add_oxbow()` in `geologic_generators.py`:

```python
def add_oxbow_physics(
    centerline: Array,
    shape: tuple[int, int],
    channel_width: float,
    rng: np.random.Generator,
    fill_width_factor: tuple[float, float] = (0.3, 0.5),
) -> tuple[Array, Array]:
    """Create oxbow lakes at neck cutoff locations (anchor-fluvial-oxbow-physics).
    
    Constraints from research:
    - O1: Neck cutoff when neck_distance < channel_width (DETERMINISTIC)
    - O2: Oxbow shape = abandoned meander loop (NOT circles)
    - O3: Location determined by geometry meeting cutoff criterion
    """
    height, width = shape
    oxbow_mask = np.zeros((height, width), dtype=np.float32)
    cutoff_centerline = centerline.copy()
    
    # Find all potential neck cutoffs
    cutoff_candidates = detect_neck_cutoff_candidates(
        centerline, 
        channel_width,
        search_range=(int(3 * channel_width), int(20 * channel_width))
    )
    
    processed_regions = []  # Track to avoid overlapping cutoffs
    
    for x1, x2 in cutoff_candidates:
        # Skip if overlaps with already processed cutoff
        if any(x1 < end and x2 > start for start, end in processed_regions):
            continue
        
        y1, y2 = centerline[x1], centerline[x2]
        neck_distance = abs(y1 - y2)
        
        # O1: DETERMINISTIC cutoff criterion
        if neck_distance >= channel_width:
            continue
        
        # Create oxbow from abandoned meander loop shape
        # Trace the original centerline from x1 to x2
        oxbow_fill_width = channel_width * rng.uniform(*fill_width_factor)
        
        for x in range(x1, x2):
            y_center = centerline[x]
            half_width = oxbow_fill_width
            y_min = int(max(0, y_center - half_width))
            y_max = int(min(height, y_center + half_width))
            
            # Gradual fill-in effect (oxbows silt up from ends)
            dist_from_ends = min(x - x1, x2 - x) / max(1, (x2 - x1) / 2)
            fill_intensity = 0.3 + 0.7 * min(1.0, dist_from_ends)
            
            oxbow_mask[y_min:y_max, x] = np.maximum(
                oxbow_mask[y_min:y_max, x],
                fill_intensity
            )
        
        # Update centerline to take cutoff path (straight line from x1 to x2)
        cutoff_centerline[x1:x2] = np.linspace(y1, y2, x2 - x1)
        processed_regions.append((x1, x2))
    
    return oxbow_mask.astype(np.float32), cutoff_centerline
```

Key changes from original:
1. Uses `detect_neck_cutoff_candidates()` for deterministic detection
2. Cutoff criterion is `neck_distance < channel_width` (not random probability)
3. Oxbow shape traces the abandoned meander loop
4. Returns both oxbow mask AND updated centerline (for subsequent generation)
5. Includes silting-up effect (fill intensity varies)

Update `generate_meandering()` to:
1. Call `add_oxbow_physics()` after centerline generation
2. Use returned `cutoff_centerline` for active channel generation
3. Original centerline sections become oxbows

**Subtasks:**
- [ ] 1. Implement neck cutoff candidate detection function
- [ ] 2. Implement deterministic cutoff criterion with overlap handling
- [ ] 3. Generate oxbow shape from abandoned meander loop with silting effect
- [ ] 4. Return updated centerline and integrate with generate_meandering()

**Test strategy:** 1. Generate centerlines with deliberate tight bends (neck_distance < channel_width)
2. Verify oxbows appear ONLY at locations meeting cutoff criterion
3. Verify oxbow shapes follow the original meander loop (not circles)
4. Verify returned cutoff_centerline takes the shorter path
5. Verify no oxbows appear where neck_distance >= channel_width
6. Visual inspection: oxbows should be crescent/arc shapes matching abandoned bends

## 6. Implement Exponential Levee Decay Profile [medium]

Replace `add_levees()` with `add_levees_exponential()` that uses the physics formula h(x) = h₀ × exp(-x/L_d) with decay length 5-15× channel width and extent limited to 3-5× channel width.

Replace `add_levees()` in `geologic_generators.py`:

```python
def add_levees_exponential(
    channel_mask: Array,
    channel_width: float,
    rng: np.random.Generator,
    h0: float = 1.0,
    decay_factor: tuple[float, float] = (5.0, 15.0),
    extent_factor: tuple[float, float] = (3.0, 5.0),
) -> Array:
    """Create levees with exponential decay profile (anchor-fluvial-levees-exponential).
    
    Constraints from research:
    - L1: h_levee(x) = h0 × exp(-x / L_d)
    - L1: L_d = 5-15× channel width for meandering
    - L2: Extent limited to 3-5× channel width
    """
    from . import utils
    
    # Sample decay length and max extent
    decay_length = rng.uniform(*decay_factor) * channel_width
    max_extent = rng.uniform(*extent_factor) * channel_width
    
    # Distance from channel edge
    dist = utils.distance_to_mask(channel_mask >= 0.5)
    
    # L1: Exponential decay formula
    levee = h0 * np.exp(-dist / decay_length)
    
    # Levees are ADJACENT to channel, not inside it
    levee = levee * (channel_mask < 0.3)
    
    # L2: Limit extent
    levee = levee * (dist < max_extent)
    
    # Smooth transition at edges
    edge_transition = np.clip((max_extent - dist) / (0.1 * max_extent), 0, 1)
    levee = levee * edge_transition
    
    return np.clip(levee, 0.0, 1.0).astype(np.float32)
```

Key changes from original:
1. Uses exponential decay instead of Gaussian blur
2. Decay length scales with channel width (5-15×)
3. Extent limited to 3-5× channel width
4. Formula matches research: h(x) = h₀ × exp(-x/L_d)
5. Takes channel_width as parameter for proper scaling

Update `generate_meandering()` to pass channel_width to levee function.

Note: `add_levees_narrow()` for anastomosing already uses exponential decay correctly.

**Subtasks:**
- [ ] 1. Replace Gaussian blur with exponential decay formula h(x) = h₀ × exp(-x/L_d)
- [ ] 2. Add extent limiting to 3-5× channel_width with smooth edge transition

**Test strategy:** 1. Generate levee profiles and measure actual decay rate
2. Verify decay follows exponential curve (plot log(h) vs distance should be linear)
3. Verify decay length is within 5-15× channel_width
4. Verify no levee pixels beyond 5× channel_width from channel
5. Verify levee mask is zero inside channel (channel_mask > 0.5)
6. Compare visual output with original - should be smoother, more realistic gradient

## 7. Implement Curvature-Driven Channel Width Variation [medium]

Replace `meander_variable_channel()` with `meander_variable_channel_curvature()` that makes channels wider in bends and narrower in straights with 15-30% variation.

**Depends on:** 1, 2

Replace `meander_variable_channel()` in `geologic_generators.py`:

```python
def meander_variable_channel_curvature(
    centerline: Array,
    shape: tuple[int, int],
    base_width: float,
    rng: np.random.Generator,
    variation_range: tuple[float, float] = (0.15, 0.30),
) -> Array:
    """Create channel mask with curvature-driven width variation (anchor-fluvial-variable-width-curvature).
    
    Constraints from research:
    - C1: Channel WIDER in bends, NARROWER in straights
    - C1: Width variation ±15-30% of mean width
    """
    height, width = shape
    
    # Compute curvature magnitude
    curvature = compute_local_curvature(centerline)
    curvature_magnitude = np.abs(curvature)
    
    # Normalize curvature to [0, 1]
    max_curvature = curvature_magnitude.max() + 1e-6
    curvature_normalized = curvature_magnitude / max_curvature
    
    # Sample variation scale within allowed range
    variation_scale = rng.uniform(*variation_range)
    
    # Width INCREASES with curvature magnitude
    # In bends (high curvature): wider channel
    # In straights (low curvature): narrower channel
    width_variation = variation_scale * base_width * curvature_normalized
    
    # Base width is the MINIMUM (at straights)
    # Add variation in bends
    width_profile = base_width + width_variation
    
    # Add small random perturbation for naturalism
    noise = rng.normal(0.0, base_width * 0.03, size=width)
    width_profile = np.clip(width_profile + noise, base_width * 0.8, base_width * 1.5)
    
    # Create mask
    rows = np.arange(height, dtype=np.float32)[:, None]
    center = centerline[None, :]
    half_width = (width_profile / 2.0).astype(np.float32)[None, :]
    
    # Smooth distance-based mask for anti-aliasing
    distance = np.abs(rows - center)
    mask = np.clip(1.0 - (distance - half_width) / 2.0, 0.0, 1.0)
    mask = (distance <= half_width).astype(np.float32) + mask * (distance > half_width) * (distance < half_width + 2)
    
    return np.clip(mask, 0.0, 1.0).astype(np.float32)
```

Key changes from original:
1. Width is driven by LOCAL CURVATURE, not arbitrary interpolation
2. Channel is wider where curvature is higher (bends)
3. Channel is narrower where curvature is lower (straights)
4. Variation constrained to 15-30% of mean width
5. Uses computed curvature from helper functions

Update `generate_meandering()` to call this function.

**Subtasks:**
- [ ] 1. Compute Local Curvature and Normalize to [0, 1] Range
- [ ] 2. Calculate Width Profile with Curvature-Driven ±15-30% Variation
- [ ] 3. Create Anti-Aliased Channel Mask with Smooth Distance-Based Edges

**Test strategy:** 1. Generate channels with varying curvature profiles
2. Measure width at high-curvature points vs low-curvature points
3. Verify bends are wider than straights
4. Verify variation is within 15-30% of mean width
5. Statistical test: correlation between curvature and width should be positive
6. Visual inspection: channel should visibly widen in bends

## 8. Rewrite Braided Network with Confluence-Bifurcation Dynamics [high]

Replace `braided_threads()` and `seed_bars()` with `braided_network()` that generates channels that actually split and merge (not parallel sinusoids) with bifurcation spacing 4-5× width and bar aspect ratio ≈5:1.

**Depends on:** 1

Replace braided generation functions in `geologic_generators.py`:

```python
def braided_network(
    height: int,
    width: int,
    channel_width: float,
    rng: np.random.Generator,
    bifurcation_factor: tuple[float, float] = (4.0, 5.0),
    bar_aspect_ratio: float = 5.0,
) -> tuple[Array, Array, list[dict]]:
    """Generate braided network with splitting/merging channels (anchor-fluvial-braided-network).
    
    Constraints from research:
    - B2: Bifurcation spacing = 4-5× channel width
    - B3: Channels SPLIT and MERGE (not parallel)
    - B4: Bar aspect ratio ≈ 5:1
    - B5: Bars form at BIFURCATION points
    """
    channel_mask = np.zeros((height, width), dtype=np.float32)
    bar_mask = np.zeros((height, width), dtype=np.float32)
    
    bifurcation_spacing = rng.uniform(*bifurcation_factor) * channel_width
    
    # Track active channels: list of {y: float, width: float, flow: float}
    active_channels = [{
        'y': height / 2.0,
        'width': channel_width,
        'flow': 1.0,
        'id': 0
    }]
    
    metadata = []
    distance_since_bifurcation = 0
    next_channel_id = 1
    
    for x in range(width):
        distance_since_bifurcation += 1
        new_channels = []
        
        for ch in active_channels:
            # Random walk for channel position
            ch['y'] += rng.normal(0, channel_width * 0.02)
            ch['y'] = np.clip(ch['y'], height * 0.15, height * 0.85)
            
            # Check for BIFURCATION
            if (distance_since_bifurcation >= bifurcation_spacing and 
                len(active_channels) < 6 and
                rng.random() < 0.4):
                
                # Create bar at bifurcation point
                bar_length = rng.uniform(4, 6) * channel_width
                bar_width = bar_length / bar_aspect_ratio
                bar = _ellipse_patch(
                    int(ch['y']), x,
                    height, width,
                    bar_width / 2, bar_length / 2
                )
                bar_mask = np.maximum(bar_mask, bar * 0.8)
                
                # Split into two channels around bar
                offset = channel_width * 0.5
                flow_split = rng.uniform(0.4, 0.6)
                ch1 = {
                    'y': ch['y'] - offset,
                    'width': ch['width'] * 0.7,
                    'flow': ch['flow'] * flow_split,
                    'id': next_channel_id
                }
                ch2 = {
                    'y': ch['y'] + offset,
                    'width': ch['width'] * 0.6,
                    'flow': ch['flow'] * (1 - flow_split),
                    'id': next_channel_id + 1
                }
                new_channels.extend([ch1, ch2])
                next_channel_id += 2
                distance_since_bifurcation = 0
                continue
            
            # Check for CONFLUENCE (merge close channels)
            merged = False
            for other in new_channels:
                if abs(ch['y'] - other['y']) < channel_width * 0.8:
                    # Merge channels
                    other['y'] = (other['y'] * other['flow'] + ch['y'] * ch['flow']) / (other['flow'] + ch['flow'])
                    other['width'] = min(channel_width * 1.2, other['width'] + ch['width'] * 0.3)
                    other['flow'] += ch['flow']
                    merged = True
                    break
            
            if not merged:
                new_channels.append(ch)
        
        # Draw channels at this x position
        for ch in new_channels:
            y_center = int(np.clip(ch['y'], 0, height - 1))
            half_w = int(ch['width'] / 2)
            y_min = max(0, y_center - half_w)
            y_max = min(height, y_center + half_w + 1)
            channel_mask[y_min:y_max, x] = np.maximum(
                channel_mask[y_min:y_max, x],
                ch['flow']
            )
        
        active_channels = new_channels
        metadata.append({'n_channels': len(active_channels), 'x': x})
    
    return (
        np.clip(channel_mask, 0.0, 1.0).astype(np.float32),
        np.clip(bar_mask, 0.0, 1.0).astype(np.float32),
        metadata
    )
```

Update `generate_braided()` to use this new function.

Key changes:
1. Channels actually SPLIT at bifurcations and MERGE at confluences
2. Bifurcation spacing is 4-5× channel width
3. Bars are placed AT bifurcation points (not random)
4. Bar aspect ratio is 5:1
5. No more parallel sinusoids

**Subtasks:**
- [ ] 1. Implement Active Channel Tracking Data Structure
- [ ] 2. Implement Bifurcation Logic with Bar Creation at Split Points
- [ ] 3. Implement Confluence Logic for Merging Close Channels
- [ ] 4. Replace Parallel Sinusoid Generation with Downstream-Marching Algorithm
- [ ] 5. Generate Metadata Tracking Bifurcation and Confluence Events

**Test strategy:** 1. Generate 50 braided networks with different seeds
2. Verify channels split and merge (count bifurcations and confluences)
3. Measure bifurcation spacing - should be 4-5× channel width
4. Measure bar dimensions - aspect ratio should be ≈5:1 (±20%)
5. Verify bars are located at bifurcation points
6. Visual inspection: should show branching/merging pattern, not parallel lines

## 9. Enhance Anastomosing Generator with Avulsion Dynamics [medium]

Enhance `anasto_paths()` with `anasto_network_avulsion()` that creates channels branching from parent channels at gradient-advantage avulsion points instead of independent parallel random walks.

**Depends on:** 1

Replace `anasto_paths()` in `geologic_generators.py`:

```python
def anasto_network_avulsion(
    height: int,
    width: int,
    branch_count: int,
    rng: np.random.Generator,
    gradient_threshold: float = 1.2,
    sinuosity_range: tuple[float, float] = (1.0, 1.3),
) -> tuple[Array, list[Array], list[dict]]:
    """Create anastomosing network with avulsion-connected channels (anchor-fluvial-anasto-avulsion).
    
    Constraints from research:
    - A2: Low sinuosity S ∈ [1.0, 1.3]
    - A3/A5: Avulsion based on gradient advantage (S_fp/S_ch > γ)
    - A7: Channels branch FROM parent channels
    """
    combined = np.zeros((height, width), dtype=np.float32)
    centerlines: list[Array] = []
    branch_info: list[dict] = []
    
    # Create PRIMARY channel first (low sinuosity)
    primary_y = height / 2.0
    primary_centerline = np.zeros(width, dtype=np.float32)
    
    # Low-sinuosity primary channel
    sinuosity_target = rng.uniform(*sinuosity_range)
    drift_scale = (sinuosity_target - 1.0) * height * 0.1
    
    for x in range(width):
        drift = rng.normal(0.0, drift_scale * 0.01)
        primary_y = np.clip(primary_y + drift, height * 0.3, height * 0.7)
        primary_centerline[x] = primary_y
    
    # Smooth for low sinuosity
    primary_centerline = ndimage.gaussian_filter1d(primary_centerline, sigma=width//20)
    
    channel_width = rng.uniform(8.0, 14.0)
    primary_mask = _centerline_mask(primary_centerline, height, width, channel_width)
    combined = np.maximum(combined, primary_mask)
    centerlines.append(primary_centerline.astype(np.float32))
    branch_info.append({'width_px': channel_width, 'parent': None, 'avulsion_x': 0})
    
    # Create AVULSION branches from primary
    for i in range(1, branch_count):
        # Select parent channel (preferentially from main trunk)
        parent_idx = 0 if rng.random() < 0.7 else rng.integers(0, len(centerlines))
        parent_centerline = centerlines[parent_idx]
        
        # Find avulsion point based on gradient advantage
        # Higher gradient = more likely avulsion
        gradients = np.abs(np.gradient(parent_centerline))
        gradient_scores = gradients / (gradients.mean() + 1e-6)
        
        # Avulsion more likely where gradient advantage exists
        avulsion_probs = np.where(gradient_scores > gradient_threshold, gradient_scores, 0)
        if avulsion_probs.sum() > 0:
            avulsion_probs = avulsion_probs / avulsion_probs.sum()
            avulsion_x = rng.choice(width, p=avulsion_probs)
        else:
            avulsion_x = rng.integers(width // 4, 3 * width // 4)
        
        # Create branch from avulsion point
        branch_centerline = np.zeros(width, dtype=np.float32)
        branch_y = parent_centerline[avulsion_x]
        
        # Branch diverges from parent
        diverge_direction = rng.choice([-1, 1])
        diverge_rate = rng.uniform(0.01, 0.03) * height
        
        for x in range(width):
            if x < avulsion_x:
                # Before avulsion: follow parent
                branch_centerline[x] = parent_centerline[x]
            else:
                # After avulsion: diverge
                dx = x - avulsion_x
                branch_y += diverge_direction * diverge_rate * 0.01 + rng.normal(0, drift_scale * 0.005)
                branch_y = np.clip(branch_y, height * 0.1, height * 0.9)
                branch_centerline[x] = branch_y
        
        branch_width = rng.uniform(6.0, 12.0)
        branch_mask = _centerline_mask(branch_centerline, height, width, branch_width)
        combined = np.maximum(combined, branch_mask)
        centerlines.append(branch_centerline.astype(np.float32))
        branch_info.append({
            'width_px': branch_width,
            'parent': parent_idx,
            'avulsion_x': int(avulsion_x)
        })
    
    return np.clip(combined, 0.0, 1.0), centerlines, branch_info
```

Update `generate_anastomosing()` to use this function and validate wetland coverage.

Key changes:
1. Primary channel established first
2. Branches AVULSE from parent channels (not independent)
3. Avulsion points selected by gradient advantage
4. Low sinuosity (1.0-1.3) enforced
5. Channels share paths before avulsion point

**Subtasks:**
- [ ] 1. Implement Primary Channel with Low Sinuosity Constraint
- [ ] 2. Implement Gradient Advantage Calculation for Avulsion Point Selection
- [ ] 3. Create Avulsion Branches Diverging from Parent Channels
- [ ] 4. Track Parent-Child Relationships and Validate Wetland Coverage

**Test strategy:** 1. Generate anastomosing networks with varying branch counts
2. Verify all branches connect to parent channel at avulsion point
3. Verify sinuosity is within [1.0, 1.3] for all channels
4. Verify avulsion points occur at gradient-advantage locations
5. Validate 60-90% wetland coverage in make_marsh output
6. Visual inspection: channels should visibly branch from each other

## 10. Implement Validation Functions and Acceptance Testing [high]

Create validation functions that measure all physics constraints and integrate them into generation pipelines. Implement acceptance criteria checking from the PRD.

**Depends on:** 1, 2, 3, 4, 5, 6, 7, 8, 9

Create `src/analog_image_generator/validation.py`:

```python
"""Validation functions for physics-based generator acceptance criteria."""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from numpy.typing import NDArray

from .geometry_helpers import (
    measure_wavelength,
    measure_sinuosity,
    measure_radius_of_curvature,
    compute_local_curvature,
)

@dataclass
class MeanderingValidation:
    wavelength_ratio: float  # λ / channel_width, should be 10-14
    radius_ratio: float  # R_c / channel_width at apexes, should be 2-3
    sinuosity: float  # should be 1.5-3.0
    point_bars_on_inner_only: bool
    scroll_bars_in_point_bars_only: bool
    oxbows_at_cutoffs_only: bool
    levee_decay_exponential: bool
    width_increases_with_curvature: bool
    
    @property
    def passes_all(self) -> bool:
        return (
            10.0 <= self.wavelength_ratio <= 14.0 and
            2.0 <= self.radius_ratio <= 3.0 and
            1.5 <= self.sinuosity <= 3.0 and
            self.point_bars_on_inner_only and
            self.scroll_bars_in_point_bars_only and
            self.oxbows_at_cutoffs_only and
            self.levee_decay_exponential and
            self.width_increases_with_curvature
        )

def validate_meandering(
    centerline: NDArray,
    channel_width: float,
    masks: dict[str, NDArray],
) -> MeanderingValidation:
    """Validate meandering generation against physics criteria."""
    
    # G1: Wavelength
    wavelength = measure_wavelength(centerline)
    wavelength_ratio = wavelength / channel_width
    
    # G2: Radius of curvature
    r_c_values = measure_radius_of_curvature(centerline)
    radius_ratio = np.median(r_c_values) / channel_width if len(r_c_values) > 0 else 0
    
    # G4: Sinuosity
    sinuosity = measure_sinuosity(centerline, len(centerline))
    
    # P1: Point bars on inner bends only
    curvature = compute_local_curvature(centerline)
    point_bar = masks.get('pointbar', np.zeros_like(centerline))
    point_bars_on_inner_only = _validate_inner_bend_only(point_bar, curvature, centerline)
    
    # P3: Scroll bars in point bars only
    scroll_bar = masks.get('scroll_bar', np.zeros(1))
    scroll_bars_in_point_bars_only = _validate_contained_in(scroll_bar, point_bar)
    
    # O1: Oxbows at cutoffs (check shape is not circular)
    oxbow = masks.get('oxbow', np.zeros(1))
    oxbows_at_cutoffs_only = _validate_oxbow_shapes(oxbow)
    
    # L1: Exponential levee decay
    levee = masks.get('levee', np.zeros(1))
    channel = masks.get('channel', np.zeros(1))
    levee_decay_exponential = _validate_exponential_decay(levee, channel)
    
    # C1: Width increases with curvature
    width_increases_with_curvature = _validate_curvature_width_correlation(channel, curvature)
    
    return MeanderingValidation(
        wavelength_ratio=wavelength_ratio,
        radius_ratio=radius_ratio,
        sinuosity=sinuosity,
        point_bars_on_inner_only=point_bars_on_inner_only,
        scroll_bars_in_point_bars_only=scroll_bars_in_point_bars_only,
        oxbows_at_cutoffs_only=oxbows_at_cutoffs_only,
        levee_decay_exponential=levee_decay_exponential,
        width_increases_with_curvature=width_increases_with_curvature,
    )

@dataclass
class BraidedValidation:
    has_bifurcations: bool
    has_confluences: bool
    bifurcation_spacing_ratio: float  # should be 4-5
    bar_aspect_ratio: float  # should be ~5
    bars_at_bifurcations: bool
    
    @property
    def passes_all(self) -> bool:
        return (
            self.has_bifurcations and
            self.has_confluences and
            4.0 <= self.bifurcation_spacing_ratio <= 5.0 and
            4.0 <= self.bar_aspect_ratio <= 6.0 and
            self.bars_at_bifurcations
        )

@dataclass  
class AnastValidation:
    sinuosity: float  # should be 1.0-1.3
    channels_branch_from_parents: bool
    wetland_coverage: float  # should be 0.6-0.9
    
    @property
    def passes_all(self) -> bool:
        return (
            1.0 <= self.sinuosity <= 1.3 and
            self.channels_branch_from_parents and
            0.6 <= self.wetland_coverage <= 0.9
        )
```

Add validation calls to `generate_meandering()`, `generate_braided()`, `generate_anastomosing()` with optional `validate=True` parameter.

Update `docs/GEOLOGIC_RULES.md` with new anchor mappings for all physics-based functions.

**Subtasks:**
- [ ] 1. Create validation.py module with dataclasses for MeanderingValidation, BraidedValidation, and AnastValidation
- [ ] 2. Implement validate_meandering() with all 8+ constraint checks for wavelength, R_c, sinuosity, point bars, scroll bars, oxbows, levees, width variation
- [ ] 3. Implement validate_braided() with bifurcation, confluence, and bar constraint checks
- [ ] 4. Implement validate_anastomosing() with sinuosity, branching hierarchy, and wetland coverage checks
- [ ] 5. Add optional validate=True parameter to generate_* functions and integrate validation calls with updated GEOLOGIC_RULES anchors

**Test strategy:** 1. Run validation on 100 generated images per style
2. Verify >95% pass rate for all mandatory criteria
3. Generate validation report CSV with per-image metrics
4. Create QA notebook showing validation results visually
5. Integration test: validation functions don't raise errors
6. Performance test: validation adds <10% overhead to generation time

## 11. Update Documentation and Anchor Mappings [medium]

Update docs/GEOLOGIC_RULES.md with new anchor mappings for all physics-based functions. Ensure notebook references are updated.

**Depends on:** 2, 3, 4, 5, 6, 7, 8, 9, 10

Update `docs/GEOLOGIC_RULES.md` with new entries:

```markdown
## Fluvial (Meandering) - Physics-Based
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Meandering | Arc-based centerline with λ=10-14×W | `geologic_generators.meander_centerline_physics()` | `#anchor-fluvial-meander-centerline-physics`
Meandering | Point bars on inner bends only | `geologic_generators.add_point_bars()` | `#anchor-fluvial-point-bars`
Meandering | Scroll bars confined to point bars | `geologic_generators.add_scroll_bars_physics()` | `#anchor-fluvial-scroll-bars-physics`
Meandering | Oxbows at neck cutoffs only | `geologic_generators.add_oxbow_physics()` | `#anchor-fluvial-oxbow-physics`
Meandering | Exponential levee decay h=h₀exp(-x/L_d) | `geologic_generators.add_levees_exponential()` | `#anchor-fluvial-levees-exponential`
Meandering | Curvature-driven width variation ±15-30% | `geologic_generators.meander_variable_channel_curvature()` | `#anchor-fluvial-variable-width-curvature`

## Fluvial (Braided) - Physics-Based
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Braided | Split/merge network with bifurcation spacing 4-5×W | `geologic_generators.braided_network()` | `#anchor-fluvial-braided-network`
Braided | Bar aspect ratio 5:1 at bifurcations | `geologic_generators.braided_network()` | `#anchor-fluvial-braided-bars`

## Fluvial (Anastomosing) - Physics-Based
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Anastomosing | Avulsion-connected branches S=1.0-1.3 | `geologic_generators.anasto_network_avulsion()` | `#anchor-fluvial-anasto-avulsion`

## Validation
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
All Fluvial | Physics constraint validation | `validation.validate_meandering()` / `validate_braided()` / `validate_anastomosing()` | `#anchor-fluvial-validation`
```

Create/update notebooks:
1. `notebooks/fluvial_physics_validation.ipynb` - QA notebook showing validation results
2. Update `notebooks/fluvial_meandering.ipynb` with new anchor cells
3. Update `notebooks/fluvial_braided.ipynb` with new anchor cells
4. Update `notebooks/fluvial_anastomosing.ipynb` with new anchor cells

Run `python scripts/validate_geo_anchors.py` to verify all anchors are consistent.

**Subtasks:**
- [ ] 1. Update docs/GEOLOGIC_RULES.md with Physics-Based Anchor Entries
- [ ] 2. Update Notebook Anchor Cells and Validate Consistency

**Test strategy:** 1. Run validate_geo_anchors.py - should pass with no errors
2. Verify all new functions have corresponding anchor entries
3. Verify notebook anchor cells reference correct functions
4. Documentation review: all PRD formulas should be traceable to code

## 12. Integration Testing and Visual QA [high]

Create comprehensive integration tests and visual QA notebooks to verify the physics-based generators produce geologically realistic outputs that pass all acceptance criteria.

**Depends on:** 10, 11

Create integration test suite in `tests/test_physics_integration.py`:

```python
import pytest
import numpy as np
from analog_image_generator import geologic_generators as gg
from analog_image_generator import utils
from analog_image_generator.validation import (
    validate_meandering,
    validate_braided,
    validate_anastomosing,
)

class TestMeanderingPhysics:
    @pytest.mark.parametrize('seed', range(10))
    def test_wavelength_constraint(self, seed):
        rng = utils.seeded_rng(seed)
        params = {'seed': seed, 'height': 512, 'width': 512}
        gray, masks = gg.generate_meandering(params, rng)
        # Extract channel_width and centerline from generation
        validation = validate_meandering(...)
        assert 10 <= validation.wavelength_ratio <= 14
    
    @pytest.mark.parametrize('seed', range(10))
    def test_point_bars_inner_only(self, seed):
        rng = utils.seeded_rng(seed)
        params = {'seed': seed}
        gray, masks = gg.generate_meandering(params, rng)
        assert 'pointbar' in masks
        validation = validate_meandering(...)
        assert validation.point_bars_on_inner_only
    
    def test_no_scroll_bars_outside_point_bars(self):
        ...
    
    def test_oxbow_shapes_are_meander_loops(self):
        ...

class TestBraidedPhysics:
    def test_channels_split_and_merge(self):
        ...
    
    def test_bifurcation_spacing(self):
        ...
    
    def test_bar_aspect_ratio(self):
        ...

class TestAnastPhysics:
    def test_channels_branch_from_parents(self):
        ...
    
    def test_low_sinuosity(self):
        ...
    
    def test_wetland_coverage(self):
        ...
```

Create visual QA notebook `notebooks/physics_qa_visual.ipynb`:
1. Generate 10 images per style with different seeds
2. Display side-by-side with validation metrics overlay
3. Highlight any failures with red borders
4. Show wavelength/R_c measurements on meandering images
5. Show bifurcation points on braided images
6. Show avulsion points on anastomosing images

Create batch validation script `scripts/batch_validate_physics.py`:
1. Generate N images per style
2. Run validation on each
3. Output CSV with all metrics
4. Print summary pass/fail rates
5. Flag any images failing acceptance criteria

Acceptance criteria from PRD:
- 100% meandering images pass wavelength validation
- 100% meandering images have point bars on inner bends
- 100% oxbows at valid cutoff locations
- 100% braided images show channel splitting
- β_iso within documented target bands

**Subtasks:**
- [ ] 1. Create tests/test_physics_integration.py with parameterized physics constraint tests
- [ ] 2. Create notebooks/physics_qa_visual.ipynb for visual validation and metric overlay
- [ ] 3. Create scripts/batch_validate_physics.py for batch validation with CSV output
- [ ] 4. Establish performance benchmarks ensuring generation time ≤ 2× original

**Test strategy:** 1. Run full test suite: pytest tests/test_physics_integration.py
2. All parameterized tests should pass
3. Run batch validation: python scripts/batch_validate_physics.py --n=100
4. Pass rate should be >95% for all criteria
5. Visual review of QA notebook outputs
6. Performance benchmark: generation time should not exceed 2x original

---

## Tag: fluvial-realism-v2 (physics-based fluvial realism, 4 of 12 tasks still pending)

## 9. Enhance Anastomosing with Avulsion Dynamics [medium]

Enhance the anastomosing generator so channels branch from parent channels at avulsion points rather than being independent parallel paths, implementing gradient-advantage avulsion path selection.

**Depends on:** 1

Enhance `anasto_paths` and add avulsion logic in `geologic_generators.py`:

```python
@dataclass
class AnastoChannel:
    """Track anastomosing channel state."""
    centerline: Array  # y positions along x
    width: float
    parent_id: int | None
    avulsion_x: int | None
    gradient: float  # Channel gradient


def anasto_network_avulsion(
    height: int,
    width: int,
    branch_count: int,
    rng: np.random.Generator,
    *,
    gradient_threshold: float = 1.2,
    sinuosity_range: tuple[float, float] = (1.0, 1.3),
) -> tuple[Array, list[Array], list[dict]]:
    """Generate anastomosing network with avulsion dynamics.
    
    Implements A2: Low sinuosity S ∈ [1.0, 1.3]
    Implements A3: Avulsion threshold S_e ≈ 1.0
    Implements A5: Avulsion where S_fp/S_ch > γ (gradient advantage)
    Implements A7: Channels avulse rather than migrate
    
    Returns:
        combined_mask: Combined channel mask
        centerlines: List of centerline arrays
        branch_metadata: List of dicts with avulsion info
    """
    channels: list[AnastoChannel] = []
    branch_metadata: list[dict] = []
    
    # Create primary channel (no parent)
    primary_centerline = _create_low_sinuosity_channel(
        height, width, height/2, rng, sinuosity_range
    )
    primary_gradient = rng.uniform(0.8, 1.0)  # Normalized gradient
    primary_width = rng.uniform(8.0, 14.0)
    
    channels.append(AnastoChannel(
        centerline=primary_centerline,
        width=primary_width,
        parent_id=None,
        avulsion_x=None,
        gradient=primary_gradient
    ))
    branch_metadata.append({
        'channel_id': 0,
        'parent_id': None,
        'avulsion_x': None,
        'gradient': primary_gradient
    })
    
    # Create branch channels via avulsion
    for i in range(1, branch_count):
        # Select parent channel for avulsion
        parent_idx = rng.integers(0, len(channels))
        parent = channels[parent_idx]
        
        # Find avulsion point based on gradient advantage
        avulsion_x = _find_avulsion_point(
            parent.centerline,
            parent.gradient,
            gradient_threshold,
            rng,
            width
        )
        
        # New channel gradient has advantage over parent
        new_gradient = parent.gradient * rng.uniform(gradient_threshold, gradient_threshold + 0.3)
        
        # Create new channel branching from avulsion point
        branch_y_start = parent.centerline[avulsion_x]
        # Diverge from parent
        direction = rng.choice([-1, 1])
        branch_y_start += direction * parent.width * rng.uniform(1.5, 3.0)
        branch_y_start = np.clip(branch_y_start, height * 0.2, height * 0.8)
        
        branch_centerline = _create_low_sinuosity_channel(
            height, width, branch_y_start, rng, sinuosity_range,
            start_x=avulsion_x
        )
        # Connect to parent at avulsion point
        branch_centerline[:avulsion_x] = np.nan  # Mark as not present
        
        branch_width = rng.uniform(6.0, 12.0)
        
        channels.append(AnastoChannel(
            centerline=branch_centerline,
            width=branch_width,
            parent_id=parent_idx,
            avulsion_x=avulsion_x,
            gradient=new_gradient
        ))
        branch_metadata.append({
            'channel_id': i,
            'parent_id': parent_idx,
            'avulsion_x': avulsion_x,
            'gradient': new_gradient,
            'gradient_advantage': new_gradient / parent.gradient
        })
    
    # Render all channels to mask
    combined_mask = np.zeros((height, width), dtype=np.float32)
    centerlines = []
    
    for ch in channels:
        mask = _centerline_mask_with_nan(
            ch.centerline, height, width, ch.width
        )
        combined_mask = np.maximum(combined_mask, mask)
        centerlines.append(ch.centerline)
    
    return combined_mask, centerlines, branch_metadata


def _create_low_sinuosity_channel(
    height: int, width: int,
    base_y: float,
    rng: np.random.Generator,
    sinuosity_range: tuple[float, float],
    start_x: int = 0
) -> Array:
    """Create low-sinuosity channel (S ∈ [1.0, 1.3])."""
    centerline = np.full(width, np.nan, dtype=np.float32)
    
    # Very gentle drift for low sinuosity
    drift_scale = height * 0.005  # Much smaller than meandering
    drift = rng.normal(0.0, drift_scale, size=width - start_x)
    smooth_drift = ndimage.gaussian_filter1d(drift, sigma=max(1, width // 40))
    
    y = base_y
    for i, d in enumerate(smooth_drift):
        x = start_x + i
        y = np.clip(y + d * 0.03, height * 0.15, height * 0.85)
        centerline[x] = y
    
    return centerline


def _find_avulsion_point(
    parent_centerline: Array,
    parent_gradient: float,
    threshold: float,
    rng: np.random.Generator,
    width: int
) -> int:
    """Find suitable avulsion point where gradient advantage exists."""
    # Prefer points in first half of channel (upstream avulsions more common)
    valid_range = range(int(width * 0.1), int(width * 0.6))
    candidates = [x for x in valid_range if not np.isnan(parent_centerline[x])]
    
    if not candidates:
        return int(width * 0.3)
    
    return int(rng.choice(candidates))


def _centerline_mask_with_nan(
    centerline: Array, height: int, width: int, channel_width: float
) -> Array:
    """Create mask, handling NaN values in centerline."""
    mask = np.zeros((height, width), dtype=np.float32)
    half_w = channel_width / 2.0
    
    for x in range(width):
        if np.isnan(centerline[x]):
            continue
        y = centerline[x]
        y_min = int(max(0, y - half_w))
        y_max = int(min(height, y + half_w + 1))
        mask[y_min:y_max, x] = 1.0
    
    return mask
```

Update `generate_anastomosing` to use `anasto_network_avulsion` and validate wetland coverage:
```python
branch_mask, centerlines, branch_metadata = anasto_network_avulsion(height, width, branch_count, rng)
# Validate A8: 60-90% wetland coverage
wetland_fraction = marsh_mask.mean()
if not 0.6 <= wetland_fraction <= 0.9:
    # Log warning but don't fail
    masks['_qa_wetland_warning'] = True
```

**Subtasks:**
- [ ] 1. Create AnastoChannel Dataclass with Parent Tracking and Gradient
- [ ] 2. Implement Primary Channel Creation with Low Sinuosity (S ∈ [1.0, 1.3])
- [ ] 3. Implement Avulsion Point Detection Based on Gradient Advantage
- [ ] 4. Integrate Branch Channel Creation and Wetland Coverage Validation

**Test strategy:** Tests:
1. Verify all non-primary channels have parent_id set (branch from parents)
2. Verify gradient_advantage > 1.1 for all avulsion channels
3. Measure sinuosity of each channel: should be in [1.0, 1.3]
4. Validate wetland coverage is 60-90% of non-channel area
5. Visual test: channels should visibly branch from parents, not be independent

## 10. Implement Physics Validation Framework [high]

Create a validation module that measures and validates all physics constraints (wavelength, curvature, sinuosity, bifurcation spacing, etc.) and integrates with the existing stats.py infrastructure.

**Depends on:** 2, 3, 4, 5, 6, 7, 8, 9

Create new file `src/analog_image_generator/physics_validation.py`:

```python
"""Physics-based validation for fluvial generators."""

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float32]


@dataclass
class ValidationResult:
    """Result of physics validation."""
    passed: bool
    constraint_name: str
    measured_value: float
    expected_range: tuple[float, float]
    tolerance: float = 0.0
    details: str = ""


@dataclass
class MeanderingValidation:
    """Validation results for meandering rivers."""
    wavelength_ratio: ValidationResult
    curvature_ratio: ValidationResult
    sinuosity: ValidationResult
    point_bars_inner_only: ValidationResult
    scroll_bars_in_point_bars: ValidationResult
    oxbows_at_cutoffs: ValidationResult
    levee_exponential: ValidationResult
    width_bend_variation: ValidationResult
    all_passed: bool = field(init=False)
    
    def __post_init__(self):
        self.all_passed = all([
            self.wavelength_ratio.passed,
            self.curvature_ratio.passed,
            self.sinuosity.passed,
            self.point_bars_inner_only.passed,
            self.scroll_bars_in_point_bars.passed,
            self.oxbows_at_cutoffs.passed,
            self.levee_exponential.passed,
            self.width_bend_variation.passed,
        ])


@dataclass
class BraidedValidation:
    """Validation results for braided rivers."""
    channels_split_merge: ValidationResult
    bifurcation_spacing: ValidationResult
    bar_aspect_ratio: ValidationResult
    bars_at_bifurcations: ValidationResult
    all_passed: bool = field(init=False)
    
    def __post_init__(self):
        self.all_passed = all([
            self.channels_split_merge.passed,
            self.bifurcation_spacing.passed,
            self.bar_aspect_ratio.passed,
            self.bars_at_bifurcations.passed,
        ])


@dataclass
class AnastomosingValidation:
    """Validation results for anastomosing rivers."""
    channels_branch_from_parents: ValidationResult
    low_sinuosity: ValidationResult
    wetland_coverage: ValidationResult
    levee_exponential: ValidationResult
    all_passed: bool = field(init=False)
    
    def __post_init__(self):
        self.all_passed = all([
            self.channels_branch_from_parents.passed,
            self.low_sinuosity.passed,
            self.wetland_coverage.passed,
            self.levee_exponential.passed,
        ])


def validate_meandering(
    centerline: Array,
    masks: dict[str, Array],
    channel_width: float,
    metrics: dict[str, float] | None = None,
    cutoff_locations: list | None = None,
) -> MeanderingValidation:
    """Validate meandering river against physics constraints."""
    from . import geologic_generators as gg
    
    # G1: Wavelength = 10-14× W
    measured_wavelength = measure_wavelength(centerline)
    wavelength_ratio = measured_wavelength / channel_width
    wavelength_valid = ValidationResult(
        passed=9.0 <= wavelength_ratio <= 15.0,  # ±1 tolerance
        constraint_name="G1: Wavelength",
        measured_value=wavelength_ratio,
        expected_range=(10.0, 14.0),
        tolerance=1.0,
        details=f"λ/W = {wavelength_ratio:.2f}"
    )
    
    # G2: R_c = 2-3× W
    mean_rc, _ = measure_radius_of_curvature(centerline)
    curvature_ratio = mean_rc / channel_width
    curvature_valid = ValidationResult(
        passed=1.5 <= curvature_ratio <= 4.0,  # ±0.5 tolerance
        constraint_name="G2: Radius of Curvature",
        measured_value=curvature_ratio,
        expected_range=(2.0, 3.0),
        tolerance=0.5
    )
    
    # G4: Sinuosity = 1.5-3.0
    sinuosity = measure_sinuosity(centerline, len(centerline))
    sinuosity_valid = ValidationResult(
        passed=1.3 <= sinuosity <= 3.5,
        constraint_name="G4: Sinuosity",
        measured_value=sinuosity,
        expected_range=(1.5, 3.0),
        tolerance=0.2
    )
    
    # P1: Point bars on inner bends only
    point_bar_valid = _validate_point_bars_inner_only(
        centerline, masks.get('pointbar'), masks.get('channel')
    )
    
    # P3: Scroll bars in point bars only
    scroll_valid = _validate_scroll_bars_in_point_bars(
        masks.get('scroll_bar'), masks.get('pointbar')
    )
    
    # O1-O3: Oxbows at cutoff locations
    oxbow_valid = _validate_oxbows_at_cutoffs(
        masks.get('oxbow'), cutoff_locations, channel_width
    )
    
    # L1: Exponential levee decay
    levee_valid = _validate_exponential_levee(
        masks.get('levee'), masks.get('channel'), channel_width
    )
    
    # C1: Width variation in bends
    width_valid = _validate_width_bend_variation(
        centerline, masks.get('channel'), channel_width
    )
    
    return MeanderingValidation(
        wavelength_ratio=wavelength_valid,
        curvature_ratio=curvature_valid,
        sinuosity=sinuosity_valid,
        point_bars_inner_only=point_bar_valid,
        scroll_bars_in_point_bars=scroll_valid,
        oxbows_at_cutoffs=oxbow_valid,
        levee_exponential=levee_valid,
        width_bend_variation=width_valid,
    )


def validate_braided(
    masks: dict[str, Array],
    channel_width: float,
    network_metadata: list[dict] | None = None,
) -> BraidedValidation:
    """Validate braided river against physics constraints."""
    # Implementation for braided validation...
    pass


def validate_anastomosing(
    masks: dict[str, Array],
    centerlines: list[Array],
    branch_metadata: list[dict] | None = None,
) -> AnastomosingValidation:
    """Validate anastomosing river against physics constraints."""
    # Implementation for anastomosing validation...
    pass


def _validate_point_bars_inner_only(
    centerline: Array,
    pointbar_mask: Array | None,
    channel_mask: Array | None,
) -> ValidationResult:
    """Check that point bars exist only on inner bends."""
    if pointbar_mask is None or channel_mask is None:
        return ValidationResult(
            passed=False,
            constraint_name="P1: Point bars inner only",
            measured_value=0.0,
            expected_range=(0.9, 1.0),
            details="Missing pointbar or channel mask"
        )
    
    curvature = compute_local_curvature(centerline)
    height, width = pointbar_mask.shape
    
    correct_side_count = 0
    total_pointbar_count = 0
    
    for x in range(width):
        if abs(curvature[x]) < 0.001:
            continue
        
        inner_side = -np.sign(curvature[x])
        y_center = centerline[x]
        
        for y in range(height):
            if pointbar_mask[y, x] > 0.3:
                total_pointbar_count += 1
                offset = (y - y_center) * inner_side
                if offset > 0:  # Correct side
                    correct_side_count += 1
    
    fraction_correct = correct_side_count / (total_pointbar_count + 1e-6)
    
    return ValidationResult(
        passed=fraction_correct >= 0.85,
        constraint_name="P1: Point bars inner only",
        measured_value=fraction_correct,
        expected_range=(0.9, 1.0),
        tolerance=0.05
    )

# Additional helper validation functions...
```

Integrate with `stats.py` by adding validation call in `compute_metrics`.

**Subtasks:**
- [ ] 1. Implement Core Validation Infrastructure and Dataclasses
- [ ] 2. Implement Meandering Geometric Validation Functions
- [ ] 3. Implement Meandering Facies Placement Validation Functions
- [ ] 4. Implement Braided and Anastomosing Validation Functions
- [ ] 5. Integrate Physics Validation with stats.py and Add Meta-Tests

**Test strategy:** Tests:
1. Unit tests for each ValidationResult computation
2. Integration test: generate 100 meandering images, validate all, expect >95% pass rate
3. Integration test: generate 100 braided images, validate all, expect >95% pass rate
4. Test that validation correctly fails on old (pre-physics) generator outputs
5. Regression test: validation results should be deterministic for same seed

## 11. Update GEOLOGIC_RULES.md Documentation [low]

Update the GEOLOGIC_RULES.md anchor mappings to reflect all new physics-based functions, adding new anchors for point bars, physics centerline, exponential levees, etc.

**Depends on:** 2, 3, 4, 5, 6, 7, 8, 9, 10

Update `docs/GEOLOGIC_RULES.md` with new entries. Add to the Meandering section:

```markdown
## Fluvial (Meandering) — Physics-Based
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Meandering | Arc-based centerline with λ=10-14×W, R_c=2-3×W | `analog_image_generator.geologic_generators.meander_centerline_physics(height: int, width: int, channel_width: float, rng: np.random.Generator) -> tuple[NDArray, dict]` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-meander-centerline-physics`
Meandering | Point bars on inner bends only | `analog_image_generator.geologic_generators.add_point_bars(centerline: NDArray, channel_mask: NDArray, channel_width: float, rng: np.random.Generator) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-point-bars`
Meandering | Scroll bars confined to point bar regions | `analog_image_generator.geologic_generators.add_scroll_bars_physics(centerline: NDArray, point_bar_mask: NDArray, channel_width: float, rng: np.random.Generator) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-scroll-bars-physics`
Meandering | Oxbows at neck cutoff locations only | `analog_image_generator.geologic_generators.add_oxbow_physics(centerline: NDArray, channel_mask: NDArray, channel_width: float, rng: np.random.Generator) -> tuple[NDArray, list]` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-oxbow-physics`
Meandering | Exponential levee decay h(x)=h0×exp(-x/Ld) | `analog_image_generator.geologic_generators.add_levees_exponential(channel_mask: NDArray, channel_width: float, rng: np.random.Generator) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-levees-exponential`
Meandering | Curvature-driven width variation ±15-30% | `analog_image_generator.geologic_generators.meander_variable_channel_curvature(centerline: NDArray, shape: tuple, base_width: float, rng: np.random.Generator) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-variable-width-curvature`
```

Add to Braided section:
```markdown
## Fluvial (Braided) — Physics-Based
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Braided | Confluence-bifurcation network, spacing 4-5×W | `analog_image_generator.geologic_generators.braided_network(height: int, width: int, channel_width: float, rng: np.random.Generator) -> tuple[NDArray, NDArray, list]` | `notebooks/fluvial_braided.ipynb#anchor-fluvial-braided-network`
Braided | Bar aspect ratio ≈5:1 at bifurcations | `analog_image_generator.geologic_generators._create_braided_bar(x: int, y: float, length: float, width: float, height: int, width: int) -> NDArray` | `notebooks/fluvial_braided.ipynb#anchor-fluvial-braided-bars`
```

Add to Anastomosing section:
```markdown
## Fluvial (Anastomosing) — Physics-Based
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Anastomosing | Avulsion-connected network with gradient advantage | `analog_image_generator.geologic_generators.anasto_network_avulsion(height: int, width: int, branch_count: int, rng: np.random.Generator) -> tuple[NDArray, list, list]` | `notebooks/fluvial_anastomosing.ipynb#anchor-fluvial-anasto-avulsion`
Anastomosing | Low sinuosity channels S ∈ [1.0, 1.3] | `analog_image_generator.geologic_generators._create_low_sinuosity_channel(height: int, width: int, base_y: float, rng: np.random.Generator, sinuosity_range: tuple) -> NDArray` | `notebooks/fluvial_anastomosing.ipynb#anchor-fluvial-anasto-low-sinuosity`
```

Add new Physics Validation section:
```markdown
## Physics Validation
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
All | Physics constraint validation framework | `analog_image_generator.physics_validation.validate_meandering(...)` / `validate_braided(...)` / `validate_anastomosing(...)` | `notebooks/fluvial_validation.ipynb#anchor-fluvial-validation`
All | Geometric helper functions | `analog_image_generator.geologic_generators.compute_local_curvature(...)` / `measure_wavelength(...)` / `measure_sinuosity(...)` | `notebooks/utilities.ipynb#anchor-utilities-geometry`
```

Also update `docs/PALETTES.md` if not already including pointbar facies.

**Subtasks:**
- [ ] 1. Add Physics-Based Meandering Section to GEOLOGIC_RULES.md
- [ ] 2. Add Physics-Based Braided Section to GEOLOGIC_RULES.md
- [ ] 3. Add Physics-Based Anastomosing Section to GEOLOGIC_RULES.md
- [ ] 4. Add Physics Validation Section to GEOLOGIC_RULES.md
- [ ] 5. Verify PALETTES.md Includes pointbar Facies
- [ ] 6. Run validate_geo_anchors.py and Fix Any Discrepancies
- [ ] 7. Add Superseded Notes for Legacy Functions

**Test strategy:** Tests:
1. Run `python scripts/validate_geo_anchors.py` to verify all anchors are valid
2. Verify each code anchor exists in source (grep for function names)
3. Verify markdown table formatting is correct (lint)
4. Check that deprecated old functions are noted as superseded
5. Cross-reference with PRD to ensure all constraints are documented

## 12. Create Visual QA Notebook and Integration Tests [medium]

Create a comprehensive visual QA notebook that generates sample images for all fluvial styles, displays validation results, and provides side-by-side comparison with the old implementation. Also create pytest integration tests.

**Depends on:** 10, 11

Create `notebooks/fluvial_physics_qa.ipynb`:

```python
# Cell 1: Setup
import numpy as np
import matplotlib.pyplot as plt
from analog_image_generator import geologic_generators as gg
from analog_image_generator import physics_validation as pv
from analog_image_generator import utils

# Cell 2: Meandering Comparison
"""## Meandering: Old vs Physics-Based

Compare the original sinusoidal implementation with the new arc-based physics implementation.
"""
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Old implementation (if kept for comparison)
params_old = {'height': 512, 'width': 512, 'seed': 42, 'style': 'meandering'}
# gray_old, masks_old = gg.generate_meandering_old(params_old, utils.seeded_rng(42))

# New physics implementation
params_new = {'height': 512, 'width': 512, 'seed': 42, 'style': 'meandering'}
rng = utils.seeded_rng(42)
gray_new, masks_new = gg.generate_meandering(params_new, rng)

# Validate
validation = pv.validate_meandering(
    masks_new['_centerline'],
    masks_new,
    masks_new['_channel_width'],
    cutoff_locations=masks_new.get('_oxbow_cutoffs')
)

# Display results
axes[0, 0].imshow(gray_new, cmap='gray')
axes[0, 0].set_title('Grayscale Output')

axes[0, 1].imshow(masks_new['channel'], cmap='Blues')
axes[0, 1].set_title('Channel Mask')

axes[0, 2].imshow(masks_new.get('pointbar', np.zeros_like(gray_new)), cmap='Oranges')
axes[0, 2].set_title('Point Bar Mask (NEW!)')

axes[1, 0].imshow(masks_new.get('scroll_bar', np.zeros_like(gray_new)), cmap='Purples')
axes[1, 0].set_title('Scroll Bars (in point bars only)')

axes[1, 1].imshow(masks_new.get('oxbow', np.zeros_like(gray_new)), cmap='Greens')
axes[1, 1].set_title('Oxbows (meander loop shapes)')

axes[1, 2].imshow(masks_new.get('levee', np.zeros_like(gray_new)), cmap='YlOrBr')
axes[1, 2].set_title('Levees (exponential decay)')

plt.tight_layout()

# Cell 3: Validation Results
"""## Validation Results

Physics constraints validation for the generated image.
"""
print("=" * 60)
print("MEANDERING VALIDATION RESULTS")
print("=" * 60)
print(f"Overall: {'PASSED ✓' if validation.all_passed else 'FAILED ✗'}")
print()
for field_name in ['wavelength_ratio', 'curvature_ratio', 'sinuosity', 
                   'point_bars_inner_only', 'scroll_bars_in_point_bars',
                   'oxbows_at_cutoffs', 'levee_exponential', 'width_bend_variation']:
    result = getattr(validation, field_name)
    status = '✓' if result.passed else '✗'
    print(f"{status} {result.constraint_name}")
    print(f"   Measured: {result.measured_value:.3f}")
    print(f"   Expected: {result.expected_range}")
    print()

# Cell 4: Batch Validation
"""## Batch Validation (100 seeds)

Validate physics constraints across 100 different seeds.
"""
pass_counts = {}
for seed in range(100):
    rng = utils.seeded_rng(seed)
    gray, masks = gg.generate_meandering(params_new | {'seed': seed}, rng)
    val = pv.validate_meandering(masks['_centerline'], masks, masks['_channel_width'])
    for field_name in ['wavelength_ratio', 'curvature_ratio', 'sinuosity', 'point_bars_inner_only']:
        result = getattr(val, field_name)
        key = result.constraint_name
        if key not in pass_counts:
            pass_counts[key] = 0
        if result.passed:
            pass_counts[key] += 1

print("Pass rates across 100 seeds:")
for key, count in pass_counts.items():
    print(f"  {key}: {count}%")
```

Create `tests/test_physics_generators.py`:

```python
import numpy as np
import pytest
from analog_image_generator import geologic_generators as gg
from analog_image_generator import physics_validation as pv
from analog_image_generator import utils


class TestMeanderingPhysics:
    @pytest.fixture
    def meandering_output(self):
        params = {'height': 512, 'width': 512, 'seed': 42}
        rng = utils.seeded_rng(42)
        return gg.generate_meandering(params, rng)
    
    def test_wavelength_constraint(self, meandering_output):
        gray, masks = meandering_output
        centerline = masks['_centerline']
        channel_width = masks['_channel_width']
        measured = pv.measure_wavelength(centerline)
        ratio = measured / channel_width
        assert 9.0 <= ratio <= 15.0, f"Wavelength ratio {ratio} outside [9, 15]"
    
    def test_point_bars_exist(self, meandering_output):
        gray, masks = meandering_output
        assert 'pointbar' in masks, "Point bar mask missing"
        assert masks['pointbar'].sum() > 0, "No point bars generated"
    
    def test_point_bars_inner_only(self, meandering_output):
        gray, masks = meandering_output
        validation = pv.validate_meandering(
            masks['_centerline'], masks, masks['_channel_width']
        )
        assert validation.point_bars_inner_only.passed
    
    def test_oxbows_not_circular(self, meandering_output):
        gray, masks = meandering_output
        # Oxbows should have aspect ratio > 2 (elongated, not circular)
        oxbow = masks.get('oxbow', np.zeros((512, 512)))
        if oxbow.sum() > 0:
            ys, xs = np.where(oxbow > 0.5)
            if len(xs) > 10:
                extent_x = xs.max() - xs.min()
                extent_y = ys.max() - ys.min()
                aspect = max(extent_x, extent_y) / (min(extent_x, extent_y) + 1)
                assert aspect > 1.5, f"Oxbow too circular: aspect={aspect}"


class TestBraidedPhysics:
    def test_channels_split_merge(self):
        params = {'height': 512, 'width': 512, 'seed': 42, 'style': 'braided'}
        rng = utils.seeded_rng(42)
        gray, masks = gg.generate_braided(params, rng)
        metadata = masks.get('_network_metadata', [])
        bifurcations = [m for m in metadata if m['event'] == 'bifurcation']
        confluences = [m for m in metadata if m['event'] == 'confluence']
        assert len(bifurcations) > 0, "No bifurcations in braided network"


@pytest.mark.parametrize("seed", range(10))
def test_meandering_batch_validation(seed):
    params = {'height': 512, 'width': 512, 'seed': seed}
    rng = utils.seeded_rng(seed)
    gray, masks = gg.generate_meandering(params, rng)
    validation = pv.validate_meandering(
        masks['_centerline'], masks, masks['_channel_width']
    )
    assert validation.wavelength_ratio.passed
    assert validation.sinuosity.passed
```

**Subtasks:**
- [ ] 1. Create fluvial_physics_qa.ipynb with Comparison Visualizations
- [ ] 2. Create tests/test_physics_generators.py with Parametrized Tests
- [ ] 3. Implement Batch Validation Framework with 100-Seed Sweeps and CI Integration

**Test strategy:** Meta-tests (tests for the test infrastructure):
1. All notebook cells execute without error
2. Batch validation completes in <5 minutes for 100 seeds
3. Test coverage report shows >80% coverage of new physics functions
4. Visual outputs render correctly (no blank images)
5. CI integration: tests run on every PR
