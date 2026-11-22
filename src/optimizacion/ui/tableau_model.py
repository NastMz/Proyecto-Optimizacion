"""Qt table model that renders one simplex tableau with its pivot highlighted."""

from __future__ import annotations

from fractions import Fraction

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QBrush, QFont

from ..core.formatting import number
from ..core.simplex import Tableau
from . import theme


def format_value(value: float | None, as_fraction: bool) -> str:
    if value is None:
        return ""
    if as_fraction:
        fraction = Fraction(value).limit_denominator(1_000)
        if abs(float(fraction) - value) < 1e-9 * max(1.0, abs(value)) and abs(fraction.numerator) < 1_000_000:
            text = str(fraction.numerator) if fraction.denominator == 1 else f"{fraction.numerator}/{fraction.denominator}"
            return text.replace("-", "−")
    if abs(value) < 5e-10:
        return "0"
    if abs(value - round(value)) < 1e-9:
        return number(round(value), 0)
    return number(value, 4 if abs(value) < 1 else 2)


class TableauModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self.tableau: Tableau | None = None
        self.as_fraction = False

    def set_tableau(self, tableau: Tableau | None, as_fraction: bool | None = None) -> None:
        self.beginResetModel()
        self.tableau = tableau
        if as_fraction is not None:
            self.as_fraction = as_fraction
        self.endResetModel()

    # Layout: CB | VB | columns... | bi | ratio ; rows: Cj, basis rows..., Zj, Cj - Zj
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if self.tableau is None else len(self.tableau.basis) + 3

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if self.tableau is None else len(self.tableau.column_names) + 4

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if self.tableau is None or orientation != Qt.Orientation.Horizontal:
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            names = ["CB", "VB", *self.tableau.column_names, "bi", "Razón"]
            return names[section]
        if role == Qt.ItemDataRole.ForegroundRole and self._column(section) == self.tableau.entering:
            return QBrush(theme.qcolor(theme.PAPRIKA))
        return None

    def _column(self, section: int) -> int | None:
        """Index into ``tableau.column_names`` for a model column, or None."""
        index = section - 2
        return index if self.tableau and 0 <= index < len(self.tableau.column_names) else None

    def _cell(self, row: int, section: int):
        t = self.tableau
        m = len(t.basis)
        column = self._column(section)
        last = len(t.column_names) + 2
        if row == 0:
            return {1: "Cj"}.get(section) if column is None else t.cj[column]
        if row <= m:
            i = row - 1
            if section == 0:
                return t.cb[i]
            if section == 1:
                return t.basis[i]
            if column is not None:
                return t.rows[i][column]
            if section == last:
                return t.rhs[i]
            return t.ratios[i] if t.ratios else None
        if row == m + 1:
            if section == 1:
                return "Zj"
            if column is not None:
                return t.zj[column]
            return t.z if section == last else None
        if section == 1:
            return "Cj − Zj"
        return t.reduced_costs[column] if column is not None else None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if self.tableau is None or not index.isValid():
            return None
        row, section = index.row(), index.column()
        t = self.tableau
        m = len(t.basis)
        column = self._column(section)
        is_pivot_row = t.leaving is not None and row == t.leaving + 1
        is_pivot_column = column is not None and column == t.entering and 1 <= row <= m + 2
        is_pivot = is_pivot_row and is_pivot_column
        is_summary = row == 0 or row > m

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._cell(row, section)
            return value if isinstance(value, str) else format_value(value, self.as_fraction)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignCenter)
        if role == Qt.ItemDataRole.BackgroundRole:
            if is_pivot:
                return QBrush(theme.qcolor(theme.PAPRIKA))
            if is_pivot_row:
                return QBrush(theme.qcolor(theme.PAPRIKA_TINT))
            if is_pivot_column:
                return QBrush(theme.qcolor(theme.SAFFRON_TINT))
            if is_summary:
                return QBrush(theme.qcolor(theme.SURFACE_ALT))
            return None
        if role == Qt.ItemDataRole.ForegroundRole:
            if is_pivot:
                return QBrush(theme.qcolor("#FFF6EA"))
            if section in (0, 1) and is_summary:
                return QBrush(theme.qcolor(theme.MUTED))
            if section == len(t.column_names) + 3:
                return QBrush(theme.qcolor(theme.MUTED))
            return QBrush(theme.qcolor(theme.INK))
        if role == Qt.ItemDataRole.FontRole:
            font = theme.mono_font(9)
            if section == 1 or is_pivot or (row == m + 2 and column == t.entering and column is not None):
                font.setWeight(QFont.Weight.Bold)
            return font
        if role == Qt.ItemDataRole.ToolTipRole and is_pivot:
            return "Elemento pivote"
        return None
