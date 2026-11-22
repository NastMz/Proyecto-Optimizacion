"""Common scaffolding for every page: scrollable body with a header."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from ..state import AppState
from ..widgets import PageHeader


class Page(QScrollArea):
    eyebrow = ""
    title = ""
    subtitle = ""

    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        container.setObjectName("content")
        self.setWidget(container)
        self.layout_ = QVBoxLayout(container)
        self.layout_.setContentsMargins(36, 28, 36, 28)
        self.layout_.setSpacing(16)
        self.header = PageHeader(self.eyebrow, self.title, self.subtitle)
        self.layout_.addWidget(self.header)

    def refresh(self) -> None:  # pragma: no cover - overridden
        """Re-render the page from :attr:`state`."""
