"""What-if simulations on the case study."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .case_study import CaseStudy, Parameter
from .sensitivity import SensitivityReport, analyze
from .simplex import SimplexResult, solve


@dataclass(frozen=True)
class Scenario:
    label: str
    case: CaseStudy
    result: SimplexResult
    sensitivity: SensitivityReport | None

    @property
    def objective(self) -> float:
        return self.result.objective


def evaluate(case: CaseStudy, label: str = "Actual") -> Scenario:
    """Solve ``case`` and, when optimal, attach its sensitivity report."""
    result = solve(case.to_problem())
    sensitivity = analyze(result) if result.is_optimal else None
    return Scenario(label, case, result, sensitivity)


def valid_range(scenario: Scenario, parameter: Parameter, product: int) -> tuple[float, float] | None:
    """Interval of ``parameter`` where the current optimal basis stays optimal."""
    if scenario.sensitivity is None:
        return None
    if parameter is Parameter.PROFIT:
        return scenario.sensitivity.variables[product].objective_range
    index = scenario.case.constraint_index(parameter, product)
    return scenario.sensitivity.constraints[index].rhs_range


def simulate(base: Scenario, parameter: Parameter, product: int, value: float, label: str) -> Scenario:
    return evaluate(base.case.with_value(parameter, product, value), label)


def parametric_curve(
    case: CaseStudy, parameter: Parameter, product: int, start: float, stop: float, points: int = 41
) -> tuple[np.ndarray, np.ndarray]:
    """Optimal objective as a function of one parameter (NaN where infeasible)."""
    xs = np.linspace(start, stop, points)
    ys = np.empty_like(xs)
    for k, value in enumerate(xs):
        result = solve(case.with_value(parameter, product, float(value)).to_problem())
        ys[k] = result.objective if result.is_optimal else math.nan
    return xs, ys


def curve_window(current: float, interval: tuple[float, float] | None) -> tuple[float, float]:
    """A plotting window around ``current`` that shows the finite ends of ``interval``."""
    low, high = interval if interval else (-math.inf, math.inf)
    span = max(abs(current), 1.0)
    left = low if math.isfinite(low) else current - span
    right = high if math.isfinite(high) else current + span
    width = max(right - left, span * 0.2)
    return max(0.0, left - 0.25 * width), right + 0.25 * width
