"""Worker unit node updated at intervals by the scheduler."""
from __future__ import annotations

from core.plugins import register_node_type
from core.simnode import SimNode
from nodes.unit import UnitNode
from nodes.resource import ResourceNode
from nodes.transform import TransformNode
from systems.scheduler import SchedulerSystem
from systems.pathfinding import PathfindingSystem


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
        self.emit("unit_idle", {}, direction="up")

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

    # ------------------------------------------------------------------
    def _find_pathfinder(self) -> PathfindingSystem | None:
        """Return the :class:`PathfindingSystem` in the simulation tree."""

        node = self
        while node.parent is not None:
            node = node.parent
        for child in node.children:
            if isinstance(child, PathfindingSystem):
                return child
        return None

    # ------------------------------------------------------------------
    def _get_transform(self, node: SimNode) -> TransformNode | None:
        if isinstance(node, TransformNode):
            return node
        for child in node.children:
            if isinstance(child, TransformNode):
                return child
        return None

    # ------------------------------------------------------------------
    def _iter_resources(self, node: SimNode):
        for child in node.children:
            if isinstance(child, ResourceNode):
                yield child
            yield from self._iter_resources(child)

    # ------------------------------------------------------------------
    def find_task(self) -> bool:
        """Assign the worker to the nearest resource or zone.

        The closest accessible :class:`ResourceNode` is selected using the
        :class:`PathfindingSystem`. If a target is found the worker's ``target``
        and ``state`` are updated and a ``unit_move`` event is emitted.

        Returns ``True`` if a task was assigned.
        """

        pathfinder = self._find_pathfinder()
        transform = self._get_transform(self)
        if pathfinder is None or transform is None:
            return False

        start = (
            int(round(transform.position[0])),
            int(round(transform.position[1])),
        )
        root = self
        while root.parent is not None:
            root = root.parent

        nearest = None
        best_len = float("inf")
        for res in self._iter_resources(root):
            r_tr = self._get_transform(res)
            if r_tr is None:
                continue
            goal = (
                int(round(r_tr.position[0])),
                int(round(r_tr.position[1])),
            )
            path = pathfinder.find_path(start, goal)
            if path and len(path) < best_len:
                best_len = len(path)
                nearest = goal

        if nearest is None:
            return False

        self.target = [nearest[0], nearest[1]]
        self.state = "moving"
        self.emit("unit_move", {"to": self.target}, direction="up")
        return True


register_node_type("WorkerNode", WorkerNode)
