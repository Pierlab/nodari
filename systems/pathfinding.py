"""A* pathfinding system leveraging terrain speed modifiers."""
from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple, Set

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.terrain import TerrainNode


class PathfindingSystem(SystemNode):
    """Compute paths on the terrain grid using the A* algorithm.

    Parameters
    ----------
    terrain:
        Reference to the :class:`TerrainNode` containing map information.
        If a string is supplied the node with this id is looked up on first
        update.
    """

    def __init__(self, terrain: TerrainNode | str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._terrain_ref = terrain
        self.terrain: TerrainNode | None = terrain if isinstance(terrain, TerrainNode) else None

    # ------------------------------------------------------------------
    def _resolve_terrain(self) -> None:
        if self.terrain is not None:
            return
        name = self._terrain_ref if isinstance(self._terrain_ref, str) else None
        root = self.parent
        if root is None:
            return
        self.terrain = self._find_terrain(root, name)

    def _find_terrain(self, node: SimNode, name: str | None) -> TerrainNode | None:
        if isinstance(node, TerrainNode) and (name is None or node.name == name):
            return node
        for child in node.children:
            found = self._find_terrain(child, name)
            if found is not None:
                return found
        return None

    # ------------------------------------------------------------------
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # ------------------------------------------------------------------
    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        blocked: Optional[Set[Tuple[int, int]]] = None,
    ) -> List[Tuple[int, int]]:
        """Return a list of coordinates from ``start`` to ``goal``.

        If no path is found an empty list is returned. ``blocked`` may contain
        additional temporarily impassable coordinates such as ongoing combats.
        """

        self._resolve_terrain()
        if self.terrain is None:
            return []
        blocked = blocked or set()
        open_set: List[Tuple[float, Tuple[int, int]]] = []
        heapq.heappush(open_set, (0.0, start))
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            for neighbor in self.terrain.get_neighbors(*current):
                if neighbor in blocked or self.terrain.is_obstacle(*neighbor):
                    continue
                cost = 1.0 / self.terrain.get_speed_modifier(*neighbor)
                tentative = g_score[current] + cost
                if tentative >= g_score.get(neighbor, float("inf")):
                    continue
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f_score = tentative + self._heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
        return []


register_node_type("PathfindingSystem", PathfindingSystem)
