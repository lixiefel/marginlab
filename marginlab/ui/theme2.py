"""
marginlab.ui.theme2
───────────────────────────────────────────────────────────────────────────
Design system for the WORKSPACE (input) side — a dark, sophisticated "cockpit"
that feels like proprietary consulting software, deliberately distinct from the
light editorial client report.

Palette: near-black ink canvas, warm off-white text, ochre accent, with
restrained semantic greens/rusts. Fraunces display, Inter body, JetBrains Mono
data. Streamlit's native widgets are heavily restyled so nothing reads as a
generic form.
"""

from __future__ import annotations
import streamlit as st

TOK = {
    "bg":       "#0E0F13",   # near-black canvas
    "bg-2":     "#16181F",   # raised panel
    "bg-3":     "#1E212B",   # input wells
    "ink":      "#F5F2EB",   # warm off-white text
    "ink-2":    "#C9CCD4",
    "slate":    "#8A90A0",
    "slate-2":  "#5E6472",
    "ochre":    "#C9A063",
    "ochre-d":  "#A8814A",
    "ochre-l":  "#E8D4AC",
    "green":    "#6FA06F",
    "rust":     "#C06A5A",
    "line":     "#262934",
    "line-2":   "#1B1E27",
}

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;"
         "1,9..144,300;1,9..144,400&family=Inter:wght@300;400;500;600&"
         "family=JetBrains+Mono:wght@400;500&display=swap")


def _vars():
    return "\n".join(f"  --{k}:{v};" for k, v in TOK.items())


