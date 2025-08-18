import os
import random

os.environ["RUN_WAR_IMPORT_ONLY"] = "1"

from nodes.world import WorldNode
from nodes.terrain import TerrainNode
from nodes.nation import NationNode
from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.builder import BuilderNode
from nodes.transform import TransformNode
from systems.movement import MovementSystem
from systems.pathfinding import PathfindingSystem
from run_war import _spawn_armies


def test_spawn_armies_creates_only_builders():
    random.seed(0)
    world = WorldNode(width=3, height=3)
    terrain = TerrainNode(parent=world, tiles=[["plain"] * 3 for _ in range(3)], obstacles=[[1, 0]])
    pathfinder = PathfindingSystem(parent=world, terrain=terrain)
    MovementSystem(parent=world, terrain=terrain, avoid_obstacles=True, pathfinder=pathfinder)

    north = NationNode(parent=world, name="north", capital_position=[0, 0], morale=100)
    g_north = GeneralNode(parent=north, style="balanced")
    TransformNode(parent=g_north, position=[0, 0])

    south = NationNode(parent=world, name="south", capital_position=[2, 2], morale=100)
    g_south = GeneralNode(parent=south, style="balanced")
    TransformNode(parent=g_south, position=[2, 2])

    _spawn_armies(world, 0, 1, 1, pathfinder)

    assert not any(isinstance(c, ArmyNode) for c in g_north.children)
    builders = [c for c in north.children if isinstance(c, BuilderNode)]
    assert len(builders) == 3
    for b in builders:
        tr = next(c for c in b.children if isinstance(c, TransformNode))
        assert tr.position == [0, 0]
        assert b.state == "exploring"
