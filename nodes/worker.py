"""Worker unit node updated at intervals by the scheduler."""
from __future__ import annotations

from core.plugins import register_node_type
from nodes.unit import UnitNode
from systems.scheduler import SchedulerSystem


class WorkerNode(UnitNode):
    """Unit capable of gathering resources or constructing buildings.

    Parameters
    ----------
    update_interval:
        Seconds between updates when scheduled.
    """

    def __init__(self, update_interval: float = 1.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.update_interval = update_interval
        # Idle workers are not updated automatically until scheduled.
        self._manual_update = True
        self.on_event("task_assigned", self._on_task_assigned)
        self.on_event("task_complete", self._on_task_complete)

    # ------------------------------------------------------------------
    def _find_scheduler(self) -> SchedulerSystem | None:
        """Return the :class:`SchedulerSystem` in the simulation tree."""

        node = self
        # ascend to root
        while node.parent is not None:
            node = node.parent
        for child in node.children:
            if isinstance(child, SchedulerSystem):
                return child
        return None

    # ------------------------------------------------------------------
    def _on_task_assigned(self, _origin, _event, payload) -> None:
        """Assign task and register with scheduler."""

        task = payload.get("task") or payload.get("state")
        if task in {"gather", "gathering"}:
            self.state = "gathering"
        elif task in {"build", "building"}:
            self.state = "building"
        else:
            self.state = "idle"
        scheduler = self._find_scheduler()
        if scheduler is not None:
            scheduler.unschedule(self)
            if self.state != "idle":
                scheduler.schedule(self, self.update_interval)

    # ------------------------------------------------------------------
    def _on_task_complete(self, _origin, _event, _payload) -> None:
        """Return to idle state and unregister from scheduler."""

        self.state = "idle"
        scheduler = self._find_scheduler()
        if scheduler is not None:
            scheduler.unschedule(self)
        # Remain excluded from automatic updates while idle.
        self._manual_update = True
        self.emit("unit_idle", {}, direction="up")


register_node_type("WorkerNode", WorkerNode)
