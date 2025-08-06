from core.simnode import SimNode


def test_child_management():
    parent = SimNode(name="parent")
    child = SimNode(name="child", parent=parent)
    assert child in parent.children
    parent.remove_child(child)
    assert child not in parent.children
    assert child.parent is None


def test_event_propagation_to_sibling():
    root = SimNode(name="root")
    a = SimNode(name="a", parent=root)
    b = SimNode(name="b", parent=root)
    received = []

    def handler(emitter, event, payload):
        received.append((emitter.name, payload["x"]))

    b.on_event("ping", handler)
    a.emit("ping", {"x": 1})
    assert received == [("a", 1)]
