"""Workspace pages 1–2 (dark cockpit): Client Overview, Menu & Cost."""
from __future__ import annotations
import streamlit as st

from .. import theme2 as T
from ..state import (goto, rows_to_items, load_demo, clear_all, symbol, competitor_cols)
from ...engine.constants import CATEGORIES, ROLES, CURRENCIES
from ...engine import Settings


def render_overview():
    T.header("01 · Engagement", "Client <em>overview</em>.",
             "Set the context for this pricing engagement. Everything downstream — the analysis, "
             "the recommendations, the client-facing report — is framed around this café.")

    c = st.session_state.client
    col1, col2 = st.columns(2, gap="large")
    with col1:
        T.section("Identity")
        c["name"] = st.text_input("Café name", c["name"], placeholder="e.g. PETAK 25")
        c["concept"] = st.text_input("Concept", c["concept"], placeholder="Specialty coffee + brunch")
        c["location"] = st.text_input("Location", c["location"], placeholder="Bintaro, Jakarta")
        c["contact"] = st.text_input("Owner / contact", c["contact"])
    with col2:
        T.section("Operating profile")
        c["seats"] = st.text_input("Seats", c["seats"], placeholder="38")
        c["daily_covers"] = st.text_input("Approx. daily covers", c["daily_covers"], placeholder="220")
        s: Settings = st.session_state.settings
        cur = st.selectbox("Currency", CURRENCIES,
                           index=CURRENCIES.index(s.currency) if s.currency in CURRENCIES else 0)
        s.currency = cur

    T.section("Engagement notes")
    c["notes"] = st.text_area("notes", c["notes"], height=88, label_visibility="collapsed",
                              placeholder="Context, constraints, owner priorities…")

    T.divider()
    d1, d2, d3 = st.columns([1, 1, 2])
    with d1:
        if st.button("Load demo café", width="stretch", type="secondary"):
            load_demo(); st.rerun()
    with d2:
        if st.button("Clear & start", width="stretch", type="secondary"):
            clear_all(); st.rerun()
    with d3:
        if st.button("Continue → Menu & Cost", width="stretch"):
            goto(1); st.rerun()


def render_input():
    s: Settings = st.session_state.settings
    sym = symbol(s.currency)
    T.header("02 · Data", "Menu &amp; <em>cost</em>.",
             "The analysis universe. Each item needs a cost, current price, and monthly units. "
             "Category sets the demand prior; role sets how far the model may move it. Add as many "
             "competitor prices as you have — they sharpen market positioning.")

    _, ctrl = st.columns([3, 1])
    with ctrl:
        n_comp = st.number_input("Competitor prices / item", 0, 8,
                                 value=st.session_state.get("n_competitors", 3), step=1)
        st.session_state.n_competitors = int(n_comp)
    comp_names = competitor_cols(int(n_comp))

    import pandas as pd
    rows = st.session_state.rows
    for r in rows:
        for cn in comp_names:
            r.setdefault(cn, None)
        for k in [k for k in list(r.keys()) if str(k).startswith("Comp") and k not in comp_names]:
            r.pop(k, None)
    order = ["Item", "Category", "Role", "Cost", "Price", "Units"] + comp_names
    df = pd.DataFrame(rows)
    for c in order:
        if c not in df.columns:
            df[c] = None
    df = df[order]

    colcfg = {
        "Item": st.column_config.TextColumn("Item", width="medium"),
        "Category": st.column_config.SelectboxColumn("Category", options=CATEGORIES, width="small"),
        "Role": st.column_config.SelectboxColumn("Role", options=ROLES, width="small"),
        "Cost": st.column_config.NumberColumn(f"Cost ({sym})", min_value=0.0, format="%.2f", width="small"),
        "Price": st.column_config.NumberColumn(f"Price ({sym})", min_value=0.0, format="%.2f", width="small"),
        "Units": st.column_config.NumberColumn("Units/mo", min_value=0, step=10, width="small"),
    }
    for cn in comp_names:
        colcfg[cn] = st.column_config.NumberColumn(cn, format="%.2f", width="small")

    edited = st.data_editor(df, num_rows="dynamic", width="stretch", height=420,
                            key="menu_editor", column_config=colcfg)
    st.session_state.rows = edited.to_dict("records")

    items = rows_to_items(st.session_state.rows)
    T.divider()
    T.section("Readiness", f"{len(items)} items configured")
    cost_bad = sum(1 for it in items if it.price > 0 and it.cost >= it.price)
    zero_u = sum(1 for it in items if it.monthly_units == 0)
    hard = (1 if cost_bad else 0) + (1 if zero_u else 0)

    k1, k2, k3, k4 = st.columns(4)
    with k1: T.metric("Items", str(len(items)))
    with k2: T.metric("Cost ≥ price", str(cost_bad), "needs review" if cost_bad else "clean")
    with k3: T.metric("Missing units", str(zero_u), "needs review" if zero_u else "clean")
    with k4:
        ready = hard == 0 and len(items) > 0
        T.metric("Status", "Ready" if ready else "Fix first",
                 "all checks pass" if ready else "see flags", glow=ready)

    T.divider()
    b1, _, b3 = st.columns([1, 2, 1])
    with b1:
        if st.button("← Client", width="stretch", type="secondary"):
            goto(0); st.rerun()
    with b3:
        disabled = len(items) == 0 or hard > 0
        if st.button("Run analysis →", width="stretch", disabled=disabled):
            goto(2); st.rerun()
