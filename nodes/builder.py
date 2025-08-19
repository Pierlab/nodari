"""Builder unit node capable of establishing new cities and roads."""
from __future__ import annotations

from typing import Iterable

from core.plugins import register_node_type
from core.simnode import SimNode
from nodes.worker import WorkerNode
from nodes.building import BuildingNode
from nodes.transform import TransformNode
from nodes.nation import NationNode


class BuilderNode(WorkerNode):
    """Worker specialised in constructing cities and connecting roads."""

    def __init__(self, build_duration: float = 5.0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.build_duration = build_duration
        self._build_elapsed = 0.0
        self._build_origin: SimNode | None = None
        self._build_position: tuple[int, int] | None = None
        self._home_tile: tuple[int, int] | None = None
        self._last_tile: tuple[int, int] | None = None
        self._returning = False

    # ------------------------------------------------------------------
    def begin_construction(self, position: tuple[int, int], origin: SimNode) -> None:
        self.state = "building"
        self._build_position = (int(round(position[0])), int(round(position[1])))
        self._build_origin = origin
        origin_tr = self._get_transform(origin)
        self._home_tile = (
            (int(round(origin_tr.position[0])), int(round(origin_tr.position[1])))
            if origin_tr is not None
            else None
        )
        self._build_elapsed = 0.0
        scheduler = self._find_scheduler()
        if scheduler is not None:
            scheduler.unschedule(self)
            scheduler.schedule(self, self.update_interval)

    def build_city(
        self,
        position: Iterable[int] | tuple[int, int],
        last_infrastructure: SimNode,
        *,
        emit_idle: bool = True,
        build_roads: bool = True,
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

        # Prevent building too close to existing cities
        nation: NationNode | None = None
        cur = self.parent
        while cur is not None:
            if isinstance(cur, NationNode):
                nation = cur
                break
            cur = cur.parent
        if nation is not None:
            radius = getattr(nation, "city_influence_radius", 0)
            for cx, cy in nation.cities_positions:
                dx = goal_x - cx
                dy = goal_y - cy
                if dx * dx + dy * dy < radius * radius:
                    # Too close to an existing city; abort construction and
                    # return the builder to exploration so it can seek another
                    # location.
                    self.state = "exploring"
                    if emit_idle:
                        self.emit("unit_idle", {}, direction="up")
                    return None

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
        if build_roads and len(path) > 2:
            for x, y in path[1:-1]:
                road = BuildingNode(parent=root, type="road")
                TransformNode(parent=road, position=[x, y])

        if nation is not None:
            nation.cities_positions.append((goal_x, goal_y))

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

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.state == "building":
            self._build_elapsed += dt
            if (
                self._build_elapsed >= self.build_duration
                and self._build_origin is not None
                and self._build_position is not None
            ):
                city = self.build_city(
                    self._build_position,
                    self._build_origin,
                    emit_idle=False,
                    build_roads=False,
                )
                if city is not None:
                    self.emit("city_built", {"city": city}, direction="up")
                    pathfinder = self._find_pathfinder()
                    start_tr = self._get_transform(city)
                    origin_tr = self._get_transform(self._build_origin)
                    if (
                        pathfinder is not None
                        and start_tr is not None
                        and origin_tr is not None
                    ):
                        start = (
                            int(round(start_tr.position[0])),
                            int(round(start_tr.position[1])),
                        )
                        goal = (
                            int(round(origin_tr.position[0])),
                            int(round(origin_tr.position[1])),
                        )
                        path = pathfinder.find_path(start, goal)
                        if path:
                            self._path = path[1:]
                            self.target = [goal[0], goal[1]]
                    self.state = "returning"
                    self._returning = True
                    tr = self._get_transform(self)
                    if tr is not None:
                        self._last_tile = (
                            int(round(tr.position[0])),
                            int(round(tr.position[1])),
                        )
                    self._build_origin = None
                    self._build_position = None
        elif self._returning:
            tr = self._get_transform(self)
            if tr is not None:
                tile = (int(round(tr.position[0])), int(round(tr.position[1])))
                if tile != self._last_tile and tile != self._home_tile:
                    root = self
                    while root.parent is not None:
                        root = root.parent
                    road = BuildingNode(parent=root, type="road")
                    TransformNode(parent=road, position=[tile[0], tile[1]])
                    self._last_tile = tile
                if tile == self._home_tile:
                    self._returning = False
                    scheduler = self._find_scheduler()
                    if scheduler is not None:
                        scheduler.unschedule(self)
                    self.state = "exploring"
                    self.emit("unit_idle", {}, direction="up")
        elif self.state == "idle":
            scheduler = self._find_scheduler()
            if scheduler is not None:
                scheduler.unschedule(self)
        super().update(dt)


register_node_type("BuilderNode", BuilderNode)
