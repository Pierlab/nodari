from core.simnode import SimNode
from nodes.officer import OfficerNode
from nodes.unit import UnitNode


def test_order_forwarding_and_unit_listing():
    root = SimNode("root")
    officer = OfficerNode(parent=root)
    unit = UnitNode(parent=officer)
    acks: list[dict] = []
    issued: list[dict] = []
    root.on_event("order_ack", lambda _o, _e, p: acks.append(p))
    root.on_event("order_issued", lambda _o, _e, p: issued.append(p))

    order = {"command": "advance", "recipient": unit.name}
    officer.emit("order_received", order)

    assert acks and acks[0]["order"] == order
    assert issued and issued[0]["recipient_group"] == "units"
    assert issued[0]["issuer_id"] == id(officer)
    assert officer.get_units() == [unit]
