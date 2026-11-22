"""Sensitivity analysis: textbook values, HiGHS duals and perturbation checks with SciPy."""

import math

import numpy as np
import pytest
from oracle import scipy_solve
from scipy.optimize import linprog

from optimizacion.core import Constraint, Goal, LinearProgram, Sense, analyze, solve

LE, GE, EQ = Sense.LE, Sense.GE, Sense.EQ
INF = math.inf


def lp(objective, rows, goal=Goal.MAX):
    return LinearProgram(tuple(objective), tuple(Constraint(tuple(a), s, b) for a, s, b in rows), goal)


WYNDOR = lp([3, 5], [([1, 0], LE, 4), ([0, 2], LE, 12), ([3, 2], LE, 18)])


def test_wyndor_textbook_sensitivity():
    report = analyze(solve(WYNDOR))
    assert [c.shadow_price for c in report.constraints] == pytest.approx([0, 1.5, 1])
    assert [c.slack for c in report.constraints] == pytest.approx([2, 0, 0])
    assert [c.is_binding for c in report.constraints] == [False, True, True]
    assert report.constraints[0].rhs_range == (pytest.approx(2), INF)
    assert report.constraints[1].rhs_range == pytest.approx((6, 18))
    assert report.constraints[2].rhs_range == pytest.approx((12, 24))
    assert report.variables[0].objective_range == pytest.approx((0, 7.5))
    assert report.variables[1].objective_range == (pytest.approx(2), INF)


def test_wyndor_duals_match_highs_marginals():
    res = linprog([-3, -5], A_ub=[[1, 0], [0, 2], [3, 2]], b_ub=[4, 12, 18], method="highs")
    report = analyze(solve(WYNDOR))
    assert [c.shadow_price for c in report.constraints] == pytest.approx(-res.ineqlin.marginals)


def test_wyndor_ranges_are_tight():
    """Just outside each finite range the optimal basis (and the dual price) changes."""
    report = analyze(solve(WYNDOR))
    x_star = np.array(solve(WYNDOR).values)
    for j, variable in enumerate(report.variables):
        for bound, step in ((variable.objective_range[0], -0.5), (variable.objective_range[1], 0.5)):
            if math.isinf(bound):
                continue
            objective = list(WYNDOR.objective)
            objective[j] = bound + step
            _, _, z = scipy_solve(lp(objective, [(c.coefficients, c.sense, c.rhs) for c in WYNDOR.constraints]))
            assert z > float(np.dot(objective, x_star)) + 1e-6
    for i, constraint in enumerate(report.constraints):
        for bound, step in ((constraint.rhs_range[0], -0.5), (constraint.rhs_range[1], 0.5)):
            if math.isinf(bound):
                continue
            rows = [(c.coefficients, c.sense, c.rhs) for c in WYNDOR.constraints]
            rows[i] = (rows[i][0], rows[i][1], bound + step)
            status, _, z = scipy_solve(lp(WYNDOR.objective, rows))
            linear = 36 + constraint.shadow_price * (bound + step - constraint.rhs)
            assert status != "optimal" or abs(z - linear) > 1e-6


def test_minimisation_signs():
    # min 2x1 + 3x2 s.t. x1 + x2 >= 4, x1 + 3x2 >= 6: duals (1.5, 0.5), raising a >= rhs raises cost.
    report = analyze(solve(lp([2, 3], [([1, 1], GE, 4), ([1, 3], GE, 6)], Goal.MIN)))
    assert [c.shadow_price for c in report.constraints] == pytest.approx([1.5, 0.5])
    assert report.variables[0].objective_range == pytest.approx((1, 3))
    assert report.variables[1].objective_range == pytest.approx((2, 6))


def test_rejects_non_optimal_results():
    with pytest.raises(ValueError):
        analyze(solve(lp([1, 1], [([1, -1], LE, 1)])))


def _random_optimal_problems():
    found = []
    seed = 0
    while len(found) < 25:
        rng = np.random.default_rng(1000 + seed)
        seed += 1
        n, m = int(rng.integers(2, 5)), int(rng.integers(2, 5))
        rows = [
            (rng.integers(0, 9, size=n).astype(float) + 1, rng.choice([LE, LE, GE]), float(rng.integers(5, 60)))
            for _ in range(m)
        ]
        goal = Goal.MAX if seed % 2 else Goal.MIN
        problem = lp(rng.integers(1, 12, size=n).astype(float), rows, goal)
        if solve(problem).is_optimal:
            found.append(problem)
    return found


@pytest.mark.parametrize("problem", _random_optimal_problems())
def test_random_sensitivity_is_consistent_with_scipy(problem):
    result = solve(problem)
    report = analyze(result)
    x_star = np.array(result.values)
    better = (lambda a, b: a > b) if problem.goal is Goal.MAX else (lambda a, b: a < b)
    rows = [(c.coefficients, c.sense, c.rhs) for c in problem.constraints]

    # Inside every RHS range the optimal value is linear with slope = shadow price.
    for i, item in enumerate(report.constraints):
        low, high = item.rhs_range
        for target in (item.rhs + 0.5 * (max(low, item.rhs - 10) - item.rhs),
                       item.rhs + 0.5 * (min(high, item.rhs + 10) - item.rhs)):
            changed = list(rows)
            changed[i] = (rows[i][0], rows[i][1], target)
            status, _, z = scipy_solve(lp(problem.objective, changed, problem.goal))
            assert status == "optimal"
            assert z == pytest.approx(result.objective + item.shadow_price * (target - item.rhs), rel=1e-7, abs=1e-6)

    # Inside every cost range the current solution stays optimal.
    for j, item in enumerate(report.variables):
        low, high = item.objective_range
        for target in (item.cost + 0.5 * (max(low, item.cost - 10) - item.cost),
                       item.cost + 0.5 * (min(high, item.cost + 10) - item.cost)):
            objective = list(problem.objective)
            objective[j] = target
            _, _, z = scipy_solve(lp(objective, rows, problem.goal))
            assert not better(z, float(np.dot(objective, x_star)) + (1e-6 if problem.goal is Goal.MAX else -1e-6))

    # Reduced costs of non-basic variables point in the "worse" direction.
    for item in report.variables:
        if not item.is_basic:
            assert item.reduced_cost <= 1e-9 if problem.goal is Goal.MAX else item.reduced_cost >= -1e-9
