from nodes.world import WorldNode
from nodes.worker import WorkerNode
from nodes.transform import TransformNode
from nodes.nation import NationNode
from nodes.terrain import TerrainNode
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


def test_ai_respects_capital_radius_and_free_tiles():
    world = WorldNode(width=20, height=20)
    terrain = TerrainNode(tiles=[[0] * 20 for _ in range(20)], obstacles=[[7, 10]])
    world.add_child(terrain)
    nation = NationNode(parent=world, morale=100, capital_position=[10, 10])
    worker = WorkerNode(parent=nation, state="exploring")
    TransformNode(parent=worker, position=[10, 10])
    blocker = WorkerNode(parent=nation, state="idle")
    TransformNode(parent=blocker, position=[8, 8])
    ai = AISystem(parent=world, exploration_radius=3, capital_min_radius=2)
    worker.emit("unit_idle", {})
    assert worker.state == "moving"
    cx, cy = nation.capital_position
    tx, ty = worker.target
    assert (tx - cx) * (tx - cx) + (ty - cy) * (ty - cy) >= 4
    assert worker.target not in ([7, 10], [8, 8])
