# Farm Simulation Engine

This project aims to build a modular simulation engine for farm scenarios and beyond. It is designed around reusable nodes, a plugin system and declarative configuration.

Project objectives, current progress and the complete roadmap live in [project_spec.md](docs/specs/project_spec.md). The document centralises goals, completed work and upcoming tasks.

An example configuration file `example_farm.json` demonstrates a minimal world setup loaded via the declarative loader.

Configurations are validated against a schema to catch structural errors early and ensure community scenarios remain consistent.

Configurations may include a `seed` in the `WorldNode` configuration to ensure
deterministic simulations.

The engine includes a `LoggingSystem` that prints selected events, offering a basic way to observe simulations from the console. A `DistanceSystem` computes distances between positioned nodes to support spatial reasoning.

All map coordinates, distances and speeds in the simulation use meters as the
base unit. Velocities are expressed in meters per second. Utility conversion
helpers (kilometres, km/h, square kilometres…) live in `core/units.py`.

Runtime parameters such as time scaling, initial time, display sizes and map
dimensions are centralised in `config.py`. By default the simulation advances
one simulated minute per real second and starts at 07:30.

## Running the simulation

After installing the dependencies, launch the Pygame-powered example farm:

```
python run_farm.py
```

The window renders terrain tiles, unit icons and yellow arrows pointing to their movement targets.

For a minimal war scenario showcasing nations, armies and real‑time combat, run:

```
python run_war.py example/war_simulation_config.json
```

Pause the simulation with the space bar and close the window or press the close button to exit.

## Map editor

An interactive map editor is provided in `tools/map_editor.py` to create
layout files for new simulations. Launch it with:

```
python tools/map_editor.py [output.json] [keymap.json] [existing_map.json]
```

Use the mouse to place objects on the map. Number keys `1`–`6` switch between
building types while `M` and `F` select male or female characters. Press `S` to
enter selection mode and use the arrow keys to resize the highlighted building.
Right‑click deletes the topmost item under the cursor and pressing `Z` undoes
the most recent placement. Export the map at any time with `E` or simply close
the window to write the chosen JSON file. The editor writes `WorldNode` JSON
with each building or character entry containing its `type` and grid
`position`. A minimal example with a single barn looks like:

```json
{
  "world": {
    "type": "WorldNode",
    "config": {"width": 100, "height": 100},
    "children": [
      {
        "type": "BarnNode",
        "id": "building1",
        "config": {"position": [10, 20]}
      }
    ]
  }
}
```

The editor focuses purely on spatial layout. To turn an exported map into a
complete scenario, run:

```
python tools/build_scenario.py custom_map.json scenario.json [profile]
```

`build_scenario.py` adds inventories and the core systems (time, economy,
viewer…) to the map file based on the selected `profile` (default: `farm`).
The editor's pixel scale and world dimensions are
controlled by `SCALE`, `WORLD_WIDTH` and `WORLD_HEIGHT` in `config.py`.

## Development

* Python 3.11+
* Install dependencies listed in `requirements.txt`
* Run checks with `flake8`, `mypy` and `pytest`
* See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines and the [Code of Conduct](CODE_OF_CONDUCT.md)

Continuous integration is currently disabled, so run all checks locally.

## Roadmap and Tasks

Project objectives, completed milestones and remaining tasks are tracked in [project_spec.md](docs/specs/project_spec.md). A high-level view of upcoming features also appears in [TODO.md](docs/checklists/todo.md).

For details on configurable parameters of each node and system, see the generated [parameter inventory](docs/parameter_inventory.md).

## Future Possibilities

Thanks to its modular design, the engine can ultimately power a wide range of simulations:

- City management with trade routes and citizen behaviours.
- Ecosystem and wildlife balance studies.
- Space-colony survival with life‑support management.
- Historical recreations exploring alternate timelines.
- Educational labs demonstrating economic or ecological principles.

## License

MIT
