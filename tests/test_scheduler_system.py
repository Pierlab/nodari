from __future__ import annotations

from core.simnode import SimNode
from nodes.world import WorldNode
from systems.scheduler import SchedulerSystem


class DummyNode(SimNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0

    def update(self, dt: float) -> None:
        self.count += 1
        super().update(dt)


def test_scheduler_updates_nodes_at_intervals():
    world = WorldNode(name="world")
    scheduler = SchedulerSystem(parent=world)
    fast = DummyNode(parent=world)
    slow = DummyNode(parent=world)

    scheduler.schedule(fast, interval=1.0)
    scheduler.schedule(slow, interval=2.0)

    for _ in range(5):
        world.update(1.0)

    assert fast.count == 5
    assert slow.count == 2
