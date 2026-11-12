"""Adaptive octree voxelization for a binary occupancy function."""

from dataclasses import dataclass
from itertools import product
from math import isfinite
from random import Random
from typing import Callable

Point = tuple[float, float, float]


@dataclass(frozen=True)
class Leaf:
    path: str
    origin: Point
    edge: float
    filled: bool
    hit_ratio: float


def voxelize(
    inside: Callable[[Point], bool],
    *,
    origin: Point = (0.0, 0.0, 0.0),
    edge: float = 1.0,
    samples: int = 96,
    max_depth: int = 5,
    lower: float = 0.02,
    upper: float = 0.98,
    fill: float = 0.5,
    seed: int = 17,
) -> list[Leaf]:
    """Split the root, then estimate occupancy and refine each mixed cube.

    The root has depth zero. A leaf path encodes the x, y and z halves at
    each level, with 0 for the low half, 1 for the high half and x between
    triplets. Each leaf covers a half-open cube.
    """
    if len(origin) != 3 or not all(isfinite(value) for value in origin):
        raise ValueError("origin must contain three finite coordinates")
    if not isfinite(edge) or edge <= 0:
        raise ValueError("edge must be finite and positive")
    if type(samples) is not int or samples < 1:
        raise ValueError("samples must be a positive integer")
    if type(max_depth) is not int or max_depth < 1:
        raise ValueError("max_depth must be a positive integer")
    if not 0 <= lower < fill < upper <= 1:
        raise ValueError("thresholds must satisfy 0 <= lower < fill < upper <= 1")

    random = Random(seed)
    leaves = []

    def split(corner: Point, width: float, depth: int, path: str) -> None:
        half = width / 2
        for x, y, z in product((0, 1), repeat=3):
            code = f"{x}{y}{z}"
            child = (corner[0] + x * half, corner[1] + y * half, corner[2] + z * half)
            visit(child, half, depth + 1, f"{path}x{code}" if path else code)

    def visit(corner: Point, width: float, depth: int, path: str) -> None:
        hits = sum(
            inside((
                corner[0] + random.random() * width,
                corner[1] + random.random() * width,
                corner[2] + random.random() * width,
            ))
            for _ in range(samples)
        )
        ratio = hits / samples
        if lower < ratio < upper and depth < max_depth:
            split(corner, width, depth, path)
        else:
            leaves.append(Leaf(path, corner, width, ratio >= fill, ratio))

    split(origin, edge, 0, "")
    return leaves
