"""Splash screen shown while the case study is solved."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget

from . import theme


class SplashScreen(QWidget):
    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(520, 300)
        frame = QFrame(self)
        frame.setGeometry(0, 0, 520, 300)
        frame.setStyleSheet(f"background: {theme.SIDEBAR};")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(40, 44, 40, 34)
        eyebrow = QLabel("PROYECTO DE OPTIMIZACIÓN")
        eyebrow.setStyleSheet(f"color: {theme.SAFFRON}; font-size: 8pt; letter-spacing: 3px; padding-top: 4px;")
        title = QLabel("Sazón Llano")
        families = ", ".join(f'"{f}"' for f in theme.DISPLAY_FAMILIES)
        title.setStyleSheet(f"color: #FFF6EA; font-family: {families}; font-size: 36pt; padding-top: 6px;")
        subtitle = QLabel("Programación lineal · simplex de dos fases · análisis de sensibilidad")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"color: {theme.SIDEBAR_MUTED}; font-size: 10pt;")
        self.status = QLabel("Cargando…")
        self.status.setStyleSheet(f"color: {theme.SIDEBAR_TEXT}; font-size: 9pt;")
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet(
            f"QProgressBar {{ background: {theme.SIDEBAR_HOVER}; border: none; border-radius: 3px; }}"
            f"QProgressBar::chunk {{ background: {theme.PAPRIKA}; border-radius: 3px; }}"
        )
        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)

    def step(self, value: int, message: str) -> None:
        self.progress.setValue(value)
        self.status.setText(message)
