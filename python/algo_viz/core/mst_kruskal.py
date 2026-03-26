from __future__ import annotations

from typing import Iterator

from algo_viz.core.graph import Graph
from algo_viz.core.union_find import UnionFind
from algo_viz.models.result import MSTResult
from algo_viz.models.step import AlgorithmStep, StepKind


def kruskal_steps(graph: Graph) -> Iterator[AlgorithmStep]:
    sorted_edges = sorted(
        (e for e in graph.edge_list if not e.blocked),
        key=lambda e: e.weight,
    )

    uf = UnionFind(graph.num_vertices)
    mst_edges: set[int] = set()
    step = 0

    for edge in sorted_edges:
        if graph.vertex_blocked[edge.src] or graph.vertex_blocked[edge.dest]:
            continue

        step += 1
        yield AlgorithmStep(
            kind=StepKind.CONSIDERING_EDGE,
            active_edges=frozenset({edge.edge_id}),
            mst_edges=frozenset(mst_edges),
            union_find_state=uf.snapshot(),
            explanation=f"Considering edge {edge.src}-{edge.dest} (weight {edge.weight})",
            step_number=step,
        )

        if uf.find(edge.src) != uf.find(edge.dest):
            uf.union(edge.src, edge.dest)
            mst_edges.add(edge.edge_id)
            step += 1
            yield AlgorithmStep(
                kind=StepKind.EDGE_ACCEPTED,
                active_edges=frozenset({edge.edge_id}),
                mst_edges=frozenset(mst_edges),
                union_find_state=uf.snapshot(),
                explanation="Accepted: connects two components",
                step_number=step,
            )
        else:
            step += 1
            yield AlgorithmStep(
                kind=StepKind.EDGE_REJECTED,
                active_edges=frozenset({edge.edge_id}),
                mst_edges=frozenset(mst_edges),
                union_find_state=uf.snapshot(),
                explanation="Rejected: would create cycle",
                step_number=step,
            )

    step += 1
    yield AlgorithmStep(
        kind=StepKind.MST_COMPLETE,
        mst_edges=frozenset(mst_edges),
        union_find_state=uf.snapshot(),
        explanation="MST complete",
        step_number=step,
    )


def kruskal(graph: Graph) -> MSTResult:
    last_step: AlgorithmStep | None = None
    for last_step in kruskal_steps(graph):
        pass

    mst_edge_ids: frozenset[int] = (
        last_step.mst_edges if last_step is not None else frozenset()
    )

    edges: list[tuple[int, int, int]] = []
    total_weight = 0
    for eid in mst_edge_ids:
        e = graph.edge_list[eid]
        edges.append((e.src, e.dest, e.weight))
        total_weight += e.weight

    is_connected = len(edges) == graph.num_vertices - 1

    return MSTResult(
        edges=edges,
        total_weight=total_weight,
        num_edges=len(edges),
        is_connected=is_connected,
    )
