"""Steering-committee deck: "HDFC Bank: the path back to 2% RoA".

Every model number is read from data/tidy/hdfc_model_outputs.json (written by pipeline/export_scenarios.py from
the recalculated workbook) or from the page-cited files in data/inputs. Nothing on a slide is typed by hand.
House style: Garamond, no italics, action titles, one accent colour with grey context, a source line on every slide.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
I, T = ROOT / "data" / "inputs", ROOT / "data" / "tidy"
FONT = "Garamond"
ACCENT, INK, MUTED, GRID, CONTEXT, WHITE, PALE = (RGBColor(0x1F, 0x3A, 0x5F), RGBColor(0x1A, 0x1A, 0x1A), RGBColor(0x6B, 0x6B, 0x6B),
                                                RGBColor(0xD9, 0xD9, 0xD9), RGBColor(0xA6, 0xA6, 0xA6), RGBColor(0xFF, 0xFF, 0xFF),
                                                RGBColor(0xE9, 0xEE, 0xF4))
YEARS = ["FY20A", "FY21A", "FY22A", "FY23A", "FY24A", "FY25A", "FY26A", "FY27E", "FY28E", "FY29E"]
DISCLAIMER = "Independent outside-in case study using public data only; not commissioned by, or affiliated with, HDFC Bank or Bain & Company."
O = json.loads((T / "hdfc_model_outputs.json").read_text())
SRC_MODEL = "HDFC_RoA_Path_FY29.xlsx (driver model built on HDFC Bank IR26 schedules)"


def v(key, year="FY29E", scn="Base"):
    """Value for a timeline row; year=None returns the column-E scalar."""
    row = O[scn][key]
    return row[2] if year is None else row[2 + YEARS.index(year)]


def ind(x, dp=0):
    """Indian digit grouping: 1,03,000."""
    neg, x = x < 0, abs(x)
    s = f"{x:,.{dp}f}"
    whole, _, frac = s.replace(",", "").partition(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts + [tail])
    out = whole + (f".{frac}" if frac else "")
    return f"({out})" if neg else out


def pct(x, dp=1):
    return f"{x * 100:.{dp}f}%"


def bp(x, dp=0):
    return f"{x:.{dp}f} bp"


class Deck:
    def __init__(self):
        self.p = Presentation(); self.p.slide_width, self.p.slide_height = Inches(13.333), Inches(7.5)
        self.n = 0

    # ---------------------------------------------------------------- primitives
    @staticmethod
    def text(s, txt, x, y, w, h, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
        tf.vertical_anchor = anchor
        for i, line in enumerate(txt.split("\n")):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = align
            r = para.add_run(); r.text = line
            r.font.size, r.font.bold, r.font.italic, r.font.color.rgb, r.font.name = Pt(size), bold, False, color, FONT
        return tb

    @staticmethod
    def bullets(s, items, x, y, w, h, size=14, gap=6):
        """items: list of (lead, rest). Lead is bold, rest regular; no italics anywhere."""
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
        for i, (lead, rest) in enumerate(items):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.space_after = Pt(gap)
            for t, b in ((lead, True), (rest, False)):
                if not t:
                    continue
                r = para.add_run(); r.text = t
                r.font.size, r.font.bold, r.font.italic, r.font.color.rgb, r.font.name = Pt(size), b, False, INK, FONT
        return tb

    @staticmethod
    def box(s, x, y, w, h, fill=PALE, line=None):
        b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        b.fill.solid(); b.fill.fore_color.rgb = fill
        if line is None:
            b.line.fill.background()
        else:
            b.line.color.rgb = line
        b.shadow.inherit = False
        return b

    def slide(self, title, source, tracker=""):
        s = self.p.slides.add_slide(self.p.slide_layouts[6]); self.n += 1
        if tracker:
            self.text(s, tracker.upper(), 0.5, 0.22, 9, 0.3, 10, MUTED, bold=True)
        self.text(s, title, 0.5, 0.48, 12.3, 1.0, 21, ACCENT, bold=True)
        ln = s.shapes.add_connector(1, Inches(0.5), Inches(1.45), Inches(12.83), Inches(1.45)); ln.line.color.rgb = GRID
        self.text(s, f"Source: {source}", 0.5, 6.88, 10.6, 0.45, 9, MUTED)
        self.text(s, f"HDFC Bank RoA | {self.n}", 11.13, 6.88, 1.7, 0.3, 9, MUTED, align=PP_ALIGN.RIGHT)
        return s

    def chart(self, s, kind, cats, series, x, y, w, h, colors=None, point_colors=None, legend=True, labels=True, fmt="0.0",
              gap=60, overlap=None, axis_fmt=None, axis_visible=True, label_colors=None, caption=None):
        cd = CategoryChartData(); cd.categories = cats
        for name, vals in series:
            cd.add_series(name, vals)
        ch = s.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd).chart
        ch.font.size, ch.font.name, ch.font.italic = Pt(11), FONT, False
        ch.has_title = False
        if caption:
            self.text(s, caption, x + 0.1, y - 0.2, w - 0.2, 0.3, 11, MUTED)
        ch.has_legend = legend and len(series) > 1
        if ch.has_legend:
            ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.BOTTOM, False
            ch.legend.font.name, ch.legend.font.size = FONT, Pt(11)
        line_kind = kind in (XL_CHART_TYPE.LINE_MARKERS, XL_CHART_TYPE.LINE)
        for i, ser in enumerate(ch.series):
            c = (colors or [ACCENT, CONTEXT])[i % len(colors or [ACCENT, CONTEXT])]
            if c is None:
                ser.format.fill.background(); ser.format.line.fill.background(); continue
            if line_kind:
                ser.format.line.color.rgb, ser.format.line.width = c, Pt(2.25); ser.smooth = False
                ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = c; ser.marker.format.line.color.rgb = c
            else:
                ser.format.fill.solid(); ser.format.fill.fore_color.rgb = c
            if point_colors and i == 0:
                for j, pc in enumerate(point_colors):
                    pt = ser.points[j]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = pc
        if labels:
            for i, ser in enumerate(ch.series):
                if (colors or [ACCENT])[i % len(colors or [ACCENT])] is None:
                    continue
                ser.data_labels.show_value = True
                dl = ser.data_labels
                dl.number_format, dl.number_format_is_linked = fmt, False
                dl.font.size, dl.font.name, dl.font.italic = Pt(10), FONT, False
                dl.font.color.rgb = (label_colors or [INK] * 9)[i]
                if line_kind:
                    dl.position = XL_LABEL_POSITION.ABOVE
                elif kind in (XL_CHART_TYPE.COLUMN_CLUSTERED, XL_CHART_TYPE.BAR_CLUSTERED):
                    dl.position = XL_LABEL_POSITION.OUTSIDE_END
        try:
            ch.plots[0].gap_width = gap
            if overlap is not None:
                ch.plots[0].overlap = overlap
        except Exception:  # noqa: BLE001 - line charts have no gap width
            pass
        va, ca = ch.value_axis, ch.category_axis
        va.has_major_gridlines = False
        va.format.line.fill.background()
        va.tick_labels.font.color.rgb, va.tick_labels.font.name, va.tick_labels.font.size = MUTED, FONT, Pt(10)
        if axis_fmt:
            va.tick_labels.number_format, va.tick_labels.number_format_is_linked = axis_fmt, False
        va.visible = axis_visible
        ca.tick_labels.font.color.rgb, ca.tick_labels.font.name, ca.tick_labels.font.size = INK, FONT, Pt(11)
        ca.format.line.color.rgb = GRID
        ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        if kind in (XL_CHART_TYPE.BAR_STACKED, XL_CHART_TYPE.BAR_CLUSTERED):
            ca.reverse_order = True
            va.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        return ch

    def table(self, s, header, rows, x, y, w, col_w=None, size=11, bold_rows=(), row_h=0.34, align_right_from=1, right_cols=None):
        t = s.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y), Inches(w), Inches(row_h * (len(rows) + 1))).table
        for i in range(len(rows) + 1):
            t.rows[i].height = Inches(row_h)
        for i, row in enumerate([header] + rows):
            for j, val in enumerate(row):
                c = t.cell(i, j); c.text = ""; c.fill.solid()
                c.fill.fore_color.rgb = ACCENT if i == 0 else (PALE if (i - 1) in bold_rows else WHITE)
                c.margin_left = c.margin_right = Inches(0.06); c.margin_top = c.margin_bottom = Inches(0.02)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                para = c.text_frame.paragraphs[0]
                rc = (j in right_cols) if right_cols is not None else (j >= align_right_from and _numeric(val))
                para.alignment = PP_ALIGN.RIGHT if (rc and j > 0) else PP_ALIGN.LEFT
                r = para.add_run(); r.text = str(val)
                r.font.size, r.font.name, r.font.italic = Pt(size), FONT, False
                r.font.bold = i == 0 or (i - 1) in bold_rows
                r.font.color.rgb = WHITE if i == 0 else INK
        if col_w:
            for j, cw in enumerate(col_w):
                t.columns[j].width = Inches(cw)
        tbl = t._tbl
        tbl.tblPr.set("bandRow", "0"); tbl.tblPr.set("firstRow", "1")
        return t

    def kpi(self, s, value, label, x, y, w=2.9, color=ACCENT):
        self.text(s, value, x, y, w, 0.8, 34, color, bold=True)
        self.text(s, label, x, y + 0.8, w, 0.9, 12, MUTED)

    def save(self, path):
        self.p.save(path)


def _numeric(val) -> bool:
    t = str(val).replace(",", "").replace("%", "").replace("bp", "").replace("x", "").replace("(", "-").replace(")", "")
    t = t.replace("INR", "").replace("₹", "").replace("−", "-").replace("+", "").strip()
    if t in ("–", "-"):
        return True
    try:
        float(t.split()[0]); return True
    except (ValueError, IndexError):
        return False


def main():
    d = Deck()
    h10 = pd.read_csv(I / "hdfc_10yr_highlights.csv").set_index("metric")
    fy = [c for c in h10.columns if c.startswith("FY")]
    roa_hist = {fy[i]: h10.loc["pat", fy[i]] / ((h10.loc["total_assets", fy[i]] + h10.loc["total_assets", fy[i - 1]]) / 2)
                for i in range(1, len(fy))}
    facts = pd.read_csv(T / "bank_facts.csv")
    q = facts[(facts.entity == "HDFCBANK") & (facts.period == "Q2FY27")].set_index("metric").value
    roa_q2 = q["pat"] * 4 / ((q["assets_open"] + q["assets_close"]) / 2)
    nimt = pd.read_csv(I / "nim_trajectory.csv").set_index("bank")
    sh = pd.read_csv(T / "bank_shapley_FY26.csv")
    shh = sh[(sh.metric == "RoA") & (sh.bank == "HDFCBANK")].iloc[0]
    grp = pd.read_csv(I / "hdfc_group_valuation_inputs.csv")
    npci = pd.read_csv(I / "npci_p2m_monthly.csv")
    mc = pd.read_csv(T / "ins_mc_summary.csv", index_col=0).reset_cr

    base29, up29, dn29 = (v("Model|Return on average assets", "FY29E", s) for s in ("Base", "Upside", "Downside"))
    lev_names = ["Re-mix advances to higher-yield retail and SME", "Branch and operations productivity", "Rebuild CASA",
                 "Retire legacy borrowings faster", "Protect bancassurance and grow card fees", "Win UPI merchant acquiring share"]
    SHORT = dict(zip(lev_names, ["Advance re-mix", "Productivity", "CASA", "Borrowings", "Bancassurance and cards", "UPI acquiring"]))
    lev = {k: O["Base"][f"Levers|{k}"] for k in lev_names}   # [pre-tax, PAT, bp, RoE, value, per share, score]
    lev_all = O["Base"]["Levers|All levers"]
    with_lev = O["Base"]["Levers|RoA FY29E with levers"][2]
    before = O["Base"]["Levers|RoA FY29E, scenario before levers"][2]
    roa26 = O["Base"]["Levers|RoA FY26A, core"][2]
    drift = O["Base"]["Levers|Scenario drift to FY29E (margin, fees, cost, credit, mix)"][2]
    ke, g, roe_impl = v("Valuation|Cost of equity", None), v("Valuation|Long-term growth", None), v("Valuation|RoE the market is pricing", None)
    price = v("Valuation|Current share price", None)
    v10 = v("Valuation|Value of +10 bp RoA (equity value)", None)
    sotp = {s: v("Valuation|Sum of the parts per share", None, s) for s in O}
    ri = {s: v("Valuation|Residual income per share", None, s) for s in O}
    roe29 = {s: v("Model|Return on average net worth", "FY29E", s) for s in O}
    ear = v("ALM|Earnings at risk, +100 bp", None)
    ear_bp = ear * (1 - 0.2517) / v("Model|Average total assets", "FY27E") * 1e4
    beta = v("ALM|Change in cost of deposits / change in average repo", None)
    ttc, recent = v("Opex_Credit|Through-the-cycle credit cost, FY21-FY26 average", None), v("Opex_Credit|Recent credit cost, FY24-FY26 average", None)
    norm_gap, norm_roa = v("Opex_Credit|Normalisation gap", None), v("Opex_Credit|RoA at risk if credit cost normalises", None)
    irdai28, irdai29 = v("Fees|Bank fee lost to caps", "FY28E"), v("Fees|Bank fee lost to caps", "FY29E")
    oi29 = v("Model|Other income", "FY29E")
    dvnb, val_life = v("Fees|Net change in annual VNB", None), v("Fees|Value effect to HDFC Bank shareholders", None)
    pool, hshare = v("Fees|Annual MDR pool at current run-rate", None), v("Fees|HDFC Bank share of payee volume", None)
    mdr = [v("Fees|HDFC Bank MDR revenue", y) for y in ("FY27E", "FY28E", "FY29E")]
    nim = {y: v("Model|Net interest margin on interest-earning assets", y) for y in YEARS[1:]}
    nii_a = {y: v("Model|NII / average assets", y) for y in YEARS[1:]}
    bshare = {y: v("Margin|Borrowings / (deposits + borrowings), average", y) for y in YEARS[1:]}
    casa26, casa29 = v("Model|CASA ratio, year end", "FY26A"), v("Model|CASA ratio, year end", "FY29E")
    oa = {y: v("Model|Opex / average assets", y) for y in YEARS[1:]}
    ci = {y: v("Model|Cost to income", y) for y in YEARS}
    cc = {y: v("Model|Credit cost", y) for y in YEARS[1:]}
    bor_le1 = pd.read_csv(I / "hdfc_borrowing_maturity_mar26.csv").amount_cr[:8].sum()

    # ================================================================ 1 Title
    s = d.p.slides.add_slide(d.p.slide_layouts[6]); d.n += 1
    d.box(s, 0, 0, 0.35, 7.5, fill=ACCENT)
    d.text(s, "HDFC Bank: the path back to 2% RoA", 0.9, 2.1, 11.5, 1.0, 36, ACCENT, bold=True)
    d.text(s, "Steering committee discussion document", 0.9, 3.1, 11.5, 0.5, 20, INK)
    d.text(s, "What restores standalone RoA to 2.0% or more by FY29, what each move is worth, and what to start in the next 12 months",
           0.9, 3.7, 11, 0.8, 15, MUTED)
    d.text(s, "3 November 2026 | Data to Q2 FY27 | Prepared by Anklesh", 0.9, 5.4, 11, 0.4, 13, INK)
    d.text(s, DISCLAIMER, 0.9, 6.6, 11.5, 0.5, 10, MUTED)

    # ================================================================ 2 Executive summary
    s = d.slide(f"HDFC Bank can be back above 2% RoA by FY29, but only by pulling six levers worth {lev_all[2]:.0f} bp. The share price already assumes it",
                f"{SRC_MODEL}; HDFC Bank IR26 p234; Q2 FY27 investor presentation; NSE prices 2 Nov 2026", "Executive summary")
    d.bullets(s, [
        ("Diagnosis. ", f"RoA held at 1.8-2.0% for a decade, then the merger reset the mix: NII fell from {pct(nii_a['FY23A'], 2)} of assets (FY23) to "
                        f"{pct(nii_a['FY26A'], 2)} (FY26). The {shh.gap * 100:.0f} bp gap to ICICI Bank is margin ({shh.nii * 100:.0f} bp), not cost. "
                        f"Q2 FY27 RoA is {pct(roa_q2, 2)} annualised."),
        ("Base case. ", f"RoA drifts back to {pct(base29, 2)} by FY29E as ₹{ind(bor_le1)} cr of legacy borrowings mature within a year. Credit cost "
                        f"normalising to its through-the-cycle level ({pct(ttc, 2)} vs {pct(recent, 2)} recently) absorbs about {norm_roa:.0f} bp."),
        ("Regulation is small for the bank, not for the group. ", f"The IRDAI caps cost ₹{ind(irdai29)} cr of fees by FY29E "
                        f"({pct(irdai29 / oi29)} of other income). UPI MDR adds ₹{ind(mdr[2])} cr. HDFC Life's VNB nets +₹{ind(dvnb)} cr if half the commission saving is kept."),
        ("Six levers add ", f"{lev_all[2]:.1f} bp, taking FY29E RoA to {with_lev / 100:.2f}%. Four carry the plan: re-mix advances "
                            f"({lev[lev_names[0]][2]:.1f} bp), branch productivity ({lev[lev_names[1]][2]:.1f}), CASA ({lev[lev_names[2]][2]:.1f}), borrowing retirement ({lev[lev_names[3]][2]:.1f})."),
        ("Value at stake. ", f"At a {pct(ke)} cost of equity the base case justifies ₹{sotp['Base']:.0f} a share (sum of the parts) against ₹{price:.0f} today. "
                             f"The price implies {pct(roe_impl)} RoE; the base case reaches {pct(roe29['Base'])}. Each 10 bp of RoA is worth about ₹{ind(v10 / 1000, 0)}k cr."),
    ], 0.5, 1.65, 12.3, 5.1, size=15, gap=10)

    # ================================================================ 3 Decisions
    s = d.slide("Three decisions for the steering committee", "Team analysis; lever values from " + SRC_MODEL, "What you must decide")
    dec = [("1. Make deposits the binding constraint, not loans",
            f"Hold advances growth to the deposit franchise (credit-deposit ratio about 93%) and fund the CASA rebuild before loan share. CASA is "
            f"{pct(casa26)} (FY26) vs 38% before the merger."),
           ("2. Retire ₹75,000 cr of legacy borrowings ahead of plan",
            f"Borrowings cost {pct(v('Model|Cost of borrowings', 'FY26A'), 2)} vs {pct(v('Model|Cost of deposits', 'FY26A'), 2)} for deposits. "
            f"₹{ind(bor_le1)} cr matures in FY27; refinancing less of it is worth {lev[lev_names[3]][2]:.1f} bp."),
           ("3. Re-price the HDFC Life partnership before the IRDAI caps land",
            "Move bancassurance pay to persistency-linked commission and longer premium terms, so the group keeps the margin the caps create.")]
    for i, (h, b) in enumerate(dec):
        y = 1.75 + i * 1.65
        d.box(s, 0.5, y, 0.08, 1.35, fill=ACCENT)
        d.text(s, h, 0.8, y, 11.8, 0.5, 17, ACCENT, bold=True)
        d.text(s, b, 0.8, y + 0.5, 11.8, 0.85, 14, INK)

    # ================================================================ 4 Situation: RoA history
    s = d.slide("For a decade HDFC Bank delivered 1.8-2.0% RoA; since the merger it has sat at the bottom of that range",
                "HDFC Bank IR26 p234 (ten-year highlights, standalone); Q2 FY27 standalone results via Screener, tied to the Q2 FY27 presentation. "
                "RoA = PAT / simple average total assets; Q2 FY27 annualised", "Situation")
    cats = list(roa_hist) + ["Q2 FY27"]
    vals = [x * 100 for x in roa_hist.values()] + [roa_q2 * 100]
    pc = [CONTEXT] * (len(cats) - 4) + [ACCENT] * 4
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, cats, [("RoA %", vals)], 0.5, 1.7, 8.4, 5.0, point_colors=pc, legend=False, fmt="0.00",
            axis_visible=False)
    d.text(s, "Merger with HDFC Ltd\n1 July 2023", 6.3, 1.7, 2.6, 0.6, 11, MUTED)
    d.kpi(s, pct(roa_q2, 2), "Q2 FY27 RoA, annualised. Reported 1.78%", 9.4, 1.9)
    d.kpi(s, pct(nimt.loc["HDFCBANK", "q2fy27_nim"] / 100, 2), f"Q2 FY27 NIM on total assets, down {abs(nimt.loc['HDFCBANK', 'change_bp']):.0f} bp from Q4 FY26", 9.4, 3.5)
    d.kpi(s, "32%", "CASA ratio, Q2 FY27, vs 38% before the merger", 9.4, 5.1)

    # ================================================================ 5 Complication: DuPont
    s = d.slide(f"The merger moved the problem from cost to margin: NII lost {(nii_a['FY23A'] - nii_a['FY26A']) * 1e4:.0f} bp of assets while opex fell {(oa['FY23A'] - oa['FY26A']) * 1e4:.0f} bp",
                f"{SRC_MODEL}, Model tab (ratios on average total assets). FY26 includes a ₹12,861 cr gain on sale of investments and ₹10,700 cr of floating and contingent provisions", "Complication")
    comp = [("NII", "Model|NII / average assets", 1), ("Other income", "Model|Other income / average assets", 1), ("Opex", "Model|Opex / average assets", -1),
            ("Provisions", "Model|Provisions / average assets", -1), ("Tax", "Model|Tax / average assets", -1), ("RoA", "Model|Return on average assets", 1)]
    rows = []
    for nm, k, sg in comp:
        a, b = v(k, "FY23A"), v(k, "FY26A")
        rows.append([nm, pct(a, 2), pct(b, 2), f"{(b - a) * 1e4 * sg:+.0f}"])
    d.table(s, ["% of average assets", "FY23 (pre-merger)", "FY26", "RoA effect, bp"], rows, 0.5, 1.8, 6.6, col_w=[2.1, 1.5, 1.4, 1.6], bold_rows=(5,))
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, ["FY21", "FY22", "FY23", "FY24", "FY25", "FY26"],
            [("NII / assets %", [nii_a[y] * 100 for y in YEARS[1:7]]), ("Opex / assets %", [oa[y] * 100 for y in YEARS[1:7]])],
            7.5, 1.7, 5.3, 4.2, colors=[ACCENT, CONTEXT], fmt="0.00", axis_visible=False)
    d.bullets(s, [("So what. ", "Cost is already best-in-class among large private banks. The recovery has to come from funding cost and asset mix.")],
              0.5, 4.5, 6.6, 1.2, size=14)

    # ================================================================ 6 Complication: market expectation
    s = d.slide(f"The market is paying for {pct(roe_impl)} RoE; the base case delivers {pct(roe29['Base'])} by FY29",
                f"{SRC_MODEL}, Valuation tab. Cost of equity by CAPM: 10-year G-sec 6.96% (RBI, Aug 2026), beta 0.95, equity risk premium 6.5%. "
                "Price ₹700 and market capitalisation from NSE, 2 Nov 2026", "Complication")
    d.kpi(s, f"{v('Valuation|Current P/B (standalone)', None):.2f}x", "Price to standalone book today", 0.6, 1.9, w=3.8)
    d.kpi(s, pct(roe_impl), f"RoE implied by that P/B at Ke {pct(ke)} and g {pct(g, 0)}", 4.6, 1.9, w=3.8)
    d.kpi(s, pct(roe29["Base"]), "Base-case RoE, FY29E", 8.6, 1.9, w=3.8, color=CONTEXT)
    d.bullets(s, [
        ("The gap is about 3 percentage points of RoE. ", f"Closing it through RoA alone needs roughly {(roe_impl - roe29['Base']) / (roe29['Base'] / base29) * 1e4:.0f} bp, "
                                                           "since leverage is fixed by the Tier 1 ratio."),
        ("Justified P/B in the base case is ", f"{v('Valuation|Justified P/B', None):.2f}x on FY29E RoE, which gives ₹{sotp['Base']:.0f} a share once listed subsidiaries are added "
                                               "at market value less a 20% holding-company discount."),
        ("The levers are therefore not optional. ", "Without them the stock carries a de-rating risk; with them and the upside scenario it is fairly priced."),
    ], 0.6, 4.0, 12, 2.6, size=15, gap=10)

    # ================================================================ 7 Issue tree
    s = d.slide("We tested five hypotheses, one per branch of the RoA tree", "Team analysis", "Approach")
    d.box(s, 0.5, 2.9, 2.6, 1.6, fill=ACCENT)
    d.text(s, "How does HDFC Bank get standalone RoA to 2.0% or more by FY29?", 0.6, 2.95, 2.4, 1.5, 14, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    br = [("Margin", f"Legacy borrowings run off mechanically; CASA must be rebuilt", f"Supported: borrowings fall from {pct(bshare['FY25A'])} to {pct(bshare['FY29E'])} of funding"),
          ("Fees", "IRDAI caps hurt the group more than the bank; UPI MDR is small", f"Supported: bank fee loss ₹{ind(irdai29)} cr; MDR ₹{ind(mdr[2])} cr"),
          ("Cost", "Opex/assets keeps falling as new branches mature", f"Partly: {pct(oa['FY26A'], 2)} to {pct(oa['FY29E'], 2)}, about {(oa['FY26A'] - oa['FY29E']) * 1e4:.0f} bp"),
          ("Credit", "Credit cost is below cycle; normalisation is a headwind", f"Supported: {norm_gap:.0f} bp gap on loans, about {norm_roa:.0f} bp of RoA"),
          ("Value", "The market price needs RoE well above the base case", f"Supported: implied RoE {pct(roe_impl)} vs {pct(roe29['Base'])}")]
    for i, (nm, hyp, res) in enumerate(br):
        y = 1.7 + i * 1.02
        ln = s.shapes.add_connector(1, Inches(3.1), Inches(3.7), Inches(3.5), Inches(y + 0.4)); ln.line.color.rgb = CONTEXT
        d.box(s, 3.5, y, 1.5, 0.8, fill=PALE)
        d.text(s, nm, 3.55, y, 1.4, 0.8, 14, ACCENT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        d.text(s, hyp, 5.2, y, 3.9, 0.8, 12, INK, anchor=MSO_ANCHOR.MIDDLE)
        d.text(s, res, 9.2, y, 3.6, 0.8, 12, MUTED, anchor=MSO_ANCHOR.MIDDLE)
    d.text(s, "Hypothesis", 5.2, 1.5, 3, 0.25, 10, MUTED, bold=True)
    d.text(s, "Finding", 9.2, 1.5, 3, 0.25, 10, MUTED, bold=True)

    # ================================================================ 8 A. Peer gap (Shapley)
    s = d.slide(f"Against ICICI Bank the {shh.gap * 100:.0f} bp RoA gap is margin plus FY26 provisions; HDFC Bank is already ahead on cost and fees",
                "Screener standalone financials FY26, tied to annual reports; Shapley (order-independent) attribution of the RoA gap, data/tidy/bank_shapley_FY26.csv",
                "A. Diagnostic")
    parts = [("Net interest income", -shh.nii), ("Other income", -shh.oi), ("Operating expenses", -shh.opex), ("Provisions", -shh.prov), ("Tax", -shh.tax_rate)]
    d.chart(s, XL_CHART_TYPE.BAR_CLUSTERED, [p[0] for p in parts], [("Contribution to HDFC Bank's RoA gap vs ICICI Bank, bp", [p[1] * 100 for p in parts])],
            0.5, 1.7, 7.4, 4.9, point_colors=[ACCENT if p[1] < 0 else CONTEXT for p in parts], legend=False, fmt='0;(0)', axis_visible=False)
    d.bullets(s, [
        ("Accent bars widen the gap. ", f"NII costs {shh.nii * 100:.0f} bp and provisions {shh.prov * 100:.0f} bp, most of it the ₹10,700 cr floating and contingent build in FY26."),
        ("Grey bars narrow it. ", f"Better other income, opex and tax give back {-(shh.oi + shh.opex + shh.tax_rate) * 100:.0f} bp."),
        ("Why. ", "The merger brought a mortgage book at thin spreads funded by wholesale borrowings, so yield fell and cost of funds rose at the same time."),
        ("Implication. ", "The provisions gap reverses as the one-off unwinds; the margin gap does not. The fix is funding and mix."),
    ], 8.3, 1.8, 4.6, 4.8, size=14, gap=10)

    # ================================================================ 9 A2. Peer RoA ranking
    PR = {k.split("|")[1]: r for k, r in O["Base"].items() if k.startswith("Peers|") and len(r) >= 8 and isinstance(r[4], float) and isinstance(r[7], float)}
    peers = [(n, r[4]) for n, r in PR.items()]
    peers.sort(key=lambda t: -t[1])
    s = d.slide("Among twelve listed banks HDFC Bank ranks third on RoA, behind ICICI Bank and Kotak",
                "Screener standalone FY26: PAT / average total assets; Peers tab of " + SRC_MODEL, "A. Diagnostic")
    d.chart(s, XL_CHART_TYPE.BAR_CLUSTERED, [p[0] for p in peers], [("FY26 RoA %", [p[1] * 100 for p in peers])], 0.5, 1.6, 7.6, 5.2,
            point_colors=[ACCENT if p[0] == "HDFC Bank" else CONTEXT for p in peers], legend=False, fmt="0.00", gap=40, axis_visible=False)
    d.bullets(s, [("The benchmark is 2.2%, not 2.0%. ", "ICICI Bank shows a large private bank can earn 2.2% RoA in this rate cycle."),
                  ("Scale is not the excuse. ", "HDFC Bank's assets are 1.8 times ICICI Bank's, yet it has the lower cost ratio."),
                  ("PSU banks are not the peer set. ", "SBI earns about 1.1%, but its Q2 FY27 NIM rose to 2.94%: the cycle is not hurting every bank equally.")],
              8.5, 1.8, 4.4, 4.8, size=14, gap=10)

    # ================================================================ 10 B. NII walk
    m_hist = sum(v("Margin|  Margin effect", y) for y in ("FY24A", "FY25A", "FY26A"))
    s = d.slide(f"Margin effects took ₹{ind(-m_hist / 1000, 1)}k cr out of NII in FY24-FY26; the model has them turning positive from FY27",
                f"{SRC_MODEL}, Margin tab. Volume effect = change in average interest-earning assets × prior-year NIM; margin effect = change in NIM × current assets",
                "B. Margin")
    yrs = YEARS[2:]
    d.chart(s, XL_CHART_TYPE.COLUMN_STACKED, [y[:4] for y in yrs],
            [("Volume effect", [v("Margin|  Volume effect", y) / 1000 for y in yrs]), ("Margin effect", [v("Margin|  Margin effect", y) / 1000 for y in yrs])],
            0.5, 1.8, 8.2, 4.9, colors=[CONTEXT, ACCENT], fmt='#,##0.0;(#,##0.0)', gap=50, overlap=100, axis_visible=False,
            label_colors=[INK, WHITE], caption="Change in NII, ₹ '000 cr")
    d.bullets(s, [("FY24-FY26: ", f"margin effects of ₹{ind(-m_hist)} cr; growth carried NII."),
                  ("FY27E-FY29E: ", f"NIM rises from {pct(nim['FY26A'], 2)} to {pct(nim['FY29E'], 2)} as borrowings run off and the October 2026 repo hike passes into loan yields."),
                  ("Watch-point. ", "The base case assumes a deposit beta of 0.35; FY26 realised beta was " + f"{beta:.2f}, which is the main risk to this walk.")],
              9.0, 1.8, 3.9, 4.8, size=14, gap=10)

    # ================================================================ 11 B2. Funding mix
    s = d.slide(f"Legacy borrowings are the cheapest margin to win back: they fall from {pct(bshare['FY25A'])} of funding to {pct(bshare['FY29E'])} by FY29E",
                "HDFC Bank IR26 p384 (maturity pattern of borrowings, 31 Mar 2026) and Schedules 4, 15; " + SRC_MODEL + ", Margin tab", "B. Margin")
    yrs = YEARS[1:]
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [y[:4] for y in yrs], [("Borrowings / (deposits + borrowings)", [bshare[y] * 100 for y in yrs])],
            0.5, 1.7, 7.6, 4.9, point_colors=[CONTEXT] * 6 + [ACCENT] * 3, legend=False, fmt="0.0", axis_visible=False)
    mat = pd.read_csv(I / "hdfc_borrowing_maturity_mar26.csv")
    grp_m = [("Within 1 year", mat.amount_cr[:8].sum()), ("1-3 years", mat.amount_cr[8]), ("3-5 years", mat.amount_cr[9]), ("Over 5 years", mat.amount_cr[10]),
             ("Total, 31 Mar 2026", mat.amount_cr.sum())]
    d.table(s, ["Borrowings maturing", "₹ cr"], [[a, ind(b)] for a, b in grp_m], 8.5, 1.8, 4.3, col_w=[2.7, 1.6], size=12, bold_rows=(4,))
    d.bullets(s, [("Each ₹1 lakh cr refinanced with deposits ", f"saves about ₹{ind((v('Model|Cost of borrowings', 'FY26A') - v('Model|Cost of deposits', 'FY26A')) * 1e5)} cr a year before tax.")],
              8.5, 4.6, 4.3, 1.5, size=13)

    # ================================================================ 12 B3. Rate sensitivity
    s = d.slide(f"HDFC Bank is asset-sensitive: +100 bp adds ₹{ind(ear)} cr to NII, so the October repo hike helps if deposit pricing holds",
                "HDFC Bank IR26 p384 (maturity pattern); external-benchmark share of advances is a labelled assumption (55%, range 45-65%); "
                f"RBI policy repo; {SRC_MODEL}, ALM tab", "B. Margin")
    buckets = [k.split("|")[1] for k in O["Base"] if k.startswith("ALM|") and k.split("|")[1][0].isdigit() or k == "ALM|Over 5 years"]
    gaps = [O["Base"][f"ALM|{b}"][5] / 1000 for b in buckets]
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, buckets, [("Repricing gap, ₹ '000 cr", gaps)], 0.5, 1.7, 8.0, 4.9,
            point_colors=[ACCENT if x >= 0 else CONTEXT for x in gaps], legend=False, fmt='#,##0;(#,##0)', axis_visible=False)
    d.kpi(s, ind(ear), "Earnings at risk, +100 bp, 12 months, ₹ cr", 8.9, 1.8, w=4)
    d.kpi(s, pct(v("ALM|As % of FY26 NII", None)), f"of FY26 NII; about {ear_bp:.0f} bp of FY27E RoA after tax", 8.9, 3.3, w=4)
    d.kpi(s, f"{beta:.2f}", "Realised deposit beta, FY25-FY26 (change in cost of deposits / change in repo)", 8.9, 4.8, w=4)

    # ================================================================ 13 B4. Say vs do
    sd = pd.read_csv(I / "concall_say_do.csv")
    sdh = sd[sd.iloc[:, 0] == "HDFCBANK"]
    s = d.slide("Management has already missed one margin range; the new guidance is directional, so the board should track it quarterly",
                "Earnings-call transcripts via FactIQ (links in data/inputs/concall_say_do.csv); HDFC Bank Q4 FY26 and Q2 FY27 investor presentations, p3. Quotes are paraphrased; verbatim text is at the links",
                "B. Margin")
    rows = [[f"Q{r.iloc[1][-1]} FY{r.iloc[1][4:6]}", r.iloc[3], r.iloc[4], r.iloc[7], r.iloc[8]] for _, r in sdh.iterrows()]
    d.table(s, ["Call", "Speaker", "What management said (paraphrase)", "What happened", "Verdict"], rows, 0.5, 1.8, 12.3,
            col_w=[1.2, 1.1, 4.4, 4.4, 1.2], size=12, row_h=0.9, align_right_from=99)
    d.bullets(s, [("Board test for Q3 FY27 (January 2027): ", f"NIM on total assets at or above {nimt.loc['HDFCBANK', 'q2fy27_nim']:.2f}%, and cost of deposits flat or lower quarter on quarter.")],
              0.5, 5.0, 12.3, 1.0, size=14)

    # ================================================================ 14 C. IRDAI fees
    s = d.slide(f"The IRDAI caps cost the bank ₹{ind(irdai29)} cr of fees by FY29E; the bigger question is how the group splits HDFC Life's saving",
                "IRDAI exposure draft on commission and expenses of management, Sept 2026 (proposal, not final); IRDAI Handbook 2024-25 T100; HDFC Life FY26 and Q2 FY27 "
                f"disclosures; {SRC_MODEL}, Fees tab", "C. Fees")
    rows = [["Bank fee lost, FY28E", ind(irdai28), "Half the cap effect in year one"],
            ["Bank fee lost, FY29E", ind(irdai29), f"{pct(irdai29 / oi29)} of FY29E other income"],
            ["HDFC Life commission above caps, all channels", ind(v("Fees|HDFC Life distributor commission above caps, all channels", None)), "Annual, on FY25 mix"],
            ["HDFC Life net change in VNB", f"+{ind(dvnb)}", "Half of saving kept; 15% of banca APE lost"],
            ["Value to HDFC Bank shareholders", f"+{ind(val_life)}", f"{v('Fees|Market-implied VNB multiple', None):.1f}x VNB multiple; 50.2% stake"]]
    d.table(s, ["Item", "₹ cr", "Basis"], rows, 0.5, 1.8, 7.6, col_w=[3.5, 1.2, 2.9], size=12, row_h=0.5, right_cols={1})
    d.bullets(s, [("For the bank: ", "a rounding error on other income, and it lands from FY28."),
                  ("For the group: ", f"bancassurance is {pct(v('Fees|Bancassurance share of individual APE', None), 0)} of HDFC Life's individual APE. If the bank pulls back, volume losses can outweigh the margin gain."),
                  ("Move: ", "agree persistency-linked pay and a longer premium-term mix with HDFC Life now, before the final rules.")],
              8.5, 1.8, 4.4, 4.8, size=14, gap=10)

    # ================================================================ 15 D. UPI MDR
    s = d.slide(f"UPI MDR opens a ₹{ind(pool / 1000, 1)}k cr pool; at today's {pct(hshare)} payee share HDFC Bank books about ₹{ind(mdr[2])} cr a year by FY29E",
                "NPCI UPI statistics via FactIQ (P2M value by ticket band, Apr 2025 to Oct 2026; payee banks Sep 2026). MDR of 0.4% above ₹2,000 per the proposal; "
                f"exempt share and acquirer share are labelled assumptions. {SRC_MODEL}, Fees tab", "D. Fees")
    mm = npci.dropna(subset=["p2m_value_cr"]) if "p2m_value_cr" in npci.columns else npci
    vcol = [c for c in npci.columns if "p2m" in c.lower() and "value" in c.lower()][0]
    mcol = npci.columns[0]
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [pd.Timestamp(str(m) + "-01").strftime("%b %y") for m in mm[mcol]], [("P2M value, ₹ lakh cr", [x / 1e5 for x in mm[vcol]])], 0.5, 1.7, 7.8, 4.6,
            point_colors=[CONTEXT] * (len(mm) - 1) + [ACCENT], legend=False, fmt="0.0", gap=40, axis_visible=False)
    d.text(s, "Merchant (P2M) UPI value per month, ₹ lakh cr. October 2026 is the record month: 25.47 bn transactions in total", 0.6, 6.3, 7.8, 0.5, 11, MUTED)
    d.bullets(s, [("Pool. ", f"{pct(v('Fees|Share of P2M value above INR 2,000', None))} of merchant value is above ₹2,000; after exempt categories and the ₹300 cap the pool is ₹{ind(pool)} cr a year."),
                  ("HDFC Bank's take. ", f"₹{ind(mdr[0])} / {ind(mdr[1])} / {ind(mdr[2])} cr in FY27E-FY29E. Yes Bank, with about 54% of payee volume, is the structural winner."),
                  ("Lever. ", f"Lifting payee share to 10% adds only {lev[lev_names[5]][2]:.1f} bp. UPI is a franchise play, not a RoA lever.")],
              8.7, 1.8, 4.2, 4.8, size=14, gap=10)

    # ================================================================ 16 E. Cost
    s = d.slide(f"Cost-to-income falls from {pct(ci['FY26A'])} to {pct(ci['FY29E'])} in the base case; the branch build-out has to start paying back",
                f"HDFC Bank IR26 Schedule 16 and p18 (9,689 branches), p420 (2,10,969 employees); {SRC_MODEL}, Opex_Credit tab", "E. Cost")
    yrs = YEARS[1:]
    d.chart(s, XL_CHART_TYPE.LINE_MARKERS, [y[:4] for y in yrs], [("Opex / average assets %", [oa[y] * 100 for y in yrs])], 0.5, 1.7, 7.6, 4.9,
            colors=[ACCENT], legend=False, fmt="0.00", axis_visible=False)
    d.kpi(s, f"₹{v('Opex_Credit|Net revenue per branch', 'FY26A'):.1f} cr", "Net revenue per branch, FY26", 8.6, 1.8, w=4)
    d.kpi(s, pct(v("Opex_Credit|Employee cost / opex", "FY26A")), "Employee cost share of opex, FY26", 8.6, 3.3, w=4)
    d.kpi(s, f"{lev[lev_names[1]][2]:.1f} bp", "RoA from 3% lower opex than plan by FY29E", 8.6, 4.8, w=4)

    # ================================================================ 17 F. Credit
    s = d.slide(f"Credit cost is {norm_gap:.0f} bp below its through-the-cycle level; the plan must absorb about {norm_roa:.0f} bp of RoA as it normalises",
                f"HDFC Bank IR26 p234 (loan loss provisions); {SRC_MODEL}, Opex_Credit and Inputs tabs. FY27E-FY29E is the base-case path", "F. Credit")
    yrs = YEARS[1:]
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [y[:4] for y in yrs], [("Credit cost, % of average advances", [cc[y] * 100 for y in yrs])], 0.5, 1.7, 7.6, 4.9,
            point_colors=[CONTEXT] * 6 + [ACCENT] * 3, legend=False, fmt="0.00", axis_visible=False)
    d.kpi(s, pct(ttc, 2), "Through-the-cycle credit cost, FY21-FY26", 8.6, 1.8, w=4)
    d.kpi(s, pct(recent, 2), "Recent average, FY24-FY26", 8.6, 3.3, w=4)
    d.kpi(s, pct(v("Model|Credit cost", "FY29E", "Downside"), 2), f"Downside case FY29E; RoA falls to {pct(dn29, 2)}", 8.6, 4.8, w=4, color=CONTEXT)

    # ================================================================ 18 G. P/B vs RoE
    s = d.slide("Across peers P/B barely tracks RoE, so we value the levers on justified P/B rather than the regression",
                "Screener market capitalisation and book value, 2-3 Nov 2026; FY26 standalone RoE; Peers tab of " + SRC_MODEL, "G. Valuation")
    cd = XyChartData()
    pr = PR
    other = cd.add_series("Other banks")
    onames = [n for n in pr if n != "HDFC Bank"]
    for n in onames:
        other.add_data_point(pr[n][5] * 100, pr[n][7])
    hd = cd.add_series("HDFC Bank"); hd.add_data_point(pr["HDFC Bank"][5] * 100, pr["HDFC Bank"][7])
    ch = s.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER, Inches(0.5), Inches(1.7), Inches(7.6), Inches(4.9), cd).chart
    ch.font.name, ch.font.size = FONT, Pt(11)
    for ser, c in zip(ch.series, (CONTEXT, ACCENT)):
        ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = c; ser.marker.size = 11; ser.marker.format.line.color.rgb = c
        ser.format.line.fill.background()
    for ser, names in ((ch.series[0], onames), (ch.series[1], ["HDFC Bank"])):
        for j, n in enumerate(names):
            dl = ser.points[j].data_label; dl.has_text_frame = True; dl.text_frame.text = n.replace(" Bank", "").replace(" Mahindra", "").replace("State of India", "SBI")
            dl.position = XL_LABEL_POSITION.RIGHT
            for r in dl.text_frame.paragraphs[0].runs:
                r.font.name, r.font.size, r.font.italic, r.font.color.rgb = FONT, Pt(9), False, INK
    ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False; ch.legend.font.name = FONT
    ch.value_axis.has_major_gridlines = False; ch.category_axis.has_major_gridlines = False
    ch.value_axis.has_title = True; ch.value_axis.axis_title.text_frame.text = "Price / book (x)"
    ch.category_axis.has_title = True; ch.category_axis.axis_title.text_frame.text = "RoE FY26 (%)"
    for ax in (ch.value_axis, ch.category_axis):
        for p_ in ax.axis_title.text_frame.paragraphs:
            for r in p_.runs:
                r.font.name, r.font.size, r.font.bold, r.font.italic = FONT, Pt(11), False, False
        ax.tick_labels.font.name = FONT
    d.bullets(s, [("R-squared " + f"{v('Peers|R-squared', None):.3f}" + " on the five clean private banks. ", "Kotak and ICICI Bank trade on franchise and growth, not on current RoE."),
                  ("Method. ", f"Justified P/B = (RoE − g) / (Ke − g) with Ke {pct(ke)} and g {pct(g, 0)}. A 10 bp rise in sustainable RoA is worth ₹{ind(v10)} cr of equity value."),
                  ("Cross-check. ", "Residual income on FY27E-FY29E with a fading terminal value gives a similar answer.")],
              8.5, 1.8, 4.4, 4.8, size=14, gap=10)

    # ================================================================ 19 G2. Football field
    s = d.slide(f"Only the upside case supports today's ₹{price:.0f} share price; the base case is worth ₹{ri['Base']:.0f}-{sotp['Base']:.0f}",
                f"{SRC_MODEL}, Valuation tab, recalculated per scenario. Bars span Downside to Upside; the base case is labelled", "G. Valuation")
    cats = [f"Residual income: ₹{ri['Downside']:.0f}-{ri['Upside']:.0f}, base ₹{ri['Base']:.0f}", f"Sum of the parts: ₹{sotp['Downside']:.0f}-{sotp['Upside']:.0f}, base ₹{sotp['Base']:.0f}",
            f"Share price, 2 Nov 2026: ₹{price:.0f}"]
    lo = [ri["Downside"], sotp["Downside"], price - 4]; hi = [ri["Upside"], sotp["Upside"], price + 4]
    ch = d.chart(s, XL_CHART_TYPE.BAR_STACKED, cats, [("low", lo), ("Downside to Upside, ₹ per share", [h - l for h, l in zip(hi, lo)])], 0.5, 1.7, 8.2, 3.4,
                 colors=[None, ACCENT], legend=False, labels=False, gap=60, overlap=100, axis_fmt="#,##0", caption="₹ per share; bars span Downside to Upside")
    ch.value_axis.minimum_scale, ch.value_axis.maximum_scale = 0, 900
    ch.series[1].points[2].format.fill.solid(); ch.series[1].points[2].format.fill.fore_color.rgb = INK
    rows = [[sc, pct(v("Model|Return on average assets", "FY29E", sc), 2), pct(roe29[sc]), f"₹{ri[sc]:.0f}", f"₹{sotp[sc]:.0f}", pct(sotp[sc] / price - 1)] for sc in ("Downside", "Base", "Upside")]
    d.table(s, ["Scenario", "RoA FY29E", "RoE FY29E", "Residual income / share", "Sum of the parts / share", "vs ₹700"], rows, 0.5, 5.3, 8.2,
            col_w=[1.3, 1.2, 1.2, 1.7, 1.7, 1.1], size=11, bold_rows=(1,), right_cols={1, 2, 3, 4, 5})
    d.bullets(s, [("Upside needs: ", "repo held at 6.25%, CASA back to 36%, 80% of maturing borrowings retired and credit cost at 0.60% by FY29E."),
                  ("Downside: ", f"faster credit normalisation (0.85%) and sticky deposit costs take RoA to {pct(dn29, 2)}. The levers cannot close that gap.")],
              9.0, 1.9, 3.9, 4.6, size=14, gap=10)

    # ================================================================ 20 H. Levers
    s = d.slide(f"Six levers add {lev_all[2]:.1f} bp of RoA and ₹{ind(lev_all[4] / 1000, 0)}k cr of equity value; four of them do 85% of the work",
                f"{SRC_MODEL}, Levers tab. Each lever is a driver change on top of the base case in FY29E; sizes, feasibility and timing are judgements for discussion", "H. Answer")
    rows = []
    for k in lev_names:
        r = lev[k]
        rows.append([k, f"{r[2]:.1f}", ind(r[1]), ind(r[4]), f"₹{r[5]:.0f}"])
    rows.append(["All levers", f"{lev_all[2]:.1f}", ind(lev_all[1]), ind(lev_all[4]), f"₹{lev_all[5]:.0f}"])
    d.table(s, ["Lever", "RoA, bp", "PAT, ₹ cr", "Equity value, ₹ cr", "Per share"], rows, 0.5, 1.8, 7.6, col_w=[3.6, 0.9, 1.0, 1.3, 0.8], size=12, right_cols={1, 2, 3, 4},
            bold_rows=(6,), row_h=0.45)
    d.chart(s, XL_CHART_TYPE.BAR_CLUSTERED, [SHORT[k] for k in lev_names], [("bp", [lev[k][2] for k in lev_names])],
            8.4, 1.9, 4.5, 3.6, colors=[ACCENT], legend=False, fmt="0.0", gap=40, axis_visible=False, caption="RoA uplift, bp")
    top4 = sum(lev[k][2] for k in lev_names[:4]) / lev_all[2]
    d.text(s, f"Top four: {pct(top4, 0)} of the uplift", 8.5, 5.4, 4.4, 0.4, 13, MUTED)

    # ================================================================ 21 Prioritisation matrix
    feas = {"Rebuild CASA": (3, 18), "Retire legacy borrowings faster": (4, 12), "Re-mix advances to higher-yield retail and SME": (3, 9),
            "Branch and operations productivity": (4, 12), "Protect bancassurance and grow card fees": (3, 12), "Win UPI merchant acquiring share": (2, 18)}
    s = d.slide("Start with borrowings and productivity: both are high-feasibility and pay back within a year",
                f"{SRC_MODEL}, Levers tab (feasibility 1-5 and months to impact are team judgements)", "H. Answer")
    X0, Y0, W, H = 1.2, 1.8, 7.0, 4.6
    d.box(s, X0, Y0, W, H, fill=WHITE, line=GRID)
    d.box(s, X0 + W / 2, Y0, W / 2, H / 2, fill=PALE)
    for t, x, y in (("Feasibility (1 = hard, 5 = easy)", X0 + 1.8, Y0 + H + 0.05), ("RoA impact, bp", 0.2, Y0 - 0.3)):
        d.text(s, t, x, y, 4, 0.3, 11, MUTED)
    for k in lev_names:
        f, mo = feas[k]
        px = X0 + (f - 1) / 4 * (W - 0.6) + 0.3
        py = Y0 + H - lev[k][2] / 6 * (H - 0.4) - 0.2
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(px - 0.1), Inches(py - 0.1), Inches(0.2), Inches(0.2))
        dot.fill.solid(); dot.fill.fore_color.rgb = ACCENT if mo <= 12 else CONTEXT; dot.line.fill.background()
        d.text(s, f"{SHORT[k]} ({mo} m)", px + 0.12, py - 0.17, 2.6, 0.35, 11, INK)
    d.text(s, "Do first", X0 + W - 1.2, Y0 + 0.05, 1.1, 0.3, 11, ACCENT, bold=True)
    for val_ in (0, 3, 6):
        d.text(s, f"{val_}", X0 - 0.45, Y0 + H - val_ / 6 * (H - 0.4) - 0.35, 0.35, 0.3, 10, MUTED, align=PP_ALIGN.RIGHT)
    for f_ in (1, 3, 5):
        d.text(s, f"{f_}", X0 + (f_ - 1) / 4 * (W - 0.6) + 0.15, Y0 + H - 0.3, 0.3, 0.3, 10, MUTED)
    d.bullets(s, [("Wave 1 (0-12 months): ", "retire borrowings, branch and operations productivity, advance re-mix."),
                  ("Wave 2 (12-18 months): ", "CASA rebuild, which is the largest structural lever but slowest; UPI acquiring as a franchise option."),
                  ("Blue dots ", "pay back within 12 months; grey take longer.")],
              8.7, 1.8, 4.2, 4.8, size=14, gap=10)

    # ================================================================ 22 Bridge
    s = d.slide(f"FY26 to FY29E: the base case adds {drift:.1f} bp, the levers {lev_all[2]:.1f} bp, for {with_lev / 100:.2f}% RoA against a 2.00% target",
                f"{SRC_MODEL}, Levers tab (bridge). Core RoA excludes the FY26 one-offs", "H. Answer")
    steps = [("FY26A", roa26, None)] + [("Drift", drift, "d")] + [(SHORT[k], lev[k][2], "l") for k in lev_names] + [("FY29E", with_lev, None)]
    base_s, vis = [], []
    run = 0.0
    for nm, val, kind in steps:
        if kind is None:
            base_s.append(0); vis.append(val); run = val
        else:
            base_s.append(run if val >= 0 else run + val); vis.append(abs(val)); run += val
    BR = {"Advance re-mix": "Re-mix", "Bancassurance and cards": "Fees", "UPI acquiring": "UPI", "Borrowings": "Borrow-\nings", "Productivity": "Product-\nivity"}
    cats = [f"{BR.get(st[0], st[0])}\n{st[1]:.0f}" if st[2] is None else f"{BR.get(st[0], st[0])}\n+{st[1]:.1f}" for st in steps]
    ch = d.chart(s, XL_CHART_TYPE.COLUMN_STACKED, cats, [("base", base_s), ("RoA, bp", vis)], 0.5, 1.9, 8.6, 4.8,
                 colors=[None, ACCENT], legend=False, labels=False, gap=40, overlap=100, axis_visible=False, caption="RoA, bp; axis starts at 150 bp")
    ch.value_axis.minimum_scale, ch.value_axis.maximum_scale = 150, 210
    ch.category_axis.tick_labels.font.size = Pt(10)
    tx = ch.category_axis._element.get_or_add_txPr(); tx.find("{http://schemas.openxmlformats.org/drawingml/2006/main}bodyPr").set("rot", "0")
    ser = ch.series[1]
    for j, (nm, val, kind) in enumerate(steps):
        pt = ser.points[j]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = CONTEXT if kind == "d" else ACCENT
    rows = [[sc, f"{O[sc]['Levers|RoA FY29E, scenario before levers'][2]:.0f}", f"{O[sc]['Levers|Levers'][2]:.1f}", f"{O[sc]['Levers|RoA FY29E with levers'][2]:.0f}",
             f"{O[sc]['Levers|Shortfall (-) / headroom (+) to target'][2]:+.0f}"] for sc in ("Downside", "Base", "Upside")]
    d.table(s, ["Scenario", "Before levers", "Levers", "With levers", "vs 200"], rows, 9.3, 1.9, 3.6, col_w=[0.85, 0.75, 0.7, 0.75, 0.55], size=10, row_h=0.42,
            bold_rows=(1,), right_cols={1, 2, 3, 4})
    d.text(s, "bp of RoA, FY29E", 9.3, 1.6, 3.6, 0.3, 10, MUTED)
    d.bullets(s, [("Downside is the real exposure: ", f"the levers add {O['Downside']['Levers|Levers'][2]:.0f} bp, but RoA still ends {-O['Downside']['Levers|Shortfall (-) / headroom (+) to target'][2]:.0f} bp short of target.")], 9.3, 3.8, 3.6, 2.0, size=13)

    # ================================================================ 23 Roadmap
    s = d.slide("A 12-month plan: three moves start now, with board checkpoints at each quarterly result", "Team analysis", "H. Answer")
    rows = [["Funding: retire borrowings", "Approve refinancing plan for ₹1.93 lakh cr maturing in FY27; set deposit-led target", "Retire ₹75,000 cr above plan; borrowings below 9% of funding", "Treasurer"],
            ["Funding: rebuild CASA", "Salary and SME current-account squads in the top 500 branches; re-price term deposits by tenor", "CASA +1.5 pp vs plan; cost of deposits flat while repo rises", "Head, Branch Banking"],
            ["Assets: re-mix advances", "Shift new mortgage origination to pricing floors; grow SME and secured retail within risk appetite", "Yield on advances +10 bp vs plan", "CRO and Head, Retail Assets"],
            ["Cost: productivity", "Branch-vintage review of FY22-FY25 openings; freeze net hiring outside sales", "Opex 3% below plan; cost-to-income under 38%", "COO"],
            ["Fees: bancassurance", "Open renegotiation with HDFC Life on persistency-linked pay; model final IRDAI rules", "New commission grid live before caps take effect", "Head, Third-party Products"],
            ["Governance", "RoA cockpit to the board monthly; lever owners named", "Quarterly lever review at each result", "CFO"]]
    d.table(s, ["Move", "0-3 months", "3-12 months", "Owner"], rows, 0.5, 1.7, 12.3, col_w=[2.4, 4.4, 3.8, 1.7], size=11, row_h=0.72, align_right_from=99)

    # ================================================================ 24 KPIs
    s = d.slide("Seven KPIs tell the board whether the plan is on track", f"{SRC_MODEL}; FY26 from HDFC Bank IR26. With-lever values apply lever sizes to the base case", "H. Answer")
    rows = [["RoA (core)", pct(roa26 / 1e4, 2), pct(base29, 2), pct(with_lev / 1e4, 2), "Quarterly"],
            ["NIM on interest-earning assets", pct(nim["FY26A"], 2), pct(nim["FY29E"], 2), "–", "Quarterly"],
            ["CASA ratio", pct(casa26), pct(casa29), pct(casa29 + 0.015), "Monthly"],
            ["Borrowings / funding", pct(bshare["FY26A"]), pct(bshare["FY29E"]), "−₹75,000 cr", "Monthly"],
            ["Opex / average assets", pct(oa["FY26A"], 2), pct(oa["FY29E"], 2), pct(oa["FY29E"] * 0.97, 2), "Quarterly"],
            ["Credit cost", pct(cc["FY26A"], 2), pct(cc["FY29E"], 2), "–", "Quarterly"],
            ["RoE", pct(v("Model|Return on average net worth", "FY26A")), pct(roe29["Base"]), pct(roe29["Base"] + lev_all[3]), "Quarterly"]]
    d.table(s, ["KPI", "FY26A", "FY29E base", "FY29E with levers", "Cadence"], rows, 0.5, 1.8, 12.3, col_w=[3.6, 2.0, 2.2, 2.6, 1.9], size=13, row_h=0.55, bold_rows=(0,), right_cols={1, 2, 3})

    # ================================================================ 25 Risks
    s = d.slide("Credit normalisation and deposit pricing are the two risks that could break the plan", f"{SRC_MODEL}, Inputs, ALM and Opex_Credit tabs; IRDAI exposure draft Sept 2026", "H. Answer")
    rows = [["Credit cost normalises faster", "Slippages above 1.5% annualised", f"{(base29 - dn29) * 1e4:.0f} bp (downside case, all drivers)", "Tighten unsecured origination; hold floating provisions"],
            ["Deposit costs stay sticky", "Cost of deposits rises faster than repo", "Deposit beta 0.35 to 0.50 removes most of the NIM gain", "CASA squads; tenor pricing"],
            ["Rate cuts in FY28", "Repo below 5.25%", f"About {ear_bp:.0f} bp per 100 bp (asset-sensitive)", "Raise fixed-rate share of new loans"],
            ["Final IRDAI caps stricter", "Final rules at or below draft limits", f"Up to ₹{ind(irdai29 * 1.5)} cr of fees (1.5x severity)", "Persistency-linked pay agreed early"],
            ["Execution of CASA rebuild", "CASA flat for two quarters", f"{lev[lev_names[2]][2]:.1f} bp lever at risk", "Named owner; monthly tracking"]]
    d.table(s, ["Risk", "Early warning", "RoA impact", "Mitigation"], rows, 0.5, 1.8, 12.3, col_w=[2.8, 3.0, 3.3, 3.2], size=12, row_h=0.7, align_right_from=99)

    # ================================================================ Appendix divider
    s = d.p.slides.add_slide(d.p.slide_layouts[6]); d.n += 1
    d.box(s, 0, 0, 0.35, 7.5, fill=ACCENT)
    d.text(s, "Appendix", 0.9, 2.8, 11, 0.8, 32, ACCENT, bold=True)
    d.text(s, "Method and model | Scenario drivers | Sector modules: IRDAI caps and SBI Q2 FY27 | Sources", 0.9, 3.7, 11, 0.6, 15, MUTED)

    # ================================================================ A1 Method
    s = d.slide("Method: a driver-based bank model, valued on justified P/B, residual income and sum of the parts",
                "Team analysis; model is models/HDFC_RoA_Path_FY29.xlsx", "Appendix")
    d.bullets(s, [
        ("Spreading. ", "FY20-FY26 standalone P&L and balance sheet from HDFC Bank IR26 schedules and ten-year highlights, tied to Screener; one-offs isolated."),
        ("Projection. ", "Interest on average balances; yields and costs move with repo through betas; investments and liquidity balance the sheet; "
                         "in-year retained profit is held as cash and deployed the next year, so the model has no circularity."),
        ("Margin and ALM. ", "Rate/volume walk of NII; repricing gap from the IR26 maturity pattern; earnings at risk for +100 bp; legacy borrowing run-off from the maturity schedule."),
        ("Fees. ", "IRDAI cap model (Monte Carlo, 10,000 draws) for commission above the proposed caps; UPI MDR pool from NPCI ticket-band data and payee-bank shares."),
        ("Valuation. ", "CAPM cost of equity; justified P/B on FY29E RoE; residual income FY27E-FY29E with terminal value; listed subsidiaries at market value less 20%."),
        ("Controls. ", "Nine model checks roll up to a master check on the Cover; a lint script fails the build on non-Garamond fonts, italics, merged cells, "
                       "hard-codes inside formulas, broken row patterns and error values."),
    ], 0.5, 1.7, 12.3, 5.0, size=14, gap=8)

    # ================================================================ A2 Scenario drivers
    s = d.slide("Scenario drivers, FY29E", "Inputs tab of " + SRC_MODEL + "; repo path from RBI Survey of Professional Forecasters, round 102 (Sept 2026)", "Appendix")
    rows = [["Policy repo, fiscal-year average", "5.75%", "6.25%", "5.00%"], ["Advances growth", "14%", "16%", "12%"], ["Deposit growth", "14%", "16%", "12%"],
            ["CASA ratio, year end", "33.5%", "36.0%", "32.0%"], ["Maturing borrowings retired", "60%", "80%", "30%"], ["Deposit cost beta", "0.35", "0.30", "0.25"],
            ["Core fee growth", "12%", "14%", "9%"], ["Opex growth", "10%", "9%", "12%"], ["Credit cost", "0.68%", "0.60%", "0.85%"], ["IRDAI severity on bank fees", "1.0x", "0.5x", "1.5x"]]
    d.table(s, ["Driver (FY29E)", "Base", "Upside", "Downside"], rows, 0.5, 1.8, 8.5, col_w=[4.3, 1.4, 1.4, 1.4], size=12, row_h=0.42, right_cols={1, 2, 3})
    d.text(s, "Read the downside deposit beta with care: a lower beta in a falling-rate path means deposit costs lag the cut, which is adverse for an asset-sensitive bank.",
           9.3, 1.8, 3.6, 2.5, 13, MUTED)

    # ================================================================ A3 Sector: IRDAI
    s = d.slide(f"Sector view: commission above the proposed caps is about ₹{ind(mc['50%'] / 1000, 1)}k cr a year across life insurers",
                "IRDAI Handbook 2024-25; IRDAI exposure draft, Sept 2026 (proposal); Monte Carlo of premium-paying-term mix, 10,000 draws, seed 20261102 (data/tidy/ins_mc_summary.csv)",
                "Appendix")
    d.kpi(s, f"₹{ind(mc['50%'] / 1000, 1)}k cr", "Median annual first-year commission above the caps", 0.6, 1.9, w=4)
    d.kpi(s, f"₹{ind(mc['10%'] / 1000, 1)}-{ind(mc['90%'] / 1000, 1)}k cr", "P10-P90 range", 4.6, 1.9, w=4)
    d.kpi(s, "38.8% vs 12.1%", "Private life commission growth vs premium growth, FY25", 8.6, 1.9, w=4.3)
    d.bullets(s, [("Who carries it. ", "Bank-promoted insurers: the sum is about 74% of SBI Life's FY25 profit and 70% of HDFC Life's, against about 6% of LIC's."),
                  ("Status. ", "A September 2026 proposal, not final. The premium-paying-term mix is an assumption, stress-tested by the Monte Carlo.")],
              0.6, 4.2, 12, 2.4, size=15, gap=10)

    # ================================================================ A4 SBI Q2 FY27
    s = d.slide("Not every bank's margin fell in Q2 FY27: SBI's NIM rose to 2.94%, which corrects our earlier sector read",
                "State Bank of India press release, Q2 FY27 results, 3 Nov 2026; HDFC Bank, ICICI Bank, Axis Bank, Kotak Q2 FY27 investor presentations (data/inputs/nim_trajectory.csv)",
                "Appendix")
    BN = {"HDFCBANK": "HDFC Bank", "ICICIBANK": "ICICI Bank", "AXISBANK": "Axis Bank", "KOTAKBANK": "Kotak Mahindra Bank", "SBIN": "State Bank of India"}
    rows = [[BN[b], f"{r.q4fy26_nim:.2f}%", f"{r.q2fy27_nim:.2f}%" if pd.notna(r.q2fy27_nim) else "2.94%", f"{r.change_bp:+.0f}" if pd.notna(r.change_bp) else "+13",
             r.basis if b != "SBIN" else "whole bank (SBI Q2 FY27 press release)"] for b, r in nimt.iterrows()]
    d.table(s, ["Bank", "NIM Q4 FY26", "NIM Q2 FY27", "Change, bp", "Basis"], rows, 0.5, 1.8, 12.3, col_w=[2.3, 1.4, 1.4, 1.3, 5.9], size=12, row_h=0.45, right_cols={1, 2, 3})
    d.bullets(s, [("SBI Q2 FY27: ", "NII ₹49,143 cr, operating profit ₹34,226 cr, PAT ₹23,038 cr, CASA 38.32%, credit cost 0.22%."),
                  ("Read-across. ", "SBI's stronger CASA base cushioned deposit repricing; it is the clearest evidence that funding mix, not the rate cycle alone, drives margin.")],
              0.5, 4.8, 12.3, 1.8, size=14, gap=8)

    # ================================================================ A5 Sources
    s = d.slide("Sources", "data/raw/manifest.csv holds a sha256 hash of every raw file", "Appendix")
    d.bullets(s, [("S1 ", "HDFC Bank Integrated Annual Report 2025-26: Schedules 3, 4, 8, 9, 13-16 (pp359-366), maturity pattern (p384), ten-year highlights (p234), stakes (p52)."),
                  ("S2 ", "HDFC Bank, ICICI Bank, Axis Bank, Kotak investor presentations Q4 FY26 and Q2 FY27; SBI Q2 FY27 press release."),
                  ("S3 ", "Screener.in standalone financials and valuation for twelve banks and three listed HDFC subsidiaries (secondary, tied to filings)."),
                  ("S4 ", "RBI: policy repo, 10-year G-sec, Survey of Professional Forecasters round 102 (via FactIQ)."),
                  ("S5 ", "NPCI UPI statistics: P2M value by ticket band, payee banks (via FactIQ); monthly totals from NPCI."),
                  ("S6 ", "IRDAI Handbook 2024-25 and the September 2026 exposure draft on commission and expenses of management."),
                  ("S7 ", "HDFC Life FY26 and Q2 FY27 public disclosures: VNB, APE, embedded value, channel mix."),
                  ("S8 ", "Earnings-call transcripts (FactIQ) for the say-versus-do tracker."),
                  ("Framing. ", DISCLAIMER)], 0.5, 1.7, 12.3, 5.0, size=13, gap=6)

    out = ROOT / "decks" / "HDFC_RoA_Steerco.pptx"
    d.save(out)
    print("wrote", out, d.n, "slides")


if __name__ == "__main__":
    main()
