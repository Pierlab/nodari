from nodes.world import WorldNode
from nodes.worker import WorkerNode
from nodes.transform import TransformNode
from systems.ai import AISystem


def test_idle_worker_explores_unknown_tiles():
    world = WorldNode(width=10, height=10)
    worker = WorkerNode(parent=world)
    TransformNode(parent=worker, position=[0, 0])

    # AI with deterministic exploration radius
    ai = AISystem(parent=world, exploration_radius=2)

    # Worker becomes idle
    worker.emit("unit_idle", {})

    # AI should send the worker exploring away from origin
    assert worker.state == "moving"
    assert worker.target == [-2, 0]
