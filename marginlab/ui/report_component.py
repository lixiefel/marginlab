"""
marginlab.ui.report_component
───────────────────────────────────────────────────────────────────────────
THE SHOWPIECE. A bespoke, fully animated client report rendered inside a
components.html iframe — so real JS runs: animated count-up numbers, SVG
charts that draw themselves in on scroll, staggered reveals, hero parallax.

Light editorial luxury (gallery-calm): warm paper, deep ink, ochre accent,
Fraunces display + Inter text + JetBrains Mono data. No chart libraries —
every visual is hand-rolled SVG animated with the Web Animations API and
IntersectionObserver, for a bespoke "expensive" feel nothing off-the-shelf
matches.

Usage:
    from streamlit.components.v1 import html as st_html
    from .report_component import build_report_html
    st_html(build_report_html(payload), height=H, scrolling=True)
"""

from __future__ import annotations
import json

# The CSS is large and deliberate. Kept as a module constant.
_CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --paper:#FBF9F5; --paper-2:#F4EFE6; --ink:#13151A; --ink-2:#2A2E38;
  --slate:#6B7280; --slate-2:#9AA1AD; --ochre:#B8935C; --ochre-d:#9A7842;
  --ochre-l:#E8D9BE; --green:#4F6B52; --green-l:#DCE6DC; --rust:#A04A3C;
  --rust-l:#F0DBD5; --line:#E7E0D3; --line-2:#F0EBE0;
  --serif:'Fraunces',Georgia,serif; --sans:'Inter',system-ui,sans-serif;
  --mono:'JetBrains Mono',monospace;
  --ease:cubic-bezier(.19,1,.22,1);
}
html{scroll-behavior:smooth}
body{
  background:var(--paper); color:var(--ink); font-family:var(--sans);
  -webkit-font-smoothing:antialiased; overflow-x:hidden; line-height:1.6;
}
.wrap{max-width:980px;margin:0 auto;padding:0 32px 120px}

/* ── reveal system ─────────────────────────────────────────── */
.reveal{opacity:0;transform:translateY(28px);transition:opacity 1s var(--ease),transform 1s var(--ease)}
.reveal.in{opacity:1;transform:none}
.reveal.d1{transition-delay:.08s}.reveal.d2{transition-delay:.16s}
.reveal.d3{transition-delay:.24s}.reveal.d4{transition-delay:.32s}
.reveal.d5{transition-delay:.40s}.reveal.d6{transition-delay:.48s}

/* ── hero ──────────────────────────────────────────────────── */
.hero{position:relative;padding:120px 0 80px;text-align:center;overflow:hidden}
.hero-orbit{position:absolute;inset:0;pointer-events:none;z-index:0}
.hero-orbit span{position:absolute;border-radius:50%;border:1px solid var(--line);opacity:.5}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.36em;text-transform:uppercase;
  color:var(--ochre-d);margin-bottom:30px;position:relative;z-index:1}
.hero h1{font-family:var(--serif);font-weight:300;font-size:clamp(40px,7vw,76px);
  line-height:1.02;letter-spacing:-.025em;position:relative;z-index:1}
.hero h1 em{font-style:italic;color:var(--ochre-d)}
.hero .sub{margin-top:26px;font-size:17px;color:var(--slate);max-width:50ch;
  margin-left:auto;margin-right:auto;position:relative;z-index:1}
.hero .meta{margin-top:38px;display:flex;gap:34px;justify-content:center;flex-wrap:wrap;
  position:relative;z-index:1}
.hero .meta .m{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--slate-2)}
.hero .meta .m b{display:block;font-family:var(--serif);font-size:19px;color:var(--ink);
  letter-spacing:0;text-transform:none;margin-top:6px;font-weight:500}
.scroll-cue{margin-top:64px;position:relative;z-index:1}
.scroll-cue .line{width:1px;height:46px;margin:0 auto;background:linear-gradient(var(--ochre),transparent);
  animation:cue 2.4s var(--ease) infinite}
@keyframes cue{0%{transform:scaleY(0);transform-origin:top}50%{transform:scaleY(1);transform-origin:top}
  50.1%{transform-origin:bottom}100%{transform:scaleY(0);transform-origin:bottom}}

/* ── the number ────────────────────────────────────────────── */
.bignum{padding:40px 0 30px;text-align:center}
.bignum .k{font-family:var(--mono);font-size:11px;letter-spacing:.24em;text-transform:uppercase;
  color:var(--ochre-d);margin-bottom:22px}
.bignum .v{font-family:var(--serif);font-style:italic;font-weight:300;
  font-size:clamp(64px,13vw,150px);line-height:.9;letter-spacing:-.03em;color:var(--ink)}
.bignum .u{margin-top:24px;font-size:15px;color:var(--slate)}
.bignum .u b{color:var(--ochre-d);font-weight:600}

/* ── section heading ───────────────────────────────────────── */
.sec{display:flex;justify-content:space-between;align-items:baseline;
  padding-bottom:16px;border-bottom:1px solid var(--line);margin:96px 0 44px}
.sec .n{font-family:var(--mono);font-size:12px;letter-spacing:.1em;color:var(--ochre-d)}
.sec h2{font-family:var(--serif);font-weight:400;font-size:clamp(26px,4vw,40px);
  letter-spacing:-.02em;flex:1;margin-left:24px}
.sec .r{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--slate-2)}

