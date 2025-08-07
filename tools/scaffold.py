#!/usr/bin/env python3
"""Scaffold new node or system plugins from templates."""
from __future__ import annotations

import argparse
import pathlib
import textwrap

TEMPLATES = {
    "node": textwrap.dedent(
        """
        from core.simnode import SimNode
        from core.plugins import register_node_type


        class {class_name}(SimNode):
            '''TODO: describe node.'''

            def update(self, dt: float) -> None:
                super().update(dt)


        register_node_type("{class_name}", {class_name})
        """
    ),
    "system": textwrap.dedent(
        """
        from core.simnode import SimNode
        from core.plugins import register_node_type


        class {class_name}(SimNode):
            '''TODO: describe system.'''

            def update(self, dt: float) -> None:
                super().update(dt)


        register_node_type("{class_name}", {class_name})
        """
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new node or system")
    parser.add_argument("kind", choices=["node", "system"], help="plugin type")
    parser.add_argument("name", help="Class name for the plugin")
    args = parser.parse_args()

    root = pathlib.Path(__file__).resolve().parent.parent
    target_dir = root / ("nodes" if args.kind == "node" else "systems")
    file_path = target_dir / f"{args.name.lower()}.py"
    if file_path.exists():
        raise SystemExit(f"{file_path} already exists")
    content = TEMPLATES[args.kind].format(class_name=args.name)
    file_path.write_text(content)
    print(f"Created {file_path}")


if __name__ == "__main__":
    main()
