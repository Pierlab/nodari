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
- [ ] Implement cautious advance behaviour for generals and subordinate units:
  - [ ] Determine general direction of enemy capital but explore terrain step by step.
  - [ ] Use pathfinding and terrain awareness rather than straight-line movement.
- [ ] Allow non-frontline troops to remain at capital unless commanded.
- [ ] Write tests for basic exploration logic.

## 3. Central Simulation Parameters
- [ ] Introduce a dedicated settings file with a `parameters` section collecting
  key simulation values (e.g., unit sizes, vision radius, AI flags).
- [ ] Load these parameters in `run_war.py` and expose them to systems via `SimParams`.
- [ ] Document parameter meanings in the file and in `docs/parameter_inventory.md`.

## 4. Menu Buttons for Live Parameters
- [ ] In the viewer menu, add +/- buttons next to parameters that already have
  keyboard bindings.
- [ ] Buttons trigger the same handlers as keyboard shortcuts for consistency.
- [ ] Update on-screen help panel to show both keyboard and button controls.

## 5. Terrain Generation (Checklist §2)

### 5.1 Code Organization
- [ ] Create `tools/terrain_generators.py` containing pure functions:
  - [ ] `generate_base(width, height, fill="plain")`
  - [ ] `carve_river(tiles, *, start, end, width_min, width_max, meander, obstacles_set)`
  - [ ] `place_lake(tiles, *, center, radius, irregularity)`
  - [ ] `place_forest(tiles, *, total_area_pct, clusters, cluster_spread)`
  - [ ] `place_mountains(tiles, *, total_area_pct, perlin_scale, peak_density, altitude_map_out=None)`
  - [ ] `place_swamp_desert(tiles, *, swamp_pct, desert_pct, clumpiness)`
  - [ ] Each function returns updated `tiles` and an `obstacles_set`.

### 5.2 Integration
- [ ] Extend `nodes/terrain.py` with optional `altitude_map` and `get_altitude` helper.
- [ ] Replace `_generate_terrain()` in `run_war.py` with a pipeline using the new
  generator functions. Respect existing speed modifiers and combat bonuses.
- [ ] Wire terrain parameters through `SimParams` and keyboard/menu controls.

### 5.3 Config Keys
- [ ] Allow terrain features to be configured in world JSON (optional keys):
  - [ ] `rivers: [{start, end, width_min, width_max, meander}]`
  - [ ] `lakes: [{center, radius, irregularity}]`
  - [ ] `forests: {total_area_pct, clusters, cluster_spread}`
  - [ ] `mountains: {total_area_pct, perlin_scale, peak_density}`
  - [ ] `swamp_desert: {swamp_pct, desert_pct, clumpiness}`
  - [ ] `obstacle_altitude_threshold`
- [ ] Update example configs to show new parameters.
- [ ] Add tests for terrain generation ensuring rivers are contiguous and
  obstacles match altitude thresholds.

---

Use this roadmap as a reference for future pull requests. Check off items as
they are completed.
