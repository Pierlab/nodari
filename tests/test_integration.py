from nodes.world import WorldNode
from nodes.farm import FarmNode
from nodes.inventory import InventoryNode
from nodes.resource_producer import ResourceProducerNode
from nodes.character import CharacterNode
from nodes.need import NeedNode
from nodes.ai_behavior import AIBehaviorNode
from systems.time import TimeSystem


def test_farm_simulation_cycle():
    world = WorldNode(name="world", width=100, height=100)
    farm = FarmNode(name="farm", parent=world)
    farm_inv = InventoryNode(name="farm_inv", items={}, parent=farm)
    producer = ResourceProducerNode(resource="wheat", rate_per_tick=1, output_inventory=farm_inv, parent=farm)

    char = CharacterNode(name="farmer", parent=world)
    hunger = NeedNode(need_name="hunger", threshold=3, increase_rate=2, parent=char)
    personal_inv = InventoryNode(name="personal", items={}, parent=char)
    ai = AIBehaviorNode(parent=char, target_inventory=farm_inv)

    time = TimeSystem(parent=world, phase_length=100)

    for _ in range(3):
        world.update(1)
    assert personal_inv.items.get("wheat", 0) >= 1
    assert hunger.value < hunger.threshold
