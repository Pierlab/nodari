"""Entry point for the colony simulation viewer with optional terrain caching."""
from __future__ import annotations

import argparse
import os
from typing import List

__all__ = ["run"]


def run(argv: List[str] | None = None) -> None:  # pragma: no cover - manual launch
    parser = argparse.ArgumentParser(description="Colony simulation viewer")
    parser.add_argument(
        "--viewer",
        choices=["pygame", "moderngl"],
        default="pygame",
        help="Backend graphique à utiliser",
    )
    args = parser.parse_args(argv)

    cache_path = os.path.join(os.path.dirname(__file__), "terrain_cache.pkl")
    if os.path.exists(cache_path):
        os.environ.setdefault("WAR_TERRAIN_CACHE", cache_path)

    from simulation.war import war_loader

    _orig_setup_world = war_loader.setup_world

    def _setup_world(config_file: str | None = None, settings_file: str | None = None):
        return _orig_setup_world(config_file or "example/colony_config.json", settings_file)

    war_loader.setup_world = _setup_world

    from simulation.war.viewer_loop import run as viewer_run
    viewer_run(viewer=args.viewer)


if __name__ == "__main__":  # pragma: no cover - manual launch
    run()
