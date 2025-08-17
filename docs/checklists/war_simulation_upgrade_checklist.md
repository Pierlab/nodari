# Nodari – War Simulation Upgrade Checklist

> Goal: implement a more realistic, configurable large‑scale battle (km-scale map, richer terrain, hierarchical armies, fog of war & command/communication), while staying aligned with the current plugin/node/system architecture.

---

## 0) Conventions & Scope

- **Units of the world grid:** keep 1 grid unit = 1 meter (default), but allow a global **`WORLD_SCALE_M`** (meters per grid unit) in `config.py`.
- **Backward compatibility:** existing JSON configs continue to work; new keys are optional.
- **File layout preserved:** all new features are added as **new modules/systems/nodes** or **extensions** to existing ones, without breaking APIs.
- **Keyboard control:** add non-numeric keys only; keep existing mappings.

---

## 1) Map Scale & Distances (km between HQs)

- [x] **Add** in `config.py`:
  - [x] `WORLD_SCALE_M = 1.0`  # meters per grid unit (float)
  - [x] `DEFAULT_WORLD_W = 1000`, `DEFAULT_WORLD_H = 600` (example large map)
- [x] **Update** `example/war_simulation_config.json` to use larger `width/height` (e.g. 10_000 × 6_000) placing capitals 8–10 km apart.
- [x] **Viewer scale bar:** in `systems/pygame_viewer.py`, update the scale bar to compute label using `WORLD_SCALE_M` so the “100 m” annotation remains correct.
- [x] **Add runtime zoom/pan keys** (see §10 Controls).

---

## 2) Terrain Generators (rivières, lacs, forêts, montagnes, marais, désert)

### 2.1 Code Organization
- [x] **Create module** `tools/terrain_generators.py` with pure functions:
  - [x] `generate_base(width, height, fill="plain") -> List[List[str]]`
  - [x] `carve_river(tiles, *, start, end, width_min, width_max, meander, obstacles_set)`
  - [x] `place_lake(tiles, *, center, radius, irregularity)`
  - [x] `place_forest(tiles, *, total_area_pct, clusters, cluster_spread)`
  - [x] `place_mountains(tiles, *, total_area_pct, perlin_scale, peak_density, altitude_map_out=None)`
  - [x] `place_swamp_desert(tiles, *, swamp_pct, desert_pct, clumpiness)`
  - [x] Each function mutates/returns `tiles` and returns an **`obstacles_set`** to feed `TerrainNode.obstacles` (water & high mountains). 

### 2.2 Integration
- [x] **Extend** `nodes/terrain.py` (no breaking change):
  - [x] Keep current API. Add optional `altitude_map` attribute (2D float list) and new `get_altitude(x, y)` helper.
- [x] **Replace** `_generate_terrain()` in `run_war.py` with a **pipeline**:
  - [x] Start from `generate_base`.
  - [x] Apply features depending on parameters (exposed via keyboard & config).
  - [x] Set `terrain.tiles` and `terrain.obstacles` accordingly.
  - [x] Preserve/extend `speed_modifiers` and `combat_bonuses` (as done today).

### 2.3 Config keys (optional, with defaults)
- [x] In world config under the `TerrainNode` or `war_world.config.terrain_params`:
  - [x] `rivers: [{start:[x,y], end:[x,y], width_min:2, width_max:8, meander:0.3}]`
  - [x] `lakes: [{center:[x,y], radius:60, irregularity:0.4}]`
  - [x] `forests: {total_area_pct: 15, clusters: 6, cluster_spread: 0.6}`
  - [x] `mountains: {total_area_pct: 8, perlin_scale: 0.01, peak_density: 0.2}`
  - [x] `swamp_desert: {swamp_pct: 3, desert_pct: 5, clumpiness: 0.5}`
  - [x] `obstacle_altitude_threshold: 0.75`  # mountains above this are impassable

---

## 3) Army Hierarchy & Composition

### 3.1 New/Extended Nodes
- [x] **Add** `nodes/strategist.py` → `StrategistNode(SimNode)` (advises general; holds recon intel).
- [x] **Add** `nodes/officer.py` → `OfficerNode(SimNode)` (commands several units).
- [x] **Add** `nodes/bodyguard.py` → `BodyguardUnitNode(UnitNode)` (small elite protective unit; sticks to general).
- [x] **Extend** `GeneralNode`:
  - [x] attributes: `caution_level`, `intel_confidence` (0–1), `command_delay_s`
  - [x] API: `issue_orders(orders: list[dict])` that emits `order_issued` events down the tree.
  - [ ] Decision uses terrain intel & enemy sightings (see §5).
- [x] **ArmyNode** unchanged API; add `get_officers()` helper.

