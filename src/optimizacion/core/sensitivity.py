"""Post-optimal sensitivity analysis from the optimal simplex basis.

Every quantity is reported in the terms of the original problem:

* ``shadow_price``: change of the optimal objective per unit increase of the
  constraint's right-hand side (the dual price).
* ``rhs_range``: interval of right-hand-side values where the current basis
  stays optimal, so the shadow price remains valid.
* ``objective_range``: interval of a cost coefficient where the current
  solution stays optimal.
* ``reduced_cost``: how much the objective would worsen per unit of a
  non-basic variable forced into the solution (zero for basic variables).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .model import Goal, Sense
from .simplex import SimplexResult

INF = math.inf
_TOL = 1e-9


@dataclass(frozen=True)
class VariableSensitivity:
    name: str
    value: float
    cost: float
    reduced_cost: float
    is_basic: bool
    objective_range: tuple[float, float]


@dataclass(frozen=True)
class ConstraintSensitivity:
    name: str
    sense: Sense
    rhs: float
    activity: float
    slack: float
    shadow_price: float
    rhs_range: tuple[float, float] | None

    @property
    def is_binding(self) -> bool:
        return abs(self.slack) <= 1e-7 * max(1.0, abs(self.rhs))


@dataclass(frozen=True)
class SensitivityReport:
    variables: tuple[VariableSensitivity, ...]
    constraints: tuple[ConstraintSensitivity, ...]


def analyze(result: SimplexResult) -> SensitivityReport:
    """Build the sensitivity report of an optimal :class:`SimplexResult`."""
    if not result.is_optimal:
        raise ValueError("Sensitivity analysis needs an optimal solution.")

    problem = result.problem
    standard = result.standard
    sign = -1.0 if problem.goal is Goal.MIN else 1.0
    cost = sign * standard.cost  # always maximise internally
    rows = list(result.basis_rows)
    a = standard.matrix[rows, :]
    b = standard.rhs[rows]
    basis = list(result.basis)
    basis_inverse = np.linalg.inv(a[:, basis])
    x_basic = basis_inverse @ b
    duals = cost[basis] @ basis_inverse
    reduced = cost - duals @ a
    alpha = basis_inverse @ a
    nonbasic = [j for j in range(a.shape[1]) if j not in basis]

    variables = []
    for j in range(standard.num_variables):
        low, high = _cost_range(j, basis, nonbasic, reduced, alpha, cost[j])
        if sign < 0:
            low, high = -high, -low
        variables.append(
            VariableSensitivity(
                name=standard.column_names[j],
                value=result.values[j],
                cost=float(standard.cost[j]),
                reduced_cost=0.0 if j in basis else float(sign * reduced[j]),
                is_basic=j in basis,
                objective_range=(low, high),
            )
        )

    x = np.array(result.values)
    constraints = []
    for i, constraint in enumerate(problem.constraints):
        activity = float(np.dot(constraint.coefficients, x))
        if constraint.sense is Sense.LE:
            slack = constraint.rhs - activity
        elif constraint.sense is Sense.GE:
            slack = activity - constraint.rhs
        else:
            slack = 0.0
        flip = standard.flips[i]
        if i in rows:
            position = rows.index(i)
            shadow = float(sign * flip * duals[position])
            low, high = _rhs_delta(basis_inverse[:, position], x_basic)
            if flip < 0:
                low, high = -high, -low
            rhs_range: tuple[float, float] | None = (constraint.rhs + low, constraint.rhs + high)
        else:  # redundant equality removed during phase 1
            shadow, rhs_range = 0.0, None
        constraints.append(
            ConstraintSensitivity(
                name=problem.constraint_names()[i],
                sense=constraint.sense,
                rhs=float(constraint.rhs),
                activity=activity,
                slack=float(slack),
                shadow_price=_clean(shadow),
                rhs_range=rhs_range,
            )
        )
    return SensitivityReport(tuple(variables), tuple(constraints))


def _cost_range(j, basis, nonbasic, reduced, alpha, cost_j) -> tuple[float, float]:
    if j not in basis:
        # Raising c_j by more than -d_j makes x_j attractive.
        return (-INF, float(cost_j - reduced[j]))
    row = basis.index(j)
    low, high = -INF, INF
    for k in nonbasic:
        coefficient = alpha[row, k]
        if abs(coefficient) <= _TOL:
            continue
        # The reduced cost of k becomes d_k - delta * alpha_rk and must stay <= 0.
        limit = reduced[k] / coefficient
        if coefficient > 0:
            low = max(low, limit)
        else:
            high = min(high, limit)
    return (float(cost_j + low), float(cost_j + high))


def _rhs_delta(column: np.ndarray, x_basic: np.ndarray) -> tuple[float, float]:
    low, high = -INF, INF
    for beta, value in zip(column, x_basic):
        if abs(beta) <= _TOL:
            continue
        limit = -value / beta
        if beta > 0:
            low = max(low, limit)
        else:
            high = min(high, limit)
    return (float(low), float(high))


def _clean(value: float) -> float:
    return 0.0 if abs(value) < 1e-10 else value
