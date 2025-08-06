from nodes.inventory import InventoryNode
from nodes.resource_producer import ResourceProducerNode


def test_resource_production():
    inv = InventoryNode(name="farm_inv", items={})
    producer = ResourceProducerNode(resource="wheat", rate_per_tick=1, output_inventory=inv)
    producer.update(1)
    assert inv.items["wheat"] == 1
