from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.nation import NationNode
from nodes.strategist import StrategistNode


def test_general_records_style_and_reports():
    general = GeneralNode(style="aggressive")
    army = ArmyNode(name="army", goal="advance")
    general.add_child(army)

    army.emit("battlefield_event", {"sector": 1})

    assert general.style == "aggressive"
    assert general.reports[0]["sector"] == 1
    assert general.get_armies() == [army]


def test_general_ai_changes_army_goal_based_on_intel():
    nation = NationNode(name="nation", morale=100, capital_position=[0, 0])
    general = GeneralNode(parent=nation, style="aggressive", caution_level=0.1)
    strategist = StrategistNode(parent=general)
    army = ArmyNode(parent=general, goal="hold", size=1)

    strategist.emit("enemy_spotted", {"enemy": "x"})
    general.update(0)
    assert army.goal in {"advance", "flank"}

    general.caution_level = 0.9
    general.intel_confidence = 0.2
    strategist.emit("enemy_spotted", {"enemy": "y"})
    general.update(0)
    assert army.goal in {"hold", "retreat"}


def test_general_attempts_flank_with_probability():
    general = GeneralNode(style="balanced", flank_success_chance=1.0)
    army = ArmyNode(parent=general, goal="advance", size=1)

    # Guaranteed success
    assert general.attempt_flank(army) is True
    assert army.goal == "flank"

    # Guaranteed failure
    other_army = ArmyNode(parent=general, goal="advance", size=1)
    general.flank_success_chance = 0.0
    assert general.attempt_flank(other_army) is False
    assert other_army.goal == "advance"
