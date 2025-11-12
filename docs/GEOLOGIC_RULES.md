# Geologic Rules Index — Principle → Code Anchors

Purpose: Provide traceability from documented geologic principles to concrete function anchors in `src/` and corresponding anchor cells in notebooks.

Usage:
- Keep entries short and specific. One principle per row.
- The Code Anchor should match a function name (and optional note) that appears in code and notebooks.
- When you change code, update this file and the matching notebook markdown cell.
- Anchor IDs follow the format `notebooks/<env>.ipynb#anchor-<env>-<principle>`, using lowercase kebab-case for the principle segment.

## Fluvial (Meandering)
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Meandering | Sinuous belt from control points | `analog_image_generator.geologic_generators.meander_centerline(H: int, W: int, n_ctrl: int, amp_range: tuple[float, float], drift_frac: float) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-meander-centerline`
Meandering | Variable bankfull width along belt | `analog_image_generator.geologic_generators.meander_variable_channel(centerline: NDArray, shape: NDArray, w0: float, w1: float) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-variable-width`
Meandering | Levees as rim via dilation | `analog_image_generator.geologic_generators.add_levees(chan: NDArray, iterations: int) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-levees`
Meandering | Scroll-bar banding (cosine of distance bands) | `analog_image_generator.geologic_generators.add_scroll_bars(chan: NDArray, lambda_px: float) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-scroll-bars`
Meandering | Oxbow/clay plug at neck cutoff | `analog_image_generator.geologic_generators.add_oxbow(centerline: NDArray, shape: NDArray, neck_tol: float) -> NDArray` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-oxbow`
Meandering | Compose facies and grayscale | `analog_image_generator.geologic_generators.compose_meandering(gray: NDArray, masks: dict[str, NDArray]) -> tuple[NDArray, dict[str, NDArray]]` | `notebooks/fluvial_meandering.ipynb#anchor-fluvial-compose`

## Fluvial (Braided)
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Braided | Multi-threads across belt | `analog_image_generator.geologic_generators.braided_threads(H: int, W: int, thread_count: int, mean_width: float) -> NDArray` | `notebooks/fluvial_braided.ipynb#anchor-fluvial-braided-threads`
Braided | Bar spacing ≈ 4–5× mean width | `analog_image_generator.geologic_generators.seed_bars(shape: NDArray, spacing_px: float, length_scale: float, width_scale: float) -> NDArray` | `notebooks/fluvial_braided.ipynb#anchor-fluvial-bar-spacing`
Braided | Chutes cross-cut bars | `analog_image_generator.geologic_generators.add_chutes(shape: NDArray, n_chutes: int) -> NDArray` | `notebooks/fluvial_braided.ipynb#anchor-fluvial-chutes`
Braided | Compose facies and grayscale | `analog_image_generator.geologic_generators.compose_braided(gray: NDArray, masks: dict[str, NDArray]) -> tuple[NDArray, dict[str, NDArray]]` | `notebooks/fluvial_braided.ipynb#anchor-fluvial-braided-compose`

## Fluvial (Anastomosing)
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Anastomosing | Narrow, stable channels | `analog_image_generator.geologic_generators.anasto_paths(H: int, W: int, branch_count: int) -> NDArray` | `notebooks/fluvial_anastomosing.ipynb#anchor-fluvial-anasto-paths`
Anastomosing | Levees for narrow channels | `analog_image_generator.geologic_generators.add_levees_narrow(chan: NDArray, iterations: int) -> NDArray` | `notebooks/fluvial_anastomosing.ipynb#anchor-fluvial-anasto-levees`
Anastomosing | Wetlands from distance + base quantile | `analog_image_generator.geologic_generators.make_marsh(chan: NDArray, base: NDArray, quantile: float) -> NDArray` | `notebooks/fluvial_anastomosing.ipynb#anchor-fluvial-anasto-marsh`
Anastomosing | Fans at levee breaches | `analog_image_generator.geologic_generators.seed_fans(chan: NDArray, n_fans: int, a_rng: tuple[float, float], b_rng: tuple[float, float]) -> NDArray` | `notebooks/fluvial_anastomosing.ipynb#anchor-fluvial-anasto-fans`
Anastomosing | Compose facies and grayscale | `analog_image_generator.geologic_generators.compose_anasto(gray: NDArray, masks: dict[str, NDArray]) -> tuple[NDArray, dict[str, NDArray]]` | `notebooks/fluvial_anastomosing.ipynb#anchor-fluvial-anasto-compose`

