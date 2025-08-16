# War Simulation Roadmap Checklist

This roadmap breaks down the tasks required to build the simplified war simulation scenario on top of the Nodari engine. Each item provides enough context to implement the feature without referring back to the specs.

## Foundations
- [x] **Confirm engine setup** – Reuse the existing `SimNode`, event bus, systems and declarative loader from the core project.
- [x] **Create base configuration** – In `example/war_simulation_config.json`, describe two nations, their generals, starting armies (100 units each) and initial terrain layout.

## Domain Nodes
- [x] **NationNode** – Holds moral, capital position and references to generals and armies. Emits `moral_changed` and `capital_captured`.
- [x] **GeneralNode** – Stores tactical style (aggressive/defensive/balanced) and owns one or more armies. Listens to partial battlefield events due to fog of war.
- [x] **ArmyNode** – Groups `UnitNode`s, tracks goal (advance, defend, retreat) and current size. Interfaces with Movement and Combat systems.
- [x] **UnitNode** – Represents ~100 soldiers with state (moving, fighting, fleeing) and attributes such as speed and morale. Emits `unit_engaged` and `unit_routed`.
- [x] **TerrainNode** – Defines map tiles: plain, forest, hill. Influences movement speed and combat bonuses.

## Global Systems
- [x] **TimeSystem extension** – Support accelerated and real‑time modes for war scenarios.
- [x] **MovementSystem** – Moves units each tick toward targets while considering terrain speed modifiers, obstacles and morale penalties. Prepare for future hex‑grid pathfinding (initial version may use square grid).
- [x] **CombatSystem** – When opposing units occupy the same tile, resolve combat using unit size, randomness and terrain modifiers. Update unit states and nation morale.
- [x] **MoralSystem** – Aggregates morale changes from defeats, general losses and events. Triggers nation collapse at zero morale.
- [x] **Event Logging/Visualization System** – Provide clear real‑time or accelerated visualisation; for now log movements and combats, later connect to a dedicated viewer.

## Map & Positioning
- [x] **Grid selection** – Start with simple square grid; evaluate hexagonal grid for future upgrade.
- [x] **Initial placements** – Define starting positions for each nation's capital, generals and armies within the config file.
- [ ] **Obstacles** – Represent impassable terrain or temporary obstacles (e.g., rivers) in the map data.

## Behaviour & AI
- [ ] **General decision making** – Implement simple AI reacting to partial information, moral status and objectives.
- [ ] **Unit behaviour** – Units move toward targets, avoid obstacles, engage enemies or retreat when morale is low.
- [ ] **Surprise maneuvers** – Allow generals to attempt flanking moves with a success probability.

## Victory Conditions
- [ ] **Capital capture** – Detect when a sufficient number of allied units occupy the enemy capital tile.
- [ ] **Moral collapse** – End simulation if a nation's morale reaches zero.

## Visualization Enhancements (Later Iterations)
- [ ] **Zoom and inspect** – Ability to zoom into specific units or armies.
- [ ] **Clear map overlay** – Show terrain types, unit icons and movement arrows.
- [ ] **Optional hex grid rendering** – If hex grid adopted, update visualization accordingly.

## Extensions & Analysis
- [ ] **Export battle logs** – Save events for replay and analysis.
- [ ] **Future features** – Plan for fatigue, logistics, diverse unit types and strategic maneuvers.

