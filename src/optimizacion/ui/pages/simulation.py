"""Simulation page: what-if analysis on one parameter at a time."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
)

from ...core.case_study import Parameter
from ...core.formatting import interval, money, number
from ...core.scenarios import curve_window, parametric_curve, valid_range
from .. import theme
from ..charts import HistoryChart, ParametricChart
from ..widgets import Card, icon, label
from .base import Page
from .sensitivity import _item

PARAMETERS = list(Parameter)
SHORT_LABELS = {
    Parameter.PROFIT: "Utilidad",
    Parameter.RAW_MATERIAL: "Materia prima",
    Parameter.BUDGET: "Presupuesto",
    Parameter.DEMAND: "Demanda",
}


class SimulationPage(Page):
    eyebrow = "Simulación"
    title = "¿Qué pasa si…?"
    subtitle = ("Cambie un parámetro del plan actual, vuelva a resolver el modelo y compare la nueva "
                "solución con la original.")

    def __init__(self, state) -> None:
        super().__init__(state)
        top = QHBoxLayout()
        top.setSpacing(14)

        controls = Card(spacing=10)
        controls.setFixedWidth(340)
        controls.body.addWidget(label("Parámetro a modificar", "sectionTitle"))
        form = QFormLayout()
        form.setVerticalSpacing(10)
        self.parameter = QComboBox()
        self.parameter.addItems([p.label for p in PARAMETERS])
        self.product = QComboBox()
        self.current = label("", "cardValue")
        self.range = label("", "cardHint", wrap=True)
        self.value = QDoubleSpinBox()
        self.value.setRange(0, 1e9)
        self.value.setDecimals(2)
        self.value.setGroupSeparatorShown(True)
        self.value.setFont(theme.mono_font(10))
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.addRow("Elemento", self.parameter)
        form.addRow("Producto", self.product)
        controls.body.addLayout(form)
        controls.body.addWidget(label("VALOR ACTUAL", "cardLabel"))
        controls.body.addWidget(self.current)
        controls.body.addWidget(self.range)
        controls.body.addWidget(label("NUEVO VALOR", "cardLabel"))
        controls.body.addWidget(self.value)
        self.status = label("", "ok", wrap=True)
        controls.body.addWidget(self.status)
        self.simulate_button = QPushButton(icon("flask", "#FFF6EA"), "  Simular")
        self.simulate_button.setObjectName("primary")
        controls.body.addWidget(self.simulate_button)
        controls.body.addStretch(1)
        top.addWidget(controls)

        curve = Card()
        self.curve = ParametricChart(height=3.6)
        curve.body.addWidget(self.curve)
        top.addWidget(curve, 1)
        self.layout_.addLayout(top)

        comparison = Card()
        comparison.body.addWidget(label("Comparación de escenarios", "sectionTitle"))
        self.table = QTableWidget(0, 0)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        comparison.body.addWidget(self.table)
        self.layout_.addWidget(comparison)

        history = Card()
        self.history_chart = HistoryChart(height=2.6)
        history.body.addWidget(self.history_chart)
        self.layout_.addWidget(history)

        self.parameter.currentIndexChanged.connect(self.update_selection)
        self.product.currentIndexChanged.connect(self.update_selection)
        self.value.valueChanged.connect(self.update_status)
        self.simulate_button.clicked.connect(self.run)
        self.state.history_changed.connect(self.update_history)
        self.refresh()

    @property
    def selection(self) -> tuple[Parameter, int]:
        return PARAMETERS[self.parameter.currentIndex()], max(self.product.currentIndex(), 0)

    def refresh(self) -> None:
        names = [p.name for p in self.state.base.case.products]
        index = max(self.product.currentIndex(), 0)
        self.product.blockSignals(True)
        self.product.clear()
        self.product.addItems(names)
        self.product.setCurrentIndex(min(index, len(names) - 1))
        self.product.blockSignals(False)
        self.update_selection()
        self.update_history()

    def _format(self, parameter: Parameter, value: float) -> str:
        return money(value) if parameter.is_money else number(value)

    def update_selection(self) -> None:
        parameter, product = self.selection
        base = self.state.base
        current = base.case.value(parameter, product)
        self.current.setText(self._format(parameter, current))
        bounds = valid_range(base, parameter, product)
        self.range.setText(f"La base óptima no cambia en {interval(bounds)}" if bounds else
                           "El modelo actual no tiene óptimo.")
        self.value.blockSignals(True)
        self.value.setValue(current)
        self.value.blockSignals(False)
        self.update_status()
        self.update_curve()

    def update_status(self) -> None:
        parameter, product = self.selection
        bounds = valid_range(self.state.base, parameter, product)
        value = self.value.value()
        if bounds is None or bounds[0] - 1e-9 <= value <= bounds[1] + 1e-9:
            self.status.setObjectName("ok")
            self.status.setText("Dentro del rango: la utilidad cambia según el precio sombra.")
        else:
            self.status.setObjectName("warning")
            self.status.setText("Fuera del rango: la base óptima cambia y el plan se recalcula.")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def update_curve(self) -> None:
        parameter, product = self.selection
        base = self.state.base
        current = base.case.value(parameter, product)
        bounds = valid_range(base, parameter, product)
        start, stop = curve_window(current, bounds)
        simulated = [
            (s.case.value(parameter, product), s.objective)
            for s in self.state.history
            if s.result.is_optimal and s.case.value(parameter, product) != current
            and start <= s.case.value(parameter, product) <= stop
        ]
        xs, ys = parametric_curve(base.case, parameter, product, start, stop, points=81)
        label_text = f"{parameter.label} · {base.case.products[product].name}"
        self.curve.plot(xs, ys, current, base.objective, bounds, label_text, simulated)

    def run(self) -> None:
        parameter, product = self.selection
        self.state.simulate(parameter, product, self.value.value())
        self.update_curve()

    def update_history(self) -> None:
        scenarios = self.state.scenarios()
        base = self.state.base
        self.history_chart.plot([s.label.replace("Simulación ", "S") for s in scenarios],
                                [s.objective if s.result.is_optimal else math.nan for s in scenarios])
        names = [p.name for p in base.case.products]
        headers = ["Escenario", "Cambio", "Utilidad", "Δ vs actual", *[f"{n} (u)" for n in names]]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(scenarios))
        for r, scenario in enumerate(scenarios):
            change = _describe_change(base.case, scenario.case)
            optimal = scenario.result.is_optimal
            delta = scenario.objective - base.objective if optimal and base.result.is_optimal else math.nan
            delta_color = theme.CARDAMOM if delta > 1e-9 else theme.PAPRIKA if delta < -1e-9 else theme.MUTED
            cells = [
                _item(scenario.label, numeric=False, bold=True),
                _item(change, numeric=False, color=theme.MUTED),
                _item(money(scenario.objective) if optimal else "Infactible" if
                      scenario.result.status.value == "infeasible" else "No acotado"),
                _item(("+" if delta > 1e-9 else "") + money(delta) if math.isfinite(delta) else "—",
                      color=delta_color),
                *[_item(number(v, 1) if optimal else "—") for v in scenario.result.values],
            ]
            for c, cell in enumerate(cells):
                self.table.setItem(r, c, cell)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setMinimumHeight(32 * max(len(scenarios), 3) + 40)
        self.table.scrollToBottom()


def _describe_change(base, case) -> str:
    for parameter in Parameter:
        for i, product in enumerate(case.products):
            before, after = base.value(parameter, i), case.value(parameter, i)
            if before != after:
                return f"{SHORT_LABELS[parameter]} {product.name}: {number(before, 0)} → {number(after, 0)}"
    return "Plan actual"

