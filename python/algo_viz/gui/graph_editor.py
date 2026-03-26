from __future__ import annotations

import math

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMenu, QInputDialog, QApplication
from PyQt6.QtGui import QAction


class GraphEditor(QObject):
    """Helper that wires matplotlib click events to obstacle-editing menus.

    Pass a GraphCanvas instance; GraphEditor connects to its figure's
    button_press_event and presents right-click context menus for blocking
    vertices / edges or setting edge penalties.

    Emits graph_modified whenever the graph is changed so the owning widget
    can reset the visualizer.
    """

    graph_modified = pyqtSignal()

    # Distance threshold in data coordinates for hit testing
    HIT_THRESHOLD = 0.05

    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self._canvas = canvas
        canvas.mpl_connect("button_press_event", self._on_mouse_press)

    # ── Event handler ────────────────────────────────────────────────────

    def _on_mouse_press(self, event):
        """Handle matplotlib mouse press events."""
        if event.button != 3:          # 3 = right-click
            return
        if event.inaxes is None:
            return
        if self._canvas.graph is None:
            return

        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return

        graph = self._canvas.graph
        pos = self._canvas.pos

        # Try to hit a vertex first (higher priority)
        hit_vertex = self._find_nearest_vertex(x, y, pos)
        if hit_vertex is not None:
            self._show_vertex_menu(hit_vertex, graph)
            return

        # Fall back to edge hit
        hit_edge = self._find_nearest_edge(x, y, graph, pos)
        if hit_edge is not None:
            self._show_edge_menu(hit_edge, graph)

    # ── Hit testing ──────────────────────────────────────────────────────

    def _find_nearest_vertex(
        self, x: float, y: float, pos: dict
    ) -> int | None:
        best_v = None
        best_dist = self.HIT_THRESHOLD
        for v, (vx, vy) in pos.items():
            d = math.hypot(x - vx, y - vy)
            if d < best_dist:
                best_dist = d
                best_v = v
        return best_v

    def _find_nearest_edge(self, x, y, graph, pos):
        """Return the Edge object nearest to (x, y) within threshold."""
        best_edge = None
        best_dist = self.HIT_THRESHOLD
        for edge in graph.edge_list:
            mx = (pos[edge.src][0] + pos[edge.dest][0]) / 2
            my = (pos[edge.src][1] + pos[edge.dest][1]) / 2
            d = math.hypot(x - mx, y - my)
            if d < best_dist:
                best_dist = d
                best_edge = edge
        return best_edge

    # ── Context menus ────────────────────────────────────────────────────

    def _show_vertex_menu(self, vertex: int, graph) -> None:
        menu = QMenu()
        blocked = graph.vertex_blocked[vertex]

        if blocked:
            action = QAction(f"Unblock Vertex {vertex}", menu)
            action.triggered.connect(
                lambda: self._unblock_vertex(vertex, graph)
            )
        else:
            action = QAction(f"Block Vertex {vertex}", menu)
            action.triggered.connect(
                lambda: self._block_vertex(vertex, graph)
            )

        menu.addAction(action)
        menu.exec(self._global_cursor_pos())

    def _show_edge_menu(self, edge, graph) -> None:
        menu = QMenu()
        label = f"Edge {edge.src}-{edge.dest} (w={edge.weight})"

        if edge.blocked:
            unblock_action = QAction(f"Unblock Edge {edge.src}-{edge.dest}", menu)
            unblock_action.triggered.connect(
                lambda: self._unblock_edge(edge, graph)
            )
            menu.addAction(unblock_action)
        else:
            block_action = QAction(f"Block Edge {edge.src}-{edge.dest}", menu)
            block_action.triggered.connect(
                lambda: self._block_edge(edge, graph)
            )
            menu.addAction(block_action)

        penalty_action = QAction(f"Set Penalty on {label}...", menu)
        penalty_action.triggered.connect(
            lambda: self._set_penalty(edge, graph)
        )
        menu.addAction(penalty_action)

        menu.exec(self._global_cursor_pos())

    # ── Graph mutation callbacks ─────────────────────────────────────────

    def _block_vertex(self, vertex: int, graph) -> None:
        graph.block_vertex(vertex)
        self.graph_modified.emit()

    def _unblock_vertex(self, vertex: int, graph) -> None:
        graph.unblock_vertex(vertex)
        self.graph_modified.emit()

    def _block_edge(self, edge, graph) -> None:
        graph.block_edge(edge.src, edge.dest)
        self.graph_modified.emit()

    def _unblock_edge(self, edge, graph) -> None:
        # Re-use block_edge infrastructure: clear the flag manually
        for e in graph.edge_list:
            if e.edge_id == edge.edge_id:
                e.blocked = False
                for lst in (graph.adj[e.src], graph.adj[e.dest]):
                    graph.adj[e.src] = [
                        type(a)(a.dest, a.weight, a.edge_id, False)
                        if a.edge_id == e.edge_id else a
                        for a in graph.adj[e.src]
                    ]
                    graph.adj[e.dest] = [
                        type(a)(a.dest, a.weight, a.edge_id, False)
                        if a.edge_id == e.edge_id else a
                        for a in graph.adj[e.dest]
                    ]
                break
        self.graph_modified.emit()

    def _set_penalty(self, edge, graph) -> None:
        value, ok = QInputDialog.getInt(
            None,
            "Set Edge Penalty",
            f"Penalty for edge {edge.src}-{edge.dest} (1 = normal):",
            value=edge.penalty,
            min=1,
            max=10,
        )
        if ok:
            graph.set_edge_penalty(edge.src, edge.dest, value)
            self.graph_modified.emit()

    # ── Utility ──────────────────────────────────────────────────────────

    @staticmethod
    def _global_cursor_pos():
        return QApplication.instance().overrideCursor() or \
               QApplication.primaryScreen().availableGeometry().center()
