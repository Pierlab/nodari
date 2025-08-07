"""Core simulation node with event bus and hierarchy management."""
from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple


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
        # Cached immutable view of ``children`` used for iteration without
        # repeated list copying. Marked dirty whenever the children list
        # changes.
        self._iter_children: Tuple[SimNode, ...] = ()
        self._children_dirty = False
        # Mapping of event name to list of (priority, handler)
        self._listeners: Dict[str, List[Tuple[int, EventHandler]]] = {}
        # When ``True`` the node is excluded from automatic updates and must
        # be advanced manually (e.g. by a scheduler system).
        self._manual_update = False
        if parent is not None:
            parent.add_child(self)

    # ------------------------------------------------------------------
    # Hierarchy management
    # ------------------------------------------------------------------
    def add_child(self, node: "SimNode") -> None:
        """Attach *node* as a child of this node."""
        node.parent = self
        self.children.append(node)
        self._children_dirty = True

    def remove_child(self, node: "SimNode") -> None:
        """Remove *node* from children."""
        self.children.remove(node)
        node.parent = None
        self._children_dirty = True

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------
    def on_event(self, event_name: str, handler: EventHandler, priority: int = 0) -> None:
        """Register *handler* for *event_name* with optional *priority*.

        Handlers with higher priority are invoked before those with lower
        priority. Handlers with the same priority keep their registration
        order thanks to the stability of list sorting.
        """

        listeners = self._listeners.setdefault(event_name, [])
        listeners.append((priority, handler))
        listeners.sort(key=lambda item: item[0], reverse=True)

    def off_event(self, event_name: str, handler: EventHandler) -> None:
        """Unregister *handler* from *event_name*."""
        handlers = self._listeners.get(event_name)
        if handlers:
            for i, (_prio, hnd) in enumerate(handlers):
                if hnd is handler:
                    del handlers[i]
                    break

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
        for _prio, handler in list(self._listeners.get(event_name, [])):
            handler(origin or self, event_name, payload)

        if direction == "up":
            for child in self._get_iter_children():
                if child is not origin:
                    child.emit(event_name, payload, direction="down", origin=origin or self)
            if self.parent is not None:
                self.parent.emit(event_name, payload, direction="up", origin=origin or self)
        elif direction == "down":
            for child in self._get_iter_children():
                if child is not origin:
                    child.emit(event_name, payload, direction="down", origin=origin or self)

    async def emit_async(
        self,
        event_name: str,
        payload: Optional[Dict[str, Any]] = None,
        direction: str = "up",
        origin: Optional["SimNode"] = None,
    ) -> None:
        """Asynchronously emit an event.

        This variant awaits any coroutine handlers and propagates events using
        ``asyncio``. Local handlers are awaited before propagation to ensure
        deterministic ordering similar to the synchronous ``emit``.
        """

        payload = payload or {}
        tasks: List[asyncio.Future] = []
        for _prio, handler in list(self._listeners.get(event_name, [])):
            result = handler(origin or self, event_name, payload)
            if inspect.isawaitable(result):
                tasks.append(asyncio.ensure_future(result))
        if tasks:
            await asyncio.gather(*tasks)

        prop_tasks: List[asyncio.Future] = []
        if direction == "up":
            for child in self._get_iter_children():
                if child is not origin:
                    prop_tasks.append(
                        child.emit_async(event_name, payload, direction="down", origin=origin or self)
                    )
            if self.parent is not None:
                prop_tasks.append(
                    self.parent.emit_async(event_name, payload, direction="up", origin=origin or self)
                )
        elif direction == "down":
            for child in self._get_iter_children():
                if child is not origin:
                    prop_tasks.append(
                        child.emit_async(event_name, payload, direction="down", origin=origin or self)
                    )
        if prop_tasks:
            await asyncio.gather(*prop_tasks)

    # ------------------------------------------------------------------
    # Simulation API
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Update the node for a simulation tick."""
        for child in self._get_iter_children():
            if getattr(child, "_manual_update", False):
                # Scheduled nodes are updated externally and skipped here.
                continue
            child.update(dt)

    # Internal helpers -------------------------------------------------
    def _get_iter_children(self) -> Tuple["SimNode", ...]:
        """Return an up-to-date immutable view of ``children``.

        The tuple is rebuilt only when the children list has changed, which
        avoids repeatedly copying large lists during tight update or event
        loops. Newly added or removed children therefore take effect on the
        next iteration.
        """

        if self._children_dirty:
            self._iter_children = tuple(self.children)
            self._children_dirty = False
        return self._iter_children

    def _serialize_value(self, value: Any) -> Any:
        """Serialise *value* supporting nested structures and node refs."""
        if isinstance(value, SimNode):
            return value.name
        if isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value

    def serialize(self) -> Dict[str, Any]:
        """Return a serialisable representation of this node with state."""
        state = {
            k: self._serialize_value(v)
            for k, v in self.__dict__.items()
            if k
            not in {
                "name",
                "parent",
                "children",
                "_listeners",
                "_iter_children",
                "_children_dirty",
            }
        }
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "state": state,
            "children": [child.serialize() for child in self.children],
        }


class SystemNode(SimNode):
    """Base class for global systems."""

    def __init__(self, name: Optional[str] = None, parent: Optional[SimNode] = None) -> None:
        super().__init__(name=name, parent=parent)
