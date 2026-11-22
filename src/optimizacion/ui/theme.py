"""Visual identity: a warm "spice rack" palette on paper, serif headings and tabular numbers."""

from __future__ import annotations

import matplotlib as mpl
from PySide6.QtGui import QColor, QFont, QFontDatabase

PAPER = "#F4EEE3"
SURFACE = "#FBF8F2"
SURFACE_ALT = "#F0E8DA"
INK = "#2A201A"
MUTED = "#7A6A5E"
LINE = "#E3D8C7"
SIDEBAR = "#2B1E17"
SIDEBAR_HOVER = "#3A2A21"
SIDEBAR_TEXT = "#EADFCF"
SIDEBAR_MUTED = "#A8978A"
PAPRIKA = "#B5462A"
PAPRIKA_DARK = "#943520"
PAPRIKA_TINT = "#F3D9CF"
SAFFRON = "#D99A2B"
SAFFRON_TINT = "#F7E6C4"
CARDAMOM = "#5E7B5A"
CARDAMOM_TINT = "#DDE7D6"

PRODUCT_COLORS = ("#9A5B34", "#5A3A2E", "#7B4B6A", "#D99A2B")

DISPLAY_FAMILIES = ["Sitka Display", "Georgia", "Noto Serif", "DejaVu Serif"]
UI_FAMILIES = ["Bahnschrift", "Segoe UI", "Noto Sans", "DejaVu Sans"]
MONO_FAMILIES = ["Cascadia Mono", "Consolas", "DejaVu Sans Mono"]


def _first_available(families: list[str]) -> str:
    available = set(QFontDatabase.families())
    return next((f for f in families if f in available), families[-1])


def display_font(size: int, bold: bool = False) -> QFont:
    font = QFont()
    font.setFamilies(DISPLAY_FAMILIES)
    font.setPointSize(size)
    font.setBold(bold)
    return font


def mono_font(size: int = 10) -> QFont:
    font = QFont()
    font.setFamilies(MONO_FAMILIES)
    font.setPointSize(size)
    return font


def ui_font(size: int = 10) -> QFont:
    font = QFont()
    font.setFamilies(UI_FAMILIES)
    font.setPointSize(size)
    return font


def product_color(index: int) -> str:
    return PRODUCT_COLORS[index % len(PRODUCT_COLORS)]


def qcolor(hex_color: str, alpha: int = 255) -> QColor:
    color = QColor(hex_color)
    color.setAlpha(alpha)
    return color


def mpl_display_family() -> str:
    """First serif display family that Matplotlib can actually load."""
    from matplotlib import font_manager

    names = {f.name for f in font_manager.fontManager.ttflist}
    return next((f for f in DISPLAY_FAMILIES if f in names), "DejaVu Serif")


def configure_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": [_first_available(UI_FAMILIES), "DejaVu Sans"],
            "font.size": 9.5,
            "text.color": INK,
            "axes.edgecolor": LINE,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": INK,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.facecolor": SURFACE,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": LINE,
            "grid.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "figure.facecolor": SURFACE,
            "axes.formatter.use_locale": False,
        }
    )


