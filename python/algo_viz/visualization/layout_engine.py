import networkx as nx

from algo_viz.core.graph import Graph


def graph_to_networkx(graph: Graph) -> nx.Graph:
    """Convert our Graph to a NetworkX graph for layout computation."""
    G = nx.Graph()
    G.add_nodes_from(range(graph.num_vertices))
    for edge in graph.edge_list:
        if not edge.blocked:
            G.add_edge(edge.src, edge.dest, weight=edge.weight)
    return G


def compute_layout(graph: Graph, layout_type: str = 'spring', **kwargs) -> dict[int, tuple[float, float]]:
    """Compute vertex positions. Returns {vertex_id: (x, y)}."""
    G = graph_to_networkx(graph)
    if layout_type == 'spring':
        return nx.spring_layout(G, seed=42, k=2.0 / max(1, graph.num_vertices ** 0.5), **kwargs)
    elif layout_type == 'kamada_kawai':
        try:
            return nx.kamada_kawai_layout(G, **kwargs)
        except ImportError:
            return nx.spring_layout(G, seed=42, k=2.0 / max(1, graph.num_vertices ** 0.5), **kwargs)
    elif layout_type == 'circular':
        return nx.circular_layout(G, **kwargs)
    elif layout_type == 'shell':
        return nx.shell_layout(G, **kwargs)
    else:
        return nx.spring_layout(G, seed=42, **kwargs)


def compute_grid_layout(rows: int, cols: int) -> dict[int, tuple[float, float]]:
    """Exact grid positions for grid graphs."""
    pos = {}
    for r in range(rows):
        for c in range(cols):
            v = r * cols + c
            pos[v] = (c, -r)  # y inverted so row 0 is at top
    return pos
