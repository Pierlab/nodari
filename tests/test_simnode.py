import asyncio

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


def test_event_priority():
    node = SimNode(name="node")
    call_order = []

    def low_handler(_emitter, _event, _payload):
        call_order.append("low")

    def high_handler(_emitter, _event, _payload):
        call_order.append("high")

    node.on_event("test", low_handler, priority=0)
    node.on_event("test", high_handler, priority=10)

    node.emit("test")

    assert call_order == ["high", "low"]


def test_async_dispatch():
    node = SimNode(name="node")
    received = []

    async def handler(emitter, event, payload):
        await asyncio.sleep(0.01)
        received.append(payload["value"])

    node.on_event("async", handler)

    asyncio.run(node.emit_async("async", {"value": 42}))

    assert received == [42]


def test_children_cache_reuse():
    parent = SimNode(name="parent")
    a = SimNode(name="a", parent=parent)
    b = SimNode(name="b", parent=parent)

    parent.update(0.1)
    cached = parent._iter_children
    parent.update(0.1)
    assert parent._iter_children is cached

    c = SimNode(name="c")
    parent.add_child(c)
    parent.update(0.1)
    assert parent._iter_children is not cached


def test_add_child_during_update():
    class RecordingNode(SimNode):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.calls = 0

        def update(self, dt: float) -> None:
            self.calls += 1
            super().update(dt)

    class ChildAdder(RecordingNode):
        def update(self, dt: float) -> None:
            if not hasattr(self, "added"):
                self.added = True
                self.parent.add_child(RecordingNode(name="child"))
            super().update(dt)

    parent = SimNode(name="parent")
    adder = ChildAdder(name="adder", parent=parent)

    parent.update(0.1)
    child = next(node for node in parent.children if node is not adder)
    assert child.calls == 0

    parent.update(0.1)
    assert child.calls == 1
