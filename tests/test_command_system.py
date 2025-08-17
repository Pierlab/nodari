from nodes.general import GeneralNode
from nodes.army import ArmyNode
from nodes.officer import OfficerNode
from nodes.unit import UnitNode
from nodes.nation import NationNode
from systems.command import CommandSystem
from nodes.transform import TransformNode


def test_command_delivery_and_ack():
    root = NationNode(morale=100, capital_position=[0, 0])
    cmd = CommandSystem(parent=root, distance_delay_factor=0.1)
    gen = GeneralNode(style="balanced", parent=root)
    army = ArmyNode(parent=gen, goal="advance", size=0)
    officer = OfficerNode(parent=army)
    unit = UnitNode(parent=officer)
    TransformNode(position=[0.0, 0.0], parent=gen)
    TransformNode(position=[10.0, 0.0], parent=officer)
    TransformNode(position=[20.0, 0.0], parent=unit)
    acks = []
    gen.on_event("order_ack", lambda _o, _e, p: acks.append(p))
    gen.issue_orders([
        {
            "order_type": "move",
            "priority": 1,
            "recipient_group": "officers",
        }
    ])
    cmd.update(1.0)
    cmd.update(1.0)
    assert unit.current_order and unit.current_order["order_type"] == "move"
    assert acks


def test_command_reliability_drop():
    root = NationNode(morale=100, capital_position=[0, 0])
    cmd = CommandSystem(parent=root, reliability=0.0)
    gen = GeneralNode(style="balanced", parent=root)
    officer = OfficerNode(parent=ArmyNode(parent=gen, goal="advance", size=0))
    unit = UnitNode(parent=officer)
    gen.issue_orders([{ "order_type": "hold", "recipient_group": "officers" }])
    cmd.update(1.0)
    cmd.update(1.0)
    assert unit.current_order is None
