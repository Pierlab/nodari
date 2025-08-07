"""System providing distance calculations between nodes."""
from __future__ import annotations

import math
from typing import Tuple

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.transform import TransformNode


class DistanceSystem(SystemNode):
    """Respond to distance queries using node positions."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.on_event("distance_request", self._on_distance_request)

    def _on_distance_request(self, emitter, event_name, payload) -> None:
        node_a: SimNode = payload["a"]
        node_b: SimNode = payload["b"]
        payload["distance"] = self.measure_distance(node_a, node_b)
        self.emit("distance_result", payload)

    def measure_distance(self, node_a: SimNode, node_b: SimNode) -> float:
        ax, ay = self._get_position(node_a)
        bx, by = self._get_position(node_b)
        return math.hypot(ax - bx, ay - by)

    def _get_position(self, node: SimNode) -> Tuple[float, float]:
        if isinstance(node, TransformNode):
            return tuple(node.position)
        for child in node.children:
            if isinstance(child, TransformNode):
                return tuple(child.position)
        raise ValueError(f"Node '{node.name}' has no TransformNode")


register_node_type("DistanceSystem", DistanceSystem)
