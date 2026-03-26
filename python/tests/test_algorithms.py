"""Tests for MST and shortest-path algorithms.

All expected values are verified against the C reference implementation.
"""
import pytest

from algo_viz.core.graph import Graph
from algo_viz.core.graph_gen import gen_demo_graph
from algo_viz.core.mst_kruskal import kruskal, kruskal_steps
from algo_viz.core.mst_prim import prim, prim_steps
from algo_viz.core.sp_dijkstra import dijkstra, reconstruct_path
from algo_viz.core.sp_obstacle import dijkstra_obstacle
from algo_viz.models.step import StepKind


def _make_5v_graph() -> Graph:
    """5-vertex graph used in Dijkstra tests.

    Edges: 0-1:10, 0-2:3, 2-1:4, 1-3:2, 2-3:8, 2-4:2, 3-4:5
    Shortest paths from 0:
      dist[0]=0, dist[1]=7 (0→2→1), dist[2]=3, dist[3]=9 (0→2→1→3), dist[4]=5 (0→2→4)
    """
    g = Graph(5)
    g.add_edge(0, 1, 10)
    g.add_edge(0, 2, 3)
    g.add_edge(2, 1, 4)
    g.add_edge(1, 3, 2)
    g.add_edge(2, 3, 8)
    g.add_edge(2, 4, 2)
    g.add_edge(3, 4, 5)
    return g


def test_kruskal_demo():
    g = gen_demo_graph()
    result = kruskal(g)
    assert result.total_weight == 37
    assert result.num_edges == 8
    assert result.is_connected is True


def test_prim_demo():
    g = gen_demo_graph()
    result = prim(g)
    assert result.total_weight == 37
    assert result.num_edges == 8
    assert result.is_connected is True


def test_mst_equality():
    """Kruskal and Prim must produce the same total MST weight."""
    g = gen_demo_graph()
    assert kruskal(g).total_weight == prim(g).total_weight


def test_kruskal_disconnected():
    """Graph with two isolated components — MST is not connected."""
    g = Graph(4)
    g.add_edge(0, 1, 1)
    g.add_edge(2, 3, 1)
    result = kruskal(g)
    assert result.is_connected is False


def test_dijkstra_basic():
    g = _make_5v_graph()
    result = dijkstra(g, 0)
    assert result.dist[0] == 0
    assert result.dist[2] == 3
    assert result.dist[1] == 7
    assert result.dist[3] == 9
    assert result.dist[4] == 5


def test_dijkstra_path():
    g = _make_5v_graph()
    result = dijkstra(g, 0)
    path = reconstruct_path(result, 3)
    assert path == [0, 2, 1, 3]


def test_dijkstra_blocked():
    """Blocking vertex 2 forces traffic through the direct 0→1 edge."""
    g = _make_5v_graph()
    g.block_vertex(2)
    result = dijkstra(g, 0)
    assert result.dist[1] == 10
    assert result.dist[3] == 12
    assert result.dist[2] == -1


def test_dijkstra_obstacle():
    """Applying penalty 10 on edge 0-2 makes the direct 0→1 path cheaper."""
    g = _make_5v_graph()
    # Edge 0-2 has weight 3; penalty 10 → effective weight 30.
    # Cheapest route to vertex 1 becomes 0→1 (cost 10) rather than 0→2→1.
    g.set_edge_penalty(0, 2, 10)
    result = dijkstra_obstacle(g, 0)
    assert result.dist[1] == 10


def test_kruskal_steps():
    g = gen_demo_graph()
    steps = list(kruskal_steps(g))

    assert len(steps) > 0
    assert steps[0].kind == StepKind.CONSIDERING_EDGE

    kinds = [s.kind for s in steps]
    assert StepKind.EDGE_ACCEPTED in kinds
    assert StepKind.EDGE_REJECTED in kinds
    assert steps[-1].kind == StepKind.MST_COMPLETE


def test_prim_steps():
    g = gen_demo_graph()
    steps = list(prim_steps(g))

    assert len(steps) > 0

    kinds = [s.kind for s in steps]
    assert StepKind.VERTEX_ADDED in kinds

    vertex_added_steps = [s for s in steps if s.kind == StepKind.VERTEX_ADDED]
    assert len(vertex_added_steps) == 9
