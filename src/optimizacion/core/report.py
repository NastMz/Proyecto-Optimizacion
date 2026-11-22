"""Managerial report (Spanish HTML) generated from a solved scenario."""

from __future__ import annotations

from html import escape

from .case_study import CONSTRAINT_GROUPS, GROUP_LABELS, Parameter
from .formatting import interval, money, number
from .scenarios import Scenario

_UNITS = {Parameter.RAW_MATERIAL: "gramo", Parameter.BUDGET: "peso", Parameter.DEMAND: "unidad"}


def build_report(
    scenario: Scenario, accent: str = "#B5462A", muted: str = "#7A6A5E", heading_font: str = "Georgia, serif"
) -> str:
    case = scenario.case
    result = scenario.result
    heading = f"font-family:{heading_font};font-weight:normal"
    title = f"<h1 style='color:{accent};margin-bottom:0;{heading}'>Plan de producción diario</h1>"
    subtitle = f"<p style='color:{muted};margin-top:2px'>{escape(case.company)} · {escape(scenario.label)}</p>"
    if not result.is_optimal or scenario.sensitivity is None:
        reason = "no tiene solución factible" if result.status.value == "infeasible" else "no está acotado"
        return f"<html><body>{title}{subtitle}<p>Con los parámetros actuales el modelo {reason}.</p></body></html>"

    sensitivity = scenario.sensitivity
    total = result.objective
    parts = [title, subtitle]
    parts.append(
        f"<p>Para maximizar la utilidad de la empresa en <b>{money(total)}</b> diarios, "
        "se deben vender las siguientes cantidades de cada producto al día:</p>"
    )
    parts.append("<table width='100%' cellspacing='0' cellpadding='6'>")
    parts.append(
        f"<tr style='color:{muted}'><th align='left'>Producto</th><th align='right'>Unidades/día</th>"
        "<th align='right'>Utilidad</th><th align='right'>Participación</th></tr>"
    )
    for product, value in zip(case.products, result.values):
        contribution = product.profit * value
        share = 100 * contribution / total if total else 0.0
        parts.append(
            f"<tr><td>{escape(product.name)}</td><td align='right'><b>{number(value)}</b></td>"
            f"<td align='right'>{money(contribution)}</td><td align='right'>{number(share, 1)} %</td></tr>"
        )
    parts.append("</table>")

    parts.append(f"<h2 style='{heading}'>Recursos y precios sombra</h2>")
    parts.append(
        "<p>El precio sombra indica cuánto cambia la utilidad diaria si se aumenta en una unidad el lado "
        "derecho de la restricción, mientras el valor se mantenga dentro del rango indicado.</p>"
    )
    for group in CONSTRAINT_GROUPS:
        parts.append(f"<h3>{GROUP_LABELS[group]}</h3><ul>")
        for i, product in enumerate(case.products):
            item = sensitivity.constraints[case.constraint_index(group, i)]
            unit = _UNITS[group]
            if item.is_binding and abs(item.shadow_price) > 0:
                verb = "aumenta" if item.shadow_price > 0 else "disminuye"
                text = (
                    f"Restricción <b>activa</b>. Cada {unit} adicional {verb} la utilidad en "
                    f"<b>{money(abs(item.shadow_price))}</b> (válido entre {interval(item.rhs_range)})."
                )
            else:
                text = (
                    f"Holgura de {number(item.slack)}; aumentar este recurso no cambia la utilidad "
                    f"(precio sombra $ 0, válido entre {interval(item.rhs_range)})."
                )
            parts.append(f"<li><b>{escape(product.name)}:</b> {text}</li>")
        parts.append("</ul>")

    parts.append(f"<h2 style='{heading}'>Rangos de optimalidad de la utilidad unitaria</h2><ul>")
    for product, variable in zip(case.products, sensitivity.variables):
        parts.append(
            f"<li><b>{escape(product.name)}:</b> el plan se mantiene mientras la utilidad por unidad esté en "
            f"{interval(variable.objective_range)} (actual {money(product.profit)}).</li>"
        )
    parts.append("</ul>")
    return "<html><body>" + "".join(parts) + "</body></html>"