## Fluvial (Sedimentary Structures & Petrology)
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Fluvial | Channel-fill deposits with erosional bases | `analog_image_generator.geologic_generators.channel_fill_sandstone(chan_mask: NDArray, erosion_depth: float) -> dict[str, NDArray]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-channel-fill`
Fluvial | Fining-upward sequences | `analog_image_generator.geologic_generators.apply_fining_upward_profile(stack: NDArray, lag_fraction: float) -> NDArray` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-fining-upward`
Fluvial | Trough & planar cross-bedding overlays | `analog_image_generator.geologic_generators.add_cross_bedding(texture: NDArray, mode: Literal["trough","planar"]) -> NDArray` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-cross-bedding`
Fluvial | Ripple marks (lower-energy flow) | `analog_image_generator.geologic_generators.add_ripple_marks(surface: NDArray, wavelength_px: float) -> NDArray` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-ripple-marks`
Fluvial | Lateral accretion surfaces (point bars) | `analog_image_generator.geologic_generators.lateral_accretion_surfaces(centerline: NDArray, floodplain_mask: NDArray) -> dict[str, NDArray]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-lateral-accretion`
Fluvial | Massive-type sandstones (high-energy bars/overbank) | `analog_image_generator.geologic_generators.massive_sandstone_overbank(bar_mask: NDArray, thickness_px: float) -> NDArray` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-massive-sandstone`
Fluvial | Overbank deposits, paleosols, ponded fines | `analog_image_generator.geologic_generators.simulate_overbank_deposits(floodplain_mask: NDArray, paleosol_rate: float) -> dict[str, NDArray]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-overbank`
Fluvial | Particle shape smoothing | `analog_image_generator.geologic_generators.model_particle_shapes(seed: int, aspect_ratio: tuple[float,float]) -> NDArray` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-particle-shape`
Fluvial | Mineralogy constraints (feldspar/kaolinite rich, glauconite absent) | `analog_image_generator.geologic_generators.enforce_mineralogy(masks: dict[str, NDArray], mineral_profile: dict[str, float]) -> dict[str, float]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-mineralogy`
Fluvial | Cement signatures (clay clasts, kaolinite cement) | `analog_image_generator.geologic_generators.apply_cementation_rules(lag_mask: NDArray, clay_fraction: float) -> dict[str, float]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-cement`
Fluvial | Scour surfaces and mud clasts | `analog_image_generator.geologic_generators.stamp_scour_surfaces(chan_mask: NDArray, frequency: float) -> dict[str, NDArray]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-scour`
Fluvial | Heterogeneity drivers (channel migration frequency) | `analog_image_generator.geologic_generators.compute_migration_heterogeneity(centerlines: list[NDArray]) -> dict[str, float]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-heterogeneity`
Fluvial | Paleocurrent statistics (unimodal/polymodal) | `analog_image_generator.geologic_generators.compute_paleocurrent_stats(centerline: NDArray) -> dict[str, float]` | `notebooks/fluvial_structures.ipynb#anchor-fluvial-paleocurrent`
## Aeolian (Barchan, Linear/Seif, Transverse)
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Aeolian | Crest/ridge generation by wind θ | `analog_image_generator.geologic_generators.aeolian_make_crests(base: NDArray, theta_deg: float, H: float, lambda_px: float, defect_rate: float) -> NDArray` | `notebooks/aeolian.ipynb#anchor-aeolian-crests`
Aeolian | Slipface orientation lee of wind | `analog_image_generator.geologic_generators.aeolian_add_slipfaces(crests: NDArray, theta_deg: float) -> NDArray` | `notebooks/aeolian.ipynb#anchor-aeolian-slipfaces`
Aeolian | Interdune corridors/fraction | `analog_image_generator.geologic_generators.aeolian_interdune(base: NDArray, f_interdune: float) -> NDArray` | `notebooks/aeolian.ipynb#anchor-aeolian-interdune`
Aeolian | Ridge continuity (linear/seif) | `analog_image_generator.geologic_generators.aeolian_ridge_continuity(crests: NDArray, q: float) -> float` | `notebooks/aeolian.ipynb#anchor-aeolian-ridge-continuity`
Aeolian | Inverse grading controls | `analog_image_generator.geologic_generators.aeolian_inverse_grading_profile(dune_mask: NDArray, invert: bool) -> NDArray` | `notebooks/aeolian.ipynb#anchor-aeolian-inverse-grading`
Aeolian | Cross-bedding & reactivation surfaces | `analog_image_generator.geologic_generators.aeolian_cross_bedding_masks(dune_mask: NDArray, dip_deg: float) -> dict[str, NDArray]` | `notebooks/aeolian.ipynb#anchor-aeolian-cross-bedding`
Aeolian | Grain rounding & surface texture trends | `analog_image_generator.geologic_generators.aeolian_grain_rounding(seed: int, transport_distance: float) -> dict[str, float]` | `notebooks/aeolian.ipynb#anchor-aeolian-rounding`
Aeolian | Impact craters / dissolution pits | `analog_image_generator.geologic_generators.aeolian_surface_impacts(mask: NDArray, intensity: float) -> NDArray` | `notebooks/aeolian.ipynb#anchor-aeolian-impacts`
Aeolian | Cementation (hematite/iron oxide palette) | `analog_image_generator.geologic_generators.aeolian_cementation(masks: dict[str, NDArray], cement_type: str) -> dict[str, str]` | `notebooks/aeolian.ipynb#anchor-aeolian-cement`
Aeolian | Compose facies and grayscale | `analog_image_generator.geologic_generators.compose_aeolian(gray: NDArray, masks: dict[str, NDArray]) -> tuple[NDArray, dict[str, NDArray]]` | `notebooks/aeolian.ipynb#anchor-aeolian-compose`

