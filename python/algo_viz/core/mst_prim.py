from __future__ import annotations

from typing import Iterator

from algo_viz.core.graph import Graph
from algo_viz.core.min_heap import MinHeap
from algo_viz.models.result import MSTResult
from algo_viz.models.step import AlgorithmStep, StepKind

INF = float("inf")


def _build_mst_edges(graph: Graph, parent: dict[int, int]) -> frozenset[int]:
    edge_ids: set[int] = set()
    for v, u in parent.items():
        if u == -1:
            continue
        for adj in graph.adj[u]:
            if adj.dest == v:
                edge_ids.add(adj.edge_id)
                break
    return frozenset(edge_ids)


def prim_steps(graph: Graph, start: int = 0) -> Iterator[AlgorithmStep]:
    dist: dict[int, float] = {v: INF for v in range(graph.num_vertices)}
    parent: dict[int, int] = {v: -1 for v in range(graph.num_vertices)}
    in_mst: set[int] = set()

    dist[start] = 0

    heap = MinHeap(graph.num_vertices)
    for v in range(graph.num_vertices):
        if not graph.vertex_blocked[v]:
            heap.insert(int(dist[v]) if dist[v] != INF else 10**18, v)

    step = 0

    while not heap.is_empty():
        key, u = heap.extract_min()

        if dist[u] == INF:
            break

        in_mst.add(u)
        current_mst_edges = _build_mst_edges(graph, parent)

        step += 1
        yield AlgorithmStep(
            kind=StepKind.VERTEX_ADDED,
            active_vertices=frozenset({u}),
            settled_vertices=frozenset(in_mst),
            mst_edges=current_mst_edges,
            distances={v: (d if d != INF else -1) for v, d in dist.items()},
            heap_contents=heap.snapshot(),
            explanation=f"Added vertex {u} to MST",
            step_number=step,
        )

        for adj in graph.neighbors(u):
            v = adj.dest
            weight = adj.weight

            if graph.vertex_blocked[v] or v in in_mst or adj.edge_blocked:
                continue

            if weight < dist[v]:
                dist[v] = weight
                parent[v] = u
                if heap.contains(v):
                    heap.decrease_key(v, weight)

                current_mst_edges = _build_mst_edges(graph, parent)
                step += 1
                yield AlgorithmStep(
                    kind=StepKind.VERTEX_RELAXED,
                    active_vertices=frozenset({v}),
                    settled_vertices=frozenset(in_mst),
                    mst_edges=current_mst_edges,
                    distances={
                        vertex: (d if d != INF else -1) for vertex, d in dist.items()
                    },
                    heap_contents=heap.snapshot(),
                    explanation=f"Relaxed: dist[{v}] updated to {weight} via {u}",
                    step_number=step,
                )

    final_mst_edges = _build_mst_edges(graph, parent)
    step += 1
    yield AlgorithmStep(
        kind=StepKind.MST_COMPLETE,
        settled_vertices=frozenset(in_mst),
        mst_edges=final_mst_edges,
        distances={v: (d if d != INF else -1) for v, d in dist.items()},
        heap_contents=heap.snapshot(),
        explanation="MST complete",
        step_number=step,
    )


def prim(graph: Graph, start: int = 0) -> MSTResult:
    last_step: AlgorithmStep | None = None
    for last_step in prim_steps(graph, start):
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
