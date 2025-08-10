from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from nodes.transform import TransformNode
    from nodes.ai_behavior import AIBehaviorNode


class BaseRoutine(ABC):
    """Interface for character behaviour routines.

    A routine encapsulates planning, navigation and interactions for an
    :class:`~nodes.ai_behavior.AIBehaviorNode`.
    """

    def __init__(self, ai: AIBehaviorNode) -> None:
        self.ai = ai

    def on_need(self, emitter, event_name: str, payload) -> None:  # pragma: no cover - optional
        """Handle need events (default: no-op)."""
        return None

    @abstractmethod
    def update(self, dt: float, transform: TransformNode) -> None:
        """Update behaviour for the character."""
        raise NotImplementedError
