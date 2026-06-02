"""Pages 3–5,7: the animated client report (seamless scroll). Page 6: scenarios (dark)."""
from __future__ import annotations
import streamlit as st
import streamlit.components.v1 as components

from .. import theme2 as T
from ..state import goto, rows_to_items, symbol
from ..serialize import audit_to_dict
from ..report_component import build_report_html
from ...engine import run_audit, Settings


def _audit():
    items = rows_to_items(st.session_state.rows)
    audit = run_audit(items, st.session_state.settings,
                      demo_mode=st.session_state.get("demo_mode", False))
    st.session_state.audit = audit
    return audit


def _render_report(scroll_to=None):
    audit = _audit()
    if audit.banner:
        st.warning(audit.banner)
    payload = audit_to_dict(audit, st.session_state.client, st.session_state.settings.currency)
    if scroll_to:
        payload["_scroll"] = scroll_to
    html = build_report_html(payload)
    # generous height; the report manages its own internal scroll/reveal
    components.html(html, height=5200, scrolling=True)


# steps 3,4,5,7 all show the seamless report (it IS the deliverable)
def render_analysis():
    _nav_top()
    _render_report()
    _nav_bottom(2)

def render_opportunities():
    _nav_top()
    _render_report()
    _nav_bottom(3)

def render_recommend():
    _nav_top()
    _render_report()
    _nav_bottom(4)


def render_review():
    audit = _audit()
    payload = audit_to_dict(audit, st.session_state.client, st.session_state.settings.currency)
    components.html(build_report_html(payload), height=5200, scrolling=True)
    T.divider()
    b1, _, b3 = st.columns([1, 2, 1])
    with b1:
        if st.button("← Scenarios", width="stretch", type="secondary"):
            goto(5); st.rerun()
    with b3:
        _pdf_download(audit)


def _pdf_download(audit):
    from ..pdf_report import build_pdf
    cur = st.session_state.settings.currency
    try:
        data = build_pdf(audit, st.session_state.client, cur, symbol(cur))
        cafe = (st.session_state.client.get("name") or "cafe").strip()
        safe = "".join(ch for ch in cafe if ch.isalnum() or ch in " -_").strip().replace(" ", "_") or "cafe"
        st.download_button("Download client PDF", data, file_name=f"MarginLab_{safe}.pdf",
                           mime="application/pdf", width="stretch")
    except Exception as e:
        st.caption(f"PDF unavailable: {e}")


# ── scenarios (dark interactive) ─────────────────────────────────────────────
def render_scenario():
    s: Settings = st.session_state.settings
    sym = symbol(s.currency)
    T.header("06 · Scenario", "Scenario <em>testing</em>.",
             "Adjust the guardrails and watch the projected lift respond. The model's discipline, "
             "made visible — how aggressive the rebalance is stays under your control.")

    T.section("Guardrails", "applies live")
    c1, c2, c3 = st.columns(3)
    with c1: mr = st.slider("Max raise / item", 0.0, 0.25, float(s.max_raise), 0.01, format="%.0f%%")
    with c2: mc = st.slider("Max cut / item", -0.20, 0.0, float(s.max_cut), 0.01, format="%.0f%%")
    with c3: shl = st.slider("LOW-confidence shrinkage", 0.0, 1.0, float(s.shr_low), 0.05)
    s.max_raise, s.max_cut, s.shr_low = mr, mc, shl

    audit = _audit()
    from ..state import fmt_money, fmt_pct
    T.divider()
    k1, k2, k3 = st.columns(3)
    with k1: T.metric("Δ profit / month", fmt_money(audit.monthly_lift, s.currency),
                      f"{fmt_pct(audit.lift_pct, signed=True)} on profit", glow=True, italic=True)
    with k2: T.metric("Items changing", audit.changes_count)
    with k3: T.metric("Robust across scenarios?", audit.sens_robust,
                      "positive in all 3 cases" if audit.sens_robust == "Yes" else "review")

    T.divider()
    b1, _, b3 = st.columns([1, 2, 1])
    with b1:
        if st.button("← Recommendations", width="stretch", type="secondary"):
            goto(4); st.rerun()
    with b3:
        if st.button("Final review →", width="stretch"):
            goto(6); st.rerun()


# ── shared nav (report pages keep the workspace chrome minimal) ──────────────
def _nav_top():
    pass

def _nav_bottom(step):
    T.divider()
    b1, _, b3 = st.columns([1, 2, 1])
    labels = {2: ("← Menu & Cost", 1, "Opportunities →", 3),
              3: ("← Analysis", 2, "Recommendations →", 4),
              4: ("← Opportunities", 3, "Scenarios →", 5)}
    back_l, back_i, fwd_l, fwd_i = labels[step]
    with b1:
        if st.button(back_l, width="stretch", type="secondary", key=f"b{step}"):
            goto(back_i); st.rerun()
    with b3:
        if st.button(fwd_l, width="stretch", key=f"f{step}"):
            goto(fwd_i); st.rerun()
