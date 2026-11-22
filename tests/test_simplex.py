"""Two-phase simplex against textbook results and the SciPy/HiGHS oracle."""

import numpy as np
import pytest
from oracle import scipy_solve

from optimizacion.core import Constraint, Goal, LinearProgram, Sense, Status, solve

LE, GE, EQ = Sense.LE, Sense.GE, Sense.EQ


def lp(objective, rows, goal=Goal.MAX):
    return LinearProgram(tuple(objective), tuple(Constraint(tuple(a), s, b) for a, s, b in rows), goal)


WYNDOR = lp([3, 5], [([1, 0], LE, 4), ([0, 2], LE, 12), ([3, 2], LE, 18)])


def test_wyndor_glass_textbook_optimum():
    # Hillier & Lieberman, Introduction to Operations Research: x = (2, 6), Z = 36.
    result = solve(WYNDOR)
    assert result.status is Status.OPTIMAL
    assert result.values == pytest.approx((2, 6))
    assert result.objective == pytest.approx(36)
    assert not result.phase(1), "only <= constraints: no phase 1 needed"


def test_minimisation_with_greater_equal_uses_phase_one():
    # Diet-style problem: min 2x1 + 3x2, x1 + x2 >= 4, x1 + 3x2 >= 6 -> x = (3, 1), Z = 9.
    problem = lp([2, 3], [([1, 1], GE, 4), ([1, 3], GE, 6)], Goal.MIN)
    result = solve(problem)
    assert result.status is Status.OPTIMAL
    assert result.values == pytest.approx((3, 1))
    assert result.objective == pytest.approx(9)
    assert result.phase(1) and result.phase(2)
    assert result.phase(1)[-1].z == pytest.approx(0)


def test_equality_and_negative_rhs_are_normalised():
    # x1 - x2 >= -2 is stored as -x1 + x2 <= 2.
    problem = lp([1, 2], [([1, 1], EQ, 6), ([1, -1], GE, -2), ([1, 0], LE, 5)])
    result = solve(problem)
    status, x, z = scipy_solve(problem)
    assert result.status is Status.OPTIMAL and status == "optimal"
    assert result.objective == pytest.approx(z)
    assert result.values == pytest.approx(tuple(x))
    assert result.standard.flips == (1, -1, 1)


def test_detects_infeasible_problem():
    result = solve(lp([1, 1], [([1, 1], LE, 2), ([1, 1], GE, 5)]))
    assert result.status is Status.INFEASIBLE
    assert result.tableaus[-1].phase == 1


def test_detects_unbounded_problem():
    result = solve(lp([1, 1], [([1, -1], LE, 1)]))
    assert result.status is Status.UNBOUNDED
    final = result.tableaus[-1]
    assert final.entering is not None and final.leaving is None
    assert all(r is None for r in final.ratios)


def test_redundant_equality_row_is_dropped():
    problem = lp([1, 1], [([1, 1], EQ, 4), ([2, 2], EQ, 8), ([1, 0], LE, 3)])
    result = solve(problem)
    assert result.status is Status.OPTIMAL
    assert result.objective == pytest.approx(4)
    assert len(result.basis) == 2


def test_beale_cycling_example_terminates():
    # Beale (1955): cycles with Dantzig's rule and naive ties; optimum Z = 0.05 (as max of the negated cost).
    problem = lp(
        [0.75, -150, 0.02, -6],
        [([0.25, -60, -0.04, 9], LE, 0), ([0.5, -90, -0.02, 3], LE, 0), ([0, 0, 1, 0], LE, 1)],
    )
    result = solve(problem)
    assert result.status is Status.OPTIMAL
    assert result.objective == pytest.approx(0.05)


def test_tableaus_follow_classroom_convention():
    result = solve(WYNDOR)
    first, last = result.tableaus[0], result.tableaus[-1]
    assert first.column_names == ("X1", "X2", "S1", "S2", "S3")
    assert first.basis == ("S1", "S2", "S3")
    # Dantzig: X2 has the largest Cj - Zj (5); the ratio test picks S2 (12 / 2 = 6 < 18 / 2 = 9).
    assert first.column_names[first.entering] == "X2"
    assert first.basis[first.leaving] == "S2"
    assert first.ratios == (None, 6.0, 9.0)
    assert last.is_final and last.entering is None
    assert max(last.reduced_costs) <= 1e-9
    assert last.z == pytest.approx(36)
    for t in result.tableaus:
        np.testing.assert_allclose(np.array(t.cb) @ np.array(t.rows), t.zj, atol=1e-9)
        np.testing.assert_allclose(np.array(t.cj) - np.array(t.zj), t.reduced_costs, atol=1e-9)


@pytest.mark.parametrize("seed", range(60))
def test_random_problems_match_scipy(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(2, 6))
    m = int(rng.integers(2, 6))
    rows = []
    for _ in range(m):
        sense = rng.choice([LE, LE, GE, EQ])
        coefficients = rng.integers(-3, 10, size=n).astype(float)
        rows.append((coefficients, sense, float(rng.integers(-5, 40))))
    goal = Goal.MAX if seed % 2 == 0 else Goal.MIN
    problem = lp(rng.integers(-5, 10, size=n).astype(float), rows, goal)

    result = solve(problem)
    status, x, z = scipy_solve(problem)
    assert result.status.value == status
    if status == "optimal":
        assert result.objective == pytest.approx(z, rel=1e-7, abs=1e-7)
        values = np.array(result.values)
        assert np.all(values >= -1e-9)
        for constraint in problem.constraints:
            activity = float(np.dot(constraint.coefficients, values))
            if constraint.sense is LE:
                assert activity <= constraint.rhs + 1e-7
            elif constraint.sense is GE:
                assert activity >= constraint.rhs - 1e-7
            else:
                assert activity == pytest.approx(constraint.rhs, abs=1e-7)


def test_model_validation():
    with pytest.raises(ValueError):
        lp([1, 2], [([1], LE, 3)])
    with pytest.raises(ValueError):
        LinearProgram((1.0,), ())
