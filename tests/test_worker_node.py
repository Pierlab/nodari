from __future__ import annotations

from nodes.worker import WorkerNode
from nodes.world import WorldNode
from systems.scheduler import SchedulerSystem


class TestWorker(WorkerNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0

    def update(self, dt: float) -> None:
        self.count += 1
        super().update(dt)


def test_worker_scheduling_and_state():
    world = WorldNode(name="world")
    scheduler = SchedulerSystem(parent=world)
    worker = TestWorker(parent=world, update_interval=2.0)

    worker.emit("task_assigned", {"task": "gathering"})

    assert worker.state == "gathering"
    assert worker._manual_update is True
    assert len(scheduler._tasks) == 1

    for _ in range(5):
        world.update(1.0)
    assert worker.count == 2

    worker.emit("task_complete", {})

    assert worker.state == "idle"
    assert worker._manual_update is True
    assert len(scheduler._tasks) == 0

    world.update(1.0)
    assert worker.count == 2
