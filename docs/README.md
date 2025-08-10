# Documentation Overview

This directory contains guides, specifications, checklists and prompts for the Nodari simulation engine.

## Guides
- [Setup visualization environment](guides/setup_visualization.md)
- [Simulation run mode](guides/run_mode.md)

## Specifications
- [Project specification](specs/project_spec.md)
- [Analysis report](specs/analysis_report.md)

## Checklists
- [Unified TODO](checklists/todo.md)
- [Maintenance checklist](checklists/maintenance.md)

## Prompts
- [Add a feature](prompts/adding_feature.md)
- [Select a task](prompts/task_selection.md)

Additional images live in the [images](images) folder.

## Map editor key bindings

The map editor (`tools/map_editor.py`) supports placing various building types. Use the number keys to select the current building:

- `1` – `HouseNode` (default)
- `2` – `BarnNode`
- `3` – `SiloNode`
- `4` – `PastureNode`
- `5` – `WellNode`
- `6` – `WarehouseNode`

Press `E` to export the current map to JSON.
