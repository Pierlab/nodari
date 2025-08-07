"""System providing distance calculations between nodes in meters."""
from __future__ import annotations

import math
from typing import Dict, Tuple

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.transform import TransformNode


class DistanceSystem(SystemNode):
    """Respond to distance queries using node positions."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.on_event("distance_request", self._on_distance_request)
        self._cache: Dict[Tuple[int, int], float] = {}

    def _on_distance_request(self, emitter, event_name, payload) -> None:
        node_a: SimNode = payload["a"]
        node_b: SimNode = payload["b"]
        payload["distance"] = self.measure_distance(node_a, node_b)
        self.emit("distance_result", payload)

    def measure_distance(self, node_a: SimNode, node_b: SimNode) -> float:
        key = tuple(sorted((id(node_a), id(node_b))))
        if key in self._cache:
            return self._cache[key]
        ax, ay = self._get_position(node_a)
        bx, by = self._get_position(node_b)
        dist = math.hypot(ax - bx, ay - by)
        self._cache[key] = dist
        return dist

    def _get_position(self, node: SimNode) -> Tuple[float, float]:
        if isinstance(node, TransformNode):
            return tuple(node.position)
        for child in node.children:
            if isinstance(child, TransformNode):
                return tuple(child.position)
        raise ValueError(f"Node '{node.name}' has no TransformNode")

    def update(self, dt: float) -> None:  # pragma: no cover - trivial cache reset
        self._cache.clear()
        super().update(dt)


register_node_type("DistanceSystem", DistanceSystem)
