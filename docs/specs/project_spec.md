# Farm Simulation Engine Project Specification

## 1. Introduction and Objectives

The goal of this project is to build a modular simulation engine from scratch. The first scenario is a farm simulation where characters (farmers) produce resources such as wheat, manage needs like hunger and fatigue, interact with their environment and trade goods through a simple economy. The base should be generic enough to support future scenarios (adventure, war, full society, etc.).

The project is a community sandbox: building blocks called "nodes" must be reusable and configurable through declarative configuration files to ease the creation and sharing of simulations.

## 2. General Requirements
- **Modularity** – every entity or mechanic lives in an independent node reusable in different contexts.
- **Extensibility** – new node types (plugins) can be added without changing the core engine.
- **Replayability** – simulations should be deterministic through a seed.
- **Model / Render separation** – simulation logic is independent from any rendering engine. Rendering modules (e.g. with Pygame) are optional.
- **Declarative loading** – the simulation tree can be described in YAML or JSON and instantiated automatically.
- **Observability** – simulation state must be inspectable (state dumps, inventory levels, needs, weather, etc.).

## 3. Proposed Architecture

### 3.1 SimNode and Event Bus
The core structure is a tree of `SimNode` objects. Each node can have a parent and children and owns an event bus allowing nodes to emit and receive named events. Events can bubble up or down the tree and may stop propagation. The bus must allow:

- Registering/unregistering handlers by event type.
- Propagation to parents and/or children with stoppable propagation.
- Event timestamps or identifiers for debugging.

Every node provides:

- `update(dt)` – called each simulation tick (default calls child updates).
- `serialize()` – returns a serialised representation of the node and its children.
- `add_child(node)` / `remove_child(node)` – manage hierarchy.

### 3.2 Systems and Simulation Loops
Global behaviours live in `SystemNode` subclasses which traverse the tree or listen to events:
- **TimeSystem** – manages time flow (ticks, day/night cycles, seasons) and emits `tick` and `phase_changed` events.
- **EconomySystem** – listens to buy/sell events, transfers money and updates prices if necessary.
- **WeatherSystem** – determines current weather, emits events like `rain_started` or `drought` and exposes state.
- **DistanceSystem** – computes distances between nodes with positions, caches results each tick and answers distance queries in meters.
- **MovementSystem** – moves units toward targets while factoring in terrain
  modifiers, morale and impassable obstacles.

Example usage:

```python
from core.simnode import SimNode
from systems.time import TimeSystem
from systems.weather import WeatherSystem

root = SimNode("world")
time = TimeSystem(parent=root)
weather = WeatherSystem(parent=root)
```

### 3.3 Generic Nodes
For modelling the farm and inhabitants:
- **InventoryNode** – manages a stock of resources. Allows add/remove/transfer and emits `inventory_changed`.
- **NeedNode** – represents a need (hunger, fatigue). Holds current value, thresholds and change rates. Emits `need_threshold_reached` and `need_satisfied`.
- **ResourceProducerNode** – produces a resource every tick consuming optional inputs. Emits `resource_produced`.
- **AIBehaviorNode** – decides actions based on internal state and events (`need_threshold_reached`, `phase_changed`, etc.).
- **TransformNode** (optional) – stores position in meters and velocity in meters per second. Used to define initial placements for capitals, generals, armies and units in scenarios like the war simulation.
- **TerrainNode** – describes terrain tiles on a square or hex grid with
  movement and combat modifiers (`grid_type` defaults to ``square``) and
  an optional list of obstacle coordinates defining impassable tiles.
- **AnimalNode** – represents livestock or wildlife with needs and optional resource production. Emits events such as `animal_fed`.

Example usage:

