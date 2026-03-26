# Graph Algorithms Visualizer

Interactive PyQt6 application for visualizing MST and shortest path algorithms step-by-step.

## Features

- **Step-by-step animation** of Kruskal's, Prim's, Dijkstra's, and Penalty-Weighted Dijkstra
- **Interactive obstacle editing** — right-click to block vertices/edges or set penalties
- **Side-by-side comparison** of two algorithms on the same graph
- **Benchmark suite** with performance charts across graph sizes
- **Multiple graph types** — demo (textbook 9V), random connected, grid, obstacle grid

## Architecture

```
algo_viz/
├── core/           Pure algorithm library (no GUI dependency)
│   ├── graph.py        Graph class (adjacency list, mirrors C struct)
│   ├── union_find.py   DSU with path compression + snapshot()
│   ├── min_heap.py     Binary min-heap with decrease-key + snapshot()
│   ├── mst_kruskal.py  Generator yielding AlgorithmStep objects
│   ├── mst_prim.py     Generator yielding AlgorithmStep objects
│   ├── sp_dijkstra.py  Generator yielding AlgorithmStep objects
│   ├── sp_obstacle.py  Penalty-weighted Dijkstra generator
│   └── graph_gen.py    Random/connected/grid/obstacle graph factories
├── models/         Pure data containers
│   ├── step.py         StepKind enum + AlgorithmStep dataclass
│   └── result.py       MSTResult, SPResult dataclasses
├── visualization/  Rendering layer
│   ├── graph_canvas.py Matplotlib canvas embedded in PyQt6
│   ├── color_scheme.py Centralized color/size constants
│   └── layout_engine.py NetworkX layout wrappers
├── gui/            PyQt6 widgets
│   ├── main_window.py  QMainWindow with 4 tabs
│   ├── visualizer_tab.py Single-algorithm view + animation
│   ├── comparison_tab.py Side-by-side two-algorithm view
│   ├── benchmark_tab.py  Performance charts + timing tables
│   ├── control_panel.py  Play/pause/step/speed controls
│   ├── info_panel.py     Algorithm state display
│   ├── graph_editor.py   Click-to-edit obstacles
│   └── animation_worker.py QThread driving step iteration
└── benchmark/      Timing and chart generation
    ├── runner.py       Times algorithms across graph sizes
    └── charts.py       Matplotlib grouped bar charts
```

## Design Decisions

**Generator Protocol**: All 4 algorithms are Python generators that `yield AlgorithmStep` objects. The GUI consumes steps without coupling to any specific algorithm. This enables:
- Play/pause/step-forward animation
- Backward navigation via cached steps
- Algorithm-agnostic rendering

**QThread Animation**: The animation worker runs in a separate thread, emitting `step_ready` signals. The GUI remains responsive during animation. Speed is adjustable from 0.1x to 10.0x.

**C/Python Parity**: The Python algorithms produce identical results to the C implementation — verified by `test_algorithms.py` comparing against known MST weights and shortest-path distances.

## Setup

```bash
cd python
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Tests

```bash
python -m pytest tests/ -v
```

## Dependencies

- PyQt6 — GUI framework
- matplotlib — graph rendering
- networkx — layout computation
- numpy — used by matplotlib/networkx
