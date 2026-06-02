"""
marginlab.ui.serialize
───────────────────────────────────────────────────────────────────────────
Turns the engine's AuditResult into a plain dict / JSON payload that the
bespoke animated report component consumes. Keeps all formatting decisions
(currency, signs, percentages) in one place so the JS layer stays dumb.
"""

from __future__ import annotations
import json

from ..engine.constants import CURRENCY_SYMBOL, LARGE_DENOM


def _sym(cur):
    return CURRENCY_SYMBOL.get(cur, "")


def _money(v, cur, decimals=None):
    if v is None:
        return "—"
    if decimals is None:
        decimals = cur not in LARGE_DENOM
    s = _sym(cur)
    return f"{s}{v:,.2f}" if decimals else f"{s}{v:,.0f}"


def audit_to_dict(audit, client: dict, currency: str) -> dict:
    cur = currency
    decimals = cur not in LARGE_DENOM
    sym = _sym(cur)

    items = []
    for r in audit.items:
        margin_pct = (r.price_from - r.cost) / r.price_from if r.price_from else 0
        base_profit = (r.price_from - r.cost) * r.monthly_units
        items.append(dict(
            name=r.name, category=r.category, role=r.role,
            quadrant=r.quadrant, action=r.action, market=r.market,
            phase=r.phase if r.action != "Hold" else "—",
            confidence=r.confidence, source=r.source,
            elasticity=round(r.elasticity, 2),
            price_from=r.price_from, price_to=r.price_to,
            price_from_fmt=_money(r.price_from, cur), price_to_fmt=_money(r.price_to, cur),
            delta_pct=round(r.delta_pct * 100, 1),
            delta_profit_mo=round(r.delta_profit_mo, 1),
            delta_profit_fmt=_money(r.delta_profit_mo, cur),
            monthly_units=r.monthly_units,
            margin_pct=round(margin_pct * 100, 1),
            base_profit=round(base_profit, 1),
            base_profit_fmt=_money(base_profit, cur),
            comp_min=r.comp_min, comp_max=r.comp_max, comp_avg=r.comp_avg,
            comp_min_fmt=_money(r.comp_min, cur) if r.comp_min else None,
            comp_max_fmt=_money(r.comp_max, cur) if r.comp_max else None,
            narrative=r.narrative,
        ))

    n_raise = sum(1 for r in audit.items if r.action == "Raise")
    n_cut = sum(1 for r in audit.items if r.action == "Cut")
    n_hold = sum(1 for r in audit.items if r.action == "Hold")
    above = sum(1 for r in audit.items if "Above" in r.market)
    within = sum(1 for r in audit.items if "Within" in r.market)
    below = sum(1 for r in audit.items if "Below" in r.market)

    return dict(
        meta=dict(
            cafe=(client.get("name") or "This café").strip(),
            concept=(client.get("concept") or "").strip(),
            location=(client.get("location") or "").strip(),
            currency=cur, symbol=sym, decimals=decimals,
            n_items=len(audit.items),
        ),
        headline=dict(
            monthly_lift=round(audit.monthly_lift, 1),
            monthly_lift_fmt=_money(abs(audit.monthly_lift), cur),
            monthly_lift_signed=("+" if audit.monthly_lift >= 0 else "−"),
            annual=round(abs(audit.monthly_lift) * 12, 1),
            annual_fmt=_money(abs(audit.monthly_lift) * 12, cur),
            baseline=round(audit.baseline_profit_mo, 1),
            baseline_fmt=_money(audit.baseline_profit_mo, cur),
            projected=round(audit.baseline_profit_mo + audit.monthly_lift, 1),
            projected_fmt=_money(audit.baseline_profit_mo + audit.monthly_lift, cur),
            lift_pct=round(audit.lift_pct * 100, 1),
            confidence=audit.confidence,
            changes_count=audit.changes_count,
            best_item=audit.best_item,
        ),
        mix=dict(n_raise=n_raise, n_cut=n_cut, n_hold=n_hold,
                 above=above, within=within, below=below),
        sensitivity=dict(
            conservative=round(audit.sens_conservative, 1),
            baseline=round(audit.sens_baseline, 1),
            optimistic=round(audit.sens_optimistic, 1),
            conservative_fmt=_money(abs(audit.sens_conservative), cur),
            baseline_fmt=_money(abs(audit.sens_baseline), cur),
            optimistic_fmt=_money(abs(audit.sens_optimistic), cur),
            robust=audit.sens_robust,
        ),
        engineering=dict(
            med_units=audit.med_units,
            med_margin_pct=round(audit.med_margin_pct * 100, 1),
        ),
        items=items,
    )


def audit_to_json(audit, client: dict, currency: str) -> str:
    return json.dumps(audit_to_dict(audit, client, currency), ensure_ascii=False)
