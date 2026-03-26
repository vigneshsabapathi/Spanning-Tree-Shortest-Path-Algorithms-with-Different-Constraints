from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QLabel, QPushButton, QComboBox, QFrame,
)
from PyQt6.QtCore import Qt, QTimer

from algo_viz.core.graph import Graph
from algo_viz.core.graph_gen import (
    gen_demo_graph,
    gen_connected_graph,
    gen_grid_graph,
    gen_obstacle_graph,
)
from algo_viz.core.mst_kruskal import kruskal, kruskal_steps
from algo_viz.core.mst_prim import prim, prim_steps
from algo_viz.core.sp_dijkstra import dijkstra, dijkstra_steps
from algo_viz.core.sp_obstacle import dijkstra_obstacle, dijkstra_obstacle_steps
from algo_viz.models.step import AlgorithmStep
from algo_viz.visualization.graph_canvas import GraphCanvas
from algo_viz.gui.animation_worker import AnimationWorker


# ── Constants ─────────────────────────────────────────────────────────────────

_GRAPHS = {
    "Demo 9V":            (gen_demo_graph,                          None),
    "Random 20V":         (lambda: gen_connected_graph(20, 0.25, seed=7), None),
    "Grid 5x5":           (lambda: gen_grid_graph(5, 5),            (5, 5)),
    "Obstacle Grid 5x5":  (lambda: gen_obstacle_graph(5, 5),        (5, 5)),
}

_ALGOS = ["Kruskal", "Prim", "Dijkstra", "Dijkstra Obstacle"]


def _make_iterator(graph: Graph, algo: str):
    if algo == "Kruskal":
        return kruskal_steps(graph)
    elif algo == "Prim":
        return prim_steps(graph, start=0)
    elif algo == "Dijkstra":
        return dijkstra_steps(graph, source=0)
    elif algo == "Dijkstra Obstacle":
        return dijkstra_obstacle_steps(graph, source=0)
    return kruskal_steps(graph)


def _run_to_completion(graph: Graph, algo: str) -> tuple[list[AlgorithmStep], int]:
    """Run *algo* on *graph* and return (all steps, key metric).

    The metric is MST total weight for Kruskal/Prim, or the maximum
    finite distance from the source for SP algorithms.
    """
    steps: list[AlgorithmStep] = list(_make_iterator(graph, algo))

    if algo in ("Kruskal", "Prim"):
        if algo == "Kruskal":
            r = kruskal(graph)
        else:
            r = prim(graph, start=0)
        metric = r.total_weight
    else:
        if algo == "Dijkstra":
            r = dijkstra(graph, source=0)
        else:
            r = dijkstra_obstacle(graph, source=0)
        metric = max((d for d in r.dist.values() if d >= 0), default=0)

    return steps, metric


# ── Per-panel widget ───────────────────────────────────────────────────────────

