# Graph Algorithms in C

Comparison of spanning tree and shortest path algorithms on undirected weighted graphs.

## Algorithms

### Minimum Spanning Tree
- **Kruskal's Algorithm** — Sort edges by weight, use Union-Find to detect cycles. O(E log E)
- **Prim's Algorithm** — Grow MST vertex-by-vertex via min-heap. O((V+E) log V)

### Shortest Path
- **Dijkstra's Algorithm** — Standard single-source shortest path with min-heap
- **Penalty-Weighted Dijkstra** — Obstacle-aware variant with blocked vertices/edges and cost-inflated penalized edges

## Project Structure

```
include/        Header files (graph, union_find, min_heap, mst, shortest_path, graph_gen, benchmark)
src/            Implementation files
tests/          Test suites for each module
```

## Build

```bash
make            # release build (optimized)
make debug      # debug build
make test       # build and run all tests
make clean      # remove build artifacts
```

## Usage

```bash
./bin/algo demo                          # hand-crafted 9-vertex demo
./bin/algo bench                         # full benchmark suite
./bin/algo mst -v 100 -d 0.3            # MST on generated graph
./bin/algo path -v 200 -d 0.2 -s 0 -t 199  # shortest path
```

## Data Structures

- **Adjacency List Graph** — with support for blocked vertices/edges and edge penalties
- **Union-Find (DSU)** — path compression + union-by-rank
- **Binary Min-Heap** — with position array for O(log n) decrease-key