```python
from nodes.inventory import InventoryNode
from nodes.need import NeedNode
from nodes.resource_producer import ResourceProducerNode
from nodes.ai_behavior import AIBehaviorNode
from nodes.transform import TransformNode
from nodes.animal import AnimalNode

inv = InventoryNode(items={"wheat": 10})
hunger = NeedNode(need_name="hunger", threshold=50, increase_rate=1)
producer = ResourceProducerNode(resource="wheat")
animal = AnimalNode(species="cow", hunger=hunger, producer=producer)
ai = AIBehaviorNode()
transform = TransformNode(position=[0, 0])
```

### 3.4 Composed Nodes
- **CharacterNode** – combines TransformNode, multiple NeedNodes, an InventoryNode and an AIBehaviorNode.
- **FarmNode** – inventory of wheat, resource producer for wheat, fixed properties like position/size.

Example:

```python
from nodes.character import CharacterNode
from nodes.farm import FarmNode

char = CharacterNode(name="farmer")
farm = FarmNode(name="farm")
```

### 3.5 Plugin Registry and Declarative Loader
Node classes live in Python modules and are registered in a plugin registry so that nodes can be instantiated by name. A loader reads YAML/JSON files describing the tree (`type`, `config`, `children`). Example YAML:
```yaml
world:
  type: WorldNode
  config:
    width: 200
    height: 200
  children:
    - type: FarmNode
      id: farm_001
      config:
        position: [50, 50]
        size: [20, 20]
      children:
        - type: InventoryNode
          config: { items: { wheat: 0 } }
        - type: ResourceProducerNode
          config: { resource: wheat, rate_per_tick: 1 }
    - type: CharacterNode
      id: farmer_001
      config:
        name: Jean
        position: [10, 10]
      children:
        - type: NeedNode
          config: { name: faim, threshold: 50, increase_rate: 1 }
        - type: NeedNode
          config: { name: fatigue, threshold: 70, increase_rate: 0.5 }
        - type: InventoryNode
          config: { items: {} }
        - type: AIBehaviorNode
```

## 4. Implementation Plan
Steps must be completed in order, each with accompanying unit tests.

### Step 1: Project Initialisation
- Set up Git repository, Python environment (>=3.9), linting (flake8) and pytest.
- Adopt PEP 8 style, use docstrings, explicit variable names in English.
- Add README explaining project and structure.
- Add `requirements.txt` (standard library for now; Pygame may come later).

### Step 2: SimNode and Event Bus
- Create `core/simnode.py` with attributes `name`, `parent`, `children`.
- Implement `add_child`, `remove_child`, `update`, `serialize`.
- Implement event bus (`emit`, `on_event`, `off_event`) with propagation rules.
- Create abstract `SystemNode` derived from `SimNode`.
- Write unit tests for hierarchy, event propagation and handlers.

### Step 3: Plugin Registry and Loader
- Create `core/plugins.py` with functions `register_node_type`, `get_node_type`, `load_plugins`.
- Validate registered classes implement required interfaces.
- Create `core/loader.py` with `load_simulation_from_file(path)` reading YAML/JSON, building the node tree and applying config.
- Write tests for simple cases and format errors.

### Step 4: Generic Nodes
#### 4.1 InventoryNode
- Attributes: `items` dict.
- Methods: `add_item`, `remove_item`, `transfer_to`.
- Emit `inventory_changed`.
- Tests for operations and failure cases.

#### 4.2 NeedNode
- Attributes: `name`, `value`, `threshold`, `increase_rate`, optional `decrease_rate`.
- Methods: `update`, `satisfy`.
- Emit `need_threshold_reached` / `need_satisfied`.
- Tests for threshold crossing and satisfaction.

#### 4.3 ResourceProducerNode
- Attributes: `resource`, `rate_per_tick`, `inputs`, `output_inventory`.
- `update` consumes inputs and produces resources into inventory.
- Emit `resource_produced`.
- Tests for production with/without required inputs.

#### 4.4 AIBehaviorNode
- Attributes: behaviour parameters (e.g., need priorities).
- Configurable daily schedule (wake, work, lunch and sleep hours).
- `on_event` reacts to needs, time and production events.
- `update` may emit regular commands.
- Tests for reacting to a need threshold by eating, etc.

