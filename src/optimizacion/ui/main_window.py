"""Main window: sidebar navigation and the page stack."""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from . import theme
from .pages.model import ModelPage
from .pages.report import ReportPage
from .pages.sensitivity import SensitivityPage
from .pages.simplex import SimplexPage
from .pages.simulation import SimulationPage
from .pages.summary import SummaryPage
from .state import AppState
from .widgets import icon, label

NAVIGATION = (
    ("Resumen", "house", SummaryPage),
    ("Modelo", "math-operations", ModelPage),
    ("Simplex", "table", SimplexPage),
    ("Sensibilidad", "scales", SensitivityPage),
    ("Simulación", "flask", SimulationPage),
    ("Reporte", "file-text", ReportPage),
)


class MainWindow(QMainWindow):
    def __init__(self, state: AppState | None = None) -> None:
        super().__init__()
        self.state = state or AppState()
        self.setWindowTitle("Sazón Llano · Optimización lineal")
        self.setWindowIcon(icon("cooking-pot", theme.PAPRIKA))
        self.resize(1360, 880)
        self.setMinimumSize(1100, 700)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._sidebar())
        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

        self.pages = [page(self.state) for _, _, page in NAVIGATION]
        for page in self.pages:
            self.stack.addWidget(page)
        self.state.base_changed.connect(self._refresh_pages)
        self.go_to(0)

    def _sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(232)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 26, 18, 20)
        layout.setSpacing(4)
        layout.addWidget(label("Sazón Llano", "brandTitle"))
        layout.addWidget(label("OPTIMIZACIÓN LINEAL", "brandSubtitle"))
        layout.addSpacing(26)
        self.nav = QButtonGroup(self)
        self.nav.setExclusive(True)
        for index, (text, icon_name, _) in enumerate(NAVIGATION):
            button = QPushButton(icon(icon_name, theme.SIDEBAR_TEXT), f"  {text}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setIconSize(QSize(18, 18))
            button.clicked.connect(lambda _=False, i=index: self.go_to(i))
            self.nav.addButton(button, index)
            layout.addWidget(button)
        layout.addStretch(1)
        layout.addWidget(label(
            f"Proyecto del curso de Optimización<br>Kevin Santiago Martinez<br>Joshep Mateo Granada<br>"
            f"v{__version__}", "sidebarFooter", wrap=True))
        return sidebar

    def go_to(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.nav.button(index).setChecked(True)

    def _refresh_pages(self) -> None:
        for page in self.pages:
            page.refresh()
