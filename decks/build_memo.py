"""Two-page CEO memo (pyramid form) built from the same model export as the steerco deck.
Garamond throughout, no italics. Output: decks/HDFC_CEO_Memo.docx (PDF rendered by LibreOffice in the build step).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_hdfc_deck import DISCLAIMER, ROOT, I, O, T, ind, pct, v  # noqa: E402

ACCENT, MUTED = RGBColor(0x1F, 0x3A, 0x5F), RGBColor(0x6B, 0x6B, 0x6B)


def run(p, text, bold=False, size=11, color=None):
    r = p.add_run(text); r.bold, r.italic = bold, False
    r.font.name, r.font.size = "Garamond", Pt(size)
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Garamond")
    if color is not None:
        r.font.color.rgb = color
    return r


def para(doc, parts, space_after=4, style=None):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after, p.paragraph_format.space_before = Pt(space_after), Pt(0)
    for t, b in parts:
        run(p, t, bold=b)
    return p


def head(doc, text):
    p = doc.add_paragraph(); p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(6), Pt(2)
    run(p, text, bold=True, size=12, color=ACCENT)


def main():
    lev_names = ["Re-mix advances to higher-yield retail and SME", "Branch and operations productivity", "Rebuild CASA",
                 "Retire legacy borrowings faster", "Protect bancassurance and grow card fees", "Win UPI merchant acquiring share"]
    lev = {k: O["Base"][f"Levers|{k}"] for k in lev_names}
    lev_all = O["Base"]["Levers|All levers"]
    with_lev = O["Base"]["Levers|RoA FY29E with levers"][2] / 1e4
    sc = {s: v("Model|Return on average assets", "FY29E", s) for s in O}
    roe = {s: v("Model|Return on average net worth", "FY29E", s) for s in O}
    sotp = {s: v("Valuation|Sum of the parts per share", None, s) for s in O}
    ri = {s: v("Valuation|Residual income per share", None, s) for s in O}
    ke, roe_impl, price = v("Valuation|Cost of equity", None), v("Valuation|RoE the market is pricing", None), v("Valuation|Current share price", None)
    v10 = v("Valuation|Value of +10 bp RoA (equity value)", None)
    facts = pd.read_csv(T / "bank_facts.csv")
    q = facts[(facts.entity == "HDFCBANK") & (facts.period == "Q2FY27")].set_index("metric").value
    roa_q2 = q["pat"] * 4 / ((q["assets_open"] + q["assets_close"]) / 2)
    sh = pd.read_csv(T / "bank_shapley_FY26.csv"); shh = sh[(sh.metric == "RoA") & (sh.bank == "HDFCBANK")].iloc[0]
    bor_le1 = pd.read_csv(I / "hdfc_borrowing_maturity_mar26.csv").amount_cr[:8].sum()
    ttc, recent = v("Opex_Credit|Through-the-cycle credit cost, FY21-FY26 average", None), v("Opex_Credit|Recent credit cost, FY24-FY26 average", None)
    irdai29, oi29 = v("Fees|Bank fee lost to caps", "FY29E"), v("Model|Other income", "FY29E")
    mdr29, dvnb = v("Fees|HDFC Bank MDR revenue", "FY29E"), v("Fees|Net change in annual VNB", None)
    ear = v("ALM|Earnings at risk, +100 bp", None)
    nii23, nii26 = v("Model|NII / average assets", "FY23A"), v("Model|NII / average assets", "FY26A")

    doc = Document()
    for s_ in doc.sections:
        s_.top_margin = s_.bottom_margin = Cm(1.6); s_.left_margin = s_.right_margin = Cm(2.0)
        fp = s_.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run(fp, DISCLAIMER, size=8, color=MUTED)
    st = doc.styles["Normal"]; st.font.name, st.font.size, st.font.italic = "Garamond", Pt(11), False
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Garamond")
    for nm in ("List Bullet", "List Number"):
        doc.styles[nm].font.name, doc.styles[nm].font.italic = "Garamond", False

    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
    run(p, "Memorandum", bold=True, size=16, color=ACCENT)
    for lab, val in (("To", "Managing Director and CEO, HDFC Bank (hypothetical addressee)"), ("From", "Anklesh"),
                     ("Date", "3 November 2026"), ("Subject", "Getting standalone RoA back to 2% by FY29")):
        para(doc, [(f"{lab}: ", True), (val, False)], space_after=0)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)

    head(doc, "The answer")
    para(doc, [("HDFC Bank can be back above 2% RoA by FY29, but the base case will not get it there and the share price already assumes it will. ", True),
               (f"On current drivers RoA recovers only to {pct(sc['Base'], 2)} by FY29E. Six management levers add {lev_all[2]:.0f} bp, to {pct(with_lev, 2)}. "
                f"The market price of ₹{price:.0f} implies a {pct(roe_impl)} RoE; the base case gives {pct(roe['Base'])}. The plan therefore has to be "
                "funding-led: deposits and borrowings first, asset mix second, cost third.", False)])

    head(doc, "1. The problem is margin, not cost")
    for t in [
        f"RoA held at 1.8-2.0% for a decade. The merger moved NII from {pct(nii23, 2)} of average assets (FY23) to {pct(nii26, 2)} (FY26); Q2 FY27 RoA is {pct(roa_q2, 2)} annualised.",
        f"The {shh.gap * 100:.0f} bp gap to ICICI Bank is {shh.nii * 100:.0f} bp of NII and {shh.prov * 100:.0f} bp of FY26's one-off provisions. HDFC Bank is already ahead on cost, other income and tax.",
        "Management missed its own 3.4-3.5% NIM range (3.16% on total assets in Q2 FY27). The CFO now calls the bottom; that should be tested at Q3 FY27.",
    ]:
        para(doc, [(t, False)], space_after=2, style="List Bullet")

    head(doc, "2. The base case helps, but not enough")
    for t in [
        f"₹{ind(bor_le1)} cr of legacy borrowings mature within a year. Replacing 60% with deposits lifts NIM from 3.12% to {pct(v('Model|Net interest margin on interest-earning assets', 'FY29E'), 2)} by FY29E.",
        f"The bank is asset-sensitive: +100 bp adds ₹{ind(ear)} cr to NII. The October 2026 repo hike helps only if deposit pricing holds.",
        f"Credit cost is {pct(recent, 2)} against a through-the-cycle {pct(ttc, 2)}. Normalisation costs about {v('Opex_Credit|RoA at risk if credit cost normalises', None):.0f} bp of RoA and is in the base case.",
        f"Regulation is small for the bank: the IRDAI caps cost ₹{ind(irdai29)} cr of fees by FY29E ({pct(irdai29 / oi29)} of other income); UPI MDR adds ₹{ind(mdr29)} cr. "
        f"For the group, HDFC Life's VNB nets +₹{ind(dvnb)} cr only if the bank keeps distributing.",
    ]:
        para(doc, [(t, False)], space_after=2, style="List Bullet")

    head(doc, "3. Six levers close the gap; four do most of the work")
    tbl = doc.add_table(rows=1, cols=4); tbl.style = "Table Grid"
    for j, h in enumerate(["Lever (FY29E, on top of base case)", "RoA, bp", "PAT, ₹ cr", "Equity value, ₹ cr"]):
        c = tbl.rows[0].cells[j]; c.text = ""; run(c.paragraphs[0], h, bold=True, size=10)
    for k in lev_names + ["All levers"]:
        r_ = lev.get(k, lev_all); cells = tbl.add_row().cells
        for j, t in enumerate([k, f"{r_[2]:.1f}", ind(r_[1]), ind(r_[4])]):
            cells[j].text = ""; pp = cells[j].paragraphs[0]
            if j:
                pp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            run(pp, t, bold=(k == "All levers"), size=10)
    tbl.autofit = False
    for j, w in enumerate((Cm(9.0), Cm(2.2), Cm(2.6), Cm(3.2))):
        tbl.columns[j].width = w
        for row in tbl.rows:
            row.cells[j].width = w
    para(doc, [("Lever sizes, feasibility and timing are judgements for discussion; each is a driver change in the model, so the values are traceable.", False)], space_after=2)

    head(doc, "4. What it is worth")
    para(doc, [(f"At a {pct(ke)} cost of equity, each 10 bp of sustainable RoA is worth about ₹{ind(v10)} cr of equity value. "
                f"The base case supports ₹{ri['Base']:.0f}-{sotp['Base']:.0f} a share (residual income to sum of the parts) against ₹{price:.0f}; "
                f"only the upside case (RoA {pct(sc['Upside'], 2)}) supports today's price, at ₹{ri['Upside']:.0f}-{sotp['Upside']:.0f}. "
                f"In the downside case (RoA {pct(sc['Downside'], 2)}) the levers still leave RoA {-O['Downside']['Levers|Shortfall (-) / headroom (+) to target'][2]:.0f} bp short.", False)])

    head(doc, "5. Decisions requested and the first 90 days")
    for t in [
        ("Make deposits the binding constraint. ", "Hold the credit-deposit ratio near 93% and fund a 1.5 pp CASA rebuild before chasing loan share."),
        ("Retire ₹75,000 cr of legacy borrowings ahead of plan. ", f"Borrowings cost {pct(v('Model|Cost of borrowings', 'FY26A'), 2)} against {pct(v('Model|Cost of deposits', 'FY26A'), 2)} for deposits."),
        ("Re-price the HDFC Life partnership now. ", "Agree persistency-linked commission and a longer premium-term mix before the IRDAI caps are final."),
        ("Govern it monthly. ", "A seven-KPI RoA cockpit to the board, with named owners for each lever and a test of the margin guidance at the Q3 FY27 result."),
    ]:
        para(doc, [(t[0], True), (t[1], False)], space_after=2, style="List Number")

    head(doc, "Main risks")
    para(doc, [(f"Faster credit normalisation and sticky deposit costs are the two that break the plan. A deposit beta of 0.50 rather than 0.35 removes most of the NIM gain; "
                f"a credit cost of 0.85% by FY29 takes RoA to {pct(sc['Downside'], 2)} before levers. Both have early-warning triggers in the cockpit.", False)])
    para(doc, [("Method and sources: models/HDFC_RoA_Path_FY29.xlsx and decks/HDFC_RoA_Steerco.pptx. Public data only: HDFC Bank IR26, quarterly presentations, RBI, NPCI, IRDAI, Screener.", False)],
         space_after=0).runs[0].font.color.rgb = MUTED

    out = ROOT / "decks" / "HDFC_CEO_Memo.docx"
    doc.save(out); print("wrote", out)


if __name__ == "__main__":
    main()
