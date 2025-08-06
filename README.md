# Farm Simulation Engine

This project aims to build a modular simulation engine for farm scenarios and beyond. It is designed around reusable nodes, a plugin system and declarative configuration.

See [project_spec.md](project_spec.md) for the full specification, architecture overview and roadmap.

An example configuration file `example_farm.json` demonstrates a minimal world setup loaded via the declarative loader.

The engine includes a `LoggingSystem` that prints selected events, offering a basic way to observe simulations from the console.

## Running the simulation

After installing the dependencies, launch the Pygame-powered example farm:

```
python run_farm.py
```

## Development

* Python 3.9+
* Install dependencies listed in `requirements.txt`
* Run tests with `pytest`

## License

MIT

## TODO

- Implement seed-based reproducibility for deterministic simulations.
