"""
marginlab.ui.pdf_report
───────────────────────────────────────────────────────────────────────────
Branded client-facing PDF — the deliverable handed to the café owner.

Pure-Python (fpdf2) so it renders on Streamlit Cloud with no system binaries.
Uses core fonts styled to the MarginLab palette (deep ink, ochre accent) with
an editorial layout: hero lift, before→after table, confidence range, and the
three honest limitations framed as the reason to book the walkthrough.
"""

from __future__ import annotations
from io import BytesIO

from fpdf import FPDF

INK = (15, 26, 46)
INK_MID = (46, 61, 87)
CREAM = (250, 247, 242)
CREAM_DEEP = (241, 235, 224)
OCHRE = (184, 147, 92)
OCHRE_DEEP = (154, 120, 66)
SLATE = (91, 102, 120)
GREEN = (74, 107, 74)
RUST = (156, 74, 60)
LINE = (229, 223, 212)


def _money(v, currency, sym):
    if currency in ("IDR", "JPY", "VND"):
        return f"{sym}{v:,.0f}"
    return f"{sym}{v:,.2f}"


class _Doc(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*SLATE)
        self.cell(0, 6,
                  "MarginLab   |   Menu profit engineering for independent cafes   |   "
                  "Projections are estimates; actual results vary. Changes implemented gradually and monitored.",
                  align="C")


