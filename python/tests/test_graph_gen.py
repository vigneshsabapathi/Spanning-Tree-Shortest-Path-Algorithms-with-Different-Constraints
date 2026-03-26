"""Tests for algo_viz.core.graph_gen — graph generator functions."""
import pytest

from algo_viz.core.graph_gen import (
    gen_connected_graph,
    gen_demo_graph,
    gen_grid_graph,
    gen_obstacle_graph,
)
from algo_viz.core.sp_dijkstra import dijkstra


# ---------------------------------------------------------------------------
# gen_demo_graph
# ---------------------------------------------------------------------------

def test_demo_graph():
    g = gen_demo_graph()
    assert g.num_vertices == 9
    assert g.num_edges == 14


# ---------------------------------------------------------------------------
# gen_connected_graph
# ---------------------------------------------------------------------------

def test_connected_graph():
    """All vertices must be reachable from vertex 0 (verified via Dijkstra)."""
    g = gen_connected_graph(50, 0.1, 100, 42)
    result = dijkstra(g, 0)
    # Every vertex must have a finite distance (dist != -1)
    unreachable = [v for v, d in result.dist.items() if d == -1]
    assert unreachable == [], f"Vertices unreachable from 0: {unreachable}"


# ---------------------------------------------------------------------------
# gen_grid_graph
# ---------------------------------------------------------------------------

def test_grid_graph():
    """3×3 grid: 9 vertices, 12 edges (6 horizontal + 6 vertical)."""
    g = gen_grid_graph(3, 3, 10, 42)
    assert g.num_vertices == 9
    # Horizontal edges: each row has (cols-1)=2 edges × 3 rows = 6
    # Vertical edges:   each col has (rows-1)=2 edges × 3 cols = 6
    # Total = 12
    assert g.num_edges == 12


# ---------------------------------------------------------------------------
# gen_obstacle_graph
# ---------------------------------------------------------------------------

def test_obstacle_graph():
    """5×5 obstacle graph must have at least one blocked vertex."""
    g = gen_obstacle_graph(5, 5, 0.2, 100, 42)
    blocked = [v for v, b in enumerate(g.vertex_blocked) if b]
    assert len(blocked) > 0, "Expected at least one blocked vertex"
