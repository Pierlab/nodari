from nodes.strategist import StrategistNode
from nodes.officer import OfficerNode
from nodes.bodyguard import BodyguardUnitNode
from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.unit import UnitNode
from nodes.nation import NationNode


def test_strategist_collects_recent_intel():
    strategist = StrategistNode()
    strategist.emit("enemy_spotted", {"enemy": "north", "timestamp": 0})
    strategist.emit("enemy_spotted", {"enemy": "south"})
    intel = strategist.get_enemy_estimates(max_age_s=60)
    assert len(intel) == 1 and intel[0]["enemy"] == "south"


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


def test_general_uses_strategist_intel():
    root = NationNode(morale=100, capital_position=[0, 0])
    gen = GeneralNode(style="aggressive", caution_level=0.1, parent=root)
    strat = StrategistNode(parent=gen)
    army = ArmyNode(parent=gen, goal="hold", size=0)
    strat.emit("enemy_spotted", {"enemy": "x"})
    gen._decide()
    assert army.goal in {"advance", "flank"}


def test_army_lists_officers():
    army = ArmyNode(goal="advance", size=0)
    officer = OfficerNode(parent=army)
    assert army.get_officers() == [officer]