### 3.2 Spawning Structure (per your spec)
- [x] In `_spawn_armies` (or a new `tools/army_builder.py`):
  - [x] For each nation:
    - [x] 1 `GeneralNode` + 1 `StrategistNode` + **5 `BodyguardUnitNode`** (size configurable, e.g. 5–10).
    - [x] **5 `OfficerNode`**; each officer commands **4 units** of **5 soldiers**.
    - [x] Total ≈ 100 soldiers per army (+ escorts).
  - [x] **Dispersion parameter**: `spawn_dispersion_radius` (meters) around HQ; used when placing `TransformNode`s.
  - [x] **Soldiers per point**: `soldiers_per_dot`; `UnitNode.size` is multiple of this for rendering.

### 3.3 Viewer
- [x] In `systems/pygame_viewer.py`:
  - [x] Draw **role rings** (outline color/style per role): general, strategist, officer, bodyguard, soldier.
  - [x] Map size → radius: `radius = f(size, soldiers_per_dot)`.
  - [x] Add legend in side panel.

---

## 4) Combat Blocking & Pathfinding

- [x] **Add** `systems/pathfinding.py` (A* on grid using `TerrainNode.get_neighbors`, speed modifiers as costs).
- [x] **MovementSystem**:
  - [x] When a unit enters `fighting` state, mark its tile **temporarily blocked** to others (except same stack/formation).
  - [x] If `avoid_obstacles=True`, consult `PathfindingSystem` for detours when the next step is blocked.
- [x] **CombatSystem**:
  - [x] Already engages when two enemy units share a tile. Ensure units in `fighting` don’t “slide through” (freeze movement until resolved).

---

## 5) Fog of War, Recon & Intel

- [x] **Add** `systems/visibility.py`:
  - [x] Per unit: `vision_radius_m` (converted using `WORLD_SCALE_M`).
  - [x] Maintain **visible tiles per nation**; publish `enemy_spotted` events with timestamp & confidence.
- [x] **StrategistNode**:
  - [x] Subscribes to intel events, aggregates & filters by recency; exposes `get_enemy_estimates()`.
- [x] **GeneralNode._decide()**:
  - [x] Use `intel_confidence`, `caution_level` and terrain features to choose: `advance`, `flank`, `hold`, `retreat`.
  - [x] Integrate simple **course-of-action scorer** (terrain bonuses, numbers ratio, known enemy positions).

---

## 6) Command & Control (C2)

- [x] **Add** `systems/command.py`:
  - [x] Orders carry: `issuer_id`, `recipient_id/group`, `order_type` (`move`, `attack`, `hold`, `fallback`, `screen`, `probe`), `waypoints`, `time_issued`, `priority`.
  - [x] **Propagation with delays**: general → officers → units; delay = function(distance, terrain difficulty).
  - [x] **Reliability** parameter: chance orders are lost/delayed (optional noise).
  - [x] Units execute the **latest valid order**; report `order_ack`/`order_complete` upstream.

---

## 7) Logistics (optional but recommended)

- [ ] **Add** `systems/logistics.py`:
  - [ ] Each unit has `supply` (0–100). Movement & combat drain supply; resupply along **supply lines** to HQ or depots.
  - [ ] If `supply` low → speed & morale penalties.
