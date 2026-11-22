"""Small reusable widgets that carry the visual identity."""

from __future__ import annotations

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from . import theme


def icon(name: str, color: str = theme.INK) -> QIcon:
    return qta.icon(f"ph.{name}", color=color)


def label(text: str = "", object_name: str = "", wrap: bool = False) -> QLabel:
    widget = QLabel(text)
    if object_name:
        widget.setObjectName(object_name)
    widget.setWordWrap(wrap)
    return widget


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None, object_name: str = "card", spacing: int = 8) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(18, 16, 18, 16)
        self.body.setSpacing(spacing)


class PageHeader(QWidget):
    def __init__(self, eyebrow: str, title: str, subtitle: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(2)
        layout.addWidget(label(eyebrow.upper(), "eyebrow"))
        layout.addWidget(label(title, "pageTitle"))
        self.subtitle = label(subtitle, "pageSubtitle", wrap=True)
        layout.addWidget(self.subtitle)


class StatCard(Card):
    def __init__(self, caption: str, hint: str = "") -> None:
        super().__init__(spacing=2)
        self.body.addWidget(label(caption.upper(), "cardLabel"))
        self.value = label("—", "cardValue")
        self.body.addWidget(self.value)
        self.hint = label(hint, "cardHint", wrap=True)
        self.body.addWidget(self.hint)

    def set(self, value: str, hint: str | None = None) -> None:
        self.value.setText(value)
        if hint is not None:
            self.hint.setText(hint)


class Pill(QLabel):
    def __init__(self, text: str = "", background: str = theme.SAFFRON_TINT, foreground: str = theme.INK) -> None:
        super().__init__(text)
        self.setObjectName("pill")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_colors(background, foreground)

    def set_colors(self, background: str, foreground: str) -> None:
        self.setStyleSheet(f"background: {background}; color: {foreground};")


class Swatch(QFrame):
    """Vertical colour stripe that identifies a product."""

    def __init__(self, color: str, width: int = 5) -> None:
        super().__init__()
        self.setFixedWidth(width)
        self.setStyleSheet(f"background: {color}; border-radius: {width // 2}px;")


def row(*widgets: QWidget, spacing: int = 14, stretch: bool = False) -> QHBoxLayout:
    layout = QHBoxLayout()
    layout.setSpacing(spacing)
    for widget in widgets:
        layout.addWidget(widget)
    if stretch:
        layout.addStretch(1)
    return layout
