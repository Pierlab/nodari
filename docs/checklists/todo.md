# Unified TODO

This checklist gathers outstanding tasks from the project specification and maintenance notes. Items are grouped by theme and ordered by priority.

## Refactoring & Maintenance
- [ ] **High** Refactor `AIBehaviorNode` by separating planning, navigation and economic interactions.
- [ ] **High** Introduce a configurable state machine or behaviour tree for `AIBehaviorNode`.
- [ ] **High** Resolve `AIBehaviorNode` references during loading to avoid repeated lookups.
- [ ] **Medium** Parameterise durations, speeds and thresholds via configuration files.

## Core Engine Enhancements
- [ ] **Medium** Hot-reload node logic without restarting simulations.
- [ ] **Medium** State diffing and time-travel debugging for deterministic replay.

## Tools for Creation
- [ ] **High** Command-line tool to scaffold new node or system plugins from templates.
- [ ] **Medium** Schema validation utility for configuration files (YAML/JSON).
- [ ] **Low** Graphical node editor allowing drag-and-drop composition and export to declarative configs.
    - [ ] **Low** Basic UI to add/remove nodes and edit properties.
    - [ ] **Low** Live simulation preview panel.
    - [ ] **Low** Plugin manager to enable/disable community packages.
- [ ] **Low** Repository or marketplace for sharing community-created nodes and scenarios.
- [ ] **Low** Configuration auto-completion and linting support for editors.
- [ ] **Low** Behaviour scripting DSL with a safe sandbox.

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
- [ ] **High** Continuous integration pipeline running tests, linting and type checks.
- [ ] **Medium** Benchmark suite with automated performance regression alerts.
- [ ] **Medium** Plugin versioning and compatibility management.
- [ ] **Medium** Packaging and distribution on PyPI with semantic versioning.
- [ ] **Low** Telemetry export to monitor performance and state.
- [ ] **Low** Plugin sandboxing and permission system.

## Documentation & Community
- [ ] **High** Expand [project_spec.md](../specs/project_spec.md) with concrete examples for every node and system type.
- [ ] **High** Write step-by-step tutorials and how-to guides.
- [ ] **Medium** Publish contribution guidelines and a code of conduct.
- [ ] **Medium** Launch a documentation website with interactive examples and API reference.
- [ ] **Low** Organise community challenges to create and share new scenarios.
- [ ] **Low** Auto-generated API reference using Sphinx.
- [ ] **Low** Example scenario pack demonstrating diverse use cases.
