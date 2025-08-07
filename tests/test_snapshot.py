from core.snapshot import serialize_world, deserialize_world
from nodes.world import WorldNode
from nodes.inventory import InventoryNode
from nodes.need import NeedNode
from nodes.character import CharacterNode
from nodes.transform import TransformNode
from nodes.ai_behavior import AIBehaviorNode


def test_snapshot_roundtrip():
    world = WorldNode(name="world")
    home = InventoryNode(name="home", items={}, parent=world)
    char = CharacterNode(name="char", parent=world)
    inv = InventoryNode(name="inv", items={"wheat": 3}, parent=char)
    NeedNode(name="hunger", need_name="hunger", threshold=10, increase_rate=1.0, value=5.0, parent=char)
    TransformNode(name="pos", position=[1.0, 2.0], parent=char)
    ai = AIBehaviorNode(name="ai", target_inventory=inv, home="home", parent=char)
    ai._idle = True

    data = serialize_world(world)
    restored = deserialize_world(data)

    new_char = next(child for child in restored.children if child.name == "char")
    inv_restored = next(
        child for child in new_char.children if isinstance(child, InventoryNode) and child.name == "inv"
    )
    need_restored = next(child for child in new_char.children if isinstance(child, NeedNode))
    ai_restored = next(child for child in new_char.children if isinstance(child, AIBehaviorNode))

    assert inv_restored.items["wheat"] == 3
    assert need_restored.value == 5.0
    assert ai_restored._idle is True
    # target inventory restored as reference string
    assert ai_restored.target_inventory == "inv"
    ai_restored._resolve_references()
    assert ai_restored.home is not None and ai_restored.home.name == "home"
