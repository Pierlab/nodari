from nodes.inventory import InventoryNode
from nodes.resource_producer import ResourceProducerNode


def test_resource_production():
    inv = InventoryNode(name="farm_inv", items={})
    producer = ResourceProducerNode(resource="wheat", rate_per_tick=1, output_inventory=inv)
    producer.update(1)
    assert inv.items["wheat"] == 1


def test_manual_production():
    inv = InventoryNode(name="farm_inv", items={"water": 5})
    producer = ResourceProducerNode(
        resource="wheat",
        rate_per_tick=2,
        inputs={"water": 1},
        output_inventory=inv,
        auto=False,
    )
    producer.work()
    assert inv.items["wheat"] == 2
    assert inv.items["water"] == 4
