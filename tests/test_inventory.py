from nodes.inventory import InventoryNode


def test_inventory_operations():
    inv_a = InventoryNode(name="A")
    inv_b = InventoryNode(name="B")
    inv_a.add_item("wheat", 5)
    inv_a.transfer_to(inv_b, "wheat", 3)
    assert inv_a.items["wheat"] == 2
    assert inv_b.items["wheat"] == 3
    inv_b.remove_item("wheat", 1)
    assert inv_b.items["wheat"] == 2
