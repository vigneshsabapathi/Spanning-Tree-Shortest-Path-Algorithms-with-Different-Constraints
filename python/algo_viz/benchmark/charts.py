from __future__ import annotations

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib.figure import Figure

from algo_viz.benchmark.runner import BenchmarkEntry

# Brand palette
_COLOR_A = "#4CAF50"   # Kruskal / Dijkstra  (green)
_COLOR_B = "#2196F3"   # Prim / Obstacle      (blue)
_BG      = "#1e1e2e"   # dark background
_GRID    = "#3a3a5c"   # subtle grid lines
_TEXT    = "#e0e0f0"   # axis / title text


def _apply_dark_style(fig: Figure, ax) -> None:
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)
    ax.tick_params(colors=_TEXT, which="both")
    ax.xaxis.label.set_color(_TEXT)
    ax.yaxis.label.set_color(_TEXT)
    ax.title.set_color(_TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRID)
    ax.grid(True, axis="y", color=_GRID, linewidth=0.6, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)


def create_mst_chart(results: list[BenchmarkEntry]) -> Figure:
    """Grouped bar chart: Kruskal (green) vs Prim (blue) timing by graph size."""
    kruskal_entries = [r for r in results if r.algorithm == "Kruskal"]
    prim_entries    = [r for r in results if r.algorithm == "Prim"]

    sizes   = [r.vertices for r in kruskal_entries]
    k_times = [r.time_us  for r in kruskal_entries]
    p_times = [r.time_us  for r in prim_entries]

    x      = np.arange(len(sizes))
    width  = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    _apply_dark_style(fig, ax)

    bars_k = ax.bar(x - width / 2, k_times, width, label="Kruskal",
                    color=_COLOR_A, alpha=0.88, edgecolor="white", linewidth=0.5)
    bars_p = ax.bar(x + width / 2, p_times, width, label="Prim",
                    color=_COLOR_B, alpha=0.88, edgecolor="white", linewidth=0.5)

    for bar in list(bars_k) + list(bars_p):
        h = bar.get_height()
        if h > 0:
            label = f"{h:,.0f}" if h >= 1 else f"{h:.2f}"
            ax.annotate(
                label,
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=7, color=_TEXT,
            )

    if k_times and p_times:
        all_times = k_times + p_times
        if max(all_times) / max(min(all_times), 1e-9) > 100:
            ax.set_yscale("log")
            ax.yaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
            )

    ax.set_xlabel("Graph Size (vertices)", fontsize=11)
    ax.set_ylabel("Average Time (µs)", fontsize=11)
    ax.set_title("MST Algorithm Comparison: Kruskal vs Prim", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in sizes], fontsize=9)

    legend = ax.legend(
        fontsize=10,
        facecolor="#2a2a4a",
        edgecolor=_GRID,
        labelcolor=_TEXT,
    )

    fig.tight_layout(pad=1.5)
    return fig


def create_sp_chart(results: list[BenchmarkEntry]) -> Figure:
    """Grouped bar chart: Dijkstra (green) vs Obstacle Dijkstra (blue) timing by graph size."""
    dijkstra_entries  = [r for r in results if r.algorithm == "Dijkstra"]
    obstacle_entries  = [r for r in results if r.algorithm == "Dijkstra Obstacle"]

    sizes   = [r.vertices for r in dijkstra_entries]
    d_times = [r.time_us  for r in dijkstra_entries]
    o_times = [r.time_us  for r in obstacle_entries]

    x     = np.arange(len(sizes))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    _apply_dark_style(fig, ax)

    bars_d = ax.bar(x - width / 2, d_times, width, label="Dijkstra",
                    color=_COLOR_A, alpha=0.88, edgecolor="white", linewidth=0.5)
    bars_o = ax.bar(x + width / 2, o_times, width, label="Dijkstra Obstacle",
                    color=_COLOR_B, alpha=0.88, edgecolor="white", linewidth=0.5)

    for bar in list(bars_d) + list(bars_o):
        h = bar.get_height()
        if h > 0:
            label = f"{h:,.0f}" if h >= 1 else f"{h:.2f}"
            ax.annotate(
                label,
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=7, color=_TEXT,
            )

    if d_times and o_times:
        all_times = d_times + o_times
        if max(all_times) / max(min(all_times), 1e-9) > 100:
            ax.set_yscale("log")
            ax.yaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}")
            )

    ax.set_xlabel("Graph Size (vertices)", fontsize=11)
    ax.set_ylabel("Average Time (µs)", fontsize=11)
    ax.set_title("SP Algorithm Comparison: Dijkstra vs Obstacle Dijkstra",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in sizes], fontsize=9)

    ax.legend(
        fontsize=10,
        facecolor="#2a2a4a",
        edgecolor=_GRID,
        labelcolor=_TEXT,
    )

    fig.tight_layout(pad=1.5)
    return fig


def create_results_table(results: list[BenchmarkEntry]) -> str:
    """Format benchmark results as a fixed-width text table."""
    header = (
        f"{'V':>6}  {'E':>8}  {'Algorithm':<22}  {'Time (µs)':>12}  {'Weight/Dist':>12}  {'OK':>4}"
    )
    sep = "-" * len(header)
    lines = [header, sep]
    for r in results:
        ok = "Yes" if r.success else "No"
        lines.append(
            f"{r.vertices:>6}  {r.edges:>8}  {r.algorithm:<22}  "
            f"{r.time_us:>12.1f}  {r.result_value:>12}  {ok:>4}"
        )
    return "\n".join(lines)
