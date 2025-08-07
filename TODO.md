# TODO Roadmap

This document mirrors the roadmap in [project_spec.md](project_spec.md)
with ambitious, long‑term tasks. Items are grouped by theme and can be
checked off as the project evolves.

## Core Engine Enhancements

- [x] Implement seed-based reproducibility for deterministic simulations.
- [ ] Expand the event bus with priority levels and asynchronous
      dispatching.
- [ ] Support serialising and reloading full world state for snapshots
      and debugging.
- [ ] Provide a scheduling system to update nodes at different rates.
- [ ] Optimise the update loop for large simulations (profiling,
      micro‑benchmarks).
- [ ] Hot-reload node logic without restarting simulations.
- [ ] State diffing and time-travel debugging for deterministic replay.

## Tools for Creation

- [ ] Command-line tool to scaffold new node or system plugins from
      templates.
- [ ] Schema validation utility for configuration files (YAML/JSON).
- [ ] Graphical node editor allowing drag-and-drop composition and
      export to declarative configs.
  - [ ] Basic UI to add/remove nodes and edit properties.
  - [ ] Live simulation preview panel.
  - [ ] Plugin manager to enable/disable community packages.
- [ ] Repository or marketplace for sharing community-created nodes and
      scenarios.
- [ ] Configuration auto-completion and linting support for editors.
- [ ] Behaviour scripting DSL with a safe sandbox.

## Visualization and Rendering

- [ ] Extend the Pygame viewer with camera controls, zoom and
      overlays for inventories, needs and events.
- [ ] Headless rendering mode that streams frames or state for remote
      dashboards.
- [ ] Web-based viewer (WebGL/Canvas) to observe simulations in the
      browser.
- [ ] Optional 3D rendering backend (e.g., Panda3D) with automatic
      asset mapping from node properties.
- [ ] Recording and replay tool to capture simulation sessions.
- [ ] VR/AR viewer for immersive observation.

## Advanced Simulation Mechanics

- [ ] Weather and seasonal systems influencing production rates and
      character behaviour.
- [ ] Animal nodes with needs, reproduction and resource generation.
- [ ] Dynamic economy with fluctuating prices and market events.
- [ ] Quest or objective system using dedicated `QuestNode` types.
- [ ] Combat mechanics including equipment, damage and defence systems.
- [ ] Behaviour tree library for complex AI decision making.
- [ ] Modular skill/experience progression for characters.
- [ ] Procedural world generation for terrain and events.

## Scenario & Narrative Development

- [ ] Campaign framework to chain multiple scenarios with persistence.
- [ ] Event scripting language for cutscenes and triggers.
- [ ] Save/load system for long-running worlds and branching paths.
- [ ] Optional multiplayer or networked simulation support.
- [ ] Social relationship system tracking friendships and rivalries.

## Infrastructure & Performance

- [ ] Continuous integration pipeline running tests, linting and type
      checks.
- [ ] Benchmark suite with automated performance regression alerts.
- [ ] Plugin versioning and compatibility management.
- [ ] Packaging and distribution on PyPI with semantic versioning.
- [ ] Telemetry export to monitor performance and state.
- [ ] Plugin sandboxing and permission system.

## Documentation & Community

- [ ] Expand `project_spec.md` with concrete examples for every node and
      system type.
- [ ] Write step-by-step tutorials and how-to guides.
- [ ] Publish contribution guidelines and a code of conduct.
- [ ] Launch a documentation website with interactive examples and API
      reference.
- [ ] Organise community challenges to create and share new scenarios.
- [ ] Auto-generated API reference using Sphinx.
- [ ] Example scenario pack demonstrating diverse use cases.

