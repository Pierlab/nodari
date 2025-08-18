from nodes.world import WorldNode
from nodes.nation import NationNode
from nodes.unit import UnitNode
from nodes.transform import TransformNode
from systems.moral import MoralSystem
from systems.victory import VictorySystem


def test_capital_captured_when_enough_enemy_units_present():
    world = WorldNode()
    VictorySystem(parent=world, capture_unit_threshold=1)
    attacker = NationNode(parent=world, morale=100, capital_position=[5, 0])
    defender = NationNode(parent=world, morale=100, capital_position=[0, 0])

    unit = UnitNode(parent=attacker)
    TransformNode(parent=unit, position=[0, 0])

    events: list[dict] = []
    defender.on_event("capital_captured", lambda _o, _e, payload: events.append(payload))
    world.update(1.0)
    assert events and events[0]["position"] == [0, 0]


def test_capture_requires_threshold_number_of_units():
    world = WorldNode()
    VictorySystem(parent=world, capture_unit_threshold=2)
    attacker = NationNode(parent=world, morale=100, capital_position=[5, 0])
    defender = NationNode(parent=world, morale=100, capital_position=[0, 0])

    unit1 = UnitNode(parent=attacker)
    TransformNode(parent=unit1, position=[0, 0])
    events: list[dict] = []
    defender.on_event("capital_captured", lambda _o, _e, payload: events.append(payload))
    world.update(1.0)
    assert not events

    unit2 = UnitNode(parent=attacker)
    TransformNode(parent=unit2, position=[0, 0])
    world.update(1.0)
    assert events and events[0]["position"] == [0, 0]


def test_nation_defeated_on_moral_collapse():
    world = WorldNode()
    MoralSystem(parent=world)
    VictorySystem(parent=world)
    nation = NationNode(parent=world, morale=1, capital_position=[0, 0])

    defeated: list[dict] = []
    nation.on_event("nation_defeated", lambda _o, _e, payload: defeated.append(payload))
    nation.change_morale(-1)
    world.update(1.0)
    assert defeated and defeated[0]["reason"] == "moral_collapse"


def test_capital_capture_emitted_only_once():
    world = WorldNode()
    VictorySystem(parent=world, capture_unit_threshold=1)
    attacker = NationNode(parent=world, morale=100, capital_position=[5, 0])
    defender = NationNode(parent=world, morale=100, capital_position=[0, 0])
    unit1 = UnitNode(parent=attacker)
    TransformNode(parent=unit1, position=[0, 0])
    events: list[dict] = []
    defender.on_event("capital_captured", lambda _o, _e, p: events.append(p))
    world.update(1.0)
    assert len(events) == 1
    unit2 = UnitNode(parent=attacker)
    TransformNode(parent=unit2, position=[0, 0])
    world.update(1.0)
    assert len(events) == 1
