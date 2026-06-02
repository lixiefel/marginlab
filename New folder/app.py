"""
MarginLab — premium pricing consulting workspace
─────────────────────────────────────────────────────────────────────────────
Run:  streamlit run app.py

Dark editorial "cockpit" for the consultant (input/workspace) → a bespoke,
fully animated light client report (output). Native v10 engine behind it all.
"""

import streamlit as st

from marginlab.ui import theme2 as T
from marginlab.ui.state import init_state, STEP_LABELS, goto
from marginlab.ui.pages.intake import render_overview, render_input
from marginlab.ui.pages.analysis import (render_analysis, render_opportunities,
                                         render_recommend, render_scenario, render_review)

st.set_page_config(page_title="MarginLab · Pricing Workspace", page_icon="◆",
                   layout="wide", initial_sidebar_state="collapsed")

T.inject()
init_state()


def top_nav():
    T.topbar(st.session_state.client.get("name") or "")
    st.markdown('<div class="d-navwrap">', unsafe_allow_html=True)
    cols = st.columns(len(STEP_LABELS), gap="small")
    for i, (col, label) in enumerate(zip(cols, STEP_LABELS)):
        with col:
            done, active = i < st.session_state.step, i == st.session_state.step
            cls = "on" if active else ("ok" if done else "")
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            mark = "✓ " if done else ""
            if st.button(f"{mark}{i+1} · {label}", key=f"nav_{i}", width="stretch"):
                goto(i); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    T.progress(st.session_state.step, len(STEP_LABELS))


RENDERERS = {0: render_overview, 1: render_input, 2: render_analysis,
             3: render_opportunities, 4: render_recommend, 5: render_scenario,
             6: render_review}


def main():
    top_nav()
    RENDERERS[st.session_state.step]()


if __name__ == "__main__":
    main()
