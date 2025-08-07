from core.simnode import SimNode
from nodes.transform import TransformNode
from systems.distance import DistanceSystem


def _make_node(name: str, pos):
    node = SimNode(name=name)
    TransformNode(position=list(pos), parent=node)
    return node


def test_measure_distance():
    system = DistanceSystem()
    a = _make_node("a", (0, 0))
    b = _make_node("b", (3, 4))
    assert system.measure_distance(a, b) == 5


def test_distance_event():
    system = DistanceSystem()
    a = _make_node("a", (0, 0))
    b = _make_node("b", (0, 5))
    result = {}

    def handler(emitter, event_name, payload):
        result["distance"] = payload["distance"]

    system.on_event("distance_result", handler)
    system.emit("distance_request", {"a": a, "b": b})
    assert result["distance"] == 5
