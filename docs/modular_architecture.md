# Modular Architecture

The simulation engine is built from loosely coupled nodes and systems.

- **Nodes** represent entities such as nations, armies or terrain. Each node
  inherits from `core.simnode.SimNode` and can emit or listen to events.
- **Systems** encapsulate global behaviours like combat resolution or pathfinding.
- **Plugins**: new nodes and systems are registered via the plugin mechanism,
  allowing features to be added without modifying core modules.

The war simulation packages these pieces under `simulation/war/` with separate
subpackages for nodes, systems, terrain generation and the viewer loop.
