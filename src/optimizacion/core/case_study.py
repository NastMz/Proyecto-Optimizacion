"""The course case study: daily production plan of the spice company "Sazón Llano".

For every product ``i`` the company decides how many units ``x_i`` to sell per
day in order to maximise profit:

    max  sum(profit_i * x_i)
    s.a. raw_material_use_i * x_i <= raw_material_stock_i   (materia prima, g)
         unit_cost_i * x_i       <= budget_i               (presupuesto, $)
         x_i                     >= min_demand_i           (demanda, unidades)
         x_i >= 0
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .model import Constraint, Goal, LinearProgram, Sense


@dataclass(frozen=True)
class Product:
    name: str
    profit: float
    raw_material_use: float
    raw_material_stock: float
    unit_cost: float
    budget: float
    min_demand: float


class Parameter(Enum):
    """Parameters the analysis page can change, with their Spanish labels."""

    PROFIT = ("profit", "Utilidad por unidad", True)
    RAW_MATERIAL = ("raw_material_stock", "Materia prima disponible", False)
    BUDGET = ("budget", "Presupuesto", True)
    DEMAND = ("min_demand", "Demanda mínima", False)

    def __init__(self, field_name: str, label: str, is_money: bool) -> None:
        self.field_name = field_name
        self.label = label
        self.is_money = is_money


CONSTRAINT_GROUPS = (Parameter.RAW_MATERIAL, Parameter.BUDGET, Parameter.DEMAND)
GROUP_LABELS = {
    Parameter.RAW_MATERIAL: "Materia prima",
    Parameter.BUDGET: "Presupuesto",
    Parameter.DEMAND: "Demanda",
}


@dataclass(frozen=True)
class CaseStudy:
    company: str
    products: tuple[Product, ...]

    def value(self, parameter: Parameter, product: int) -> float:
        return float(getattr(self.products[product], parameter.field_name))

    def with_value(self, parameter: Parameter, product: int, value: float) -> CaseStudy:
        products = list(self.products)
        products[product] = replace(products[product], **{parameter.field_name: float(value)})
        return replace(self, products=tuple(products))

    def constraint_index(self, parameter: Parameter, product: int) -> int:
        """Position of the constraint controlled by ``parameter`` in :meth:`to_problem`."""
        return CONSTRAINT_GROUPS.index(parameter) * len(self.products) + product

    def to_problem(self) -> LinearProgram:
        n = len(self.products)

        def unit(i: int, value: float) -> tuple[float, ...]:
            return tuple(value if k == i else 0.0 for k in range(n))

        constraints = []
        for i, p in enumerate(self.products):
            constraints.append(Constraint(unit(i, p.raw_material_use), Sense.LE, p.raw_material_stock,
                                          f"Materia prima · {p.name}"))
        for i, p in enumerate(self.products):
            constraints.append(Constraint(unit(i, p.unit_cost), Sense.LE, p.budget, f"Presupuesto · {p.name}"))
        for i, p in enumerate(self.products):
            constraints.append(Constraint(unit(i, 1.0), Sense.GE, p.min_demand, f"Demanda · {p.name}"))
        return LinearProgram(
            objective=tuple(p.profit for p in self.products),
            constraints=tuple(constraints),
            goal=Goal.MAX,
            variable_names=tuple(f"X{i + 1}" for i in range(n)),
        )


SAZON_LLANO = CaseStudy(
    company="Sazón Llano",
    products=(
        Product("Canela", profit=1918, raw_material_use=12, raw_material_stock=19051,
                unit_cost=1421, budget=750000, min_demand=10),
        Product("Clavo", profit=1158, raw_material_use=10, raw_material_stock=22680,
                unit_cost=858, budget=325000, min_demand=10),
        Product("Uva pasa", profit=896, raw_material_use=50, raw_material_stock=10000,
                unit_cost=664, budget=325000, min_demand=4),
        Product("Ajo sal", profit=1868, raw_material_use=60, raw_material_stock=3780,
                unit_cost=1384, budget=600000, min_demand=6),
    ),
)
