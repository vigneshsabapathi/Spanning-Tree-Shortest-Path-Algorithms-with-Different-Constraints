"""Tests for algo_viz.core.union_find — UnionFind data structure."""
import pytest

from algo_viz.core.union_find import UnionFind


def test_initial_state():
    uf = UnionFind(5)
    for i in range(5):
        assert uf.find(i) == i


def test_union_and_connected():
    uf = UnionFind(5)
    assert not uf.connected(0, 1)
    uf.union(0, 1)
    assert uf.connected(0, 1)
    # Other pairs still disconnected
    assert not uf.connected(0, 2)
    assert not uf.connected(1, 3)


def test_transitive():
    uf = UnionFind(5)
    uf.union(0, 1)
    uf.union(1, 2)
    assert uf.connected(0, 2)
    assert uf.connected(2, 0)
    # Vertex 3 and 4 still isolated
    assert not uf.connected(0, 3)
    assert not uf.connected(2, 4)


def test_reset():
    uf = UnionFind(4)
    uf.union(0, 1)
    uf.union(2, 3)
    assert uf.connected(0, 1)
    assert uf.connected(2, 3)

    uf.reset()

    for i in range(4):
        assert uf.find(i) == i
    assert not uf.connected(0, 1)
    assert not uf.connected(2, 3)


def test_snapshot():
    uf = UnionFind(4)
    # Before any union: every vertex is its own root
    snap = uf.snapshot()
    assert snap == {0: 0, 1: 1, 2: 2, 3: 3}

    uf.union(0, 1)
    snap2 = uf.snapshot()
    # 0 and 1 must share the same root
    assert snap2[0] == snap2[1]
    # 2 and 3 still isolated
    assert snap2[2] == 2
    assert snap2[3] == 3
