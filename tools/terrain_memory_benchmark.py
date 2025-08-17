"""Simple benchmark comparing string vs byte-based terrain grids."""

from __future__ import annotations

import sys
from typing import List

import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.terrain_generators import generate_base


def _string_grid(width: int, height: int, fill: str = "plain") -> List[List[str]]:
    return [[fill] * width for _ in range(height)]


def _sizeof_str_grid(grid: List[List[str]]) -> int:
    total = sys.getsizeof(grid)
    for row in grid:
        total += sys.getsizeof(row)
        for cell in row:
            total += sys.getsizeof(cell)
    return total


def _sizeof_byte_grid(grid: List[bytearray]) -> int:
    total = sys.getsizeof(grid)
    for row in grid:
        total += sys.getsizeof(row)
    return total


def benchmark(width: int = 1000, height: int = 1000) -> None:
    """Print approximate memory usage for both grid implementations."""

    str_grid = _string_grid(width, height)
    byte_grid = generate_base(width, height)
    s = _sizeof_str_grid(str_grid)
    b = _sizeof_byte_grid(byte_grid)
    print(f"String grid: {s / 1024 / 1024:.2f} MB")
    print(f"Byte grid  : {b / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    benchmark()
