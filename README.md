# Farm Simulation Engine

This project aims to build a modular simulation engine for farm scenarios and beyond. It is designed around reusable nodes, a plugin system and declarative configuration.

Project objectives, current progress and the complete roadmap live in [project_spec.md](project_spec.md). The document centralises goals, completed work and upcoming tasks.

An example configuration file `example_farm.json` demonstrates a minimal world setup loaded via the declarative loader.

Configurations may include a `seed` in the `WorldNode` configuration to ensure
deterministic simulations.

The engine includes a `LoggingSystem` that prints selected events, offering a basic way to observe simulations from the console. A `DistanceSystem` computes distances between positioned nodes to support spatial reasoning.

## Running the simulation

After installing the dependencies, launch the Pygame-powered example farm:

```
python run_farm.py
```

## Development

* Python 3.9+
* Install dependencies listed in `requirements.txt`
* Run tests with `pytest`

## Roadmap and Tasks

Project objectives, completed milestones and remaining tasks are tracked in [project_spec.md](project_spec.md). A high-level view of upcoming features also appears in [TODO.md](TODO.md).

## Future Possibilities

Thanks to its modular design, the engine can ultimately power a wide range of simulations:

- City management with trade routes and citizen behaviours.
- Ecosystem and wildlife balance studies.
- Space-colony survival with life‑support management.
- Historical recreations exploring alternate timelines.
- Educational labs demonstrating economic or ecological principles.

## License

MIT
