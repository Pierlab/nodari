import logging
import random

from nodes.world import WorldNode
from nodes.transform import TransformNode
from nodes.unit import UnitNode
from nodes.nation import NationNode
from systems.movement import MovementSystem
from systems.combat import CombatSystem
from systems.logger import LoggingSystem


def test_unit_movement_logged(caplog):
    world = WorldNode(name="world")
    MovementSystem(parent=world)
    logger_sys = LoggingSystem(parent=world, events=["unit_moved"])
    unit = UnitNode(name="u1", target=[1, 0], parent=world)
    TransformNode(position=[0, 0], parent=unit)
    with caplog.at_level(logging.INFO, logger=logger_sys.logger.name):
        world.update(1)
    assert any("unit_moved" in message for message in caplog.messages)


def test_combat_logged(caplog):
    random.seed(0)
    world = WorldNode(name="world")
    CombatSystem(parent=world)
    logger_sys = LoggingSystem(parent=world, events=["combat_occurred"])
    nation_a = NationNode(name="a", morale=100, capital_position=[0, 0], parent=world)
    nation_b = NationNode(name="b", morale=100, capital_position=[1, 0], parent=world)
    unit_a = UnitNode(name="ua", size=20, parent=nation_a)
    TransformNode(position=[0, 0], parent=unit_a)
    unit_b = UnitNode(name="ub", size=10, parent=nation_b)
    TransformNode(position=[0, 0], parent=unit_b)
    with caplog.at_level(logging.INFO, logger=logger_sys.logger.name):
        world.update(1)
    assert any("combat_occurred" in message for message in caplog.messages)
