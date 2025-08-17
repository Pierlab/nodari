from nodes.strategist import StrategistNode
from nodes.officer import OfficerNode
from nodes.bodyguard import BodyguardUnitNode
from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.unit import UnitNode


def test_strategist_collects_intel():
    strategist = StrategistNode()
    strategist.emit("intel_report", {"enemy": "north"})
    assert strategist.get_intel()[0]["enemy"] == "north"


def test_officer_lists_units():
    officer = OfficerNode(name="officer")
    unit = UnitNode(name="u1")
    officer.add_child(unit)
    assert officer.get_units() == [unit]


def test_bodyguard_defaults_and_is_unit():
    bodyguard = BodyguardUnitNode()
    assert isinstance(bodyguard, UnitNode)
    assert bodyguard.size == 5


def test_general_issue_orders_and_attributes():
    general = GeneralNode(style="balanced")
    army = ArmyNode(parent=general, goal="advance", size=0)
    orders: list[dict] = []
    army.on_event("order_issued", lambda _o, _e, payload: orders.append(payload))
    general.issue_orders([{ "cmd": "hold" }])
    assert orders[0]["cmd"] == "hold"
    assert general.caution_level == 0.5
    assert general.intel_confidence == 1.0
    assert general.command_delay_s == 0.0


def test_army_lists_officers():
    army = ArmyNode(goal="advance", size=0)
    officer = OfficerNode(parent=army)
    assert army.get_officers() == [officer]
