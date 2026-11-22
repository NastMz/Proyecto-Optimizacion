"""Render every page of the real application to ``docs/screenshots``.

Usage:  python scripts/capture_screenshots.py [output-dir]
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from optimizacion.app import create_application
from optimizacion.core.case_study import Parameter
from optimizacion.ui.main_window import MainWindow
from optimizacion.ui.splash import SplashScreen

PAGES = ("resumen", "modelo", "simplex", "sensibilidad", "simulacion", "reporte")


def settle() -> None:
    for _ in range(5):
        QApplication.processEvents()


def main() -> int:
    output = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "docs" / "screenshots")
    output.mkdir(parents=True, exist_ok=True)
    create_application()

    splash = SplashScreen()
    splash.step(60, "Resolviendo con simplex de dos fases…")
    splash.show()
    settle()
    splash.grab().save(str(output / "splash.png"))
    splash.close()

    window = MainWindow()
    window.resize(1440, 920)
    window.show()
    state = window.state
    state.simulate(Parameter.RAW_MATERIAL, 3, 4500)
    state.simulate(Parameter.BUDGET, 0, 900000)
    state.simulate(Parameter.RAW_MATERIAL, 3, 6000)

    for index, name in enumerate(PAGES):
        window.go_to(index)
        page = window.pages[index]
        if name == "simplex":
            page.slider.setValue(2)
        if name == "simulacion":
            page.parameter.setCurrentIndex(list(Parameter).index(Parameter.RAW_MATERIAL))
            page.product.setCurrentIndex(3)
        settle()
        window.resize(1440, max(920, page.widget().sizeHint().height()))
        settle()
        window.grab().save(str(output / f"{name}.png"))
        window.resize(1440, 920)

    simplex = window.pages[PAGES.index("simplex")]
    window.go_to(PAGES.index("simplex"))
    simplex.slider.setValue(simplex.slider.maximum())
    simplex.fractions.setChecked(True)
    settle()
    window.grab().save(str(output / "simplex-optimo.png"))
    print(f"Screenshots saved to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
