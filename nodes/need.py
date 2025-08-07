"""Node representing a consumable need."""
from __future__ import annotations

from core.simnode import SimNode
from core.plugins import register_node_type


class NeedNode(SimNode):
    """Represents a need such as hunger or fatigue."""

    def __init__(
        self,
        need_name: str,
        threshold: float,
        increase_rate: float,
        decrease_rate: float = 0.0,
        value: float = 0.0,
        update_interval: float | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.need_name = need_name
        self.threshold = threshold
        self.increase_rate = increase_rate
        self.decrease_rate = decrease_rate
        self.value = value
        self._threshold_reached = False
        self.update_interval = update_interval
        if update_interval:
            scheduler = self._scheduler_system()
            if scheduler:
                scheduler.schedule(self, update_interval)

    def update(self, dt: float) -> None:
        self.value += self.increase_rate * dt
        if not self._threshold_reached and self.value >= self.threshold:
            self._threshold_reached = True
            self.emit("need_threshold_reached", {"need": self.need_name, "value": self.value})
        super().update(dt)

    def satisfy(self, amount: float) -> None:
        prev = self.value
        self.value = max(0.0, self.value - amount)
        if self._threshold_reached and self.value < self.threshold:
            self._threshold_reached = False
            self.emit("need_satisfied", {"need": self.need_name, "value": self.value})

    def _scheduler_system(self):
        from systems.scheduler import SchedulerSystem

        root = self
        while root.parent is not None:
            root = root.parent
        stack = [root]
        while stack:
            node = stack.pop()
            if isinstance(node, SchedulerSystem):
                return node
            stack.extend(node.children)
        return None


register_node_type("NeedNode", NeedNode)
