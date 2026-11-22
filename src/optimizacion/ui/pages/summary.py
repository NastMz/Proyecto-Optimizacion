"""Summary page: optimal plan, key figures and charts."""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout

from ...core.formatting import money, number
from .. import theme
from ..charts import ProductionChart, ShareChart
from ..widgets import Card, StatCard, Swatch, label
from .base import Page

_STATUS_TEXT = {
    "infeasible": "El modelo no tiene solución factible con estos parámetros.",
    "unbounded": "La utilidad no está acotada con estos parámetros.",
}


class ProductCard(Card):
    def __init__(self, index: int) -> None:
        super().__init__(spacing=4)
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(Swatch(theme.product_color(index)))
        text = QVBoxLayout()
        text.setSpacing(2)
        self.name = label("", "productName")
        self.units = label("", "cardValue")
        self.detail = label("", "cardHint", wrap=True)
        text.addWidget(self.name)
        text.addWidget(self.units)
        text.addWidget(self.detail)
        layout.addLayout(text, 1)
        self.body.addLayout(layout)

    def set(self, name: str, units: float, profit: float) -> None:
        self.name.setText(name)
        self.units.setText(f"{number(units, 1)} <span style='font-size:10pt;color:{theme.MUTED}'>u/día</span>")
        self.detail.setText(f"Utilidad unitaria {money(profit, 0)}<br>Aporta {money(units * profit, 0)} al día")


class SummaryPage(Page):
    eyebrow = "Resumen"
    title = "Plan óptimo de producción"
    subtitle = "Cuánto vender de cada producto al día para maximizar la utilidad de la empresa."

    def __init__(self, state) -> None:
        super().__init__(state)
        top = QHBoxLayout()
        top.setSpacing(14)
        self.hero = Card(object_name="heroCard", spacing=4)
        self.hero.body.setContentsMargins(24, 20, 24, 20)
        self.hero.body.addWidget(label("UTILIDAD MÁXIMA DIARIA", "cardLabel"))
        self.hero_value = label("", "heroValue")
        self.hero_hint = label("", "cardHint", wrap=True)
        self.hero.body.addWidget(self.hero_value)
        self.hero.body.addWidget(self.hero_hint)
        top.addWidget(self.hero, 2)
        self.units = StatCard("Unidades por día")
        self.binding = StatCard("Restricciones activas")
        self.best = StatCard("Recurso más valioso")
        for card in (self.units, self.binding, self.best):
            top.addWidget(card, 1)
        self.layout_.addLayout(top)

        self.products_grid = QGridLayout()
        self.products_grid.setSpacing(14)
        self.product_cards: list[ProductCard] = []
        self.layout_.addLayout(self.products_grid)

        charts = QHBoxLayout()
        charts.setSpacing(14)
        self.production_chart = ProductionChart()
        self.share_chart = ShareChart()
        for chart, stretch in ((self.production_chart, 3), (self.share_chart, 2)):
            card = Card()
            card.body.addWidget(chart)
            charts.addWidget(card, stretch)
        self.layout_.addLayout(charts)
        self.layout_.addStretch(1)
        self.refresh()

    def refresh(self) -> None:
        scenario = self.state.base
        case, result = scenario.case, scenario.result
        names = [p.name for p in case.products]
        while len(self.product_cards) < len(names):
            card = ProductCard(len(self.product_cards))
            self.products_grid.addWidget(card, 0, len(self.product_cards))
            self.product_cards.append(card)

        iterations = sum(1 for t in result.tableaus if not t.is_final)
        if not result.is_optimal:
            self.hero_value.setText("Sin solución")
            self.hero_hint.setText(_STATUS_TEXT[result.status.value])
            for card in (self.units, self.binding, self.best):
                card.set("—", "")
            for card, product in zip(self.product_cards, case.products):
                card.set(product.name, 0, product.profit)
            self.production_chart.plot(names, [0] * len(names))
            self.share_chart.plot(names, [1] * len(names), 0)
            return

        self.hero_value.setText(money(result.objective))
        phases = "dos fases" if result.phase(1) else "una fase"
        self.hero_hint.setText(f"Simplex de {phases} · {iterations} pivoteos · {len(result.tableaus)} tableros")
        self.units.set(number(sum(result.values), 1), "Suma de los cuatro productos")
        constraints = scenario.sensitivity.constraints
        active = sum(1 for c in constraints if c.is_binding)
        self.binding.set(f"{active} de {len(constraints)}", "Recursos agotados en el plan óptimo")
        best = max(constraints, key=lambda c: c.shadow_price)
        if best.shadow_price > 0:
            self.best.set(money(best.shadow_price), f"{best.name}: utilidad extra por unidad adicional")
        else:
            self.best.set("—", "Ningún recurso limita la utilidad")
        contributions = [p.profit * x for p, x in zip(case.products, result.values)]
        for card, product, value in zip(self.product_cards, case.products, result.values):
            card.set(product.name, value, product.profit)
        self.production_chart.plot(names, list(result.values))
        self.share_chart.plot(names, contributions, result.objective)
