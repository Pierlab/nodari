from __future__ import annotations

import random

from nodes.world import WorldNode


def test_world_seed_reproducibility() -> None:
    """WorldNode seeds the global RNG for deterministic simulations."""
    state = random.getstate()
    try:
        WorldNode(name="w1", seed=123)
        seq1 = [random.random() for _ in range(3)]
        WorldNode(name="w2", seed=123)
        seq2 = [random.random() for _ in range(3)]
        assert seq1 == seq2

        WorldNode(name="w3", seed=456)
        seq3 = [random.random() for _ in range(3)]
        assert seq1 != seq3
    finally:
        random.setstate(state)

