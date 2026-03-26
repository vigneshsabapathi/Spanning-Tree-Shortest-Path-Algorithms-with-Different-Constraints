from __future__ import annotations

import matplotlib  # noqa: F401  – imported for side-effects; backend set by graph_canvas

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar,
    QTextEdit, QDoubleSpinBox, QSpinBox,
    QSplitter, QSizePolicy,
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from algo_viz.benchmark.runner import run_mst_benchmark, run_sp_benchmark, BenchmarkEntry
from algo_viz.benchmark.charts import create_mst_chart, create_sp_chart, create_results_table


# ── Background worker ──────────────────────────────────────────────────────────

class BenchmarkWorker(QThread):
    """Run MST and SP benchmarks in a background thread.

    Signals
    -------
    progress(int)
        Emitted with an integer in [0, 100] as work proceeds.
    finished(list, list)
        Emitted when both suites complete; carries (mst_results, sp_results).
    error(str)
        Emitted if an exception is raised.
    """

    progress = pyqtSignal(int)
    finished = pyqtSignal(list, list)
    error    = pyqtSignal(str)

    def __init__(
        self,
        sizes: list[int],
        density: float,
        runs: int,
        parent=None,
    ):
        super().__init__(parent)
        self._sizes   = sizes
        self._density = density
        self._runs    = runs

    def run(self) -> None:
        try:
            self.progress.emit(5)
            mst = run_mst_benchmark(
                sizes=self._sizes,
                density=self._density,
                runs=self._runs,
            )
            self.progress.emit(55)
            sp = run_sp_benchmark(
                sizes=self._sizes,
                density=self._density,
                runs=self._runs,
            )
            self.progress.emit(100)
            self.finished.emit(mst, sp)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))


# ── Thin wrapper so we can replace the figure easily ─────────────────────────

class _ChartHolder(QWidget):
    """Holds a single FigureCanvasQTAgg and can swap it out."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._canvas: FigureCanvasQTAgg | None = None

    def set_figure(self, fig) -> None:
        # Remove old canvas
        if self._canvas is not None:
            self._layout.removeWidget(self._canvas)
            self._canvas.setParent(None)  # type: ignore[call-arg]
            self._canvas.figure.clf()
            self._canvas = None

        canvas = FigureCanvasQTAgg(fig)
        canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._layout.addWidget(canvas)
        self._canvas = canvas
        canvas.draw()


# ── Main benchmark tab ────────────────────────────────────────────────────────

class BenchmarkTab(QWidget):
    """Benchmark tab: run MST and SP benchmarks and display charts + table."""

    _DEFAULT_SIZES = [50, 100, 250, 500, 1000]

    def __init__(self, parent=None):
        super().__init__(parent)

        self._worker: BenchmarkWorker | None = None

        # ── Top bar ───────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self._btn_run = QPushButton("Run Benchmark")
        self._btn_run.setFixedHeight(30)
        top_bar.addWidget(self._btn_run)

        top_bar.addSpacing(12)
        top_bar.addWidget(QLabel("Density:"))
        self._density_spin = QDoubleSpinBox()
        self._density_spin.setRange(0.1, 0.9)
        self._density_spin.setSingleStep(0.1)
        self._density_spin.setValue(0.2)
        self._density_spin.setDecimals(1)
        self._density_spin.setFixedWidth(70)
        self._density_spin.setToolTip(
            "Edge density for generated graphs (fraction of all possible edges)"
        )
        top_bar.addWidget(self._density_spin)

        top_bar.addSpacing(12)
        top_bar.addWidget(QLabel("Runs:"))
        self._runs_spin = QSpinBox()
        self._runs_spin.setRange(1, 10)
        self._runs_spin.setValue(3)
        self._runs_spin.setFixedWidth(55)
        self._runs_spin.setToolTip("Number of timing repetitions per data point")
        top_bar.addWidget(self._runs_spin)

        top_bar.addSpacing(16)
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        self._progress.setFixedHeight(22)
        self._progress.setVisible(False)
        top_bar.addWidget(self._progress, stretch=1)

        self._status_label = QLabel("Ready.")
        self._status_label.setStyleSheet("color: #a0c0ff; font-size: 11px;")
        top_bar.addWidget(self._status_label)

        # ── Chart holders ─────────────────────────────────────────────────
        self._mst_chart_holder = _ChartHolder()
        self._sp_chart_holder  = _ChartHolder()

        chart_splitter = QSplitter(Qt.Orientation.Horizontal)
        chart_splitter.addWidget(self._mst_chart_holder)
        chart_splitter.addWidget(self._sp_chart_holder)
        chart_splitter.setStretchFactor(0, 1)
        chart_splitter.setStretchFactor(1, 1)

        # ── Results table ─────────────────────────────────────────────────
        self._table_edit = QTextEdit()
        self._table_edit.setReadOnly(True)
        mono = QFont("Courier New", 9)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self._table_edit.setFont(mono)
        self._table_edit.setStyleSheet(
            "background: #1a1a2e; color: #c8c8e0; border: 1px solid #3a3a5c;"
        )
        self._table_edit.setFixedHeight(180)
        self._table_edit.setPlaceholderText(
            "Benchmark results will appear here after running…"
        )

        # ── Master layout ─────────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)
        root.addLayout(top_bar)
        root.addWidget(chart_splitter, stretch=1)
        root.addWidget(QLabel("Results Table:"))
        root.addWidget(self._table_edit)

        # ── Wire signals ──────────────────────────────────────────────────
        self._btn_run.clicked.connect(self._on_run)

    # ── Slots ─────────────────────────────────────────────────────────────

    def _on_run(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return

        density = self._density_spin.value()
        runs    = self._runs_spin.value()

        self._btn_run.setEnabled(False)
        self._progress.setValue(0)
        self._progress.setVisible(True)
        self._status_label.setText("Running…")
        self._table_edit.clear()

        self._worker = BenchmarkWorker(
            sizes=self._DEFAULT_SIZES,
            density=density,
            runs=runs,
            parent=self,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, value: int) -> None:
        self._progress.setValue(value)

    def _on_finished(
        self,
        mst_results: list[BenchmarkEntry],
        sp_results: list[BenchmarkEntry],
    ) -> None:
        # Render charts
        mst_fig = create_mst_chart(mst_results)
        sp_fig  = create_sp_chart(sp_results)
        self._mst_chart_holder.set_figure(mst_fig)
        self._sp_chart_holder.set_figure(sp_fig)

        # Render table
        all_results = mst_results + sp_results
        # Sort by vertices then algorithm name for a tidy table
        all_results.sort(key=lambda r: (r.vertices, r.algorithm))
        self._table_edit.setPlainText(create_results_table(all_results))

        self._btn_run.setEnabled(True)
        self._progress.setVisible(False)
        self._status_label.setText(
            f"Done — {len(mst_results)} MST entries, {len(sp_results)} SP entries."
        )

    def _on_error(self, msg: str) -> None:
        self._btn_run.setEnabled(True)
        self._progress.setVisible(False)
        self._status_label.setText(f"Error: {msg}")
        self._table_edit.setPlainText(f"Benchmark failed:\n{msg}")
