"""Scheduler system to update nodes at individual intervals."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.simnode import SimNode, SystemNode
from core.plugins import register_node_type


@dataclass
class _Task:
    node: SimNode
    interval: float
    acc: float = 0.0


class SchedulerSystem(SystemNode):
    """Call ``update`` on registered nodes at specific intervals."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tasks: List[_Task] = []

    def schedule(self, node: SimNode, interval: float) -> None:
        """Schedule *node* to be updated every *interval* seconds."""
        node._manual_update = True
        self._tasks.append(_Task(node=node, interval=interval))

    def unschedule(self, node: SimNode) -> None:
        """Remove *node* from scheduling."""
        for i, task in enumerate(list(self._tasks)):
            if task.node is node:
                del self._tasks[i]
        node._manual_update = False

    def update(self, dt: float) -> None:
        for task in self._tasks:
            task.acc += dt
            while task.acc >= task.interval:
                task.acc -= task.interval
                task.node.update(task.interval)
        super().update(dt)


register_node_type("SchedulerSystem", SchedulerSystem)