def build_pdf(audit, client: dict, currency: str, sym: str) -> bytes:
    cafe = _ascii((client.get("name") or "This cafe").strip())
    pdf = _Doc(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    W = pdf.w - 2 * pdf.l_margin

    # ── wordmark ──
    pdf.set_font("Times", "I", 20)
    pdf.set_text_color(*INK)
    pdf.cell(0, 9, "MarginLab", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*OCHRE_DEEP)
    pdf.cell(0, 4, "P R I C I N G   I N T E L L I G E N C E", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ── title ──
    pdf.set_font("Times", "", 26)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 10, f"{cafe}: a menu profit rebalance.")
    pdf.ln(1)
    meta = []
    if client.get("concept"): meta.append(_ascii(client["concept"]))
    if client.get("location"): meta.append(_ascii(client["location"]))
    meta.append(f"{len(audit.items)} items reviewed")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*SLATE)
    pdf.cell(0, 5, "   |   ".join(meta), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # ── hero band ──
    sign = "+" if audit.monthly_lift >= 0 else "-"
    y0 = pdf.get_y()
    pdf.set_fill_color(*INK)
    pdf.rect(pdf.l_margin, y0, W, 34, "F")
    pdf.set_xy(pdf.l_margin + 6, y0 + 5)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*OCHRE)
    pdf.cell(0, 4, "PROJECTED MONTHLY CHANGE IN PROFIT", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin + 6)
    pdf.set_font("Times", "I", 30)
    pdf.set_text_color(*CREAM)
    pdf.cell(80, 14, f"{sign}{_money(abs(audit.monthly_lift), currency, sym)}")
    # right side: confidence + annual
    pdf.set_xy(pdf.l_margin + W - 70, y0 + 6)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*OCHRE)
    pdf.cell(64, 5, f"{audit.confidence} CONFIDENCE", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(pdf.l_margin + W - 70, y0 + 14)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*CREAM)
    lift_pct = f"{audit.lift_pct*100:+.1f}% on profit"
    pdf.cell(64, 5, lift_pct, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(pdf.l_margin + W - 70, y0 + 20)
    pdf.cell(64, 5, f"Indicative annual {sign}{_money(abs(audit.monthly_lift)*12, currency, sym)}",
             align="R")
    pdf.set_y(y0 + 40)

    # ── before / after table ──
    _section(pdf, "RECOMMENDED CHANGES", W)
    headers = ["Item", "Now", "New", "Change", "Action", "Phase"]
    widths = [W*0.30, W*0.14, W*0.14, W*0.13, W*0.15, W*0.14]
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*SLATE)
    for h, wd in zip(headers, widths):
        pdf.cell(wd, 7, h.upper(), border="B")
    pdf.ln(7)
    pdf.set_font("Helvetica", "", 9)
    for it in audit.items:
        pdf.set_text_color(*INK)
        pdf.cell(widths[0], 7, _ascii(it.name))
        pdf.cell(widths[1], 7, _money(it.price_from, currency, sym))
        pdf.cell(widths[2], 7, _money(it.price_to, currency, sym))
        dp = it.delta_pct * 100
        pdf.set_text_color(*(GREEN if dp > 0 else RUST if dp < 0 else SLATE))
        pdf.cell(widths[3], 7, f"{'+' if dp>0 else ''}{dp:.1f}%")
        pdf.set_text_color(*INK_MID)
        pdf.cell(widths[4], 7, it.action)
        pdf.set_text_color(*SLATE)
        pdf.cell(widths[5], 7, it.phase if it.action != "Hold" else "-")
        pdf.ln(6.4)
        pdf.set_draw_color(*LINE)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + W, pdf.get_y())
        pdf.ln(0.6)
    pdf.ln(4)

    # ── confidence range ──
    _section(pdf, "CONFIDENCE RANGE - STRESS TEST", W)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*INK_MID)
    c, b, o = audit.sens_conservative, audit.sens_baseline, audit.sens_optimistic
    pdf.cell(W/3, 6, f"Conservative   {('+' if c>=0 else '-')}{_money(abs(c),currency,sym)}")
    pdf.cell(W/3, 6, f"Baseline   {('+' if b>=0 else '-')}{_money(abs(b),currency,sym)}")
    pdf.cell(W/3, 6, f"Optimistic   {('+' if o>=0 else '-')}{_money(abs(o),currency,sym)}")
    pdf.ln(7)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*SLATE)
    robust = "remains positive across all three scenarios" if audit.sens_robust == "Yes" \
        else "is not positive in every scenario - review before rollout"
    pdf.multi_cell(0, 5, f"The recommendation {robust}. Conservative assumes customers are "
                          f"20% more price-sensitive than estimated; optimistic, 20% less.")
    pdf.ln(3)

    # ── limitations ──
    _section(pdf, "WHAT THIS ANALYSIS DOES NOT CAPTURE", W)
    pdf.set_font("Helvetica", "", 9)
    lims = [
        ("Switching between your own items",
         "when one drink moves, some customers shift to another. Each item is priced on its own."),
        ("The basket effect",
         "a coffee price change can move pastry attach-rate too; the model sees only the coffee."),
        ("Time-of-day & weekday mix",
         "a 7am and a 3pm order are different products, averaged into one number here."),
    ]
    for i, (h, body) in enumerate(lims, 1):
        pdf.set_text_color(*OCHRE_DEEP)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(6, 5.5, f"{i}.")
        pdf.set_text_color(*INK)
        pdf.cell(0, 5.5, _ascii(h), new_x="LMARGIN", new_y="NEXT")
        pdf.set_x(pdf.l_margin + 6)
        pdf.set_text_color(*SLATE)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.multi_cell(0, 4.6, _ascii(body))
        pdf.ln(1.5)

    pdf.ln(2)
    y = pdf.get_y()
    pdf.set_fill_color(*CREAM_DEEP)
    pdf.rect(pdf.l_margin, y, W, 16, "F")
    pdf.set_xy(pdf.l_margin + 5, y + 3)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*INK)
    pdf.multi_cell(W - 10, 5,
                   "These three gaps are why pricing isn't a spreadsheet. On a 60-minute walkthrough "
                   "we read this against how your cafe actually trades and turn the directional "
                   "numbers into a confident 30-day plan.")

    out = pdf.output()
    return bytes(out)


def _section(pdf, label, W):
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*SLATE)
    pdf.cell(0, 6, label, new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*INK)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + W, pdf.get_y())
    pdf.ln(2.5)


def _ascii(s: str) -> str:
    """fpdf core fonts are latin-1; map common typographic glyphs, then strip."""
    if not s:
        return ""
    repl = {"\u2014": "-", "\u2013": "-", "\u2212": "-", "\u2192": "->",
            "\u00b7": "|", "\u2018": "'", "\u2019": "'", "\u201c": '"',
            "\u201d": '"', "\u2026": "...", "\u2713": "v"}
    for k, v in repl.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")
