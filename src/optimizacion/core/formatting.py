"""Number formatting with Colombian conventions (``.`` thousands, ``,`` decimals)."""

from __future__ import annotations

import math


def number(value: float, decimals: int = 2) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "—"
    if math.isinf(value):
        return "∞" if value > 0 else "−∞"
    if abs(value) < 0.5 * 10 ** (-decimals):
        value = 0.0
    text = f"{value:,.{decimals}f}"
    text = text.replace(",", "_").replace(".", ",").replace("_", ".")
    return text.replace("-", "−")


def money(value: float, decimals: int = 2) -> str:
    text = number(value, decimals)
    if text.startswith("−"):
        return "−$ " + text[1:]
    if text in ("—", "∞"):
        return text
    return "$ " + text


def interval(bounds: tuple[float, float] | None, decimals: int = 2) -> str:
    if bounds is None:
        return "—"
    return f"[{number(bounds[0], decimals)} ; {number(bounds[1], decimals)}]"