class _AlgoPanel(QWidget):
    """A graph canvas paired with a small info label below it."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = GraphCanvas(width=5, height=4, dpi=90)

        self._info = QLabel("—")
        self._info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._info.setStyleSheet("font-size: 11px; color: #c0c0d0; padding: 4px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        layout.addWidget(self.canvas, stretch=1)
        layout.addWidget(self._info)

    def set_info(self, text: str) -> None:
        self._info.setText(text)

    def clear_info(self) -> None:
        self._info.setText("—")


# ── Main comparison tab ────────────────────────────────────────────────────────

class ComparisonTab(QWidget):
    """Side-by-side comparison of two algorithms on the same graph.

    Supports two modes:
      • "Run Comparison": executes both algorithms to completion and
        renders their final states simultaneously.
      • Step-by-step: Play/Pause and Step buttons advance both canvases
        in lock-step using two AnimationWorkers.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Shared state ──────────────────────────────────────────────────
        self._graph: Graph | None = None
        self._graph_name: str = "Demo 9V"

        self._steps_1: list[AlgorithmStep] = []
        self._steps_2: list[AlgorithmStep] = []
        self._step_idx: int = -1
        self._exhausted_1 = False
        self._exhausted_2 = False
        self._playing = False

        # ── Workers ───────────────────────────────────────────────────────
        self._worker1 = AnimationWorker()
        self._worker2 = AnimationWorker()
        self._pending_steps: dict[int, AlgorithmStep] = {}  # worker_id -> buffered step

        # ── Panels ───────────────────────────────────────────────────────
        self._panel1 = _AlgoPanel()
        self._panel2 = _AlgoPanel()

        # ── Top bar ───────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        top_bar.addWidget(QLabel("Graph:"))
        self._graph_combo = QComboBox()
        self._graph_combo.addItems(list(_GRAPHS.keys()))
        top_bar.addWidget(self._graph_combo)

        top_bar.addSpacing(16)
        top_bar.addWidget(QLabel("Algorithm 1:"))
        self._algo1_combo = QComboBox()
        self._algo1_combo.addItems(_ALGOS)
        self._algo1_combo.setCurrentIndex(0)  # Kruskal
        top_bar.addWidget(self._algo1_combo)

        top_bar.addSpacing(8)
        top_bar.addWidget(QLabel("Algorithm 2:"))
        self._algo2_combo = QComboBox()
        self._algo2_combo.addItems(_ALGOS)
        self._algo2_combo.setCurrentIndex(1)  # Prim
        top_bar.addWidget(self._algo2_combo)

        top_bar.addSpacing(16)
        self._btn_run = QPushButton("Run Comparison")
        self._btn_run.setFixedHeight(28)
        top_bar.addWidget(self._btn_run)
        top_bar.addStretch()

        # ── Step controls ─────────────────────────────────────────────────
        ctrl_bar = QHBoxLayout()
        ctrl_bar.setSpacing(6)

        self._btn_play_pause = QPushButton("Play")
        self._btn_play_pause.setFixedWidth(60)
        self._btn_step = QPushButton("Step >")
        self._btn_step.setFixedWidth(60)
        self._btn_reset = QPushButton("Reset")
        self._btn_reset.setFixedWidth(60)
        self._step_label = QLabel("Step: 0 / 0")

        ctrl_bar.addWidget(self._btn_play_pause)
        ctrl_bar.addWidget(self._btn_step)
        ctrl_bar.addWidget(self._btn_reset)
        ctrl_bar.addSpacing(16)
        ctrl_bar.addWidget(self._step_label)
        ctrl_bar.addStretch()

        # ── Canvas splitter ───────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._panel1)
        splitter.addWidget(self._panel2)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        # ── Status bar ────────────────────────────────────────────────────
        self._status = QLabel("Select algorithms and click Run Comparison.")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setStyleSheet(
            "background: #2a2a4a; color: #a0c0ff; "
            "padding: 6px; border-radius: 4px; font-size: 12px;"
        )

        # ── Master layout ─────────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)
        root.addLayout(top_bar)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #444;")
        root.addWidget(sep)

        root.addWidget(splitter, stretch=1)
        root.addLayout(ctrl_bar)
        root.addWidget(self._status)

        # ── Timer for auto-play ───────────────────────────────────────────
        self._play_timer = QTimer(self)
        self._play_timer.setInterval(600)
        self._play_timer.timeout.connect(self._timer_tick)

        # ── Wire signals ──────────────────────────────────────────────────
        self._btn_run.clicked.connect(self._on_run_comparison)
        self._btn_play_pause.clicked.connect(self._on_play_pause)
        self._btn_step.clicked.connect(self._on_step)
        self._btn_reset.clicked.connect(self._on_reset)
        self._graph_combo.currentTextChanged.connect(self._on_graph_changed)
        self._algo1_combo.currentTextChanged.connect(self._on_algo_changed)
        self._algo2_combo.currentTextChanged.connect(self._on_algo_changed)

        # ── Initial graph load ────────────────────────────────────────────
        self._load_graph("Demo 9V")

    # ── Graph loading ─────────────────────────────────────────────────────

    def _load_graph(self, name: str) -> None:
        factory, grid_dims = _GRAPHS.get(name, (gen_demo_graph, None))
        self._graph = factory()
        layout = "spring" if grid_dims else "kamada_kawai"

        self._panel1.canvas.set_graph(
            self._graph, layout_type=layout, grid_dims=grid_dims
        )
        self._panel2.canvas.set_graph(
            self._graph, layout_type=layout, grid_dims=grid_dims
        )
        self._graph_name = name
        self._clear_step_state()

    def _clear_step_state(self) -> None:
        self._steps_1 = []
        self._steps_2 = []
        self._step_idx = -1
        self._exhausted_1 = False
        self._exhausted_2 = False
        self._panel1.canvas.render_step(None)
        self._panel2.canvas.render_step(None)
        self._panel1.clear_info()
        self._panel2.clear_info()
        self._status.setText("Select algorithms and click Run Comparison.")
        self._step_label.setText("Step: 0 / 0")

    # ── Top-bar slots ─────────────────────────────────────────────────────

    def _on_graph_changed(self, name: str) -> None:
        self._stop_playback()
        self._load_graph(name)

    def _on_algo_changed(self) -> None:
        self._stop_playback()
        self._clear_step_state()
        self._status.setText("Click Run Comparison to start.")

    # ── Run Comparison (to completion) ────────────────────────────────────

    def _on_run_comparison(self) -> None:
        if self._graph is None:
            return

        self._stop_playback()

        algo1 = self._algo1_combo.currentText()
        algo2 = self._algo2_combo.currentText()

        self._steps_1, metric1 = _run_to_completion(self._graph, algo1)
        self._steps_2, metric2 = _run_to_completion(self._graph, algo2)

        n1 = len(self._steps_1)
        n2 = len(self._steps_2)

        # Show final states
        if self._steps_1:
            self._panel1.canvas.render_step(self._steps_1[-1])
        if self._steps_2:
            self._panel2.canvas.render_step(self._steps_2[-1])

        # Panel info labels
        metric_label = "MST weight" if algo1 in ("Kruskal", "Prim") else "Max dist"
        self._panel1.set_info(f"{algo1} | {n1} steps | {metric_label}: {metric1}")
        metric_label2 = "MST weight" if algo2 in ("Kruskal", "Prim") else "Max dist"
        self._panel2.set_info(f"{algo2} | {n2} steps | {metric_label2}: {metric2}")

        # Status bar comparison summary
        if algo1 in ("Kruskal", "Prim") and algo2 in ("Kruskal", "Prim"):
            match = "Match" if metric1 == metric2 else "Differ"
            self._status.setText(
                f"MST weight: {algo1}={metric1}, {algo2}={metric2}  ({match})  |  "
                f"Steps: {algo1}={n1}, {algo2}={n2}"
            )
        else:
            self._status.setText(
                f"{algo1}: {n1} steps, max-dist={metric1}  |  "
                f"{algo2}: {n2} steps, max-dist={metric2}"
            )

        # Position step index at the end
        self._step_idx = max(n1, n2) - 1
        self._exhausted_1 = True
        self._exhausted_2 = True
        self._update_step_label()

    # ── Step-by-step playback ─────────────────────────────────────────────

    def _on_play_pause(self) -> None:
        if self._playing:
            self._stop_playback()
        else:
            self._start_playback()

    def _start_playback(self) -> None:
        if self._graph is None:
            return
        # Ensure iterators are created
        if not self._steps_1 and not self._steps_2:
            algo1 = self._algo1_combo.currentText()
            algo2 = self._algo2_combo.currentText()
            self._iter1 = _make_iterator(self._graph, algo1)
            self._iter2 = _make_iterator(self._graph, algo2)
        self._playing = True
        self._btn_play_pause.setText("Pause")
        self._play_timer.start()

    def _stop_playback(self) -> None:
        self._playing = False
        self._play_timer.stop()
        self._btn_play_pause.setText("Play")

    def _timer_tick(self) -> None:
        advanced = self._advance_one_step()
        if not advanced:
            self._stop_playback()

    def _on_step(self) -> None:
        self._stop_playback()
        self._advance_one_step()

    def _advance_one_step(self) -> bool:
        """Pull next step from each iterator and render it. Returns False when both exhausted."""
        if self._graph is None:
            return False

        # Lazily create iterators the first time
        if not hasattr(self, "_iter1") or self._exhausted_1 and self._exhausted_2:
            algo1 = self._algo1_combo.currentText()
            algo2 = self._algo2_combo.currentText()
            self._iter1 = _make_iterator(self._graph, algo1)
            self._iter2 = _make_iterator(self._graph, algo2)
            self._steps_1 = []
            self._steps_2 = []
            self._step_idx = -1
            self._exhausted_1 = False
            self._exhausted_2 = False

        got_any = False

        if not self._exhausted_1:
            try:
                step = next(self._iter1)
                self._steps_1.append(step)
                self._panel1.canvas.render_step(step)
                self._panel1.set_info(
                    f"{self._algo1_combo.currentText()} | step {step.step_number}"
                )
                got_any = True
            except StopIteration:
                self._exhausted_1 = True

        if not self._exhausted_2:
            try:
                step = next(self._iter2)
                self._steps_2.append(step)
                self._panel2.canvas.render_step(step)
                self._panel2.set_info(
                    f"{self._algo2_combo.currentText()} | step {step.step_number}"
                )
                got_any = True
            except StopIteration:
                self._exhausted_2 = True

        if got_any:
            self._step_idx += 1
            self._update_step_label()

        return got_any

    def _on_reset(self) -> None:
        self._stop_playback()
        # Destroy old iterators
        if hasattr(self, "_iter1"):
            del self._iter1
        if hasattr(self, "_iter2"):
            del self._iter2
        self._clear_step_state()
        # Re-render blank canvases with the current graph layout
        self._load_graph(self._graph_combo.currentText())

    def _update_step_label(self) -> None:
        n1 = len(self._steps_1)
        n2 = len(self._steps_2)
        self._step_label.setText(
            f"Step: {n1} ({self._algo1_combo.currentText()}) | "
            f"{n2} ({self._algo2_combo.currentText()})"
        )
