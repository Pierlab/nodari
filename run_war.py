"""Entry point for the war simulation viewer with optional terrain caching."""
from __future__ import annotations

import argparse
import os
from typing import Any, List

__all__ = ["load_sim_params", "_spawn_armies", "sim_params", "run"]

def load_sim_params(path: str) -> dict:
    from simulation.war.war_loader import load_sim_params as _load
    return _load(path)

def _spawn_armies(*args: Any, **kwargs: Any) -> None:
    from simulation.war.war_loader import _spawn_armies as _spawn
    return _spawn(*args, **kwargs)


class _SimParamsProxy(dict):
    def _data(self):
        from simulation.war.war_loader import sim_params as data
        return data
    def __getitem__(self, key):
        return self._data()[key]
    def __setitem__(self, key, value):
        self._data()[key] = value
    def __iter__(self):
        return iter(self._data())
    def items(self):
        return self._data().items()
    def keys(self):
        return self._data().keys()
    def values(self):
        return self._data().values()
    def get(self, key, default=None):
        return self._data().get(key, default)
    def update(self, *args, **kwargs):
        return self._data().update(*args, **kwargs)
    def __repr__(self):
        return repr(self._data())

sim_params = _SimParamsProxy()


def run(argv: List[str] | None = None) -> None:  # pragma: no cover - manual launch
    parser = argparse.ArgumentParser(description="War simulation viewer")
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
    from simulation.war.viewer_loop import run as viewer_run
    viewer_run(viewer=args.viewer)

if __name__ == "__main__":  # pragma: no cover - manual launch
    run()
