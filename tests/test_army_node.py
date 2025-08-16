from core.simnode import SimNode
from nodes.army import ArmyNode


def test_goal_change_and_unit_listing():
    army = ArmyNode(goal="defend", size=0)
    events: list[dict] = []
    army.on_event("goal_changed", lambda _o, _e, payload: events.append(payload))

    army.change_goal("advance")

    assert army.goal == "advance"
    assert events[0]["previous"] == "defend"
    assert events[0]["goal"] == "advance"

    class UnitNode(SimNode):
        pass

    unit = UnitNode(name="unit")
    army.add_child(unit)

    assert army.get_units() == [unit]


def test_unit_events_update_size_and_emit_report():
    root = SimNode("root")
    army = ArmyNode(goal="advance", size=1, parent=root)

    class UnitNode(SimNode):
        pass

    unit = UnitNode(parent=army)

    reports: list[dict] = []
    root.on_event("battlefield_event", lambda _o, _e, payload: reports.append(payload))

    unit.emit("unit_routed", {}, direction="up")

    assert army.size == 0
    assert reports[0]["type"] == "unit_routed"
