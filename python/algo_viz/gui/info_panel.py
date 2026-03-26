from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from algo_viz.models.step import AlgorithmStep, StepKind


class InfoPanel(QWidget):
    """Right-side panel showing algorithm state details."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ── Algorithm name ───────────────────────────────────────────────
        self._algo_label = QLabel("—")
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self._algo_label.setFont(font)
        self._algo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Step description ─────────────────────────────────────────────
        self._desc_label = QLabel("")
        self._desc_label.setWordWrap(True)
        self._desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── State group ──────────────────────────────────────────────────
        state_box = QGroupBox("State")
        state_layout = QVBoxLayout(state_box)
        self._state_edit = QTextEdit()
        self._state_edit.setReadOnly(True)
        mono = QFont("Monospace")
        mono.setStyleHint(QFont.StyleHint.TypeWriter)
        mono.setPointSize(9)
        self._state_edit.setFont(mono)
        self._state_edit.setMinimumHeight(120)
        state_layout.addWidget(self._state_edit)

        # ── Statistics group ─────────────────────────────────────────────
        stats_box = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_box)
        self._stat_weight = QLabel("Total weight / dist: —")
        self._stat_edges = QLabel("Edges in MST: —")
        self._stat_settled = QLabel("Vertices settled: —")
        self._stat_step_kind = QLabel("Step kind: —")
        for lbl in (self._stat_weight, self._stat_edges,
                    self._stat_settled, self._stat_step_kind):
            stats_layout.addWidget(lbl)

        layout.addWidget(self._algo_label)
        layout.addWidget(self._desc_label)
        layout.addWidget(state_box)
        layout.addWidget(stats_box)
        layout.addStretch()

    # ── Public API ───────────────────────────────────────────────────────

    def set_algorithm(self, name: str) -> None:
        self._algo_label.setText(name)

    def clear(self) -> None:
        self._desc_label.setText("")
        self._state_edit.setPlainText("")
        self._stat_weight.setText("Total weight / dist: —")
        self._stat_edges.setText("Edges in MST: —")
        self._stat_settled.setText("Vertices settled: —")
        self._stat_step_kind.setText("Step kind: —")

    def update_step(self, step: AlgorithmStep) -> None:
        self._desc_label.setText(step.explanation)
        self._stat_step_kind.setText(f"Step kind: {step.kind.name}")

        # Build state text
        state_lines = []

        if step.union_find_state:
            state_lines.append(self._format_union_find(step.union_find_state))

        if step.distances:
            state_lines.append(self._format_distances(step.distances))

        if step.heap_contents:
            state_lines.append(self._format_heap(step.heap_contents))

        self._state_edit.setPlainText("\n".join(state_lines))

        # Statistics
        if step.mst_edges:
            self._stat_edges.setText(f"Edges in MST: {len(step.mst_edges)}")
        else:
            self._stat_edges.setText("Edges in MST: 0")

        if step.settled_vertices:
            self._stat_settled.setText(
                f"Vertices settled: {len(step.settled_vertices)}"
            )
        else:
            self._stat_settled.setText("Vertices settled: 0")

        # Total weight / distance
        if step.distances:
            reachable = [d for d in step.distances.values() if d >= 0]
            if reachable:
                self._stat_weight.setText(
                    f"Total weight / dist: {sum(reachable)}"
                )
            else:
                self._stat_weight.setText("Total weight / dist: —")
        else:
            self._stat_weight.setText("Total weight / dist: —")

    # ── Formatting helpers ────────────────────────────────────────────────

    @staticmethod
    def _format_union_find(uf_state: dict) -> str:
        """Group vertices by their root and display as components."""
        # uf_state maps vertex -> parent; walk to root
        def find_root(v, state):
            seen = []
            while state.get(v, v) != v:
                seen.append(v)
                v = state[v]
            return v

        components: dict[int, list[int]] = {}
        for v in sorted(uf_state.keys()):
            root = find_root(v, uf_state)
            components.setdefault(root, []).append(v)

        lines = ["Union-Find Components:"]
        for root in sorted(components):
            members = components[root]
            lines.append(f"  {{{', '.join(str(m) for m in members)}}}")
        return "\n".join(lines)

    @staticmethod
    def _format_distances(distances: dict) -> str:
        """Display distances as a two-column table."""
        lines = ["Distances:"]
        for v in sorted(distances.keys()):
            d = distances[v]
            dist_str = str(d) if d >= 0 else "inf"
            lines.append(f"  v{v:>3}: {dist_str}")
        return "\n".join(lines)

    @staticmethod
    def _format_heap(heap_contents: tuple) -> str:
        """Display heap as a sorted priority list."""
        lines = ["Heap (key, vertex):"]
        for key, vertex in heap_contents:
            lines.append(f"  ({key}, v{vertex})")
        return "\n".join(lines)
