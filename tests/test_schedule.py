from __future__ import annotations

import random

from core.simnode import SimNode
from nodes.world import WorldNode
from nodes.character import CharacterNode
from nodes.inventory import InventoryNode
from nodes.transform import TransformNode
from nodes.ai_behavior import AIBehaviorNode
from systems.time import TimeSystem


def _create_ai():
    world = WorldNode(name="world")
    home = SimNode(name="home", parent=world)
    TransformNode(position=[0.0, 0.0], parent=home)
    work = SimNode(name="work", parent=world)
    TransformNode(position=[10.0, 0.0], parent=work)
    char = CharacterNode(name="char", parent=world)
    trans = TransformNode(position=[0.0, 0.0], parent=char)
    InventoryNode(name="inv", items={}, parent=char)
    ai = AIBehaviorNode(parent=char, home="home", work="work")
    time = TimeSystem(parent=world)
    ai._resolve_references()
    return ai, time, trans


def test_schedule_and_sleeping():
    ai, time, _ = _create_ai()

    time.current_time = 5 * 3600
    target = ai._determine_target()
    assert ai._sleeping is True
    assert target == [0.0, 0.0]

    time.current_time = 9 * 3600
    target = ai._determine_target()
    assert ai._sleeping is False
    assert target == [10.0, 0.0]

    time.current_time = 23 * 3600
    target = ai._determine_target()
    assert ai._sleeping is True
    assert target == [0.0, 0.0]


def test_idle_jitter():
    random.seed(0)
    ai, time, trans = _create_ai()

    time.current_time = 7 * 3600
    ai.update(1.0)
    assert ai._sleeping is False
    assert trans.position != [0.0, 0.0]
    assert abs(trans.position[0]) <= 0.5
    assert abs(trans.position[1]) <= 0.5

    trans.position = [0.0, 0.0]
    time.current_time = 23 * 3600
    ai.update(1.0)
    assert trans.position == [0.0, 0.0]


def test_return_to_work_after_lunch():
    ai, time, _ = _create_ai()
    # Force idle during lunch
    ai.idle_chance = 1.0
    time.current_time = 13 * 3600
    target = ai._determine_target()
    assert target == ai.lunch_position
    assert ai._idle is True

    # After lunch ends, worker should go back to work
    time.current_time = 14 * 3600
    target = ai._determine_target()
    assert ai._idle is False
    assert target == [10.0, 0.0]


def test_drop_inventory_after_work():
    world = WorldNode(name="world")
    home = SimNode(name="home", parent=world)
    TransformNode(position=[0.0, 0.0], parent=home)
    home_inv = InventoryNode(name="home_inv", items={}, parent=home)
    work = SimNode(name="work", parent=world)
    TransformNode(position=[10.0, 0.0], parent=work)
    char = CharacterNode(name="char", parent=world)
    TransformNode(position=[10.0, 0.0], parent=char)
    personal_inv = InventoryNode(name="inv", items={"water": 2, "wheat": 3, "money": 5}, parent=char)
    ai = AIBehaviorNode(parent=char, home="home", work="work", home_inventory="home_inv")
    time = TimeSystem(parent=world)
    ai._resolve_references()

    time.current_time = 19 * 3600
    ai.update(1.0)

    assert all(qty == 0 for qty in personal_inv.items.values())
    assert home_inv.items == {"water": 2, "wheat": 3, "money": 5}
