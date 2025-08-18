"""ModernGL-based viewer system implementing the :class:`Viewer` interface."""
from __future__ import annotations

from typing import Any, List

import config
from core.simnode import SystemNode
from core.plugins import register_node_type
from systems.pygame_viewer import Viewer

try:  # pragma: no cover - optional dependency
    import moderngl
    import pygame
except Exception:  # pragma: no cover - gracefully handle missing libs
    moderngl = None  # type: ignore
    pygame = None  # type: ignore


class ModernGLViewerSystem(SystemNode, Viewer):
    """Viewer backend leveraging ModernGL for GPU acceleration."""

    def __init__(
        self,
        width: int = config.VIEW_WIDTH,
        height: int = config.VIEW_HEIGHT,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if moderngl is None or pygame is None:  # pragma: no cover - depends on env
            raise RuntimeError("moderngl and pygame are required for ModernGLViewerSystem")
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption(self.name)
        self.ctx = moderngl.create_context()  # pragma: no cover - visual output
        self.width = width
        self.height = height

    def process_events(self, events: List[Any]) -> None:
        """Basic event processing for compatibility with the viewer loop."""
        for event in events:
            if event.type == pygame.QUIT:  # type: ignore[attr-defined]
                pygame.quit()

    def update(self, dt: float) -> None:
        """Update internal state (no-op for this simple viewer)."""
        pass

    def render(self) -> None:  # pragma: no cover - requires OpenGL context
        """Clear the screen using ModernGL and swap buffers."""
        self.ctx.clear(0.1, 0.1, 0.1)
        pygame.display.flip()


register_node_type("ModernGLViewerSystem", ModernGLViewerSystem)
