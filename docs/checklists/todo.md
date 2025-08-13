# Unified TODO

This checklist gathers outstanding tasks from the project specification and maintenance notes. Items are grouped by theme and ordered by priority.

## Refactoring & Maintenance
- [x] **High** Refactor `AIBehaviorNode` by separating planning, navigation and economic interactions.
- [x] **High** Introduce a configurable state machine or behaviour tree for `AIBehaviorNode`.
- [x] **High** Resolve `AIBehaviorNode` references during loading to avoid repeated lookups.
- [ ] **Medium** Parameterise durations, speeds and thresholds via configuration files.
- [ ] **Medium** Replace `_manual_update` flag with explicit update control in `SimNode` to avoid deep call chains.
- [ ] **Low** Add duplicate detection and error handling to the plugin registry.
- [ ] **Low** Optimise configuration loader by reducing runtime introspection and enforcing JSON schema validation.
- [ ] **Low** Replace global constants file with structured configuration supporting dynamic overrides.

## Core Engine Enhancements
- [ ] **Medium** Hot-reload node logic without restarting simulations.
- [ ] **Medium** State diffing and time-travel debugging for deterministic replay.
- [ ] **Medium** Implement `decrease_rate` in `NeedNode` and cache scheduler lookup.
- [ ] **Medium** Refactor `SchedulerSystem` to avoid manipulating node internals and to use a priority-based queue with pause/prioritisation API.
- [ ] **Low** Extend `DistanceSystem` with persistent caching and 3D position support.
- [ ] **Low** Allow `TimeSystem` to configure day length and support global pause or external clocks.

## Tools for Creation
- [x] **High** Command-line tool to scaffold new node or system plugins from templates.
- [ ] **Medium** Schema validation utility for configuration files (YAML/JSON).
- [ ] **Low** Graphical node editor allowing drag-and-drop composition and export to declarative configs.
    - [ ] **Low** Basic UI to add/remove nodes and edit properties.
    - [ ] **Low** Live simulation preview panel.
    - [ ] **Low** Plugin manager to enable/disable community packages.
- [ ] **Low** Repository or marketplace for sharing community-created nodes and scenarios.
- [ ] **Low** Configuration auto-completion and linting support for editors.
- [ ] **Low** Behaviour scripting DSL with a safe sandbox.

### Map Editor & Scenario Builder
- [ ] Clarify documentation: editor handles spatial layout while scenarios add behaviour and systems.
- [ ] Generic scenario builder supporting multiple profiles (farm, quest, battle…).
- [ ] Load and edit existing maps or scenarios from JSON.
- [ ] In-editor property panel to configure node attributes.
- [ ] Visual linking tool to define dependencies between nodes.
- [ ] Scenario profiles and presets for different genres.
- [ ] Export extended to include properties and links with plugin-based validation.
- [ ] Optional simulation preview launched directly from the editor.
- [ ] Refactor map editor into UI, node management and serialisation modules.
- [ ] Dynamic form generation for node-specific properties.
- [ ] Graphical module to manage and display links between nodes.
- [ ] Round-trip tests and CLI to combine map layouts with scenario profiles.
- [ ] Documentation and examples for non-farm scenarios.

## Visualization and Rendering
- [ ] **Medium** Extend the Pygame viewer with camera controls, zoom and overlays.
- [ ] **Low** Headless rendering mode that streams frames or state for remote dashboards.
- [ ] **Low** Web-based viewer (WebGL/Canvas) to observe simulations in the browser.
- [ ] **Low** Optional 3D rendering backend with automatic asset mapping from node properties.
- [ ] **Low** Recording and replay tool to capture simulation sessions.
- [ ] **Low** VR/AR viewer for immersive observation.

## Advanced Simulation Mechanics
- [ ] **Medium** Extend `WeatherSystem` to influence production rates and character behaviour.
- [ ] **Low** Animal nodes with needs, reproduction and resource generation.
- [ ] **Low** Advanced dynamic economy with market events and complex price fluctuations.
- [ ] **Low** Quest or objective system using dedicated `QuestNode` types.
- [ ] **Low** Combat mechanics including equipment, damage and defence systems.
- [ ] **Low** Behaviour tree library for complex AI decision making.
- [ ] **Low** Modular skill/experience progression for characters.
- [ ] **Low** Procedural world generation for terrain and events.

## Scenario & Narrative Development
- [ ] **Low** Campaign framework to chain multiple scenarios with persistence.
- [ ] **Low** Event scripting language for cutscenes and triggers.
- [ ] **Low** Save/load system for long-running worlds and branching paths.
- [ ] **Low** Optional multiplayer or networked simulation support.
- [ ] **Low** Social relationship system tracking friendships and rivalries.

## Infrastructure & Performance
- [x] **High** Continuous integration pipeline running tests, linting and type checks.
- [ ] **Medium** Benchmark suite with automated performance regression alerts.
- [ ] **Medium** Plugin versioning and compatibility management.
- [ ] **Medium** Packaging and distribution on PyPI with semantic versioning.
- [ ] **Low** Telemetry export to monitor performance and state.
- [ ] **Low** Plugin sandboxing and permission system.

## Documentation & Community
- [x] **High** Expand [project_spec.md](../specs/project_spec.md) with concrete examples for every node and system type.
- [x] **High** Write step-by-step tutorials and how-to guides.
- [x] **Medium** Publish contribution guidelines and a code of conduct.
- [ ] **Medium** Launch a documentation website with interactive examples and API reference.
- [ ] **Low** Organise community challenges to create and share new scenarios.
- [ ] **Low** Auto-generated API reference using Sphinx.
- [ ] **Low** Example scenario pack demonstrating diverse use cases.
