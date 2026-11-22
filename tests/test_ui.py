"""Offscreen smoke tests of the PySide6 interface."""

import pytest
from PySide6.QtCore import Qt

from optimizacion.app import create_application, main
from optimizacion.core.case_study import SAZON_LLANO, Parameter
from optimizacion.ui import theme
from optimizacion.ui.main_window import NAVIGATION, MainWindow
from optimizacion.ui.pages.report import export_pdf
from optimizacion.ui.pages.simplex import explain
from optimizacion.ui.tableau_model import format_value


@pytest.fixture(scope="module")
def app():
    return create_application()


@pytest.fixture
def window(app):
    window = MainWindow()
    yield window
    window.close()


def page(window, cls):
    return next(p for p in window.pages if isinstance(p, cls))


def test_navigation_shows_every_page(window):
    assert len(window.pages) == len(NAVIGATION) == 6
    for index in range(len(NAVIGATION)):
        window.go_to(index)
        assert window.stack.currentIndex() == index
        assert window.nav.button(index).isChecked()


def test_summary_shows_optimal_profit(window):
    from optimizacion.ui.pages.summary import SummaryPage

    summary = page(window, SummaryPage)
    assert summary.hero_value.text() == "$ 1.747.835,63"
    assert summary.binding.value.text() == "4 de 12"
    assert "Ajo sal" in summary.best.hint.text()


def test_simplex_page_steps_through_tableaus(window):
    from optimizacion.ui.pages.simplex import SimplexPage

    simplex = page(window, SimplexPage)
    tableaus = window.state.base.result.tableaus
    first = tableaus[0]
    assert simplex.model.rowCount() == len(first.basis) + 3
    assert simplex.phase.text() == "FASE 1"
    pivot = simplex.model.index(first.leaving + 1, first.entering + 2)
    assert simplex.model.data(pivot, Qt.ItemDataRole.BackgroundRole).color().name() == theme.PAPRIKA.lower()
    assert not simplex.previous.isEnabled()

    simplex.next.click()
    assert simplex.slider.value() == 1
    simplex.slider.setValue(simplex.slider.maximum())
    assert simplex.phase.text() == "FASE 2"
    assert "Solución óptima" in simplex.explanation.text()
    assert not simplex.next.isEnabled()


def test_tableau_formatting():
    assert format_value(0.5, as_fraction=True) == "1/2"
    assert format_value(-12.0, as_fraction=False) == "−12"
    assert format_value(1 / 1421, as_fraction=True) == "0,0007"  # denominator too large for a clean fraction
    assert format_value(1421.0, as_fraction=False) == "1.421"
    assert format_value(None, as_fraction=False) == ""


def test_explain_unbounded_tableau():
    from optimizacion.core import Constraint, LinearProgram, Sense, solve

    result = solve(LinearProgram((1.0, 1.0), (Constraint((1.0, -1.0), Sense.LE, 1.0),)))
    assert "no está acotado" in explain(result.tableaus[-1])


def test_simulation_page_runs_what_if(window):
    from optimizacion.ui.pages.simulation import PARAMETERS, SimulationPage

    simulation = page(window, SimulationPage)
    simulation.parameter.setCurrentIndex(PARAMETERS.index(Parameter.RAW_MATERIAL))
    simulation.product.setCurrentIndex(3)
    assert simulation.value.value() == 3780
    simulation.value.setValue(50000)
    assert simulation.status.objectName() == "warning"
    simulation.value.setValue(4000)
    assert simulation.status.objectName() == "ok"
    simulation.simulate_button.click()
    assert len(window.state.history) == 1
    assert simulation.table.rowCount() == 2
    assert simulation.table.item(1, 0).text() == "Simulación 1"
    assert "+$" in simulation.table.item(1, 3).text()


def test_model_page_resolves_and_restores(window):
    from optimizacion.ui.pages.model import ModelPage
    from optimizacion.ui.pages.summary import SummaryPage

    model = page(window, ModelPage)
    model.spins[3][2].setValue(4380)  # Ajo sal raw material stock
    model.solve_button.click()
    assert window.state.base.case.products[3].raw_material_stock == 4380
    assert page(window, SummaryPage).hero_value.text() != "$ 1.747.835,63"
    model.reset_button.click()
    assert window.state.base.case == SAZON_LLANO


def test_infeasible_case_is_reported_everywhere(window):
    from optimizacion.ui.pages.report import ReportPage
    from optimizacion.ui.pages.sensitivity import SensitivityPage
    from optimizacion.ui.pages.summary import SummaryPage

    window.state.resolve(SAZON_LLANO.with_value(Parameter.DEMAND, 2, 5000))
    assert page(window, SummaryPage).hero_value.text() == "Sin solución"
    assert page(window, SensitivityPage).constraints.rowCount() == 0
    assert "no tiene solución factible" in page(window, ReportPage).browser.toPlainText()


def test_report_lists_scenarios_and_exports_pdf(window, tmp_path):
    from optimizacion.ui.pages.report import ReportPage

    window.state.simulate(Parameter.BUDGET, 0, 900000)
    report = page(window, ReportPage)
    assert [report.scenario.itemText(i) for i in range(report.scenario.count())] == ["Actual", "Simulación 1"]
    report.scenario.setCurrentIndex(1)
    assert "Simulación 1" in report.browser.toPlainText()
    pdf = export_pdf(report.html(), tmp_path / "reporte.pdf")
    assert pdf.read_bytes().startswith(b"%PDF")


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert "1.0.0" in capsys.readouterr().out