STYLESHEET = f"""
* {{
    font-family: {", ".join(f'"{f}"' for f in UI_FAMILIES)};
    font-size: 10pt;
    color: {INK};
}}
QMainWindow, #content {{ background: {PAPER}; }}
QToolTip {{ background: {SIDEBAR}; color: {SIDEBAR_TEXT}; border: none; padding: 6px 8px; }}

#sidebar {{ background: {SIDEBAR}; }}
#sidebar QLabel {{ color: {SIDEBAR_TEXT}; }}
#brandTitle {{ font-family: {", ".join(f'"{f}"' for f in DISPLAY_FAMILIES)}; font-size: 20pt; color: #FFF6EA; }}
#brandSubtitle {{ color: {SAFFRON}; font-size: 8pt; letter-spacing: 2px; padding-top: 4px; }}
#sidebarFooter {{ color: {SIDEBAR_MUTED}; font-size: 8pt; }}
#navButton {{
    background: transparent; border: none; border-radius: 8px; text-align: left;
    padding: 10px 14px; color: {SIDEBAR_TEXT}; font-size: 10.5pt;
}}
#navButton:hover {{ background: {SIDEBAR_HOVER}; }}
#navButton:checked {{ background: {PAPRIKA}; color: #FFF6EA; }}

#pageTitle {{ font-family: {", ".join(f'"{f}"' for f in DISPLAY_FAMILIES)}; font-size: 24pt; color: {INK}; }}
#pageSubtitle {{ color: {MUTED}; font-size: 10.5pt; }}
#eyebrow {{ color: {PAPRIKA}; font-size: 8pt; font-weight: bold; letter-spacing: 2px; padding-top: 4px; }}

#card {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 12px; }}
#heroCard {{ background: {SIDEBAR}; border-radius: 14px; }}
#heroCard QLabel {{ color: {SIDEBAR_TEXT}; }}
#heroValue {{ font-family: {", ".join(f'"{f}"' for f in DISPLAY_FAMILIES)}; font-size: 30pt; color: #FFF6EA; }}
#cardLabel {{ color: {MUTED}; font-size: 8.5pt; letter-spacing: 1px; padding-top: 4px; }}
#cardValue {{ font-family: {", ".join(f'"{f}"' for f in DISPLAY_FAMILIES)}; font-size: 19pt; }}
#cardHint {{ color: {MUTED}; font-size: 9pt; }}
#productName {{ font-family: {", ".join(f'"{f}"' for f in DISPLAY_FAMILIES)}; font-size: 15pt; }}
#sectionTitle {{ font-family: {", ".join(f'"{f}"' for f in DISPLAY_FAMILIES)}; font-size: 14pt; }}

#pill {{ border-radius: 10px; padding: 3px 10px; font-size: 8.5pt; font-weight: bold; }}
#explanation {{ background: {SAFFRON_TINT}; border-radius: 10px; padding: 10px 14px; }}
#warning {{ background: {PAPRIKA_TINT}; color: {PAPRIKA_DARK}; border-radius: 8px; padding: 8px 12px; }}
#ok {{ background: {CARDAMOM_TINT}; color: #3F5A3C; border-radius: 8px; padding: 8px 12px; }}

QPushButton {{
    background: {SURFACE}; border: 1px solid {LINE}; border-radius: 8px; padding: 8px 16px;
}}
QPushButton:hover {{ border-color: {PAPRIKA}; }}
QPushButton:disabled {{ color: #B9AC9F; border-color: {LINE}; }}
QPushButton#primary {{ background: {PAPRIKA}; border: none; color: #FFF6EA; font-weight: bold; }}
QPushButton#primary:hover {{ background: {PAPRIKA_DARK}; }}

QComboBox, QDoubleSpinBox, QLineEdit {{
    background: {SURFACE}; border: 1px solid {LINE}; border-radius: 8px; padding: 6px 10px; min-height: 20px;
}}
QComboBox:focus, QDoubleSpinBox:focus {{ border-color: {PAPRIKA}; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    width: 10px; border: none; background: transparent; image: none;
}}
QComboBox QAbstractItemView {{
    background: {SURFACE}; border: 1px solid {LINE}; selection-background-color: {PAPRIKA_TINT};
    selection-color: {INK};
}}
QCheckBox {{ spacing: 8px; }}

QTableView, QTableWidget {{
    background: {SURFACE}; border: 1px solid {LINE}; border-radius: 10px; gridline-color: {LINE};
    selection-background-color: {PAPRIKA_TINT}; selection-color: {INK};
}}
QHeaderView::section {{
    background: {SURFACE_ALT}; color: {MUTED}; border: none; border-bottom: 1px solid {LINE};
    padding: 6px 8px; font-size: 8.5pt; font-weight: bold;
}}
QTableCornerButton::section {{ background: {SURFACE_ALT}; border: none; }}

QTextBrowser {{ background: {SURFACE}; border: 1px solid {LINE}; border-radius: 12px; }}

QSlider::groove:horizontal {{ height: 4px; background: {LINE}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {PAPRIKA}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: {PAPRIKA}; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px;
}}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: {LINE}; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; }}
QScrollBar::handle:horizontal {{ background: {LINE}; border-radius: 5px; min-width: 30px; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{
    background: transparent; padding: 8px 16px; color: {MUTED}; border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{ color: {INK}; border-bottom: 2px solid {PAPRIKA}; }}
QProgressBar {{ background: {LINE}; border: none; border-radius: 3px; height: 6px; }}
QProgressBar::chunk {{ background: {PAPRIKA}; border-radius: 3px; }}
"""
