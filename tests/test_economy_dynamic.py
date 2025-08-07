from nodes.world import WorldNode
from nodes.inventory import InventoryNode
from systems.economy import EconomySystem


def test_dynamic_pricing_adjusts_after_purchase():
    world = WorldNode(name="world")
    econ = EconomySystem(parent=world)
    buyer = InventoryNode(name="buyer", items={"money": 100}, parent=world)
    seller = InventoryNode(name="seller", items={"wheat": 10}, parent=world)

    for _ in range(2):
        world.emit(
            "buy_request",
            {"buyer": buyer, "seller": seller, "item": "wheat", "quantity": 3},
        )

    assert econ.prices["wheat"] == 2.0
