from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class StepKind(Enum):
    CONSIDERING_EDGE = auto()
    EDGE_ACCEPTED = auto()
    EDGE_REJECTED = auto()
    VERTEX_ADDED = auto()
    VERTEX_SETTLED = auto()
    VERTEX_RELAXED = auto()
    VERTEX_DISCOVERED = auto()
    HEAP_STATE = auto()
    PATH_FOUND = auto()
    MST_COMPLETE = auto()
    ALGORITHM_DONE = auto()


@dataclass(frozen=True)
class AlgorithmStep:
    kind: StepKind
    active_vertices: frozenset[int] = frozenset()
    active_edges: frozenset[int] = frozenset()
    mst_edges: frozenset[int] = frozenset()
    settled_vertices: frozenset[int] = frozenset()
    path_vertices: tuple[int, ...] = ()
    distances: dict[int, int] = field(default_factory=dict)
    union_find_state: dict[int, int] = field(default_factory=dict)
    heap_contents: tuple[tuple[int, int], ...] = ()
    explanation: str = ""
    step_number: int = 0