#### 4.5 TerrainNode
- Attributes: `tiles`, optional `grid_type` (``square`` or ``hex``),
  `speed_modifiers`, `combat_bonuses`, `obstacles`.
- Methods: `get_tile`, `get_speed_modifier`, `get_combat_bonus`,
  `get_neighbors`, `is_obstacle`.
- Tests for tile lookup, modifiers, obstacle detection and neighbour calculation.

### Step 5: Global Systems
#### 5.1 TimeSystem
- Parameters: tick duration, phase lengths, start time.
- `update` increments ticks, determines current phase, emits `tick` and `phase_changed`.
- Tests for phase progression.

#### 5.2 EconomySystem
- Listens to `buy_request` / `sell_request` events, checks conditions and transfers money/resources.
- Tests for successful and failed transactions.

#### 5.3 WeatherSystem (optional)
- Parameters: current state and transition rules.
- `update` determines weather changes, emits `weather_changed`.
- Tests for transitions.

### Step 6: Farm Simulation Composition
- Implement `WorldNode` as root container with map size (meters), systems, buildings and characters.
- Implement `FarmNode` with position, an `InventoryNode` and `ResourceProducerNode` producing wheat.
- Implement `CharacterNode` combining a `TransformNode`, `NeedNode`s, an `InventoryNode` and an `AIBehaviorNode` with simple farmer logic.
- Provide minimal configuration file for loader initialisation.
- Write integration tests ensuring wheat production, farmer consumption and resting behaviour.
- Optional: simple rendering/logging of simulation state.

### Step 7: Documentation and Guidelines
- Document every class with detailed docstrings.
- Update README with installation, configuration and simulation launch instructions plus an example configuration file.
- Provide architecture documentation and explain plugin creation.
- Maintain the checklist of progress.

## 5. Progress and Roadmap

### 5.1 Completed
- [x] Initialise Git repository, environment and dependencies.
- [x] Implement `SimNode` with event bus and unit tests.
- [x] Create base `SystemNode` and minimal test.
- [x] Set up plugin registry and declarative loader.
- [x] Define and implement `InventoryNode` with tests.
- [x] Define and implement `NeedNode` with tests.
- [x] Define and implement `ResourceProducerNode` with tests.
- [x] Define and implement `AIBehaviorNode` with tests.
- [x] Implement `TimeSystem`, `EconomySystem` (and optionally `WeatherSystem`) with tests.
- [x] Implement `WorldNode` as root container.
- [x] Implement `FarmNode` with `InventoryNode` and `ResourceProducerNode`.
- [x] Implement `CharacterNode` composed of generic nodes and simple farmer logic.
- [x] Create minimal farm simulation configuration file.
- [x] Write integration tests for farmer working, eating and sleeping.
- [x] Provide minimal rendering/logging to observe the simulation (LoggingSystem outputs events to console).
- [x] Add Pygame-based visualization interface.
- [x] Introduce `DistanceSystem` for distance calculations between nodes.
- [x] Cache distance measurements for faster repeated queries.
- [x] Document architecture and nodes, update README.
- [x] Implement seed-based reproducibility. The `WorldNode` accepts a `seed` to initialise the global RNG for deterministic runs.
- [x] Prepare foundations for future plugins and scenarios.
- [x] Integrate `SchedulerSystem` to allow nodes like `NeedNode` and `AIBehaviorNode` to update at custom intervals.
- [x] Implement a basic `WeatherSystem` emitting `weather_changed` events.
- [x] Enhance `EconomySystem` with simple dynamic pricing reacting to stock levels.
- [x] Generate parameter inventory documentation for all nodes and systems.
- [x] Support class-level default configuration merged by the loader (e.g. `WellNode` dimensions).

