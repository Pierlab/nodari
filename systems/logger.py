"""Event logging system."""
from __future__ import annotations

import logging
from typing import Iterable, Optional

from core.simnode import SystemNode
from core.plugins import register_node_type


class LoggingSystem(SystemNode):
    """Log specified events for observation.

    Parameters
    ----------
    events:
        Iterable of event names to log. If ``None``, a default set of
        common events is used.
    logger:
        Optional :class:`logging.Logger` instance. Defaults to one named
        after the system.
    """

    DEFAULT_EVENTS = [
        "tick",
        "phase_changed",
        "inventory_changed",
        "resource_produced",
        "need_threshold_reached",
        "need_satisfied",
    ]

    def __init__(
        self,
        events: Optional[Iterable[str]] = None,
        logger: Optional[logging.Logger] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.logger = logger or logging.getLogger(self.name)
        self.events = list(events) if events is not None else list(self.DEFAULT_EVENTS)
        for event in self.events:
            self.on_event(event, self._log_event)

    def _log_event(self, origin, event_name, payload) -> None:
        """Log an incoming event."""
        self.logger.info("%s from %s: %s", event_name, origin.name, payload)


register_node_type("LoggingSystem", LoggingSystem)
