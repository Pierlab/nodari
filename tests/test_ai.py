from nodes.world import WorldNode
from nodes.worker import WorkerNode
from nodes.resource import ResourceNode
from nodes.transform import TransformNode
from nodes.terrain import TerrainNode
from systems.pathfinding import PathfindingSystem
from systems.ai import AISystem


def test_idle_worker_receives_task():
    world = WorldNode(width=5, height=5)
    terrain = TerrainNode(parent=world, tiles=[["plain"] * 5 for _ in range(5)])
    PathfindingSystem(parent=world, terrain=terrain)
    AISystem(parent=world)

    worker = WorkerNode(parent=world)
    TransformNode(parent=worker, position=[0, 0])

    resource = ResourceNode(parent=world, kind="wood", quantity=10)
    TransformNode(parent=resource, position=[3, 0])

    # Worker becomes idle
    worker.emit("unit_idle", {})

    assert worker.target == [3, 0]
    assert worker.state == "moving"
