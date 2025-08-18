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


def test_order_acknowledgement_and_completion():
    root = SimNode("root")
    unit = UnitNode(parent=root)
    acks: list[dict] = []
    completed: list[dict] = []
    root.on_event("order_ack", lambda _o, _e, p: acks.append(p))
    root.on_event("order_complete", lambda _o, _e, p: completed.append(p))

    order = {"action": "move", "priority": 1, "time_issued": 1}
    root.emit("order_received", order, direction="down")

    assert unit.current_order == order
    assert acks and acks[0]["order"] == order

    unit.complete_order()

    assert unit.current_order is None
    assert completed and completed[0]["order"] == order
