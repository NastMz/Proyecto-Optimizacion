"""Simplex page: step through every tableau of the two-phase method."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSlider,
    QTableView,
)

from ...core.formatting import number
from ...core.simplex import Tableau
from .. import theme
from ..tableau_model import TableauModel, format_value
from ..widgets import Card, Pill, icon, label
from .base import Page


def explain(tableau: Tableau, as_fraction: bool = False) -> str:
    """Plain-language description of what happens in ``tableau``."""
    names = tableau.column_names
    rule = "más negativo" if tableau.minimize else "más positivo"
    goal = "minimizar la suma de artificiales" if tableau.phase == 1 else (
        "minimizar Z" if tableau.minimize else "maximizar Z")
    if tableau.entering is None:
        if tableau.phase == 1:
            return (f"<b>Fin de la fase 1.</b> Z = {format_value(tableau.z, as_fraction)}: las variables "
                    "artificiales salen del problema y la fase 2 parte de esta base factible.")
        return (f"<b>Solución óptima.</b> Ningún Cj − Zj mejora el objetivo; "
                f"Z = <b>{format_value(tableau.z, as_fraction)}</b>.")
    entering = names[tableau.entering]
    reduced = format_value(tableau.reduced_costs[tableau.entering], as_fraction)
    if tableau.leaving is None:
        return (f"Entra <b>{entering}</b> (Cj − Zj = {reduced}), pero ninguna fila tiene coeficiente positivo: "
                "<b>el problema no está acotado</b>.")
    leaving = tableau.basis[tableau.leaving]
    ratio = format_value(tableau.ratios[tableau.leaving], as_fraction)
    pivot = format_value(tableau.rows[tableau.leaving][tableau.entering], as_fraction)
    return (f"Objetivo: {goal}. Entra <b>{entering}</b> (Cj − Zj {rule}: {reduced}) y sale "
            f"<b>{leaving}</b> (razón mínima bi / a = {ratio}). Elemento pivote: <b>{pivot}</b>.")


class SimplexPage(Page):
    eyebrow = "Simplex"
    title = "Método simplex de dos fases"
    subtitle = ("Cada tablero muestra una iteración antes de pivotear: la columna que entra, la fila que "
                "sale y el elemento pivote.")

    def __init__(self, state) -> None:
        super().__init__(state)
        controls = QHBoxLayout()
        controls.setSpacing(12)
        self.phase = Pill()
        self.counter = label("", "sectionTitle")
        self.previous = QPushButton(icon("caret-left"), "")
        self.next = QPushButton(icon("caret-right"), "")
        for button, tip in ((self.previous, "Tablero anterior"), (self.next, "Tablero siguiente")):
            button.setToolTip(tip)
            button.setFixedWidth(44)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.fractions = QCheckBox("Mostrar fracciones")
        controls.addWidget(self.phase)
        controls.addWidget(self.counter)
        controls.addSpacing(8)
        controls.addWidget(self.previous)
        controls.addWidget(self.slider, 1)
        controls.addWidget(self.next)
        controls.addSpacing(8)
        controls.addWidget(self.fractions)
        self.layout_.addLayout(controls)

        self.explanation = label("", "explanation", wrap=True)
        self.layout_.addWidget(self.explanation)

        card = Card()
        self.model = TableauModel()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.verticalHeader().setVisible(False)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.view.verticalHeader().setDefaultSectionSize(30)
        self.view.setShowGrid(True)
        card.body.addWidget(self.view)
        legend = QHBoxLayout()
        legend.setSpacing(8)
        legend.addWidget(Pill("Columna que entra", theme.SAFFRON_TINT, theme.INK))
        legend.addWidget(Pill("Fila que sale", theme.PAPRIKA_TINT, theme.PAPRIKA_DARK))
        legend.addWidget(Pill("Elemento pivote", theme.PAPRIKA, "#FFF6EA"))
        legend.addStretch(1)
        self.basis_values = label("", "cardHint", wrap=True)
        card.body.addLayout(legend)
        card.body.addWidget(self.basis_values)
        self.layout_.addWidget(card)
        self.layout_.addStretch(1)

        self.previous.clicked.connect(lambda: self.slider.setValue(self.slider.value() - 1))
        self.next.clicked.connect(lambda: self.slider.setValue(self.slider.value() + 1))
        self.slider.valueChanged.connect(self.show_tableau)
        self.fractions.toggled.connect(lambda _: self.show_tableau(self.slider.value()))
        self.refresh()

    @property
    def tableaus(self) -> tuple[Tableau, ...]:
        return self.state.base.result.tableaus

    def refresh(self) -> None:
        self.slider.blockSignals(True)
        self.slider.setRange(0, max(len(self.tableaus) - 1, 0))
        self.slider.setValue(0)
        self.slider.blockSignals(False)
        self.show_tableau(0)

    def _fit_columns(self) -> None:
        """Size columns to their contents and spread any spare width evenly."""
        self.view.resizeColumnsToContents()
        header = self.view.horizontalHeader()
        count = header.count()
        spare = self.view.viewport().width() - sum(header.sectionSize(i) for i in range(count))
        if count and spare > 0:
            for i in range(count):
                header.resizeSection(i, header.sectionSize(i) + spare // count)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._fit_columns()

    def show_tableau(self, index: int) -> None:
        if not self.tableaus:
            return
        tableau = self.tableaus[index]
        as_fraction = self.fractions.isChecked()
        self.model.set_tableau(tableau, as_fraction)
        self.view.setFixedHeight(30 * (len(tableau.basis) + 3) + 34 + 14)
        self._fit_columns()
        in_phase = [t for t in self.tableaus if t.phase == tableau.phase]
        self.counter.setText(f"Iteración {tableau.iteration} de {len(in_phase) - 1}")
        if tableau.phase == 1:
            self.phase.setText("FASE 1")
            self.phase.set_colors(theme.SAFFRON_TINT, theme.INK)
        else:
            self.phase.setText("FASE 2")
            self.phase.set_colors(theme.CARDAMOM_TINT, "#3F5A3C")
        self.previous.setEnabled(index > 0)
        self.next.setEnabled(index < len(self.tableaus) - 1)
        self.explanation.setText(explain(tableau, as_fraction))
        values = ", ".join(f"{name} = {number(value)}" for name, value in zip(tableau.basis, tableau.rhs))
        self.basis_values.setText(f"Solución básica de este tablero: {values}; las demás variables valen 0.")
