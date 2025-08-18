from nodes.builder import BuilderNode
from nodes.building import BuildingNode
from nodes.world import WorldNode
from nodes.transform import TransformNode
from nodes.terrain import TerrainNode
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
