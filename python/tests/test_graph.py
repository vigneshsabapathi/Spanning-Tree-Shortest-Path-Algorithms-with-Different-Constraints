"""Tests for algo_viz.core.graph — Graph data structure."""
import pytest

from algo_viz.core.graph import Graph


def test_create():
    g = Graph(6)
    assert g.num_vertices == 6
    assert g.num_edges == 0
    for v in range(6):
        assert g.adj[v] == []


def test_add_edge():
    g = Graph(5)
    pairs = [(0, 1, 3), (0, 2, 7), (1, 3, 5), (2, 4, 2), (3, 4, 8)]
    for src, dest, w in pairs:
        g.add_edge(src, dest, w)

    assert g.num_edges == 5

    dests_0 = {a.dest for a in g.adj[0]}
    assert 1 in dests_0
    assert 2 in dests_0

    dests_1 = {a.dest for a in g.adj[1]}
    assert 0 in dests_1
    assert 3 in dests_1

    dests_4 = {a.dest for a in g.adj[4]}
    assert 2 in dests_4
    assert 3 in dests_4


def test_block_vertex():
    g = Graph(4)
    assert g.vertex_blocked[2] is False
    g.block_vertex(2)
    assert g.vertex_blocked[2] is True
    assert g.vertex_blocked[0] is False
    assert g.vertex_blocked[3] is False


def test_block_edge():
    g = Graph(4)
    g.add_edge(0, 1, 5)
    g.add_edge(1, 2, 3)
    g.add_edge(2, 3, 4)

    g.block_edge(1, 2)

    blocked_edges = [e for e in g.edge_list if e.blocked]
    assert len(blocked_edges) == 1
    e = blocked_edges[0]
    assert (e.src, e.dest) == (1, 2) or (e.src, e.dest) == (2, 1)

    adj1_entry = next(a for a in g.adj[1] if a.dest == 2)
    adj2_entry = next(a for a in g.adj[2] if a.dest == 1)
    assert adj1_entry.edge_blocked is True
    assert adj2_entry.edge_blocked is True

    adj0_entry = next(a for a in g.adj[0] if a.dest == 1)
    assert adj0_entry.edge_blocked is False


def test_set_penalty():
    g = Graph(3)
    eid = g.add_edge(0, 1, 6)
    g.add_edge(1, 2, 4)

    g.set_edge_penalty(0, 1, 3)

    assert g.effective_weight(eid) == 18

    other_eid = g.edge_list[1].edge_id
    assert g.effective_weight(other_eid) == 4
