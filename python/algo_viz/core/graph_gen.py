from __future__ import annotations

import random

from algo_viz.core.graph import Graph


def gen_demo_graph() -> Graph:
    """Return the exact 9-vertex textbook graph used in MST examples.

    Edges (undirected, with weights):
      0-1(4), 0-7(8), 1-2(8), 1-7(11), 2-3(7), 2-5(4), 2-8(2),
      3-4(9), 3-5(14), 4-5(10), 5-6(2), 6-7(1), 6-8(6), 7-8(7)
    MST total weight = 37.
    """
    g = Graph(9)
    g.add_edge(0, 1, 4)
    g.add_edge(0, 7, 8)
    g.add_edge(1, 2, 8)
    g.add_edge(1, 7, 11)
    g.add_edge(2, 3, 7)
    g.add_edge(2, 5, 4)
    g.add_edge(2, 8, 2)
    g.add_edge(3, 4, 9)
    g.add_edge(3, 5, 14)
    g.add_edge(4, 5, 10)
    g.add_edge(5, 6, 2)
    g.add_edge(6, 7, 1)
    g.add_edge(6, 8, 6)
    g.add_edge(7, 8, 7)
    return g


def gen_random_graph(
    n: int,
    density: float = 0.3,
    max_weight: int = 20,
    seed: int = 0,
) -> Graph:
    """Return a random undirected graph with *n* vertices.

    For each pair (i, j) with i < j an edge is added with probability
    *density* and a random weight in [1, max_weight].
    """
    random.seed(seed)
    g = Graph(n)
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < density:
                weight = random.randint(1, max_weight)
                g.add_edge(i, j, weight)
    return g


def gen_connected_graph(
    n: int,
    density: float = 0.3,
    max_weight: int = 20,
    seed: int = 0,
) -> Graph:
    """Return a guaranteed-connected random undirected graph with *n* vertices.

    Algorithm:
      1. Shuffle the vertex order (Fisher-Yates via random.shuffle).
      2. Connect shuffled[i] to shuffled[i+1] for i in 0..n-2 to form a
         spanning tree.
      3. Randomly add extra edges until the number of edges reaches
         target_edges = max(n - 1, int(density * n * (n - 1) / 2)).
    """
    random.seed(seed)
    g = Graph(n)

    shuffled = list(range(n))
    random.shuffle(shuffled)

    # Build spanning tree
    for i in range(n - 1):
        weight = random.randint(1, max_weight)
        g.add_edge(shuffled[i], shuffled[i + 1], weight)

    # Collect candidate extra edges (pairs not yet connected)
    existing: set[tuple[int, int]] = set()
    for edge in g.edge_list:
        u, v = min(edge.src, edge.dest), max(edge.src, edge.dest)
        existing.add((u, v))

    target_edges = max(n - 1, int(density * n * (n - 1) / 2))

    candidates: list[tuple[int, int]] = [
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if (i, j) not in existing
    ]
    random.shuffle(candidates)

    for u, v in candidates:
        if g.num_edges >= target_edges:
            break
        weight = random.randint(1, max_weight)
        g.add_edge(u, v, weight)

    return g


def gen_grid_graph(
    rows: int,
    cols: int,
    max_weight: int = 10,
    seed: int = 0,
) -> Graph:
    """Return a grid graph with *rows* x *cols* vertices.

    Vertex numbering: vertex = r * cols + c.
    Each vertex is connected to its right neighbor (r, c+1) and its
    down neighbor (r+1, c) with random weights in [1, max_weight].
    """
    random.seed(seed)
    n = rows * cols
    g = Graph(n)

    for r in range(rows):
        for c in range(cols):
            v = r * cols + c
            # Connect right
            if c + 1 < cols:
                weight = random.randint(1, max_weight)
                g.add_edge(v, v + 1, weight)
            # Connect down
            if r + 1 < rows:
                weight = random.randint(1, max_weight)
                g.add_edge(v, v + cols, weight)

    return g


def gen_obstacle_graph(
    rows: int,
    cols: int,
    obstacle_fraction: float = 0.2,
    max_weight: int = 100,
    seed: int = 42,
) -> Graph:
    """Return a grid graph with randomly blocked vertices and edge penalties.

    Steps:
      1. Build a standard grid graph via gen_grid_graph.
      2. Block a random fraction (*obstacle_fraction*) of interior vertices
         (excluding vertex 0 and vertex V-1).
      3. Set random penalties in [2, 5] on approximately 20% of edges.
    """
    random.seed(seed)
    g = gen_grid_graph(rows, cols, max_weight, seed)

    n = rows * cols
    # Interior vertices: all except 0 and n-1
    interior = [v for v in range(1, n - 1)]
    num_blocked = max(1, int(obstacle_fraction * len(interior)))
    random.shuffle(interior)
    for v in interior[:num_blocked]:
        g.block_vertex(v)

    # Apply random penalties to ~20% of edges
    for edge in g.edge_list:
        if random.random() < 0.2:
            penalty = random.randint(2, 5)
            g.set_edge_penalty(edge.src, edge.dest, penalty)

    return g
