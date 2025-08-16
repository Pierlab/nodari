"""Nation node representing a faction in the war simulation."""
from __future__ import annotations

from typing import List

from core.simnode import SimNode
from core.plugins import register_node_type


class NationNode(SimNode):
    """Represent a nation with morale and capital position.

    Parameters
    ----------
    morale:
        Initial morale value.
    capital_position:
        ``[x, y]`` coordinates of the nation's capital.
    """

    def __init__(self, morale: int, capital_position: List[int], **kwargs) -> None:
        super().__init__(**kwargs)
        self.morale = morale
        self.capital_position = capital_position

    # ------------------------------------------------------------------
    def change_morale(self, delta: int) -> None:
        """Adjust morale by *delta* and emit ``moral_changed``."""

        previous = self.morale
        self.morale += delta
        self.emit(
            "moral_changed",
            {"previous": previous, "morale": self.morale, "delta": delta},
            direction="down",
        )

    # ------------------------------------------------------------------
    def capture_capital(self) -> None:
        """Emit ``capital_captured`` for this nation's capital."""

        self.emit(
            "capital_captured",
            {"position": self.capital_position},
            direction="down",
        )

    # ------------------------------------------------------------------
    def get_generals(self) -> List[SimNode]:
        """Return direct child nodes considered generals."""

        return [c for c in self.children if c.__class__.__name__ == "GeneralNode"]

    # ------------------------------------------------------------------
    def get_armies(self) -> List[SimNode]:
        """Return all descendant nodes considered armies."""

        armies: List[SimNode] = []
        stack = list(self.children)
        while stack:
            node = stack.pop()
            if node.__class__.__name__ == "ArmyNode":
                armies.append(node)
            stack.extend(node.children)
        return armies


register_node_type("NationNode", NationNode)

