from __future__ import annotations

import copy
from typing import NamedTuple


class AdjEntry(NamedTuple):
    dest: int
    weight: int
    edge_id: int
    edge_blocked: bool = False


class Edge:
    __slots__ = ('src', 'dest', 'weight', 'edge_id', 'blocked', 'penalty')

    def __init__(self, src: int, dest: int, weight: int, edge_id: int):
        self.src = src
        self.dest = dest
        self.weight = weight
        self.edge_id = edge_id
        self.blocked = False
        self.penalty = 1


class Graph:
    def __init__(self, num_vertices: int):
        self.num_vertices = num_vertices
        self.num_edges = 0
        self.adj: list[list[AdjEntry]] = [[] for _ in range(num_vertices)]
        self.edge_list: list[Edge] = []
        self.vertex_blocked: list[bool] = [False] * num_vertices

    def add_edge(self, src: int, dest: int, weight: int) -> int:
        edge_id = self.num_edges
        edge = Edge(src, dest, weight, edge_id)
        self.edge_list.append(edge)
        self.adj[src].append(AdjEntry(dest, weight, edge_id))
        self.adj[dest].append(AdjEntry(src, weight, edge_id))
        self.num_edges += 1
        return edge_id

    def block_vertex(self, v: int) -> None:
        self.vertex_blocked[v] = True

    def unblock_vertex(self, v: int) -> None:
        self.vertex_blocked[v] = False

    def block_edge(self, src: int, dest: int) -> None:
        for edge in self.edge_list:
            if (edge.src == src and edge.dest == dest) or (edge.src == dest and edge.dest == src):
                edge.blocked = True
                self.adj[src] = [
                    AdjEntry(a.dest, a.weight, a.edge_id, True)
                    if a.edge_id == edge.edge_id else a
                    for a in self.adj[src]
                ]
                self.adj[dest] = [
                    AdjEntry(a.dest, a.weight, a.edge_id, True)
                    if a.edge_id == edge.edge_id else a
                    for a in self.adj[dest]
                ]
                return

    def set_edge_penalty(self, src: int, dest: int, penalty: int) -> None:
        for edge in self.edge_list:
            if (edge.src == src and edge.dest == dest) or (edge.src == dest and edge.dest == src):
                edge.penalty = penalty
                return

    def effective_weight(self, edge_id: int) -> int:
        e = self.edge_list[edge_id]
        return e.weight * e.penalty

    def neighbors(self, v: int) -> list[AdjEntry]:
        return self.adj[v]

    def copy(self) -> Graph:
        return copy.deepcopy(self)