def inject():
    css = f"""<style>
@import url('{FONTS}');
:root{{
{_vars()}
  --ease:cubic-bezier(.19,1,.22,1);
  --sh:0 1px 2px rgba(0,0,0,.4),0 8px 24px rgba(0,0,0,.28);
}}
@keyframes mlrise{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
@keyframes mlglow{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}

html,body,[data-testid="stAppViewContainer"]{{background:var(--bg)!important}}
[data-testid="stAppViewContainer"]{{
  background:
    radial-gradient(1100px 500px at 80% -8%,rgba(201,160,99,.08),transparent 60%),
    radial-gradient(900px 600px at -5% 105%,rgba(201,160,99,.04),transparent 55%),
    var(--bg)!important;
}}
.block-container{{max-width:1120px;padding-top:2rem;padding-bottom:5rem;animation:mlrise .6s var(--ease) both}}
[data-testid="stHeader"]{{background:transparent}}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stSidebar"]{{display:none!important}}

*{{font-family:'Inter',system-ui,sans-serif}}
h1,h2,h3,h4{{font-family:'Fraunces',serif!important;color:var(--ink);font-weight:400;letter-spacing:-.015em}}
p,span,div,label,li{{color:var(--ink-2)}}
.stMarkdown p{{color:var(--ink-2);line-height:1.6}}

/* buttons */
.stButton>button,.stDownloadButton>button{{
  font-family:'JetBrains Mono',monospace!important;font-size:11.5px!important;
  letter-spacing:.14em;text-transform:uppercase;
  background:var(--ochre)!important;color:#1A1408!important;border:1px solid var(--ochre)!important;
  border-radius:8px!important;padding:.6rem 1.4rem!important;transition:all .25s var(--ease)!important;
  font-weight:500!important;box-shadow:var(--sh)!important;
}}
.stButton>button:hover,.stDownloadButton>button:hover{{
  background:var(--ochre-l)!important;border-color:var(--ochre-l)!important;
  transform:translateY(-2px);box-shadow:0 6px 20px rgba(201,160,99,.3)!important;
}}
button[kind="secondary"]{{
  background:transparent!important;color:var(--ink-2)!important;border:1px solid var(--line)!important;
}}
button[kind="secondary"]:hover{{border-color:var(--ochre)!important;color:var(--ink)!important;background:var(--bg-2)!important}}

/* inputs */
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,.stTextArea textarea{{
  background:var(--bg-3)!important;border:1px solid var(--line)!important;border-radius:9px!important;
  color:var(--ink)!important;font-family:'Inter',sans-serif!important;
}}
[data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,.stTextArea textarea:focus{{
  border-color:var(--ochre)!important;box-shadow:0 0 0 3px rgba(201,160,99,.15)!important;
}}
[data-baseweb="select"]>div{{background:var(--bg-3)!important;border-color:var(--line)!important;color:var(--ink)!important}}
label,.stMarkdown label{{font-family:'JetBrains Mono',monospace!important;font-size:10px!important;
  letter-spacing:.12em;text-transform:uppercase;color:var(--slate)!important;font-weight:400}}
::placeholder{{color:var(--slate-2)!important}}

/* data editor → dark data grid */
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{{
  border:1px solid var(--line)!important;border-radius:12px;overflow:hidden;box-shadow:var(--sh);
}}
[data-testid="stDataFrame"] *,[data-testid="stDataEditor"] *{{font-family:'Inter',sans-serif}}
.glideDataEditor{{--gdg-bg-cell:var(--bg-2)!important;--gdg-bg-header:var(--bg-3)!important;
  --gdg-text-dark:var(--ink)!important;--gdg-text-header:var(--slate)!important;
  --gdg-border-color:var(--line)!important;--gdg-bg-cell-medium:var(--bg-3)!important}}

/* tabs */
.stTabs [data-baseweb="tab-list"]{{gap:4px;border-bottom:1px solid var(--line)}}
.stTabs [data-baseweb="tab"]{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--slate);padding:10px 18px}}
.stTabs [aria-selected="true"]{{color:var(--ink)!important;border-bottom:2px solid var(--ochre)!important}}

/* sliders */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]{{background:var(--ochre)!important}}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div{{background:var(--ochre)!important}}

/* alerts */
[data-testid="stAlert"]{{background:var(--bg-2)!important;border:1px solid var(--line)!important;border-radius:10px;color:var(--ink-2)}}

/* ── ML components (dark) ─────────────────────────────────── */
.d-eyebrow{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.28em;
  text-transform:uppercase;color:var(--ochre);margin-bottom:14px}}
.d-h1{{font-family:'Fraunces',serif;font-weight:300;font-size:42px;line-height:1.05;
  color:var(--ink);letter-spacing:-.02em;margin:0 0 10px}}
.d-h1 em{{font-style:italic;color:var(--ochre)}}
.d-lede{{font-size:15.5px;color:var(--slate);line-height:1.6;max-width:62ch}}

.d-sec{{font-family:'JetBrains Mono',monospace;font-size:10.5px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--slate);margin:34px 0 16px;padding-bottom:9px;
  border-bottom:1px solid var(--line);display:flex;justify-content:space-between}}
.d-sec span:last-child{{color:var(--slate-2)}}

.d-metric{{background:var(--bg-2);border:1px solid var(--line);border-radius:13px;padding:20px 22px;
  position:relative;overflow:hidden;transition:transform .25s var(--ease),box-shadow .25s var(--ease)}}
.d-metric:hover{{transform:translateY(-3px);box-shadow:var(--sh)}}
.d-metric::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;background:var(--ochre)}}
.d-metric .k{{font-family:'JetBrains Mono',monospace;font-size:9.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--slate);margin-bottom:10px}}
.d-metric .v{{font-family:'Fraunces',serif;font-size:30px;font-weight:500;color:var(--ink);line-height:1}}
.d-metric .v.it{{font-style:italic;font-weight:300}}
.d-metric .s{{font-size:12px;color:var(--slate);margin-top:8px}}
.d-metric.glow{{background:linear-gradient(135deg,#1A1D26,#14161D);border-color:var(--ochre-d)}}
.d-metric.glow .v{{color:var(--ochre-l)}}

.d-divider{{height:1px;background:var(--line);margin:24px 0;border:none}}

/* top nav */
.d-topbar{{display:flex;justify-content:space-between;align-items:center;padding:4px 0 2px;animation:mlrise .5s var(--ease) both}}
.d-brand .wm{{font-family:'Fraunces',serif;font-style:italic;font-size:24px;color:var(--ink);letter-spacing:-.01em}}
.d-brand .tag{{font-family:'JetBrains Mono',monospace;font-size:8.5px;letter-spacing:.26em;
  text-transform:uppercase;color:var(--ochre);margin-top:2px}}
.d-eng{{text-align:right}}
.d-eng .k{{font-family:'JetBrains Mono',monospace;font-size:8.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--slate-2)}}
.d-eng .v{{font-family:'Fraunces',serif;font-size:16px;color:var(--ink);margin-top:2px}}

.d-navwrap{{margin:16px 0 10px}}
.d-navwrap .stButton>button{{width:100%;background:transparent!important;border:none!important;
  border-bottom:2px solid var(--line)!important;border-radius:0!important;color:var(--slate)!important;
  padding:.55rem .2rem!important;font-size:10px!important;letter-spacing:.06em;box-shadow:none!important}}
.d-navwrap .stButton>button:hover{{color:var(--ink)!important;border-bottom-color:var(--ochre-d)!important;
  transform:none!important;background:transparent!important}}
.d-navwrap .on .stButton>button{{color:var(--ink)!important;border-bottom:2px solid var(--ochre)!important;font-weight:600}}
.d-navwrap .ok .stButton>button{{color:var(--ochre)!important}}
.d-prog{{height:2px;background:var(--line);border-radius:99px;overflow:hidden;margin:6px 0 28px}}
.d-prog .f{{height:100%;background:linear-gradient(90deg,var(--ochre-d),var(--ochre));transition:width .6s var(--ease)}}

/* readiness chips */
.d-chip{{display:inline-flex;align-items:center;gap:7px;font-family:'JetBrains Mono',monospace;
  font-size:10px;letter-spacing:.08em;text-transform:uppercase;padding:6px 13px;border-radius:99px;
  border:1px solid var(--line);background:var(--bg-2);color:var(--slate)}}
.d-chip .dot{{width:7px;height:7px;border-radius:50%}}
.d-chip.ok{{color:var(--green)}}.d-chip.ok .dot{{background:var(--green)}}
.d-chip.bad{{color:var(--rust)}}.d-chip.bad .dot{{background:var(--rust);animation:mlglow 1.6s infinite}}

/* cover */
.d-cover{{text-align:center;padding:80px 20px 40px;animation:mlrise .8s var(--ease) both}}
.d-cover .wm{{font-family:'Fraunces',serif;font-style:italic;font-size:72px;color:var(--ink);letter-spacing:-.03em;line-height:1}}
.d-cover .tag{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:.34em;text-transform:uppercase;color:var(--ochre);margin-top:16px}}
.d-cover .lede{{font-size:17px;color:var(--slate);max-width:52ch;margin:24px auto 0;line-height:1.65}}
</style>"""
    if hasattr(st, "html"):
        st.html(css)
    else:
        st.markdown(css, unsafe_allow_html=True)


