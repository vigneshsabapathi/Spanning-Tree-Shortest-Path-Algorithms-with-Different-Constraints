from __future__ import annotations

import random
import time
from dataclasses import dataclass

from algo_viz.core.graph_gen import gen_connected_graph
from algo_viz.core.mst_kruskal import kruskal
from algo_viz.core.mst_prim import prim
from algo_viz.core.sp_dijkstra import dijkstra
from algo_viz.core.sp_obstacle import dijkstra_obstacle


@dataclass
class BenchmarkEntry:
    vertices: int
    edges: int
    density: float
    algorithm: str
    time_us: float      # microseconds
    result_value: int   # MST total weight or SP distance from source to last vertex
    success: bool


def run_mst_benchmark(
    sizes: list[int] | None = None,
    density: float = 0.2,
    max_weight: int = 1000,
    runs: int = 5,
) -> list[BenchmarkEntry]:
    """Time Kruskal and Prim across a range of graph sizes.

    For each size a single graph is generated (seed=42) so that both
    algorithms operate on identical input.  Each algorithm is timed
    *runs* times and the average is stored.
    """
    if sizes is None:
        sizes = [50, 100, 250, 500, 1000]

    results: list[BenchmarkEntry] = []

    for n in sizes:
        g = gen_connected_graph(n, density, max_weight, seed=42)

        # ── Kruskal ──────────────────────────────────────────────────────
        times: list[float] = []
        r_kruskal = None
        for _ in range(runs):
            start = time.perf_counter_ns()
            r_kruskal = kruskal(g)
            elapsed = (time.perf_counter_ns() - start) / 1_000  # ns -> µs
            times.append(elapsed)
        avg = sum(times) / len(times)
        results.append(
            BenchmarkEntry(
                vertices=n,
                edges=g.num_edges,
                density=density,
                algorithm="Kruskal",
                time_us=avg,
                result_value=r_kruskal.total_weight,
                success=r_kruskal.is_connected,
            )
        )

        # ── Prim ─────────────────────────────────────────────────────────
        times = []
        r_prim = None
        for _ in range(runs):
            start = time.perf_counter_ns()
            r_prim = prim(g, start=0)
            elapsed = (time.perf_counter_ns() - start) / 1_000
            times.append(elapsed)
        avg = sum(times) / len(times)
        results.append(
            BenchmarkEntry(
                vertices=n,
                edges=g.num_edges,
                density=density,
                algorithm="Prim",
                time_us=avg,
                result_value=r_prim.total_weight,
                success=r_prim.is_connected,
            )
        )

    return results


def run_sp_benchmark(
    sizes: list[int] | None = None,
    density: float = 0.2,
    max_weight: int = 1000,
    runs: int = 5,
) -> list[BenchmarkEntry]:
    """Time Dijkstra and obstacle-aware Dijkstra across a range of graph sizes.

    A single graph is generated per size (seed=42).  Before running the
    obstacle variant, random penalties in [2, 5] are applied to ~20 % of
    edges so the two algorithms see meaningfully different cost landscapes.
    The reported *result_value* is the shortest distance from vertex 0 to
    the last reachable vertex (or 0 when no path exists).
    """
    if sizes is None:
        sizes = [50, 100, 250, 500, 1000]

    results: list[BenchmarkEntry] = []

    for n in sizes:
        g_plain = gen_connected_graph(n, density, max_weight, seed=42)

        # Build a penalty-augmented copy for the obstacle variant
        g_obstacle = gen_connected_graph(n, density, max_weight, seed=42)
        rng = random.Random(99)
        for edge in g_obstacle.edge_list:
            if rng.random() < 0.2:
                penalty = rng.randint(2, 5)
                g_obstacle.set_edge_penalty(edge.src, edge.dest, penalty)

        # ── Plain Dijkstra ────────────────────────────────────────────────
        times: list[float] = []
        r_dijkstra = None
        for _ in range(runs):
            start = time.perf_counter_ns()
            r_dijkstra = dijkstra(g_plain, source=0)
            elapsed = (time.perf_counter_ns() - start) / 1_000
            times.append(elapsed)
        avg = sum(times) / len(times)

        # Pick the maximum reachable distance as a representative scalar
        max_dist = max(
            (d for d in r_dijkstra.dist.values() if d >= 0),
            default=0,
        )
        results.append(
            BenchmarkEntry(
                vertices=n,
                edges=g_plain.num_edges,
                density=density,
                algorithm="Dijkstra",
                time_us=avg,
                result_value=max_dist,
                success=True,
            )
        )

        # ── Obstacle Dijkstra ─────────────────────────────────────────────
        times = []
        r_obstacle = None
        for _ in range(runs):
            start = time.perf_counter_ns()
            r_obstacle = dijkstra_obstacle(g_obstacle, source=0)
            elapsed = (time.perf_counter_ns() - start) / 1_000
            times.append(elapsed)
        avg = sum(times) / len(times)

        max_dist_obs = max(
            (d for d in r_obstacle.dist.values() if d >= 0),
            default=0,
        )
        results.append(
            BenchmarkEntry(
                vertices=n,
                edges=g_obstacle.num_edges,
                density=density,
                algorithm="Dijkstra Obstacle",
                time_us=avg,
                result_value=max_dist_obs,
                success=True,
            )
        )

    return results
