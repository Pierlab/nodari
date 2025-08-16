from core.simnode import SimNode
from nodes.unit import UnitNode
from nodes.nation import NationNode
from nodes.army import ArmyNode
from nodes.transform import TransformNode


def test_engage_and_route_events():
    root = SimNode("root")
    unit = UnitNode(parent=root)
    events: list[tuple[str, dict]] = []
    root.on_event("unit_engaged", lambda _o, _e, p: events.append(("engaged", p)))
    root.on_event("unit_routed", lambda _o, _e, p: events.append(("routed", p)))

    unit.engage(enemy="enemy_unit")
    assert unit.state == "fighting"
    assert events[0][0] == "engaged"
    assert events[0][1]["enemy"] == "enemy_unit"

    unit.route()
    assert unit.state == "fleeing"
    assert events[1][0] == "routed"
    assert events[1][1]["loss"] == 1


def test_unit_retreats_when_morale_low():
    root = SimNode("root")
    nation = NationNode(parent=root, morale=100, capital_position=[0, 0])
    army = ArmyNode(parent=nation, goal="advance")
    unit = UnitNode(parent=army, morale=10, target=[10, 0])
    TransformNode(parent=unit, position=[5, 0])

    unit.update(0)

    assert unit.state == "fleeing"
    assert unit.target == [0, 0]
