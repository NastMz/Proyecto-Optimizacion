"""Sazón Llano case study: optimum, duals and ranges (cross-checked with the original CPLEX run)."""

import math

import numpy as np
import pytest
from oracle import scipy_solve

from optimizacion.core import Sense
from optimizacion.core.case_study import SAZON_LLANO, Parameter
from optimizacion.core.formatting import interval, money, number
from optimizacion.core.report import build_report
from optimizacion.core.scenarios import curve_window, evaluate, parametric_curve, simulate, valid_range

INF = math.inf


@pytest.fixture(scope="module")
def base():
    return evaluate(SAZON_LLANO)


def test_model_shape():
    problem = SAZON_LLANO.to_problem()
    assert problem.num_variables == 4 and problem.num_constraints == 12
    assert [c.sense for c in problem.constraints] == [Sense.LE] * 8 + [Sense.GE] * 4
    assert problem.constraints[9].coefficients == (0, 1, 0, 0)
    assert problem.constraints[9].rhs == 10


def test_optimal_plan(base):
    # Each product is limited by the tighter of raw material and budget.
    expected = (750000 / 1421, 325000 / 858, 10000 / 50, 3780 / 60)
    assert base.result.values == pytest.approx(expected)
    assert base.objective == pytest.approx(1747835.634572324)
    _, x, z = scipy_solve(SAZON_LLANO.to_problem())
    assert base.objective == pytest.approx(z)
    np.testing.assert_allclose(base.result.values, x, rtol=1e-9)


def test_shadow_prices_match_original_cplex_report(base):
    duals = [c.shadow_price for c in base.sensitivity.constraints]
    assert duals[:8] == pytest.approx([0, 0, 17.92, 31.133333333, 1.349753694, 1.349650349, 0, 0])
    assert duals[8:] == pytest.approx([0, 0, 0, 0])


def test_ranges(base):
    constraints = base.sensitivity.constraints
    # Values shared with the CPLEX sensitivity report of the original project.
    assert constraints[0].rhs_range == (pytest.approx(6333.567909922589), INF)
    assert constraints[2].rhs_range[1] == pytest.approx(24472.89156626506)
    assert constraints[3].rhs_range[1] == pytest.approx(26011.56069364162)
    assert constraints[5].rhs_range[1] == pytest.approx(1945944)
    # Demand is in units (x >= d): lower ends follow from the minimum demand.
    assert constraints[2].rhs_range[0] == pytest.approx(4 * 50)
    assert constraints[4].rhs_range[0] == pytest.approx(10 * 1421)
    for variable in base.sensitivity.variables:
        assert variable.objective_range == (pytest.approx(0, abs=1e-9), INF)


def test_valid_range_maps_parameters(base):
    assert valid_range(base, Parameter.PROFIT, 0) == base.sensitivity.variables[0].objective_range
    assert valid_range(base, Parameter.BUDGET, 1) == base.sensitivity.constraints[5].rhs_range
    assert valid_range(base, Parameter.DEMAND, 3) == base.sensitivity.constraints[11].rhs_range


def test_simulation_inside_range_follows_shadow_price(base):
    scenario = simulate(base, Parameter.RAW_MATERIAL, 3, 3780 + 600, "Simulación 1")
    assert scenario.label == "Simulación 1"
    assert scenario.objective == pytest.approx(base.objective + 600 * 31.133333333)
    assert scenario.case.products[3].raw_material_stock == 4380
    assert SAZON_LLANO.products[3].raw_material_stock == 3780, "the base case is immutable"


def test_simulation_can_become_infeasible(base):
    scenario = simulate(base, Parameter.DEMAND, 2, 1000, "Simulación 2")
    assert scenario.result.status.value == "infeasible"
    assert scenario.sensitivity is None
    assert valid_range(scenario, Parameter.DEMAND, 2) is None
    assert "no tiene solución factible" in build_report(scenario)


def test_parametric_curve_is_piecewise_linear():
    xs, ys = parametric_curve(SAZON_LLANO, Parameter.RAW_MATERIAL, 2, 0, 30000, 31)
    assert math.isnan(ys[0]), "below the minimum demand (200 g) the model is infeasible"
    inside = (xs >= 200) & (xs <= 24472)
    slopes = np.diff(ys[inside]) / np.diff(xs[inside])
    assert slopes == pytest.approx(17.92)
    assert ys[-1] == pytest.approx(ys[-2]), "beyond the budget limit more raw material is useless"


def test_curve_window_covers_finite_bounds():
    left, right = curve_window(100, (40, INF))
    assert left < 40 and right > 100
    assert curve_window(5, None)[0] == 0


def test_report_mentions_plan_and_binding_resources(base):
    html = build_report(base)
    assert "$ 1.747.835,63" in html
    assert "Uva pasa" in html and "Restricción <b>activa</b>" in html
    assert "$ 17,92" in html


def test_formatting():
    assert number(1234567.891) == "1.234.567,89"
    assert number(-3.5, 1) == "−3,5"
    assert number(float("nan")) == "—"
    assert money(-2) == "−$ 2,00"
    assert money(INF) == "∞"
    assert interval((0, INF)) == "[0,00 ; ∞]"
    assert interval(None) == "—"
