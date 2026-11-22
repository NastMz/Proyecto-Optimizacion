"""Matplotlib charts embedded in Qt, styled with the application theme."""

from __future__ import annotations

import math

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from ..core.formatting import number
from . import theme

_THOUSANDS = FuncFormatter(lambda v, _: number(v, 0))


class Chart(FigureCanvasQTAgg):
    def __init__(self, height: float = 3.2) -> None:
        self.figure = Figure(figsize=(5, height), layout="constrained")
        super().__init__(self.figure)
        self.setMinimumHeight(int(height * 70))
        self.ax = self.figure.add_subplot()

    def _reset(self, title: str) -> None:
        self.ax.clear()
        self.ax.set_title(title, pad=10)


class ProductionChart(Chart):
    """Units per day of each product."""

    def plot(self, names: list[str], values: list[float]) -> None:
        self._reset("Unidades por día")
        colors = [theme.product_color(i) for i in range(len(names))]
        bars = self.ax.bar(names, values, color=colors, width=0.58, zorder=3)
        self.ax.yaxis.set_major_formatter(_THOUSANDS)
        self.ax.tick_params(axis="x", length=0, labelcolor=theme.INK, labelsize=10)
        top = max(values) if values and max(values) > 0 else 1
        for bar, value in zip(bars, values):
            self.ax.text(bar.get_x() + bar.get_width() / 2, value + top * 0.02, number(value, 1),
                         ha="center", va="bottom", fontsize=9.5, color=theme.INK, fontweight="bold")
        self.ax.set_ylim(0, top * 1.15)
        self.draw_idle()


class ShareChart(Chart):
    """Donut with the share of the total profit contributed by each product."""

    def plot(self, names: list[str], contributions: list[float], total: float) -> None:
        self._reset("Participación en la utilidad")
        self.ax.grid(False)
        self.ax.set_axis_off()
        colors = [theme.product_color(i) for i in range(len(names))]
        wedges, _ = self.ax.pie(
            contributions, colors=colors, startangle=90, counterclock=False,
            wedgeprops={"width": 0.36, "edgecolor": theme.SURFACE, "linewidth": 2},
        )
        self.ax.text(0, 0.08, "$ " + number(total / 1e6, 2) + " M", ha="center", va="center",
                     fontsize=15, color=theme.INK, family=theme.mpl_display_family())
        self.ax.text(0, -0.2, "por día", ha="center", va="center", fontsize=9, color=theme.MUTED)
        shares = [100 * c / total if total else 0 for c in contributions]
        self.ax.legend(wedges, [f"{n}  {number(s, 1)} %" for n, s in zip(names, shares)],
                       loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False, fontsize=9.5)
        self.ax.set_aspect("equal")
        self.draw_idle()


class ParametricChart(Chart):
    """Optimal profit as a function of one parameter, with the valid range shaded."""

    def plot(self, xs: np.ndarray, ys: np.ndarray, current: float, current_z: float,
             valid: tuple[float, float] | None, label: str, simulated: list[tuple[float, float]]) -> None:
        self._reset("Utilidad óptima según el parámetro")
        if valid is not None:
            low = valid[0] if math.isfinite(valid[0]) else xs[0]
            high = valid[1] if math.isfinite(valid[1]) else xs[-1]
            self.ax.axvspan(max(low, xs[0]), min(high, xs[-1]), color=theme.CARDAMOM_TINT, zorder=0,
                            label="Rango sin cambio de base")
        self.ax.plot(xs, ys, color=theme.PAPRIKA, linewidth=2.2, zorder=3)
        self.ax.scatter([current], [current_z], s=70, color=theme.SIDEBAR, zorder=4, label="Valor actual")
        if simulated:
            sx, sy = zip(*simulated)
            self.ax.scatter(sx, sy, s=60, color=theme.SAFFRON, edgecolor=theme.SIDEBAR, zorder=5,
                            label="Simulaciones")
        self.ax.set_xlabel(label)
        self.ax.set_ylabel("Utilidad diaria ($)")
        self.ax.yaxis.set_major_formatter(_THOUSANDS)
        self.ax.xaxis.set_major_formatter(_THOUSANDS)
        self.ax.legend(frameon=False, fontsize=8.5, loc="upper left")
        self.draw_idle()


class HistoryChart(Chart):
    """Optimal profit of the base scenario and of every simulation."""

    def plot(self, labels: list[str], values: list[float]) -> None:
        self._reset("Histórico de simulaciones")
        positions = np.arange(len(labels))
        clean = [v if v is not None and math.isfinite(v) else np.nan for v in values]
        self.ax.plot(positions, clean, color=theme.PAPRIKA, marker="o", linewidth=2, markersize=7,
                     markerfacecolor=theme.SAFFRON, markeredgecolor=theme.SIDEBAR, zorder=3)
        if clean and math.isfinite(clean[0]):
            self.ax.axhline(clean[0], color=theme.MUTED, linestyle=(0, (4, 4)), linewidth=1)
        self.ax.set_xticks(positions, labels)
        self.ax.yaxis.set_major_formatter(_THOUSANDS)
        self.ax.set_xlim(-0.5, max(len(labels) - 0.5, 0.5))
        self.draw_idle()
