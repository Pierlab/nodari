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
