from __future__ import annotations

from typing import Iterator

from algo_viz.core.graph import Graph
from algo_viz.core.min_heap import MinHeap
from algo_viz.models.result import SPResult
from algo_viz.models.step import AlgorithmStep, StepKind

INF = float("inf")


def dijkstra_steps(graph: Graph, source: int) -> Iterator[AlgorithmStep]:
    dist: dict[int, float] = {v: INF for v in range(graph.num_vertices)}
    prev: dict[int, int] = {v: -1 for v in range(graph.num_vertices)}
    visited: set[int] = set()

    dist[source] = 0

    heap = MinHeap(graph.num_vertices)
    for v in range(graph.num_vertices):
        if not graph.vertex_blocked[v]:
            heap.insert(int(dist[v]) if dist[v] != INF else 10**18, v)

    step = 0

    while not heap.is_empty():
        key, u = heap.extract_min()

        if dist[u] == INF:
            break

        visited.add(u)
        step += 1
        yield AlgorithmStep(
            kind=StepKind.VERTEX_SETTLED,
            active_vertices=frozenset({u}),
            settled_vertices=frozenset(visited),
            distances={v: (d if d != INF else -1) for v, d in dist.items()},
            heap_contents=heap.snapshot(),
            explanation=f"Settled vertex {u} with dist {dist[u]}",
            step_number=step,
        )

        for adj in graph.neighbors(u):
            v = adj.dest
            weight = adj.weight

            if v in visited or graph.vertex_blocked[v] or adj.edge_blocked:
                continue

            new_dist = dist[u] + weight

            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                if heap.contains(v):
                    heap.decrease_key(v, int(new_dist))

                step += 1
                yield AlgorithmStep(
                    kind=StepKind.VERTEX_RELAXED,
                    active_vertices=frozenset({v}),
                    settled_vertices=frozenset(visited),
                    distances={
                        vertex: (d if d != INF else -1) for vertex, d in dist.items()
                    },
                    heap_contents=heap.snapshot(),
                    explanation=(
                        f"dist[{v}] = dist[{u}] + {weight} = {int(new_dist)}"
                    ),
                    step_number=step,
                )

    step += 1
    yield AlgorithmStep(
        kind=StepKind.ALGORITHM_DONE,
        settled_vertices=frozenset(visited),
        distances={v: (d if d != INF else -1) for v, d in dist.items()},
        explanation="Algorithm complete",
        step_number=step,
    )


def dijkstra(graph: Graph, source: int) -> SPResult:
    _dist: dict[int, float] = {v: INF for v in range(graph.num_vertices)}
    _prev: dict[int, int] = {v: -1 for v in range(graph.num_vertices)}
    visited: set[int] = set()

    _dist[source] = 0

    heap = MinHeap(graph.num_vertices)
    for v in range(graph.num_vertices):
        if not graph.vertex_blocked[v]:
            heap.insert(int(_dist[v]) if _dist[v] != INF else 10**18, v)

    while not heap.is_empty():
        key, u = heap.extract_min()
        if _dist[u] == INF:
            break
        visited.add(u)

        for adj in graph.neighbors(u):
            v = adj.dest
            weight = adj.weight
            if v in visited or graph.vertex_blocked[v] or adj.edge_blocked:
                continue
            new_dist = _dist[u] + weight
            if new_dist < _dist[v]:
                _dist[v] = new_dist
                _prev[v] = u
                if heap.contains(v):
                    heap.decrease_key(v, int(new_dist))

    return SPResult(
        dist={v: (int(d) if d != INF else -1) for v, d in _dist.items()},
        prev=_prev,
        source=source,
        num_vertices=graph.num_vertices,
    )


def reconstruct_path(result: SPResult, target: int) -> list[int]:
    if result.prev.get(target, -1) == -1 and target != result.source:
        return []

    path: list[int] = []
    current = target
    while current != -1:
        path.append(current)
        current = result.prev.get(current, -1)

    path.reverse()

    if not path or path[0] != result.source:
        return []

    return path
