from nodes.ai_behavior import AIBehaviorNode
from nodes.inventory import InventoryNode
from nodes.need import NeedNode
from nodes.character import CharacterNode


def test_ai_eats_when_hungry():
    farm_inv = InventoryNode(name="farm", items={"wheat": 5})
    char = CharacterNode(name="farmer")
    hunger = NeedNode(need_name="hunger", threshold=5, increase_rate=5, parent=char)
    personal_inv = InventoryNode(name="personal", items={}, parent=char)
    ai = AIBehaviorNode(parent=char, target_inventory=farm_inv)
    hunger.update(1)  # value =5 -> threshold
    assert personal_inv.items.get("wheat", 0) == 1
    assert hunger.value < hunger.threshold
