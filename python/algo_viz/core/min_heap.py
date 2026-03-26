class MinHeap:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data: list[list[int]] = []   # each entry: [key, value]
        self.pos: dict[int, int] = {}     # value -> index in data
        self.size = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _swap(self, i: int, j: int) -> None:
        self.pos[self.data[i][1]] = j
        self.pos[self.data[j][1]] = i
        self.data[i], self.data[j] = self.data[j], self.data[i]

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self.data[parent][0] > self.data[i][0]:
                self._swap(parent, i)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        while True:
            smallest = i
            left = 2 * i + 1
            right = 2 * i + 2
            if left < self.size and self.data[left][0] < self.data[smallest][0]:
                smallest = left
            if right < self.size and self.data[right][0] < self.data[smallest][0]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def insert(self, key: int, value: int) -> None:
        self.data.append([key, value])
        self.pos[value] = self.size
        self.size += 1
        self._sift_up(self.size - 1)

    def extract_min(self) -> tuple[int, int]:
        if self.size == 0:
            raise IndexError("extract_min from empty heap")
        min_key, min_val = self.data[0]
        last = self.size - 1
        self._swap(0, last)
        self.data.pop()
        del self.pos[min_val]
        self.size -= 1
        if self.size > 0:
            self._sift_down(0)
        return (min_key, min_val)

    def decrease_key(self, value: int, new_key: int) -> None:
        if value not in self.pos:
            raise KeyError(f"value {value!r} not in heap")
        i = self.pos[value]
        if new_key > self.data[i][0]:
            raise ValueError("new_key is greater than current key")
        self.data[i][0] = new_key
        self._sift_up(i)

    def is_empty(self) -> bool:
        return self.size == 0

    def contains(self, value: int) -> bool:
        return value in self.pos

    def snapshot(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (entry[0], entry[1])
            for entry in sorted(self.data[: self.size], key=lambda e: e[0])
        )