## Estuarine (Tide-, Wave-, Mixed-Dominated)
Env | Principle | Code Anchor | Notebook Anchor
--- | --- | --- | ---
Estuarine | Ebb/flood channels and tidal bars | `analog_image_generator.geologic_generators.estu_channels_and_bars(prism: float, sinuosity: float, mud_frac: float) -> dict[str, NDArray]` | `notebooks/estuarine.ipynb#anchor-estuarine-channels`
Estuarine | Wave-parallel bars / smoother shoreline | `analog_image_generator.geologic_generators.estu_wave_bars(wave_index: float, phi_deg: float) -> NDArray` | `notebooks/estuarine.ipynb#anchor-estuarine-wave-bars`
Estuarine | Mixed-energy dominance control δ | `analog_image_generator.geologic_generators.estu_mix(delta: float, tide_masks: dict, wave_masks: dict) -> dict[str, NDArray]` | `notebooks/estuarine.ipynb#anchor-estuarine-delta`
Estuarine | Shoreline curvature shaping | `analog_image_generator.geologic_generators.estu_shoreline_curvature(phi_deg: float, shoreline: NDArray) -> NDArray` | `notebooks/estuarine.ipynb#anchor-estuarine-curvature`
Estuarine | Compose facies and grayscale | `analog_image_generator.geologic_generators.compose_estuarine(gray: NDArray, masks: dict[str, NDArray]) -> tuple[NDArray, dict[str, NDArray]]` | `notebooks/estuarine.ipynb#anchor-estuarine-compose`

Maintenance:
- Keep this aligned with `src/` and notebook anchors. Update alongside code changes.
