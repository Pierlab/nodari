"""Builder unit node capable of establishing new cities and roads."""
from __future__ import annotations

from typing import Iterable

from core.plugins import register_node_type
from core.simnode import SimNode
from nodes.worker import WorkerNode
from nodes.building import BuildingNode
from nodes.transform import TransformNode


class BuilderNode(WorkerNode):
    """Worker specialised in constructing cities and connecting roads."""

    def build_city(
        self,
        position: Iterable[int] | tuple[int, int],
        last_infrastructure: SimNode,
        *,
        emit_idle: bool = True,
    ) -> BuildingNode | None:
        """Create a city at ``position`` and link it to ``last_infrastructure``.

        A :class:`BuildingNode` of type ``"city"`` is created at the supplied
        coordinates. For each intermediate tile on the path between the last
        infrastructure and the new city, a ``BuildingNode`` of type ``"road"``
        is added as well.

        Returns the newly created city node or ``None`` if the operation could
        not be completed (e.g. missing transforms or pathfinder).
        """

        # Resolve root of the simulation tree
        root = self
        while root.parent is not None:
            root = root.parent

        # Determine start position from the last infrastructure
        start_tr = self._get_transform(last_infrastructure)
        if start_tr is None:
            return None

        goal_x, goal_y = int(round(position[0])), int(round(position[1]))

        # Compute path using the existing pathfinding system if available
        pathfinder = self._find_pathfinder()
        path: list[tuple[int, int]] = []
        if pathfinder is not None:
            start = (
                int(round(start_tr.position[0])),
                int(round(start_tr.position[1])),
            )
            path = pathfinder.find_path(start, (goal_x, goal_y))

        # Create the city at the goal position
        city = BuildingNode(parent=root, type="city")
        TransformNode(parent=city, position=[goal_x, goal_y])

        # Create road segments along the path (excluding endpoints)
        if len(path) > 2:
            for x, y in path[1:-1]:
                road = BuildingNode(parent=root, type="road")
                TransformNode(parent=road, position=[x, y])

        # Return to exploration after construction so the builder may seek
        # the next expansion target.
        self.state = "exploring"
        if emit_idle:
            # Notify systems that the builder finished its task so it can be
            # assigned a new one by emitting ``unit_idle``.
            self.emit("unit_idle", {}, direction="up")
        return city

    # ------------------------------------------------------------------
    def build_cities(
        self,
        positions: Iterable[Iterable[int] | tuple[int, int]],
        last_infrastructure: SimNode,
        max_cities: int | None = None,
        max_coverage: int | None = None,
    ) -> list[BuildingNode]:
        """Construct multiple cities sequentially.

        Each city is linked by roads to the previously built infrastructure.
        After every construction the builder returns to the ``exploring``
        state. Building stops once ``max_cities`` is reached or the number of
        unique tiles covered by roads and cities meets ``max_coverage``.
        """

        built: list[BuildingNode] = []
        covered: set[tuple[int, int]] = set()
        current = last_infrastructure
        pathfinder = self._find_pathfinder()

        start_tr = self._get_transform(last_infrastructure)
        if start_tr is not None:
            covered.add(
                (int(round(start_tr.position[0])), int(round(start_tr.position[1])))
            )

        for pos in positions:
            if max_cities is not None and len(built) >= max_cities:
                break

            goal = (int(round(pos[0])), int(round(pos[1])))
            path: list[tuple[int, int]] = []
            if pathfinder is not None:
                start_tr = self._get_transform(current)
                if start_tr is None:
                    break
                start = (
                    int(round(start_tr.position[0])),
                    int(round(start_tr.position[1])),
                )
                path = pathfinder.find_path(start, goal)
            prospective = set(path or [goal])
            if max_coverage is not None and len(covered | prospective) > max_coverage:
                break
            city = self.build_city(goal, current, emit_idle=False)
            if city is None:
                break
            built.append(city)
            covered.update(prospective)
            current = city

        return built


register_node_type("BuilderNode", BuilderNode)