### 5.2 Upcoming
#### Core Engine Enhancements
- [x] Expand the event bus with priority levels, asynchronous dispatching, stoppable propagation and automatic event timestamps. Handlers now accept a priority and asynchronous handlers are supported via ``emit_async``.
- [x] Support serialising and reloading full world state for snapshots and debugging.
- [x] Provide a scheduling system to update nodes at different rates (``SchedulerSystem`` allows manual update intervals).
- [x] Optimise the update loop for large simulations (profiling, micro-benchmarks).
-   Cached immutable child lists avoid per-tick allocations in tight loops.
- [ ] Hot-reload node logic without restarting simulations.
- [ ] State diffing and time-travel debugging for deterministic replay.

#### Tools for Creation
- [ ] Command-line tool to scaffold new node or system plugins from templates.
- [ ] Schema validation utility for configuration files (YAML/JSON).
- [ ] Graphical node editor allowing drag-and-drop composition and export to declarative configs.
  - [ ] Basic UI to add/remove nodes and edit properties.
  - [ ] Live simulation preview panel.
  - [ ] Plugin manager to enable/disable community packages.
- [ ] Repository or marketplace for sharing community-created nodes and scenarios.
- [ ] Configuration auto-completion and linting support for editors.
- [ ] Behaviour scripting DSL with a safe sandbox.

#### Visualization and Rendering
- [ ] Extend the Pygame viewer with camera controls, zoom and overlays for inventories, needs and events.
- [ ] Headless rendering mode that streams frames or state for remote dashboards.
- [ ] Web-based viewer (WebGL/Canvas) to observe simulations in the browser.
- [ ] Optional 3D rendering backend (e.g., Panda3D) with automatic asset mapping from node properties.
- [ ] Recording and replay tool to capture simulation sessions.
- [ ] VR/AR viewer for immersive observation.

#### Advanced Simulation Mechanics
- [ ] Extend `WeatherSystem` to influence production rates and character behaviour.
- [ ] Animal nodes with needs, reproduction and resource generation.
- [ ] Advanced dynamic economy with market events and complex price fluctuations.
- [ ] Quest or objective system using dedicated `QuestNode` types.
- [ ] Combat mechanics including equipment, damage and defence systems.
- [ ] Behaviour tree library for complex AI decision making.
- [ ] Modular skill/experience progression for characters.
- [ ] Procedural world generation for terrain and events.

#### Scenario & Narrative Development
- [ ] Campaign framework to chain multiple scenarios with persistence.
- [ ] Event scripting language for cutscenes and triggers.
- [ ] Save/load system for long-running worlds and branching paths.
- [ ] Optional multiplayer or networked simulation support.
- [ ] Social relationship system tracking friendships and rivalries.

#### Infrastructure & Performance
- [ ] Continuous integration pipeline running tests, linting and type checks.
- [ ] Benchmark suite with automated performance regression alerts.
- [ ] Plugin versioning and compatibility management.
- [ ] Packaging and distribution on PyPI with semantic versioning.
- [ ] Telemetry export to monitor performance and state.
- [ ] Plugin sandboxing and permission system.

#### Documentation & Community
- [ ] Expand `project_spec.md` with concrete examples for every node and system type.
- [ ] Write step-by-step tutorials and how-to guides.
- [ ] Publish contribution guidelines and a code of conduct.
- [ ] Launch a documentation website with interactive examples and API reference.
- [ ] Organise community challenges to create and share new scenarios.
- [ ] Auto-generated API reference using Sphinx.
- [ ] Example scenario pack demonstrating diverse use cases.

## 6. Contribution Guidelines
- Atomic commits with explicit English messages.
- Write tests before or alongside implementation.
- Run pytest and linter before proposing changes.
- Document new nodes or systems clearly in code and docs.
- Update the checklist as tasks evolve or complete.

## 7. Future Possibilities
- Medieval city builders simulating trade routes and citizen needs.
- Post-apocalyptic survival with scavenging and base management.
- Ecological simulations exploring predator-prey balance or climate impact.
- Space-colony management with life support, exploration and diplomacy.
- Educational scenarios teaching resource planning or sustainability principles.
