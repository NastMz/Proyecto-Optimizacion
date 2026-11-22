"""Report page: managerial report generated from any scenario, exportable to PDF."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout

from ...core.report import build_report
from .. import theme
from ..charts import ShareChart
from ..widgets import Card, icon, label
from .base import Page


def export_pdf(html: str, path: str | Path) -> Path:
    """Render ``html`` to an A4 PDF at ``path``."""
    path = Path(path)
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(str(path))
    printer.setPageLayout(QPageLayout(QPageSize(QPageSize.PageSizeId.A4), QPageLayout.Orientation.Portrait,
                                      printer.pageLayout().margins()))
    document = QTextDocument()
    document.setDefaultFont(theme.ui_font(10))
    document.setHtml(html)
    document.print_(printer)
    return path


class ReportPage(Page):
    eyebrow = "Reporte"
    title = "Reporte gerencial"
    subtitle = "Generado automáticamente a partir de la solución óptima y su análisis de sensibilidad."

    def __init__(self, state) -> None:
        super().__init__(state)
        body = QHBoxLayout()
        body.setSpacing(14)
        self.browser = QTextBrowser()
        self.browser.setMinimumHeight(560)
        self.browser.document().setDocumentMargin(22)
        self.browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body.addWidget(self.browser, 3)

        side = QVBoxLayout()
        side.setSpacing(14)
        options = Card(spacing=10)
        options.body.addWidget(label("ESCENARIO", "cardLabel"))
        self.scenario = QComboBox()
        options.body.addWidget(self.scenario)
        self.export_button = QPushButton(icon("file-pdf", "#FFF6EA"), "  Exportar PDF")
        self.export_button.setObjectName("primary")
        options.body.addWidget(self.export_button)
        self.message = label("", "cardHint", wrap=True)
        options.body.addWidget(self.message)
        side.addWidget(options)
        chart = Card()
        self.chart = ShareChart(height=3.4)
        chart.body.addWidget(self.chart)
        side.addWidget(chart)
        side.addStretch(1)
        body.addLayout(side, 2)
        self.layout_.addLayout(body, 1)

        self.scenario.currentIndexChanged.connect(self.render)
        self.export_button.clicked.connect(self.export)
        self.state.history_changed.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        current = self.scenario.currentIndex()
        scenarios = self.state.scenarios()
        self.scenario.blockSignals(True)
        self.scenario.clear()
        self.scenario.addItems([s.label for s in scenarios])
        self.scenario.setCurrentIndex(current if 0 <= current < len(scenarios) else 0)
        self.scenario.blockSignals(False)
        self.render()

    def selected(self):
        return self.state.scenarios()[max(self.scenario.currentIndex(), 0)]

    def html(self) -> str:
        families = ", ".join(f'"{f}"' for f in theme.DISPLAY_FAMILIES)
        return build_report(self.selected(), accent=theme.PAPRIKA, muted=theme.MUTED, heading_font=families)

    def render(self) -> None:
        scenario = self.selected()
        self.browser.setHtml(self.html())
        names = [p.name for p in scenario.case.products]
        if scenario.result.is_optimal:
            contributions = [p.profit * x for p, x in zip(scenario.case.products, scenario.result.values)]
            self.chart.plot(names, contributions, scenario.objective)
        else:
            self.chart.plot(names, [1] * len(names), 0)
        self.message.setText("")

    def export(self) -> None:
        name = f"reporte-{self.selected().label.lower().replace(' ', '-')}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Exportar reporte", name, "PDF (*.pdf)")
        if path:
            export_pdf(self.html(), path)
            self.message.setText(f"Reporte guardado en {Path(path).name}")
