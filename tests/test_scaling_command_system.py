import pytest
import config
from nodes.world import WorldNode
from nodes.unit import UnitNode
from nodes.transform import TransformNode
from systems.movement import MovementSystem
from systems.command import CommandSystem


def test_unit_movement_and_command_delay_scaling():
    distance_m = 100.0
    distance_units = distance_m / config.WORLD_SCALE_M

    world = WorldNode(width=int(distance_units) + 10, height=10)
    MovementSystem(parent=world)
    cmd = CommandSystem(parent=world, base_delay_s=2.0, distance_delay_factor=0.5)

    unit_a = UnitNode(parent=world, speed=1.0, target=[distance_units, 0])
    TransformNode(parent=unit_a, position=[0.0, 0.0])

    unit_b = UnitNode(parent=world, speed=0.0)
    TransformNode(parent=unit_b, position=[distance_units, 0.0])

    ticks = 3
    for _ in range(ticks):
        world.update(config.TIME_SCALE)

    transform_a = next(c for c in unit_a.children if isinstance(c, TransformNode))
    moved_m = transform_a.position[0] * config.WORLD_SCALE_M
    expected_m = unit_a.speed * ticks * config.TIME_SCALE * config.WORLD_SCALE_M
    assert moved_m == pytest.approx(expected_m)

    received: list[dict] = []
    unit_b.on_event("order_received", lambda _o, _e, p: received.append(p))
    unit_a.emit("order_issued", {"order_type": "hold", "recipient": unit_b})

    transform_b = next(c for c in unit_b.children if isinstance(c, TransformNode))
    dist_units = abs(transform_b.position[0] - transform_a.position[0])
    expected_delay = 2.0 + dist_units * 0.5

    cmd.update(expected_delay - 0.1)
    assert not received
    cmd.update(0.1)
    assert received and received[0]["order_type"] == "hold"
