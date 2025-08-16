from core.simnode import SimNode
from nodes.unit import UnitNode


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