/* ── kpi strip ─────────────────────────────────────────────── */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:16px;overflow:hidden}
.kpi{background:var(--paper);padding:28px 24px}
.kpi .k{font-family:var(--mono);font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--slate-2);margin-bottom:14px}
.kpi .v{font-family:var(--serif);font-size:34px;font-weight:500;line-height:1;letter-spacing:-.01em}
.kpi .v.it{font-style:italic;font-weight:300}
.kpi .s{font-size:12px;color:var(--slate);margin-top:10px}
.kpi.hero-kpi{background:var(--ink)}
.kpi.hero-kpi .k{color:var(--ochre)}
.kpi.hero-kpi .v,.kpi.hero-kpi .s{color:var(--paper)}

/* ── cards ─────────────────────────────────────────────────── */
.cards{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.card{background:var(--paper);border:1px solid var(--line);border-left:2px solid var(--ochre);
  border-radius:12px;padding:26px 28px;transition:transform .5s var(--ease),box-shadow .5s var(--ease)}
.card:hover{transform:translateY(-4px);box-shadow:0 22px 50px rgba(19,21,26,.08)}
.card .h{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--ochre-d);margin-bottom:12px}
.card .b{font-family:var(--serif);font-size:18px;line-height:1.45;font-weight:400}
.card .b b{color:var(--ochre-d);font-weight:600}

/* ── chart frames ──────────────────────────────────────────── */
.chart{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:30px}
.chart svg{display:block;width:100%;height:auto;overflow:visible}
.legend{display:flex;gap:22px;flex-wrap:wrap;margin-top:22px;justify-content:center}
.legend .li{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:10px;
  letter-spacing:.08em;text-transform:uppercase;color:var(--slate)}
.legend .dot{width:11px;height:11px;border-radius:3px}

/* svg text */
.svg-lab{font-family:var(--mono);font-size:10px;fill:var(--slate);letter-spacing:.04em}
.svg-nm{font-family:var(--serif);font-size:13px;fill:var(--ink)}
.svg-val{font-family:var(--mono);font-size:11px;fill:var(--ink-2)}
.svg-axis{stroke:var(--line);stroke-width:1}
.svg-grid{stroke:var(--line-2);stroke-width:1}

/* ── before/after rows ─────────────────────────────────────── */
.baf{display:flex;flex-direction:column;gap:2px}
.baf .row{display:grid;grid-template-columns:160px 1fr 116px;align-items:center;gap:20px;
  padding:16px 6px;border-bottom:1px solid var(--line-2)}
.baf .nm{font-family:var(--serif);font-size:16px;font-weight:500}
.baf .nm small{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--slate-2);margin-top:4px;font-weight:400}
.baf .track{position:relative;height:34px}
.baf .bar{position:absolute;height:9px;border-radius:99px;top:4px}
.baf .bar.now{background:var(--paper-2);border:1px solid var(--line)}
.baf .bar.to{top:18px}
.baf .bar.to.raise{background:var(--ochre)}
.baf .bar.to.cut{background:var(--rust)}
.baf .bar.to.hold{background:var(--ink-2)}
.baf .pl{position:absolute;font-family:var(--mono);font-size:10px;color:var(--slate);
  top:0;transform:translateY(-1px)}
.baf .pl.to{top:14px;color:var(--ink-2)}
.baf .delta{text-align:right}
.baf .delta .p{font-family:var(--serif);font-size:21px;font-weight:500}
.baf .delta .p.up{color:var(--green)}.baf .delta .p.dn{color:var(--rust)}.baf .delta .p.fl{color:var(--slate-2)}
.baf .delta .pf{font-family:var(--mono);font-size:10px;color:var(--slate);margin-top:2px}

/* ── limitations ───────────────────────────────────────────── */
.lims{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:8px 32px}
.lims .li{display:flex;gap:20px;padding:22px 0;border-top:1px solid var(--line-2)}
.lims .li:first-child{border-top:none}
.lims .li .no{font-family:var(--serif);font-style:italic;font-size:30px;color:var(--ochre-l);
  line-height:1;min-width:42px}
.lims .li .tx h4{font-family:var(--serif);font-weight:500;font-size:18px;margin-bottom:6px}
.lims .li .tx p{font-size:14px;color:var(--slate);line-height:1.55}
.hook{margin-top:22px;background:var(--ink);border-radius:14px;padding:26px 30px;
  font-family:var(--serif);font-size:18px;line-height:1.5;color:var(--paper)}
.hook b{color:var(--ochre)}

/* ── pills ─────────────────────────────────────────────────── */
.pill{display:inline-flex;align-items:center;font-family:var(--mono);font-size:10px;
  letter-spacing:.1em;text-transform:uppercase;padding:5px 13px;border-radius:99px;font-weight:500}
.pill.HIGH{background:var(--green-l);color:var(--green)}
.pill.MEDIUM{background:var(--ochre-l);color:var(--ochre-d)}
.pill.LOW{background:var(--rust-l);color:var(--rust)}

.footer{margin-top:90px;padding-top:24px;border-top:1px solid var(--line);
  font-family:var(--mono);font-size:10px;letter-spacing:.06em;color:var(--slate-2);line-height:1.8;text-align:center}

@media(max-width:720px){
  .wrap{padding:0 20px 80px}.kpis{grid-template-columns:1fr 1fr}
  .cards{grid-template-columns:1fr}.baf .row{grid-template-columns:1fr}
}
"""

# JS is built in report_component_js.py to keep files readable.
from .report_component_js import build_js  # noqa: E402


def build_report_html(payload: dict) -> str:
    data_json = json.dumps(payload, ensure_ascii=False)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300;1,9..144,400;1,9..144,500&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{_CSS}</style></head>
<body>
<div id="root" class="wrap"></div>
<script>const DATA = {data_json};</script>
<script>{build_js()}</script>
</body></html>"""
