from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

from algo_viz.core.graph import Graph
from algo_viz.core.graph_gen import (
    gen_demo_graph,
    gen_connected_graph,
    gen_grid_graph,
    gen_obstacle_graph,
)
from algo_viz.core.mst_kruskal import kruskal_steps
from algo_viz.core.mst_prim import prim_steps
from algo_viz.core.sp_dijkstra import dijkstra_steps
from algo_viz.core.sp_obstacle import dijkstra_obstacle_steps
from algo_viz.models.step import AlgorithmStep
from algo_viz.visualization.graph_canvas import GraphCanvas
from algo_viz.gui.control_panel import ControlPanel
from algo_viz.gui.info_panel import InfoPanel
from algo_viz.gui.animation_worker import AnimationWorker
from algo_viz.gui.graph_editor import GraphEditor


class VisualizerTab(QWidget):
    """Main single-algorithm visualization widget."""

    # Maps graph dropdown label -> (factory callable, grid_dims or None)
    _GRAPH_FACTORIES = {
        "Demo 9V":            (gen_demo_graph,                None),
        "Random 20V":         (lambda: gen_connected_graph(20, density=0.25, seed=7), None),
        "Grid 5x5":           (lambda: gen_grid_graph(5, 5),  (5, 5)),
        "Obstacle Grid 5x5":  (lambda: gen_obstacle_graph(5, 5), (5, 5)),
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── State ────────────────────────────────────────────────────────
        self.graph: Graph | None = None
        self.steps_cache: list[AlgorithmStep] = []
        self.current_index: int = -1         # index of the displayed step
        self._iterator = None
        self._current_graph_name = "Demo 9V"
        self._current_algo_name = "Kruskal"
        self._exhausted = False              # True when iterator is done

        # ── Child widgets ─────────────────────────────────────────────────
        self.canvas = GraphCanvas()
        self.info_panel = InfoPanel()
        self.control_panel = ControlPanel()
        self.worker = AnimationWorker()
        self.editor = GraphEditor(self.canvas, parent=self)

        # ── Layout ───────────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.info_panel)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(splitter, stretch=1)
        main_layout.addWidget(self.control_panel)

        # ── Wire signals ─────────────────────────────────────────────────
        self.control_panel.play_clicked.connect(self._on_play)
        self.control_panel.pause_clicked.connect(self._on_pause)
        self.control_panel.step_forward.connect(self._on_step_forward)
        self.control_panel.step_backward.connect(self._on_step_backward)
        self.control_panel.jump_start.connect(self._on_jump_start)
        self.control_panel.jump_end.connect(self._on_jump_end)
        self.control_panel.speed_changed.connect(self.worker.set_speed)
        self.control_panel.algorithm_changed.connect(self._on_algorithm_changed)
        self.control_panel.graph_changed.connect(self._on_graph_changed)

        self.worker.step_ready.connect(self._on_step_ready)
        self.worker.finished_signal.connect(self._on_worker_finished)

        self.editor.graph_modified.connect(self._on_graph_modified)

        # ── Initial state ─────────────────────────────────────────────────
        self._create_graph("Demo 9V")

    # ── Graph & iterator factory ─────────────────────────────────────────

    def _create_graph(self, name: str) -> None:
        factory, grid_dims = self._GRAPH_FACTORIES.get(
            name, (gen_demo_graph, None)
        )
        self.graph = factory()
        if grid_dims is not None:
            self.canvas.set_graph(self.graph, layout_type='spring', grid_dims=grid_dims)
        else:
            self.canvas.set_graph(self.graph, layout_type='kamada_kawai')
        self._current_graph_name = name

    def _create_iterator(self, algo_name: str):
        if self.graph is None:
            return None
        if algo_name == "Kruskal":
            return kruskal_steps(self.graph)
        elif algo_name == "Prim":
            return prim_steps(self.graph, start=0)
        elif algo_name == "Dijkstra":
            return dijkstra_steps(self.graph, source=0)
        elif algo_name == "Dijkstra Obstacle":
            return dijkstra_obstacle_steps(self.graph, source=0)
        return kruskal_steps(self.graph)

    # ── Internal helpers ─────────────────────────────────────────────────

    def _reset(self) -> None:
        """Stop worker, clear cache, redraw base graph."""
        if self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)
        self.steps_cache.clear()
        self.current_index = -1
        self._exhausted = False
        self._iterator = self._create_iterator(self._current_algo_name)
        self.worker.set_iterator(self._iterator)
        self.canvas.render_step(None)
        self.info_panel.clear()
        self.info_panel.set_algorithm(self._current_algo_name)
        self.control_panel.set_step_count(0, 0)
        self.control_panel.set_playing(False)

    def _render_current(self) -> None:
        if 0 <= self.current_index < len(self.steps_cache):
            step = self.steps_cache[self.current_index]
            self.canvas.render_step(step)
            self.info_panel.update_step(step)
            self.control_panel.set_step_count(
                self.current_index + 1, len(self.steps_cache)
            )

    def _advance_cache_one(self) -> bool:
        """Pull one step from the iterator into the cache. Returns True if got one."""
        if self._exhausted or self._iterator is None:
            return False
        try:
            step = next(self._iterator)
            self.steps_cache.append(step)
            return True
        except StopIteration:
            self._exhausted = True
            return False

    def _drain_iterator(self) -> None:
        """Pull all remaining steps from the iterator into the cache."""
        while self._advance_cache_one():
            pass

    # ── Control panel slots ───────────────────────────────────────────────

    def _on_play(self) -> None:
        if not self.worker.isRunning():
            if self._exhausted and self.current_index >= len(self.steps_cache) - 1:
                return  # nothing left to play
            self.worker.set_iterator(self._create_fresh_iterator_from(
                self.current_index + 1
            ))
            self.worker.start()
        else:
            self.worker.resume()
        self.control_panel.set_playing(True)

    def _create_fresh_iterator_from(self, skip_count: int):
        """Create a new iterator and fast-forward past already-cached steps."""
        it = self._create_iterator(self._current_algo_name)
        if it is None:
            return None
        for _ in range(skip_count):
            try:
                next(it)
            except StopIteration:
                break
        return it

    def _on_pause(self) -> None:
        self.worker.pause()
        self.control_panel.set_playing(False)

    def _on_step_forward(self) -> None:
        if self.worker.isRunning() and not self.worker._paused:
            self.worker.pause()
            self.control_panel.set_playing(False)

        next_index = self.current_index + 1
        if next_index < len(self.steps_cache):
            self.current_index = next_index
            self._render_current()
        elif not self._exhausted:
            # Pull one more step from the iterator synchronously
            if self._advance_cache_one():
                self.current_index = len(self.steps_cache) - 1
                self._render_current()

    def _on_step_backward(self) -> None:
        if self.worker.isRunning() and not self.worker._paused:
            self.worker.pause()
            self.control_panel.set_playing(False)
        if self.current_index > 0:
            self.current_index -= 1
            self._render_current()

    def _on_jump_start(self) -> None:
        if self.worker.isRunning() and not self.worker._paused:
            self.worker.pause()
            self.control_panel.set_playing(False)
        if self.steps_cache:
            self.current_index = 0
            self._render_current()
        else:
            self.canvas.render_step(None)

    def _on_jump_end(self) -> None:
        if self.worker.isRunning() and not self.worker._paused:
            self.worker.pause()
            self.control_panel.set_playing(False)
        self._drain_iterator()
        if self.steps_cache:
            self.current_index = len(self.steps_cache) - 1
            self._render_current()

    def _on_algorithm_changed(self, algo_name: str) -> None:
        self._current_algo_name = algo_name
        self.info_panel.set_algorithm(algo_name)
        self._reset()

    def _on_graph_changed(self, graph_name: str) -> None:
        self._create_graph(graph_name)
        self._reset()

    def _on_graph_modified(self) -> None:
        """Called when GraphEditor changes the graph structure."""
        self.canvas.render_step(None)
        self._reset()

    # ── Worker slots ─────────────────────────────────────────────────────

    def _on_step_ready(self, step: AlgorithmStep) -> None:
        """Receive a step from the animation worker thread."""
        self.steps_cache.append(step)
        self.current_index = len(self.steps_cache) - 1
        self.canvas.render_step(step)
        self.info_panel.update_step(step)
        self.control_panel.set_step_count(
            self.current_index + 1, len(self.steps_cache)
        )

    def _on_worker_finished(self) -> None:
        self._exhausted = True
        self.control_panel.set_playing(False)
