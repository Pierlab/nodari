from nodes.world import WorldNode
from nodes.character import CharacterNode
from nodes.need import NeedNode
from systems.scheduler import SchedulerSystem


def test_neednode_can_be_scheduled():
    world = WorldNode(name="world")
    SchedulerSystem(parent=world)
    char = CharacterNode(parent=world)
    need = NeedNode("hunger", threshold=10, increase_rate=1, parent=char, update_interval=2.0)

    for _ in range(5):
        world.update(1.0)

    assert need.value == 4.0
