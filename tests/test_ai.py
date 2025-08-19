from core.simnode import SimNode
from nodes.world import WorldNode
from nodes.worker import WorkerNode
from nodes.builder import BuilderNode
from nodes.building import BuildingNode
from nodes.transform import TransformNode
from nodes.nation import NationNode
from nodes.terrain import TerrainNode
from systems.ai import AISystem
from systems.movement import MovementSystem


def test_idle_worker_explores_unknown_tiles():
    world = WorldNode(width=10, height=10)
    worker = WorkerNode(parent=world)
    TransformNode(parent=worker, position=[0, 0])

    # AI with deterministic exploration radius
    ai = AISystem(parent=world, exploration_radius=2)

    worker.emit("unit_idle", {})

    assert worker.state == "exploring"
    assert worker.target is None


def test_ai_respects_capital_radius_and_free_tiles():
    world = WorldNode(width=20, height=20)
    terrain = TerrainNode(tiles=[[0] * 20 for _ in range(20)], obstacles=[[7, 10]])
    world.add_child(terrain)
    MovementSystem(parent=world, terrain=terrain)
    nation = NationNode(parent=world, morale=100, capital_position=[10, 10])
    worker = WorkerNode(parent=nation, state="exploring")
    TransformNode(parent=worker, position=[10, 10])
    blocker = WorkerNode(parent=nation, state="idle")
    TransformNode(parent=blocker, position=[8, 8])
    ai = AISystem(parent=world, exploration_radius=3, capital_min_radius=2)
    worker.emit("unit_idle", {})
    assert worker.state == "exploring"
    for _ in range(3):
        world.update(1.0)
    tr = next(c for c in worker.children if isinstance(c, TransformNode))
    cx, cy = nation.capital_position
    dx, dy = tr.position[0] - cx, tr.position[1] - cy
    assert dx * dx + dy * dy >= 4
    assert (int(round(tr.position[0])), int(round(tr.position[1]))) not in [(7, 10), (8, 8)]


def test_builder_constructs_city_when_idle_far_from_last():
    world = WorldNode(width=20, height=20)
    nation = NationNode(parent=world, morale=100, capital_position=[0, 0])
    builder = BuilderNode(parent=nation, state="idle")
    TransformNode(parent=builder, position=[3, 0])
    ai = AISystem(parent=world, exploration_radius=2, capital_min_radius=2)
    builder.emit("unit_idle", {})
    cities = [c for c in world.children if isinstance(c, BuildingNode) and c.type == "city"]
    positions = []
    for city in cities:
        for child in city.children:
            if isinstance(child, TransformNode):
                positions.append(child.position)
    assert [3, 0] in positions
    assert builder.state == "exploring"


def test_build_city_resets_state_and_emits_idle():
    world = WorldNode(width=10, height=10)
    builder = BuilderNode(parent=world, state="building")
    last = BuildingNode(parent=world, type="city")
    TransformNode(parent=last, position=[0, 0])

    events: list[SimNode] = []
    world.on_event("unit_idle", lambda origin, _e, _p: events.append(origin))

    builder.build_city([1, 0], last)

    assert builder.state == "exploring"
    assert builder in events


def test_build_city_refuses_within_influence_radius():
    world = WorldNode(width=10, height=10)
    nation = NationNode(
        parent=world, morale=100, capital_position=[0, 0], city_influence_radius=5
    )
    builder = BuilderNode(parent=nation, state="building")
    TransformNode(parent=builder, position=[1, 0])
    last = BuildingNode(parent=world, type="city")
    TransformNode(parent=last, position=[0, 0])

    events: list[SimNode] = []
    world.on_event("unit_idle", lambda origin, _e, _p: events.append(origin))

    result = builder.build_city([3, 0], last)

    assert result is None
    assert builder.state == "exploring"
    assert builder in events


def test_ai_initializes_last_city_with_capital():
    world = WorldNode(width=20, height=20)
    nation = NationNode(parent=world, morale=100, capital_position=[5, 5])
    ai = AISystem(parent=world, exploration_radius=2, capital_min_radius=2)
    last = ai._last_city.get(id(nation))
    assert isinstance(last, BuildingNode)
    tr = next((c for c in last.children if isinstance(c, TransformNode)), None)
    assert tr is not None
    assert tr.position == [5, 5]


def test_builder_respects_city_influence_radius():
    world = WorldNode(width=20, height=20)
    nation = NationNode(
        parent=world, morale=100, capital_position=[0, 0], city_influence_radius=5
    )
    builder = BuilderNode(parent=nation, state="idle")
    TransformNode(parent=builder, position=[3, 0])
    ai = AISystem(
        parent=world,
        exploration_radius=2,
        capital_min_radius=2,
        city_influence_radius=5,
    )
    builder.emit("unit_idle", {})
    cities = [c for c in world.children if isinstance(c, BuildingNode) and c.type == "city"]
    positions = []
    for city in cities:
        for child in city.children:
            if isinstance(child, TransformNode):
                positions.append(child.position)
    assert [3, 0] not in positions
    assert builder.state == "exploring"


def test_exploring_builder_auto_builds_new_city():
    world = WorldNode(width=20, height=20)
    nation = NationNode(parent=world, morale=100, capital_position=[0, 0])
    builder = BuilderNode(parent=nation, state="exploring")
    TransformNode(parent=builder, position=[3, 0])
    ai = AISystem(parent=world, exploration_radius=2, capital_min_radius=2)

    # During update the builder has moved outside the influence of the capital
    # and should establish a new city automatically.
    ai.update(1.0)

    positions = [
        child.position
        for city in world.children
        if isinstance(city, BuildingNode) and city.type == "city"
        for child in city.children
        if isinstance(child, TransformNode)
    ]
    assert [3, 0] in positions
    assert (3.0, 0.0) in nation.cities_positions
