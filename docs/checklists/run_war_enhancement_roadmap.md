# Run War Enhancement Roadmap

This checklist guides the next iteration on `run_war.py` and related modules.
It focuses on more realistic unit interactions, smarter army movement, centralized
configuration and UI improvements. Tasks are organized to fit Nodari's modular
architecture as described in `docs/specs/project_spec.md`.

## 1. Combat Engagement Fix
- [x] Update movement/combat integration so opposing units stop and fight when
  entering the same tile.
- [x] Ensure combat blocks tiles for other units until resolution.
- [x] Add regression test verifying units no longer pass through each other.

## 2. Army AI and Movement
- [x] Implement cautious advance behaviour for generals and subordinate units:
  - [x] Determine general direction of enemy capital but explore terrain step by step.
  - [x] Use pathfinding and terrain awareness rather than straight-line movement.
- [x] Allow non-frontline troops to remain at capital unless commanded.
- [x] Write tests for basic exploration logic.

## 3. Central Simulation Parameters
- [x] Introduce a dedicated settings file with a `parameters` section collecting
  key simulation values (e.g., unit sizes, vision radius, AI flags).
- [x] Load these parameters in `run_war.py` and expose them to systems via `SimParams`.
- [x] Document parameter meanings in the file and in `docs/parameter_inventory.md`.

## 4. Menu Buttons for Live Parameters
- [x] In the viewer menu, add +/- buttons next to parameters that already have
  keyboard bindings.
- [x] Buttons trigger the same handlers as keyboard shortcuts for consistency.
- [x] Update on-screen help panel to show both keyboard and button controls.

## 5. Terrain Generation (Checklist §2)

### 5.1 Code Organization
- [x] Create `tools/terrain_generators.py` containing pure functions:
  - [x] `generate_base(width, height, fill="plain")`
  - [x] `carve_river(tiles, *, start, end, width_min, width_max, meander, obstacles_set)`
  - [x] `place_lake(tiles, *, center, radius, irregularity)`
  - [x] `place_forest(tiles, *, total_area_pct, clusters, cluster_spread)`
  - [x] `place_mountains(tiles, *, total_area_pct, perlin_scale, peak_density, altitude_map_out=None)`
  - [x] `place_swamp_desert(tiles, *, swamp_pct, desert_pct, clumpiness)`
  - [x] Each function returns updated `tiles` and an `obstacles_set`.

### 5.2 Integration
- [x] Extend `nodes/terrain.py` with optional `altitude_map` and `get_altitude` helper.
- [x] Replace `_generate_terrain()` in `run_war.py` with a pipeline using the new
  generator functions. Respect existing speed modifiers and combat bonuses.
- [x] Wire terrain parameters through `SimParams` and keyboard/menu controls.

### 5.3 Config Keys
- [x] Allow terrain features to be configured in world JSON (optional keys):
  - [x] `rivers: [{start, end, width_min, width_max, meander}]`
  - [x] `lakes: [{center, radius, irregularity}]`
  - [x] `forests: {total_area_pct, clusters, cluster_spread}`
  - [x] `mountains: {total_area_pct, perlin_scale, peak_density}`
  - [x] `swamp_desert: {swamp_pct, desert_pct, clumpiness}`
  - [x] `obstacle_altitude_threshold`
- [x] Update example configs to show new parameters.
- [x] Add tests for terrain generation ensuring rivers are contiguous and
  obstacles match altitude thresholds.

---

Use this roadmap as a reference for future pull requests. Check off items as
they are completed.