- [ ] **nodes/depot.py`**: optional `DepotNode` with stock; visible on map; vulnerable target.

---

## 8) Configuration Schema Additions

- [x] Add a `war` section (or extend existing nodes) in JSON:
  - [x] `army_composition`: numbers of officers, units per officer, soldiers per unit, bodyguards per general.
  - [x] `spawn_dispersion_radius_m`: e.g. `200`.
  - [x] `soldiers_per_dot`: affects rendering radius.
  - [x] `vision_radius_m` (defaults per role).
  - [x] `command_delay_s`, `order_reliability`.
  - [x] `terrain_params` (see §2.3).
- [x] **Validate** with permissive loader: ignore unknown keys; log warnings.

---

## 9) Documentation & Examples

- [x] **docs/checklists/** → add `war_simulation_upgrade.md` (this file).
- [x] **docs/guides/** → add guide “Keyboard control & parameters on-the-fly”.
- [x] **example/** → add `war_simulation_config_km.json` showcasing:
  - [x] 10 km distance, large river, two forests (bosquets vs grande forêt), massif montagneux.
  - [x] 2×100 soldats + hiérarchie complète, brouillard de guerre, C2 activés.

---

## 10) Keyboard Controls (non‑numériques)

> Implement in `run_war.py` (event loop) + pass live parameters down to systems/viewer.

- **Simulation/time**
  - [ ] `SPACE` pause/continue (déjà en place).
  - [ ] `S` / `X` : diminuer/augmenter `TIME_SCALE` (déjà en place).
  - [ ] `[` / `]` : diminuer/augmenter `viewer.scale` (zoom).
  - [ ] `H/J/K/L` : pan view (←/↓/↑/→) by 10% of view (vim-like).

- **Terrain (while paused)**
  - [ ] `F/G` : −/+ densité globale (déjà en place).
  - [ ] `R` : regénérer *terrain pipeline* (REMPLACE l’actuel reset aléatoire).
  - [ ] `W` : −/+ **river width** (toggle through presets) & re‑carve rivers.
  - [ ] `M` : toggle *mountainousness* preset (low/med/high) → affects `total_area_pct` & obstacle threshold.
  - [ ] `V` : cycle forest layout (*bosquets* ↔ *immense forêt*) by adjusting `{clusters, cluster_spread, total_area_pct}`.

- **Armées / déploiement (while paused)**
  - [ ] `D` : *cluster* ↔ *spread* (déjà en place).
  - [ ] `P` / `O` : −/+ `spawn_dispersion_radius_m`.
  - [ ] `Q` / `A` : −/+ **troops per nation** (déjà A/Z; garder alias Q/A en AZERTY).
  - [ ] `Y/U` : −/+ variation de stats (déjà en place).
  - [ ] `E/T` : −/+ variation de vitesse (déjà en place).
  - [ ] `C` : cycle **soldiers_per_dot** (1, 2, 5, 10).

- **C2 / Intel**
  - [ ] `I` : toggle **fog of war**.
  - [ ] `;` : toggle **intel overlay** (dernier spot ennemi, cônes de vision).
  - [ ] `,` / `.` : −/+ `command_delay_s`.
  - [ ] `N` : order reliability preset (strict/reliable/flaky).

- **Affichage**
  - [ ] `B` : toggle **role rings & legend**.
  - [ ] `K` (already used for pan up per vim-like? If conflict, use `UP`/`DOWN` alt): ensure no numeric keys used.

> Keep an on‑screen **help panel** listing the active bindings when paused (extend `viewer.extra_info`).

---

## 11) Systems Wiring & Runtime Parameters

- [ ] In `run_war.py`:
  - [ ] Maintain a central **`SimParams`** dict (current values: dispersion, soldiers_per_dot, terrain presets, foW on/off, command delay…).
  - [ ] On key events, update `SimParams` and notify systems via method calls or events:
    - [ ] `viewer.set_render_params(...)`
    - [ ] `movement.set_blocking(True/False)`
    - [ ] `visibility.set_enabled(True/False)`
    - [ ] `command.set_delay(delay_s)`
    - [ ] `terrain_regen(params)` → rebuild tiles/obstacles in-place.
- [ ] Ensure all systems are discoverable as today (`load_plugins` + `core.loader`).

---

## 12) Tests & Validation

- [ ] **Unit tests** for:
  - [ ] Terrain carving functions (rivers contiguous, obstacle integrity).
  - [ ] Pathfinding cost monotonicity and obstacle avoidance.
  - [ ] Fog of war visibility masks.
  - [ ] Command delay & delivery order (FIFO per chain).
  - [ ] Combat blocking: no pass-through during `fighting`.
- [ ] **Smoke test script** `tools/build_scenario.py --preset war_km` producing a runnable world JSON.
- [ ] **Performance**: profile with 2×100 soldiers (and scalable to thousands). Optimize viewer draws (tile blitting cache).

---

## 13) Minimal Code Changes (pointers)

- [ ] `run_war.py`: replace `_generate_terrain` with pipeline call; add `SimParams`, richer `_spawn_armies` (or move to `tools/army_builder.py`), extend event loop.
- [ ] `systems/pygame_viewer.py`: role rings, dynamic scale bar using `WORLD_SCALE_M`, extra help panel, smooth zoom/pan.
- [ ] `nodes/*`: add Strategist/Officer/Bodyguard; extend General with C2 fields.
- [ ] `systems/*`: add `visibility.py`, `command.py`, `pathfinding.py`, `logistics.py` (optional), update `movement.py` and `combat.py` for blocking & pathfinding integration.
- [ ] `docs/*` & `example/*`: new example + user guide.

---

## 14) Done Criteria

- [ ] Two HQs **8–10 km apart** on a **single large map**.
- [ ] Rivers/lakes/forests/mountains rendered **coherently** (not pixel-noise), with adjustable presets live via keyboard.
- [ ] Each side: **1 general + 1 strategist + 5 bodyguards + 5 officers × (4×5) soldiers ≈ 100**; dispersion & dot‑scale adjustable.
- [ ] Units cannot pass through ongoing combats; pathfinding provides detours.
- [ ] Fog of war & intel overlays; decisions depend on intel confidence & caution.
- [ ] Orders propagate with delays and acknowledgements; reliability configurable.
- [ ] All major parameters **tweakable au clavier** (non-numériques), shown in the side panel.
