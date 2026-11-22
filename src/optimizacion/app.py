"""Application entry point."""

from __future__ import annotations

import argparse
import sys

from PySide6.QtCore import QLocale, QTimer
from PySide6.QtWidgets import QApplication

from . import __version__


def create_application(argv: list[str] | None = None) -> QApplication:
    from .ui import theme

    app = QApplication.instance() or QApplication(argv or sys.argv[:1])
    app.setApplicationName("Sazón Llano")
    app.setApplicationVersion(__version__)
    QLocale.setDefault(QLocale(QLocale.Language.Spanish, QLocale.Country.Colombia))
    app.setFont(theme.ui_font(10))
    app.setStyle("Fusion")
    app.setStyleSheet(theme.STYLESHEET)
    theme.configure_matplotlib()
    return app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sazon-llano", description="Optimización lineal del caso Sazón Llano.")
    parser.add_argument("--no-splash", action="store_true", help="abre la ventana principal directamente")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    app = create_application()
    from .ui.main_window import MainWindow
    from .ui.splash import SplashScreen
    from .ui.state import AppState

    if args.no_splash:
        window = MainWindow()
        window.show()
        return app.exec()

    splash = SplashScreen()
    splash.show()
    holder: dict[str, MainWindow] = {}
    steps = [
        (25, "Construyendo el modelo…", lambda: None),
        (60, "Resolviendo con simplex de dos fases…", lambda: holder.setdefault("state", AppState())),
        (90, "Calculando el análisis de sensibilidad…", lambda: holder.setdefault("window", MainWindow(holder["state"]))),
        (100, "Listo", lambda: None),
    ]

    def advance(index: int = 0) -> None:
        if index == len(steps):
            splash.close()
            holder["window"].show()
            return
        value, message, action = steps[index]
        splash.step(value, message)
        action()
        QTimer.singleShot(280, lambda: advance(index + 1))

    QTimer.singleShot(100, advance)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
