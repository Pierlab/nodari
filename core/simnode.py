"""Core simulation node with event bus and hierarchy management."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


EventHandler = Callable[["SimNode", str, Dict[str, Any]], None]


class SimNode:
    """Base class for all nodes in the simulation tree.

    Parameters
    ----------
    name:
        Optional name for the node. Defaults to class name.
    parent:
        Optional parent node in the tree.
    """

    def __init__(self, name: Optional[str] = None, parent: Optional["SimNode"] = None) -> None:
        self.name = name or self.__class__.__name__
        self.parent = parent
        self.children: List[SimNode] = []
        self._listeners: Dict[str, List[EventHandler]] = {}
        if parent is not None:
            parent.add_child(self)

    # ------------------------------------------------------------------
    # Hierarchy management
    # ------------------------------------------------------------------
    def add_child(self, node: "SimNode") -> None:
        """Attach *node* as a child of this node."""
        node.parent = self
        self.children.append(node)

    def remove_child(self, node: "SimNode") -> None:
        """Remove *node* from children."""
        self.children.remove(node)
        node.parent = None

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------
    def on_event(self, event_name: str, handler: EventHandler) -> None:
        """Register *handler* for *event_name*."""
        self._listeners.setdefault(event_name, []).append(handler)

    def off_event(self, event_name: str, handler: EventHandler) -> None:
        """Unregister *handler* from *event_name*."""
        handlers = self._listeners.get(event_name)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def emit(
        self,
        event_name: str,
        payload: Optional[Dict[str, Any]] = None,
        direction: str = "up",
        origin: Optional["SimNode"] = None,
    ) -> None:
        """Emit an event.

        Parameters
        ----------
        event_name:
            Name of the event.
        payload:
            Optional dictionary of data.
        direction:
            ``"up"`` bubbles to the parent and siblings, ``"down"``
            propagates to children. Default ``"up"``.
        origin:
            Original node from which the event was emitted. Used internally
            to avoid echoing events back to the sender.
        """

        payload = payload or {}
        for handler in list(self._listeners.get(event_name, [])):
            handler(origin or self, event_name, payload)

        if direction == "up":
            for child in list(self.children):
                if child is not origin:
                    child.emit(event_name, payload, direction="down", origin=origin or self)
            if self.parent is not None:
                self.parent.emit(event_name, payload, direction="up", origin=origin or self)
        elif direction == "down":
            for child in list(self.children):
                if child is not origin:
                    child.emit(event_name, payload, direction="down", origin=origin or self)

    # ------------------------------------------------------------------
    # Simulation API
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Update the node for a simulation tick."""
        for child in list(self.children):
            child.update(dt)

    def serialize(self) -> Dict[str, Any]:
        """Return a serialisable representation of this node."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "children": [child.serialize() for child in self.children],
        }


class SystemNode(SimNode):
    """Base class for global systems."""

    def __init__(self, name: Optional[str] = None, parent: Optional[SimNode] = None) -> None:
        super().__init__(name=name, parent=parent)
