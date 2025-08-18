from nodes.world import WorldNode
from nodes.building import BuildingNode
from systems.combat import CombatSystem


def test_building_destroyed_after_sufficient_damage():
    world = WorldNode()
    CombatSystem(parent=world)
    building = BuildingNode(parent=world, type="warehouse", hit_points=50)
    events = []
    building.on_event("building_destroyed", lambda _o, _e, p: events.append(p))

    world.emit("attack_building", {"target": building, "damage": 30})
    assert building.hit_points == 20
    assert building in world.children

    world.emit("attack_building", {"target": building, "damage": 20})
    assert building.hit_points == 0
    assert events and events[0]["building"] == "warehouse"
    assert building not in world.children
