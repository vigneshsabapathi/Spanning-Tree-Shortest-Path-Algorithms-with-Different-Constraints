class UnionFind:
    def __init__(self, size: int):
        self._size = size
        self.parent: list[int] = list(range(size))
        self.rank: list[int] = [0] * size

    def find(self, x: int) -> int:
        # First pass: walk to root
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        # Second pass: flatten (path compression)
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        # Union by rank
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def reset(self) -> None:
        self.parent = list(range(self._size))
        self.rank = [0] * self._size

    def snapshot(self) -> dict[int, int]:
        return {v: self.find(v) for v in range(self._size)}