# ── helpers ──────────────────────────────────────────────────────────────────
def header(eyebrow, title_html, lede=""):
    l = f'<div class="d-lede">{lede}</div>' if lede else ""
    st.markdown(f'<div style="margin-bottom:24px"><div class="d-eyebrow">{eyebrow}</div>'
                f'<div class="d-h1">{title_html}</div>{l}</div>', unsafe_allow_html=True)


def section(label, right=""):
    st.markdown(f'<div class="d-sec"><span>{label}</span><span>{right}</span></div>', unsafe_allow_html=True)


def metric(k, v, s="", glow=False, italic=False):
    cls = "d-metric glow" if glow else "d-metric"
    vcls = "v it" if italic else "v"
    sub = f'<div class="s">{s}</div>' if s else ""
    st.markdown(f'<div class="{cls}"><div class="k">{k}</div><div class="{vcls}">{v}</div>{sub}</div>',
                unsafe_allow_html=True)


def chip(text, kind="neutral"):
    return f'<span class="d-chip {kind}"><span class="dot"></span>{text}</span>'


def divider():
    st.markdown('<hr class="d-divider">', unsafe_allow_html=True)


def topbar(engagement=""):
    eng = (f'<div class="d-eng"><div class="k">Engagement</div><div class="v">{engagement}</div></div>'
           if engagement else "")
    st.markdown(f'<div class="d-topbar"><div class="d-brand"><div class="wm">MarginLab</div>'
                f'<div class="tag">Pricing Intelligence</div></div>{eng}</div>', unsafe_allow_html=True)


def progress(cur, total):
    pct = ((cur + 1) / total) * 100
    st.markdown(f'<div class="d-prog"><div class="f" style="width:{pct:.0f}%"></div></div>',
                unsafe_allow_html=True)
