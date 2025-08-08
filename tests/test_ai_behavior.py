from core.simnode import SimNode
from nodes.ai_behavior import AIBehaviorNode
from nodes.inventory import InventoryNode
from nodes.need import NeedNode
from nodes.character import CharacterNode
from nodes.transform import TransformNode
from systems.time import TimeSystem


def test_ai_eats_when_hungry():
    farm_inv = InventoryNode(name="farm", items={"wheat": 5})
    char = CharacterNode(name="farmer")
    hunger = NeedNode(need_name="hunger", threshold=5, increase_rate=5, parent=char)
    personal_inv = InventoryNode(name="personal", items={}, parent=char)
    ai = AIBehaviorNode(parent=char, target_inventory=farm_inv)
    hunger.update(1)  # value =5 -> threshold
    assert personal_inv.items.get("wheat", 0) == 1
    assert hunger.value < hunger.threshold


def test_ai_schedule_configurable():
    world = SimNode()
    time = TimeSystem(start_time=22 * 3600, parent=world)
    char = CharacterNode(name="farmer", parent=world)
    TransformNode(parent=char, position=[0.0, 0.0])
    ai = AIBehaviorNode(parent=char, home=char, wake_hour=5, sleep_hour=21)
    ai._determine_target()
    assert ai._sleeping is True
    time.current_time = 5.5 * 3600
    ai._determine_target()
    assert ai._sleeping is False
