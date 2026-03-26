import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.patches import FancyBboxPatch
import numpy as np

from algo_viz.core.graph import Graph
from algo_viz.models.step import AlgorithmStep, StepKind
from algo_viz.visualization.color_scheme import Colors
from algo_viz.visualization.layout_engine import compute_layout, compute_grid_layout


class GraphCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)

        self.graph: Graph | None = None
        self.pos: dict[int, tuple[float, float]] = {}
        self.current_step: AlgorithmStep | None = None

        self.fig.patch.set_facecolor(Colors.BACKGROUND)
        self.ax.set_facecolor(Colors.BACKGROUND)

    def set_graph(self, graph: Graph, layout_type: str = 'kamada_kawai', grid_dims: tuple[int, int] | None = None) -> None:
        self.graph = graph
        if grid_dims is not None:
            rows, cols = grid_dims
            pos_raw = compute_grid_layout(rows, cols)
        else:
            pos_raw = compute_layout(graph, layout_type)
        # Normalise to (x, y) float tuples regardless of numpy array type
        self.pos = {v: (float(xy[0]), float(xy[1])) for v, xy in pos_raw.items()}
        self.render_step(None)

    def render_step(self, step: AlgorithmStep | None) -> None:
        self.current_step = step
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_facecolor(Colors.BACKGROUND)

        if self.graph is None:
            self.draw()
            return

        self._draw_edges(step)
        self._draw_vertices(step)
        self._draw_labels(step)

        if step and step.explanation:
            self.ax.set_title(
                step.explanation,
                fontsize=10,
                color=Colors.TEXT,
                pad=8,
                wrap=True,
            )

        self.fig.tight_layout()
        self.draw()

    # ------------------------------------------------------------------
    # Internal drawing helpers
    # ------------------------------------------------------------------

    def _draw_edges(self, step: AlgorithmStep | None) -> None:
        for edge in self.graph.edge_list:
            x1, y1 = self.pos[edge.src]
            x2, y2 = self.pos[edge.dest]

            # Determine style
            if edge.blocked:
                color = Colors.EDGE_BLOCKED
                lw = Colors.EDGE_WIDTH
                ls = 'dashed'
            elif edge.penalty > 1:
                color = Colors.EDGE_PENALTY
                lw = Colors.EDGE_WIDTH_ACTIVE
                ls = 'solid'
            elif step is not None and edge.edge_id in step.active_edges:
                color = Colors.EDGE_ACTIVE
                lw = Colors.EDGE_WIDTH_BOLD
                ls = 'solid'
            elif step is not None and edge.edge_id in step.mst_edges:
                color = Colors.EDGE_MST
                lw = Colors.EDGE_WIDTH_BOLD
                ls = 'solid'
            else:
                color = Colors.EDGE_NORMAL
                lw = Colors.EDGE_WIDTH
                ls = 'solid'

            self.ax.plot(
                [x1, x2], [y1, y2],
                color=color,
                linewidth=lw,
                linestyle=ls,
                zorder=1,
            )

            # Weight label at midpoint
            midx = (x1 + x2) / 2
            midy = (y1 + y2) / 2
            label = str(edge.weight)
            if edge.penalty > 1:
                label += f' \xd7{edge.penalty}'
            self.ax.text(
                midx, midy, label,
                fontsize=Colors.FONT_SIZE_EDGE,
                ha='center', va='center',
                bbox=dict(
                    boxstyle='round,pad=0.15',
                    facecolor='white',
                    edgecolor='none',
                    alpha=0.8,
                ),
                zorder=3,
            )

    def _draw_vertices(self, step: AlgorithmStep | None) -> None:
        for v in range(self.graph.num_vertices):
            x, y = self.pos[v]
            blocked = self.graph.vertex_blocked[v]

            if blocked:
                color = Colors.VERTEX_BLOCKED
                size = Colors.VERTEX_SIZE
            elif step is not None and v in step.active_vertices:
                color = Colors.VERTEX_ACTIVE
                size = Colors.VERTEX_SIZE_LARGE
            elif step is not None and v in step.settled_vertices:
                color = Colors.VERTEX_SETTLED
                size = Colors.VERTEX_SIZE
            elif step is not None and v in step.path_vertices:
                color = Colors.VERTEX_PATH
                size = Colors.VERTEX_SIZE
            else:
                color = Colors.VERTEX_NORMAL
                size = Colors.VERTEX_SIZE

            self.ax.scatter(
                x, y,
                s=size,
                c=color,
                edgecolors='white',
                linewidths=1.5,
                zorder=4,
            )

            if blocked:
                # Draw an X overlay using two short crossing lines
                delta = 0.04
                self.ax.plot(
                    [x - delta, x + delta], [y - delta, y + delta],
                    color='white', linewidth=2.0, zorder=6,
                )
                self.ax.plot(
                    [x - delta, x + delta], [y + delta, y - delta],
                    color='white', linewidth=2.0, zorder=6,
                )

    def _draw_labels(self, step: AlgorithmStep | None) -> None:
        for v in range(self.graph.num_vertices):
            x, y = self.pos[v]
            self.ax.text(
                x, y, str(v),
                fontsize=Colors.FONT_SIZE_VERTEX,
                ha='center', va='center',
                fontweight='bold',
                color='white',
                zorder=5,
            )
