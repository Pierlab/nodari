# War Simulation Guide

This guide explains how to run and experiment with the war simulation.

## Running the simulation

```
python run_war.py [config.json] [settings.json]
```

- **config.json**: world layout and initial entities.
- **settings.json**: simulation parameters such as unit size or terrain presets.

The default files in the `example/` directory are used when no arguments are
supplied.

## Controls

- `Space` – advance the simulation by one tick.
- `P` – toggle continuous play.
- `Q` – quit the viewer.

## Extending

Nodes and systems are loaded through the plugin mechanism. New units or gameplay
systems can be added by creating new modules and registering them with
`core.plugins.register_node_type` or `register_system_type`.
