from PyQt6.QtWidgets import QMainWindow, QTabWidget, QLabel
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Algorithms Visualizer")
        self.setMinimumSize(1200, 800)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Tab 1: Single algorithm visualizer
        from algo_viz.gui.visualizer_tab import VisualizerTab
        self.visualizer = VisualizerTab()
        tabs.addTab(self.visualizer, "Visualizer")

        # Tab 2: Side-by-side algorithm comparison
        from algo_viz.gui.comparison_tab import ComparisonTab
        self.comparison = ComparisonTab()
        tabs.addTab(self.comparison, "Compare")

        # Tab 3: Benchmark runner with charts
        from algo_viz.gui.benchmark_tab import BenchmarkTab
        self.benchmark = BenchmarkTab()
        tabs.addTab(self.benchmark, "Benchmark")

        # Tab 4: About
        about_text = (
            "<h2>Graph Algorithms Visualizer</h2>"
            "<p>An interactive PyQt6 application for exploring and comparing "
            "classic graph algorithms.</p>"
            "<h3>Algorithms</h3>"
            "<ul>"
            "<li><b>Kruskal's MST</b> — greedy edge-sorting with Union-Find</li>"
            "<li><b>Prim's MST</b> — greedy vertex-growing with a min-heap</li>"
            "<li><b>Dijkstra's SP</b> — single-source shortest paths</li>"
            "<li><b>Obstacle Dijkstra</b> — Dijkstra with edge penalties "
            "(simulates weighted terrain)</li>"
            "</ul>"
            "<h3>Tabs</h3>"
            "<ul>"
            "<li><b>Visualizer</b> — step-through any algorithm on any graph "
            "with full playback controls</li>"
            "<li><b>Compare</b> — run two algorithms side-by-side on the same "
            "graph, step-by-step or to completion</li>"
            "<li><b>Benchmark</b> — time algorithms across graph sizes and "
            "display grouped bar charts</li>"
            "</ul>"
            "<p style='color:#808090; font-size:11px;'>Built with Python 3.12 · "
            "PyQt6 · Matplotlib · NumPy</p>"
        )
        about_label = QLabel(about_text)
        about_label.setWordWrap(True)
        about_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        about_label.setContentsMargins(24, 20, 24, 20)
        about_label.setStyleSheet("font-size: 13px; line-height: 1.5;")
        tabs.addTab(about_label, "About")

        # Status bar
        self.statusBar().showMessage("Ready")
