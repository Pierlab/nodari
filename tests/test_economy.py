import pytest

from nodes.world import WorldNode
from nodes.resource import ResourceNode
from systems.economy import EconomySystem


def test_produce_emits_event_and_increases_stock():
    world = WorldNode()
    econ = EconomySystem(parent=world)
    stock = ResourceNode(kind="wood", parent=world)
    events: list[dict] = []
    stock.on_event("resource_produced", lambda _o, _e, p: events.append(p))

    econ.produce(stock, "wood", 5)

    assert stock.quantity == 5
    assert events and events[0]["amount"] == 5 and events[0]["kind"] == "wood"


def test_transfer_moves_resources_and_emits_events():
    world = WorldNode()
    econ = EconomySystem(parent=world)
    src = ResourceNode(kind="grain", quantity=10, parent=world)
    dst = ResourceNode(kind="grain", parent=world)
    consumed: list[dict] = []
    produced: list[dict] = []
    src.on_event("resource_consumed", lambda _o, _e, p: consumed.append(p))
    dst.on_event("resource_produced", lambda _o, _e, p: produced.append(p))

    econ.transfer(src, dst, "grain", 4)

    assert src.quantity == 6
    assert dst.quantity == 4
    assert consumed and consumed[0]["amount"] == 4
    assert produced and produced[0]["amount"] == 4


def test_transfer_raises_on_insufficient_stock():
    world = WorldNode()
    econ = EconomySystem(parent=world)
    src = ResourceNode(kind="stone", quantity=2, parent=world)
    dst = ResourceNode(kind="stone", parent=world)

    with pytest.raises(ValueError):
        econ.transfer(src, dst, "stone", 5)


def test_transfer_raises_when_destination_full():
    world = WorldNode()
    econ = EconomySystem(parent=world)
    src = ResourceNode(kind="iron", quantity=5, parent=world)
    dst = ResourceNode(kind="iron", quantity=0, max_quantity=3, parent=world)

    with pytest.raises(ValueError):
        econ.transfer(src, dst, "iron", 4)

    # quantities remain unchanged on failure
    assert src.quantity == 5
    assert dst.quantity == 0
