"""Application state shared by every page."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ..core.case_study import SAZON_LLANO, CaseStudy, Parameter
from ..core.scenarios import Scenario, evaluate, simulate


class AppState(QObject):
    base_changed = Signal()
    history_changed = Signal()

    def __init__(self, case: CaseStudy = SAZON_LLANO) -> None:
        super().__init__()
        self.base: Scenario = evaluate(case)
        self.history: list[Scenario] = []

    def resolve(self, case: CaseStudy) -> None:
        """Solve a new base case; previous simulations no longer apply and are cleared."""
        self.base = evaluate(case)
        self.history = []
        self.base_changed.emit()
        self.history_changed.emit()

    def simulate(self, parameter: Parameter, product: int, value: float) -> Scenario:
        scenario = simulate(self.base, parameter, product, value, f"Simulación {len(self.history) + 1}")
        self.history.append(scenario)
        self.history_changed.emit()
        return scenario

    def scenarios(self) -> list[Scenario]:
        return [self.base, *self.history]
