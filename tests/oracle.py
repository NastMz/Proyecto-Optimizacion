"""SciPy (HiGHS) reference solver used as an independent oracle in the tests."""

from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from optimizacion.core.model import Goal, LinearProgram, Sense


def scipy_solve(problem: LinearProgram):
    """Return ``(status, x, objective)`` with status in {"optimal", "infeasible", "unbounded"}."""
    sign = -1.0 if problem.goal is Goal.MAX else 1.0
    c = sign * np.array(problem.objective, dtype=float)
    a_ub, b_ub, a_eq, b_eq = [], [], [], []
    for constraint in problem.constraints:
        row = list(constraint.coefficients)
        if constraint.sense is Sense.LE:
            a_ub.append(row)
            b_ub.append(constraint.rhs)
        elif constraint.sense is Sense.GE:
            a_ub.append([-v for v in row])
            b_ub.append(-constraint.rhs)
        else:
            a_eq.append(row)
            b_eq.append(constraint.rhs)
    res = linprog(
        c,
        A_ub=a_ub or None,
        b_ub=b_ub or None,
        A_eq=a_eq or None,
        b_eq=b_eq or None,
        bounds=[(0, None)] * problem.num_variables,
        method="highs",
    )
    status = {0: "optimal", 2: "infeasible", 3: "unbounded"}.get(res.status, f"other:{res.status}")
    if status != "optimal":
        return status, None, None
    return status, res.x, sign * res.fun
