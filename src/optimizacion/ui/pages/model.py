"""Model page: mathematical formulation and editable case parameters."""

from __future__ import annotations

from dataclasses import replace
from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QHeaderView, QPushButton, QTableWidget

from ...core.case_study import SAZON_LLANO, CaseStudy
from ...core.formatting import number
from .. import theme
from ..widgets import Card, icon, label
from .base import Page

COLUMNS = (
    ("profit", "Utilidad ($/u)"),
    ("raw_material_use", "Consumo MP (g/u)"),
    ("raw_material_stock", "MP disponible (g)"),
    ("unit_cost", "Costo ($/u)"),
    ("budget", "Presupuesto ($)"),
    ("min_demand", "Demanda mín. (u)"),
)


def formulation_html(case: CaseStudy) -> str:
    """Render the linear program of ``case`` as rich text."""
    mono = ", ".join(f"'{f}'" for f in theme.MONO_FAMILIES)
    n = len(case.products)

    def term(coefficient: float, i: int) -> str:
        return f"{number(coefficient, 0 if float(coefficient).is_integer() else 2)}&thinsp;X{i + 1}"

    objective = " + ".join(term(p.profit, i) for i, p in enumerate(case.products))
    groups = [
        ("Materia prima", [f"{term(p.raw_material_use, i)} ≤ {number(p.raw_material_stock, 0)}"
                           for i, p in enumerate(case.products)]),
        ("Presupuesto", [f"{term(p.unit_cost, i)} ≤ {number(p.budget, 0)}" for i, p in enumerate(case.products)]),
        ("Demanda", [f"X{i + 1} ≥ {number(p.min_demand, 0)}" for i, p in enumerate(case.products)]),
    ]
    rows = [f"<tr><td style='color:{theme.PAPRIKA};font-weight:bold;padding-right:18px'>max&nbsp;Z</td>"
            f"<td colspan='{n}'>= {objective}</td></tr>"]
    for title, items in groups:
        cells = "".join(f"<td style='padding:3px 22px 3px 0'>{item}</td>" for item in items)
        rows.append(f"<tr><td style='color:{theme.MUTED};padding-right:18px'>{title}</td>{cells}</tr>")
    rows.append(f"<tr><td style='color:{theme.MUTED}'>Signo</td><td colspan='{n}'>"
                + ", ".join(f"X{i + 1}" for i in range(n)) + " ≥ 0</td></tr>")
    legend = " · ".join(f"<b>X{i + 1}</b> = unidades de {escape(p.name.lower())} vendidas al día"
                        for i, p in enumerate(case.products))
    return (f"<table style=\"font-family:{mono};font-size:10.5pt\" cellspacing='0'>{''.join(rows)}</table>"
            f"<p style='color:{theme.MUTED}'>{legend}</p>")


class ModelPage(Page):
    eyebrow = "Modelo"
    title = "Formulación del problema"
    subtitle = ("Programa lineal del caso Sazón Llano. Cambie los parámetros y vuelva a resolver: "
                "todas las vistas se actualizan.")

    def __init__(self, state) -> None:
        super().__init__(state)
        formulation = Card()
        formulation.body.addWidget(label("Modelo matemático", "sectionTitle"))
        self.formulation = label(wrap=True)
        formulation.body.addWidget(self.formulation)
        self.layout_.addWidget(formulation)

        parameters = Card()
        parameters.body.addWidget(label("Parámetros por producto", "sectionTitle"))
        self.table = QTableWidget(len(SAZON_LLANO.products), len(COLUMNS))
        self.table.setHorizontalHeaderLabels([title for _, title in COLUMNS])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setMinimumHeight(44 * len(SAZON_LLANO.products) + 40)
        self.spins: list[list[QDoubleSpinBox]] = []
        for r in range(self.table.rowCount()):
            spins = []
            for c in range(len(COLUMNS)):
                spin = QDoubleSpinBox()
                spin.setRange(0, 1e9)
                spin.setDecimals(2)
                spin.setGroupSeparatorShown(True)
                spin.setFont(theme.mono_font(10))
                spin.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setCellWidget(r, c, spin)
                spins.append(spin)
            self.spins.append(spins)
        parameters.body.addWidget(self.table)

        buttons = QHBoxLayout()
        self.solve_button = QPushButton(icon("play", "#FFF6EA"), "  Resolver modelo")
        self.solve_button.setObjectName("primary")
        self.reset_button = QPushButton(icon("arrow-counter-clockwise"), "  Restaurar datos del caso")
        self.message = label("", "cardHint", wrap=True)
        buttons.addWidget(self.solve_button)
        buttons.addWidget(self.reset_button)
        buttons.addWidget(self.message, 1)
        parameters.body.addLayout(buttons)
        self.layout_.addWidget(parameters)
        self.layout_.addStretch(1)

        self.solve_button.clicked.connect(self.solve)
        self.reset_button.clicked.connect(lambda: self.state.resolve(SAZON_LLANO))
        self.refresh()

    def _set_names(self, case: CaseStudy) -> None:
        self.table.setVerticalHeaderLabels([p.name for p in case.products])

    def refresh(self) -> None:
        case = self.state.base.case
        self._set_names(case)
        for spins, product in zip(self.spins, case.products):
            for spin, (field, _) in zip(spins, COLUMNS):
                spin.setValue(getattr(product, field))
        self.formulation.setText(formulation_html(case))
        status = self.state.base.result.status.value
        self.message.setText({"optimal": "", "infeasible": "Con estos datos el modelo es infactible.",
                              "unbounded": "Con estos datos el modelo no está acotado."}[status])

    def edited_case(self) -> CaseStudy:
        case = self.state.base.case
        products = tuple(
            replace(product, **{field: spin.value() for spin, (field, _) in zip(spins, COLUMNS)})
            for spins, product in zip(self.spins, case.products)
        )
        return replace(case, products=products)

    def solve(self) -> None:
        self.state.resolve(self.edited_case())
