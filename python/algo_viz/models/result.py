from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MSTResult:
    edges: list[tuple[int, int, int]]  # (src, dest, weight)
    total_weight: int
    num_edges: int
    is_connected: bool


@dataclass
class SPResult:
    dist: dict[int, int]
    prev: dict[int, int]
    source: int
    num_vertices: int
