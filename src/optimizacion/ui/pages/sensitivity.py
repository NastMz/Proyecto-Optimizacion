"""Sensitivity page: shadow prices, slacks and optimality ranges."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QTabWidget

from ...core.formatting import interval, money, number
from .. import theme
from ..widgets import Card, label
from .base import Page

CONSTRAINT_HEADERS = ("Restricción", "Tipo", "Lado derecho", "Uso", "Holgura", "Precio sombra",
                      "Rango del lado derecho", "Estado")
VARIABLE_HEADERS = ("Variable", "Producto", "Valor óptimo", "Utilidad unitaria", "Costo reducido",
                    "Rango de optimalidad")


def _table(headers: tuple[str, ...]) -> QTableWidget:
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(34)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
    return table


def _item(text: str, numeric: bool = True, color: str | None = None, bold: bool = False) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setTextAlignment(
        (Qt.AlignmentFlag.AlignRight if numeric else Qt.AlignmentFlag.AlignLeft) | Qt.AlignmentFlag.AlignVCenter
    )
    if numeric:
        item.setFont(theme.mono_font(10))
    if color:
        item.setForeground(theme.qcolor(color))
    if bold:
        font = item.font()
        font.setBold(True)
        item.setFont(font)
    return item


class SensitivityPage(Page):
    eyebrow = "Sensibilidad"
    title = "Análisis de sensibilidad"
    subtitle = ("Precios sombra, holguras y rangos en los que la solución actual sigue siendo óptima, "
                "calculados a partir de la base óptima (B⁻¹) del último tablero.")

    def __init__(self, state) -> None:
        super().__init__(state)
        card = Card()
        self.tabs = QTabWidget()
        self.constraints = _table(CONSTRAINT_HEADERS)
        self.variables = _table(VARIABLE_HEADERS)
        self.tabs.addTab(self.constraints, "Restricciones")
        self.tabs.addTab(self.variables, "Variables")
        card.body.addWidget(self.tabs)
        self.layout_.addWidget(card)
        notes = Card()
        notes.body.addWidget(label("Cómo leer la tabla", "sectionTitle"))
        notes.body.addWidget(label(
            "<b>Precio sombra:</b> cambio de la utilidad diaria por cada unidad adicional del lado derecho. "
            "Solo es válido dentro del <b>rango del lado derecho</b>; fuera de él cambia la base óptima.<br>"
            "<b>Rango de optimalidad:</b> valores de la utilidad unitaria para los que el plan de producción "
            "no cambia (la utilidad total sí cambia).<br>"
            "<b>Costo reducido:</b> cuánto empeora el objetivo por cada unidad de una variable no básica.",
            "cardHint", wrap=True))
        self.layout_.addWidget(notes)
        self.layout_.addStretch(1)
        self.refresh()

    def refresh(self) -> None:
        scenario = self.state.base
        report = scenario.sensitivity
        self.constraints.setRowCount(0 if report is None else len(report.constraints))
        self.variables.setRowCount(0 if report is None else len(report.variables))
        if report is None:
            self.header.subtitle.setText("No hay análisis de sensibilidad: el modelo actual no tiene óptimo.")
            return
        self.header.subtitle.setText(self.subtitle)
        for r, c in enumerate(report.constraints):
            price_color = theme.PAPRIKA if abs(c.shadow_price) > 0 else theme.MUTED
            cells = (
                _item(c.name, numeric=False, bold=True),
                _item({"<=": "≤", ">=": "≥"}.get(c.sense.value, "=")),
                _item(number(c.rhs)),
                _item(number(c.activity)),
                _item(number(c.slack)),
                _item(money(c.shadow_price), color=price_color, bold=abs(c.shadow_price) > 0),
                _item(interval(c.rhs_range)),
                _item("Activa" if c.is_binding else "Con holgura", numeric=False,
                      color=theme.PAPRIKA_DARK if c.is_binding else theme.CARDAMOM, bold=c.is_binding),
            )
            for col, cell in enumerate(cells):
                self.constraints.setItem(r, col, cell)
        for r, (v, product) in enumerate(zip(report.variables, scenario.case.products)):
            cells = (
                _item(v.name, numeric=False, bold=True),
                _item(product.name, numeric=False),
                _item(number(v.value)),
                _item(money(v.cost)),
                _item(money(v.reduced_cost)),
                _item(interval(v.objective_range)),
            )
            for col, cell in enumerate(cells):
                self.variables.setItem(r, col, cell)
        for table in (self.constraints, self.variables):
            header = table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            for column in (0, table.columnCount() - 2 if table is self.constraints else table.columnCount() - 1):
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
            table.setFixedHeight(34 * table.rowCount() + 40)
