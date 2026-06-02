# MarginLab — Pricing Consulting Workspace

A premium pricing-analysis environment for independent cafés. Not a SaaS app, not a
public sales page — the proprietary consulting tool you open during or after a pitch.

Two deliberately distinct worlds:

- **The workspace (consultant side)** — a dark, editorial "cockpit." Client setup,
  menu & cost intake, scenario tuning. Feels like proprietary software.
- **The client report (output)** — a bespoke, fully animated light editorial document:
  numbers that count up, SVG charts that draw themselves in on scroll, staggered reveals,
  hero parallax. This is the screen you turn the laptop around for.

Flow: **Client → Menu & Cost → Analysis → Opportunities → Recommendations → Scenarios → Final Review**

## Why it's credible beyond a spreadsheet

- **Native v10 engine** — the full MarginLab_Pricing_Lab_v10 model (Lerner-optimal markup,
  ln-ln OLS elasticity calibration with 95% CIs, confidence shrinkage, role caps, global
  guardrails, USD/IDR psychology thresholds, charm endings, menu-engineering quadrants,
  sensitivity, competitor positioning, QA) ported to Python. Instant, no spreadsheet recalc.
  Validated to the cent: `python -m marginlab.engine.validate`.
- **Bespoke animated report** — every visual is hand-rolled SVG animated with the Web
  Animations API + IntersectionObserver. No chart library, no generic dashboard look.
- **Branded PDF deliverable** — generated on the Final Review page (fpdf2, pure Python).

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
Click **Load demo café** on the first page to explore.

## Structure
```
app.py                      # dark cockpit shell, top nav, routing
marginlab/
├── engine/                 # native v10 port (validated)
│   ├── constants.py  calibration.py  model.py  validate.py
└── ui/
    ├── theme2.py           # dark workspace design system
    ├── serialize.py        # AuditResult → JSON for the report
    ├── report_component.py # the animated client report (HTML/CSS shell)
    ├── report_component_js.py # count-ups, draw-in SVG charts, reveals, parallax
    ├── pdf_report.py        # branded client PDF
    ├── state.py             # session state, currency, demo data
    └── pages/
        ├── intake.py        # 1 Client · 2 Menu & Cost (dark)
        └── analysis.py      # 3–5,7 animated report · 6 Scenarios (dark)
```
See `DEPLOY.md` for GitHub + Streamlit Cloud.
