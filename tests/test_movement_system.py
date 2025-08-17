from nodes.world import WorldNode
from nodes.terrain import TerrainNode
from nodes.unit import UnitNode
from nodes.transform import TransformNode
from systems.movement import MovementSystem
from systems.pathfinding import PathfindingSystem


def test_movement_considers_terrain_and_morale():
    world = WorldNode()
    terrain = TerrainNode(tiles=[["forest", "forest"]], speed_modifiers={"forest": 0.5})
    MovementSystem(parent=world, terrain=terrain)
    unit = UnitNode(parent=world, speed=1.0, morale=50, target=[1, 0])
    TransformNode(parent=unit, position=[0.0, 0.0])

    world.update(1.0)
    transform = next(c for c in unit.children if isinstance(c, TransformNode))
    assert transform.position[0] == 0.25

    world.update(3.0)
    assert transform.position[0] == 1.0


def test_map_obstacle_blocks_movement():
    world = WorldNode()
    terrain = TerrainNode(tiles=[["plain", "plain"]], obstacles=[[1, 0]])
    MovementSystem(parent=world, terrain=terrain)
    unit = UnitNode(parent=world, speed=1.0, morale=100, target=[2, 0])
    TransformNode(parent=unit, position=[0.0, 0.0])

    world.update(1.0)
    transform = next(c for c in unit.children if isinstance(c, TransformNode))
    assert transform.position[0] == 0.0


def test_fighting_unit_blocks_and_pathfinder_detours():
    world = WorldNode()
    terrain = TerrainNode(tiles=[["plain"] * 3 for _ in range(3)])
    pathfinder = PathfindingSystem(parent=world, terrain=terrain)
    MovementSystem(parent=world, terrain=terrain, avoid_obstacles=True, pathfinder=pathfinder)
    moving = UnitNode(parent=world, speed=1.0, morale=100, target=[2, 0])
    TransformNode(parent=moving, position=[0.0, 0.0])
    blocker = UnitNode(parent=world, state="fighting")
    TransformNode(parent=blocker, position=[1.0, 0.0])

    # first update computes detour path without moving
    world.update(1.0)
    # second update follows the path around the fighting unit
    world.update(1.0)
    transform = next(c for c in moving.children if isinstance(c, TransformNode))
    # The unit should move north to avoid the fighting tile at (1,0)
    assert transform.position == [0.0, 1.0]
