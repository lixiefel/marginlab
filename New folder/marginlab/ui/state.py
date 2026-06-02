"""
marginlab.ui.state
───────────────────────────────────────────────────────────────────────────
Session state, currency formatting, demo data, and helpers shared across
all workflow pages. Keeps page modules thin and consistent.
"""

from __future__ import annotations
import streamlit as st

from ..engine import Item, Settings
from ..engine.constants import CURRENCY_SYMBOL, LARGE_DENOM


# ── workflow definition ──────────────────────────────────────────────────────
STEPS = [
    ("overview",      "Client"),
    ("input",         "Menu & Cost"),
    ("analysis",      "Analysis"),
    ("opportunities", "Opportunities"),
    ("recommend",     "Recommendations"),
    ("scenario",      "Scenarios"),
    ("review",        "Final Review"),
]
STEP_KEYS = [s[0] for s in STEPS]
STEP_LABELS = [s[1] for s in STEPS]


def init_state():
    ss = st.session_state
    ss.setdefault("step", 0)
    ss.setdefault("started", False)
    ss.setdefault("client", dict(name="", concept="", location="", contact="",
                                 seats="", daily_covers="", notes=""))
    ss.setdefault("settings", Settings())
    ss.setdefault("n_competitors", 3)
    ss.setdefault("rows", _demo_rows())          # list of dict rows for the editor
    ss.setdefault("audit", None)
    ss.setdefault("demo_mode", True)


def goto(step_index: int):
    st.session_state.step = max(0, min(len(STEPS) - 1, step_index))


# ── currency formatting ──────────────────────────────────────────────────────
def fmt_money(value: float, currency: str, *, decimals: bool | None = None) -> str:
    sym = CURRENCY_SYMBOL.get(currency, "")
    if decimals is None:
        decimals = currency not in LARGE_DENOM
    if value is None:
        return "—"
    if decimals:
        return f"{sym}{value:,.2f}"
    return f"{sym}{value:,.0f}"


def fmt_pct(value: float, signed: bool = False) -> str:
    if value is None:
        return "—"
    s = f"{value*100:.1f}%"
    if signed and value > 0:
        s = "+" + s
    return s


def symbol(currency: str) -> str:
    return CURRENCY_SYMBOL.get(currency, "")


# ── rows <-> engine Items ────────────────────────────────────────────────────
ROW_TEMPLATE = dict(Item="", Category="Coffee", Role="Core",
                    Cost=0.0, Price=0.0, Units=0)


def competitor_cols(n: int) -> list[str]:
    return [f"Comp {i+1}" for i in range(n)]


def rows_to_items(rows) -> list[Item]:
    items = []
    for r in rows:
        name = (r.get("Item") or "").strip()
        if not name:
            continue
        comps = []
        for k, v in r.items():
            if str(k).startswith("Comp"):
                fv = _f(v)
                if fv is not None:
                    comps.append(fv)
        items.append(Item(
            name=name,
            category=r.get("Category") or "Other",
            role=r.get("Role") or "Other",
            cost=float(r.get("Cost") or 0),
            price=float(r.get("Price") or 0),
            monthly_units=int(r.get("Units") or 0),
            competitors=comps,
        ))
    return items


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


# ── demo café (Neighborhood, Operating Manual Sim 1) ─────────────────────────
def _demo_rows():
    return [
        dict(Item="Espresso",      Category="Coffee",        Role="Traffic Driver", Cost=0.50, Price=2.80, Units=2400, **{"Comp 1":2.70,"Comp 2":2.90,"Comp 3":2.80}),
        dict(Item="Latte",         Category="Coffee",        Role="Core",           Cost=0.90, Price=3.80, Units=2100, **{"Comp 1":3.90,"Comp 2":4.10,"Comp 3":4.00}),
        dict(Item="Cappuccino",    Category="Coffee",        Role="Core",           Cost=0.80, Price=3.60, Units=1800, **{"Comp 1":3.70,"Comp 2":3.80,"Comp 3":3.60}),
        dict(Item="Flat White",    Category="Specialty Drink",Role="Profit Driver", Cost=0.95, Price=4.10, Units=1100, **{"Comp 1":4.30,"Comp 2":4.50,"Comp 3":4.20}),
        dict(Item="Croissant",     Category="Pastry",        Role="Complement",     Cost=1.10, Price=3.20, Units=1200, **{"Comp 1":3.10,"Comp 2":3.40,"Comp 3":3.20}),
        dict(Item="Avocado Toast", Category="Sandwich/Food", Role="Profit Driver",  Cost=2.80, Price=6.80, Units=750,  **{"Comp 1":7.00,"Comp 2":7.50,"Comp 3":6.90}),
        dict(Item="Cheesecake",    Category="Dessert",       Role="Signature",      Cost=1.90, Price=4.80, Units=600,  **{"Comp 1":5.00,"Comp 2":5.40,"Comp 3":5.10}),
    ]


def load_demo():
    st.session_state.rows = _demo_rows()
    st.session_state.settings = Settings(currency="USD")
    st.session_state.demo_mode = True
    st.session_state.client = dict(
        name="Demo — Neighborhood Café", concept="Specialty coffee + brunch",
        location="Sample data", contact="", seats="38", daily_covers="220",
        notes="Built-in synthetic café for demonstrating the workspace.")


def clear_all():
    st.session_state.rows = [dict(ROW_TEMPLATE) for _ in range(6)]
    st.session_state.demo_mode = False
    st.session_state.audit = None
    st.session_state.client = dict(name="", concept="", location="", contact="",
                                   seats="", daily_covers="", notes="")
