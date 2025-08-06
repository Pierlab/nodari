import logging

from nodes.world import WorldNode
from nodes.character import CharacterNode
from nodes.need import NeedNode
from systems.logger import LoggingSystem


def test_logging_system_records_events(caplog):
    world = WorldNode(name="world")
    char = CharacterNode(name="char", parent=world)
    need = NeedNode(need_name="hunger", threshold=1, increase_rate=2, parent=char)
    logger_sys = LoggingSystem(parent=world, events=["need_threshold_reached"])
    with caplog.at_level(logging.INFO, logger=logger_sys.logger.name):
        world.update(1)
    assert any("need_threshold_reached" in message for message in caplog.messages)
