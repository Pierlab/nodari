from nodes.builder import BuilderNode
from nodes.building import BuildingNode
from nodes.world import WorldNode
from nodes.transform import TransformNode
from nodes.terrain import TerrainNode
from nodes.nation import NationNode
from systems.pathfinding import PathfindingSystem


def test_builder_creates_city_and_roads():
    world = WorldNode(name="world")
    terrain = TerrainNode(parent=world, tiles=[["plain"] * 5])
    pathfinder = PathfindingSystem(parent=world, terrain=terrain)

    last = BuildingNode(parent=world, type="capital")
    TransformNode(parent=last, position=[0, 0])

    builder = BuilderNode(parent=world)
    city = builder.build_city([4, 0], last)

    # check city created at correct location
    assert isinstance(city, BuildingNode)
    assert city.type == "city"
    city_pos = None
    for child in city.children:
        if isinstance(child, TransformNode):
            city_pos = child.position
    assert city_pos == [4, 0]

    # ensure roads connect intermediate tiles
    road_positions = sorted(
        child.children[0].position
        for child in world.children
        if isinstance(child, BuildingNode) and child.type == "road"
    )
    assert road_positions == [[1, 0], [2, 0], [3, 0]]

    # builder should resume exploration after construction
    assert builder.state == "exploring"


def test_builder_creates_road_without_pathfinder():
    world = WorldNode(name="world")
    last = BuildingNode(parent=world, type="capital")
    TransformNode(parent=last, position=[0, 0])

    builder = BuilderNode(parent=world)
    city = builder.build_city([3, 3], last)

    assert isinstance(city, BuildingNode)

    road_positions = sorted(
        child.children[0].position
        for child in world.children
        if isinstance(child, BuildingNode) and child.type == "road"
    )
    assert road_positions == [[1, 1], [2, 2]]
    assert builder.state == "exploring"


def test_builder_build_cities_respects_city_limit():
    world = WorldNode(name="world")
    terrain = TerrainNode(parent=world, tiles=[["plain"] * 10])
    PathfindingSystem(parent=world, terrain=terrain)

    last = BuildingNode(parent=world, type="capital")
    TransformNode(parent=last, position=[0, 0])

    builder = BuilderNode(parent=world)
    cities = builder.build_cities([(4, 0), (8, 0)], last, max_cities=1)
    assert len(cities) == 1
    assert builder.state == "exploring"


def test_builder_build_cities_respects_coverage_limit():
    world = WorldNode(name="world")
    terrain = TerrainNode(parent=world, tiles=[["plain"] * 10])
    PathfindingSystem(parent=world, terrain=terrain)

    last = BuildingNode(parent=world, type="capital")
    TransformNode(parent=last, position=[0, 0])

    builder = BuilderNode(parent=world)
    cities = builder.build_cities([(4, 0), (8, 0)], last, max_coverage=5)
    assert len(cities) == 1
    assert builder.state == "exploring"


def test_builder_returns_to_capital_and_leaves_road():
    world = WorldNode(name="world")
    terrain = TerrainNode(parent=world, tiles=[["plain"] * 5])
    PathfindingSystem(parent=world, terrain=terrain)

    nation = NationNode(parent=world, morale=100, capital_position=[0, 0])
    last = BuildingNode(parent=world, type="city")
    TransformNode(parent=last, position=[2, 0])

    builder = BuilderNode(parent=nation, build_duration=0.0)
    TransformNode(parent=builder, position=[4, 0])
    builder.begin_construction((4, 0), last)
    builder.update(1.0)

    tr = next(c for c in builder.children if isinstance(c, TransformNode))
    for gx, gy in list(getattr(builder, "_path", [])):
        tr.position = [gx, gy]
        builder.update(0.0)
    tr.position = list(builder._home_tile)
    builder.update(0.0)

    assert builder.parent is None
    road_positions = sorted(
        child.children[0].position
        for child in world.children
        if isinstance(child, BuildingNode) and child.type == "road"
    )
    assert road_positions == [[1, 0], [2, 0], [3, 0]]
