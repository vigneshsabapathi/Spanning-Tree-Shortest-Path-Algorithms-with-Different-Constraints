# Graph Algorithms — C Implementation + Python Visualizer

Implementation and comparison of Minimum Spanning Tree and Shortest Path algorithms on undirected weighted graphs. Two complete implementations: a systems-level C library and an interactive Python GUI visualizer.

## Algorithms

### Minimum Spanning Tree
- **Kruskal's Algorithm** — Sort edges by weight, use Union-Find to detect cycles. O(E log E)
- **Prim's Algorithm** — Grow MST vertex-by-vertex via min-heap. O((V+E) log V)

### Shortest Path
- **Dijkstra's Algorithm** — Standard single-source shortest path with min-heap
- **Penalty-Weighted Dijkstra** — Obstacle-aware variant with blocked vertices/edges and cost-inflated penalized edges

## Project Structure

```
algo/
├── c/                  C implementation
│   ├── include/          Header files (7 headers)
│   ├── src/              Source files (10 modules)
│   ├── tests/            Test suites (5 suites)
│   └── Makefile
│
├── python/             Python visualizer (PyQt6 + NetworkX + Matplotlib)
│   ├── algo_viz/         Core algorithms + GUI application
│   ├── tests/            Python test suite (24 tests)
│   ├── main.py           GUI entry point
│   └── requirements.txt
│
├── README.md
└── .gitignore
```

## C Build & Run

```bash
cd c
make            # release build
make debug      # debug build
make test       # run all tests
./bin/algo demo                          # 9-vertex textbook demo
./bin/algo bench                         # full benchmark suite
./bin/algo mst -v 100 -d 0.3            # MST on generated graph
./bin/algo path -v 200 -d 0.2 -s 0 -t 199
```

## Python Visualizer

```bash
cd python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Features:
- Step-by-step algorithm animation with play/pause/speed control
- Interactive obstacle editing (right-click to block vertices/edges)
- Side-by-side algorithm comparison
- Benchmark suite with performance charts

## Data Structures

- **Adjacency List Graph** — with support for blocked vertices/edges and edge penalties
- **Union-Find (DSU)** — path compression + union-by-rank
- **Binary Min-Heap** — with position array for O(log n) decrease-key

## Implementation Notes

- The Python algorithms produce identical results to the C implementations, verified by test suite comparing against known MST weights and shortest-path distances
- All algorithms implemented as Python generators yielding `AlgorithmStep` objects — the GUI is algorithm-agnostic
- Graph generators use matching seeded random logic for cross-language reproducibility
