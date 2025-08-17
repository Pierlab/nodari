from nodes.terrain import TerrainNode
from systems.pathfinding import PathfindingSystem


def test_pathfinder_avoids_slow_tiles():
    tiles = [
        ["plain", "swamp", "plain"],
        ["plain", "plain", "plain"],
        ["plain", "plain", "plain"],
    ]
    terrain = TerrainNode(tiles=tiles, speed_modifiers={"plain": 1.0, "swamp": 0.1})
    pf = PathfindingSystem(terrain=terrain)
    path = pf.find_path((0, 0), (2, 0))
    assert (1, 0) not in path


def test_pathfinder_respects_blocked_tiles():
    terrain = TerrainNode(tiles=[["plain"] * 3 for _ in range(3)])
    pf = PathfindingSystem(terrain=terrain)
    path = pf.find_path((0, 0), (2, 0), blocked={(1, 0)})
    assert (1, 0) not in path
