"""Generate models/01_Bank_RoA_Benchmark.xlsx with live formulas.

Hard-coded numbers live only in 1_Inputs_Raw (each with a source comment) and 9_Shapley (Python output,
labelled as such). Everything else is a formula, so the workbook recalculates if an input changes.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name, xl_rowcol_to_cell

ROOT = Path(__file__).resolve().parents[1]
TIDY = ROOT / "data" / "tidy"
OUT = ROOT / "models" / "01_Bank_RoA_Benchmark.xlsx"

INPUT_ROWS = [  # key, label, unit
    ("annualise", "Annualisation factor", "x"),
    ("nii", "Net interest income", "INR cr"),
    ("other_income", "Other income (fees, treasury, misc.)", "INR cr"),
    ("opex", "Operating expenses", "INR cr"),
    ("provisions", "Provisions & contingencies (ex-tax)", "INR cr"),
    ("pbt", "Profit before tax", "INR cr"),
    ("tax", "Tax (PBT - PAT)", "INR cr"),
    ("pat", "Profit after tax", "INR cr"),
    ("assets_open", "Total assets - opening", "INR cr"),
    ("assets_close", "Total assets - closing", "INR cr"),
    ("equity_open", "Net worth - opening", "INR cr"),
    ("equity_close", "Net worth - closing", "INR cr"),
    ("nim_reported", "NIM (as reported)", "%"),
    ("roa_reported", "RoA (as reported)", "%"),
    ("ci_reported", "Cost-to-income (as reported)", "%"),
    ("gnpa", "Gross NPA ratio", "%"),
    ("nnpa", "Net NPA ratio", "%"),
]
SOURCES = {
    "nii": "Screener standalone: Revenue - Interest; tied to bank deck NII",
    "other_income": "Screener standalone 'Other Income'; tied to bank deck",
    "opex": "Derived: Screener (Expenses + Depreciation) - provisions; equals deck opex where cited",
    "provisions": "Bank deck / NSE XBRL, see data/inputs/bank_reported.csv for page",
    "pbt": "Screener standalone 'Profit before tax'",
    "tax": "PBT - PAT",
    "pat": "Screener standalone 'Net Profit'; tied to press release",
    "assets_open": "Screener standalone balance sheet",
    "assets_close": "Screener standalone balance sheet",
    "equity_open": "Screener: Equity Capital + Reserves",
    "equity_close": "Screener: Equity Capital + Reserves",
}


def main() -> None:
    w = pd.read_csv(TIDY / "bank_model_inputs.csv")
    rep = pd.read_csv(ROOT / "data" / "inputs" / "bank_reported.csv")
    shap = pd.read_csv(TIDY / "bank_shapley_FY26.csv")
    facts = pd.read_csv(TIDY / "bank_facts.csv")
    # column order: FY26 for all, then Q2FY27 (SBI placeholder kept blank until results land)
    order = [("SBIN", "FY26"), ("HDFCBANK", "FY26"), ("ICICIBANK", "FY26"), ("AXISBANK", "FY26"), ("KOTAKBANK", "FY26"),
             ("SBIN", "Q2FY27"), ("HDFCBANK", "Q2FY27"), ("ICICIBANK", "Q2FY27"), ("AXISBANK", "Q2FY27"), ("KOTAKBANK", "Q2FY27")]
    names = dict(zip(w.bank, w.name))
    names.setdefault("SBIN", "SBI")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(OUT, {"default_format_properties": {"font_name": "Garamond"}})
    F = {
        "title": wb.add_format({"bold": True, "font_size": 16, "font_color": "#1F2937"}),
        "sub": wb.add_format({"font_color": "#6B7280"}),
        "hdr": wb.add_format({"bold": True, "bg_color": "#1F2937", "font_color": "white", "border": 1, "align": "center", "text_wrap": True}),
        "lbl": wb.add_format({"border": 1}),
        "inp": wb.add_format({"num_format": "#,##0", "font_color": "#1D4ED8", "border": 1, "bg_color": "#EFF6FF"}),
        "inp_pct": wb.add_format({"num_format": "0.00", "font_color": "#1D4ED8", "border": 1, "bg_color": "#EFF6FF"}),
        "num": wb.add_format({"num_format": "#,##0", "border": 1}),
        "pct": wb.add_format({"num_format": "0.00", "border": 1}),
        "bp": wb.add_format({"num_format": "+0;-0;0", "border": 1}),
        "x": wb.add_format({"num_format": "0.0x", "border": 1}),
        "bold_pct": wb.add_format({"num_format": "0.00", "border": 1, "bold": True, "bg_color": "#F3F4F6"}),
        "wrap": wb.add_format({"text_wrap": True, "valign": "top"}),
        "ok": wb.add_format({"bg_color": "#DCFCE7", "font_color": "#166534", "border": 1}),
        "warn": wb.add_format({"bg_color": "#FEF3C7", "font_color": "#92400E", "border": 1}),
        "bad": wb.add_format({"bg_color": "#FEE2E2", "font_color": "#991B1B", "border": 1}),
        "sel": wb.add_format({"bold": True, "bg_color": "#FEF9C3", "border": 2}),
    }
    ncol = len(order)
    first_col = 2  # column C

    # ---------------- 0_Cover
    cv = wb.add_worksheet("0_Cover")
    cv.set_column("A:A", 3); cv.set_column("B:B", 110)
    cv.write("B2", "Why Indian bank RoA diverges: five-bank benchmark (standalone, FY26 and Q2 FY27)", F["title"])
    cv.write("B3", "Prepared by Anklesh | data as of 2 Nov 2026 | SBI Q2 FY27 column left blank until results on 3 Nov 2026", F["sub"])
    best = shap[(shap.metric == "RoA") & (shap.benchmark == "ICICIBANK")].set_index("bank")
    lines = [
        "ANSWER",
        "1. ICICI Bank earns the highest FY26 RoA in the peer set. The four gaps to it have different causes, so there is no single fix.",
        f"2. SBI (gap {best.loc['SBIN','gap']:.2f} pp): almost entirely margin. NII explains {best.loc['SBIN','nii']:.2f} pp; SBI's opex per rupee of assets is LOWER than ICICI's ({best.loc['SBIN','opex']:+.2f} pp).",
        f"3. Axis (gap {best.loc['AXISBANK','gap']:.2f} pp): margin {best.loc['AXISBANK','nii']:.2f} pp plus credit cost {best.loc['AXISBANK','prov']:.2f} pp, which includes a one-off Rs 2,001 cr standard-asset provision in Q4.",
        f"4. Kotak (gap {best.loc['KOTAKBANK','gap']:.2f} pp): a cost problem. It has the best NII margin but opex absorbs {best.loc['KOTAKBANK','opex']:.2f} pp.",
        f"5. HDFC Bank (gap {best.loc['HDFCBANK','gap']:.2f} pp): post-merger margin dilution ({best.loc['HDFCBANK','nii']:.2f} pp) and FY26 provision build ({best.loc['HDFCBANK','prov']:.2f} pp).",
        "",
        "HOW TO READ THIS WORKBOOK",
        "1_Inputs_Raw   only hard-coded inputs (blue), each with a source comment. Change an input and every tab recalculates.",
        "2_Definitions  formulas and definitional caveats (NIM bases differ across banks).",
        "3_Calc_Ratios  DuPont ratios as % of average assets (Q2 FY27 annualised x4).",
        "4_RoA_Tree     NII + other income - opex - provisions - tax = RoA, per bank-period.",
        "5_PBT_Bridge   pick a bank and a benchmark (yellow cells) for a per-Rs-100-of-assets bridge.",
        "6_History      FY17-FY26 trend, from Screener standalone history.",
        "7_Sensitivity  RoA and RoE response to NIM and credit-cost shocks for the selected bank.",
        "8_Checks       reconciliations; green = pass, amber = explained difference, red = fail.",
        "9_Shapley      order-independent gap attribution (Python output, pipeline/shapley.py).",
        "",
        "CAVEATS: computed RoA uses simple (opening+closing)/2 assets. Banks report on daily averages, so computed RoA runs 0-16 bp below reported.",
        "Reported NIM bases differ (HDFC on total assets, others on interest-earning assets). Screener is a secondary source, tied out to filings in 8_Checks.",
    ]
    for i, t in enumerate(lines):
        cv.write(4 + i, 1, t, F["wrap"] if t not in ("ANSWER", "HOW TO READ THIS WORKBOOK") else F["hdr"])

    # ---------------- 1_Inputs_Raw
    ws = wb.add_worksheet("1_Inputs_Raw")
    ws.set_column("A:A", 38); ws.set_column("B:B", 9); ws.set_column(first_col, first_col + ncol - 1, 13)
    ws.write("A1", "Inputs (blue = hard-coded; hover for source)", F["title"])
    ws.write(2, 0, "Metric", F["hdr"]); ws.write(2, 1, "Unit", F["hdr"])
    ws.write(3, 0, "Bank", F["hdr"]); ws.write(3, 1, "", F["hdr"])
    labels = []
    for j, (b, p) in enumerate(order):
        lab = f"{b}_{p}"
        labels.append(lab)
        ws.write(2, first_col + j, lab, F["hdr"])
        ws.write(3, first_col + j, f"{names.get(b, b)} {p}", F["hdr"])
    row_of = {}
    for i, (k, lab, unit) in enumerate(INPUT_ROWS):
        r = 4 + i
        row_of[k] = r
        ws.write(r, 0, lab, F["lbl"]); ws.write(r, 1, unit, F["lbl"])
        for j, (b, p) in enumerate(order):
            m = w[(w.bank == b) & (w.period == p)]
            v = None if m.empty else m.iloc[0][k]
            fmt = F["inp_pct"] if unit == "%" else F["inp"]
            if v is None or pd.isna(v):
                ws.write_blank(r, first_col + j, None, fmt)
                continue
            ws.write_number(r, first_col + j, float(v), fmt)
            src = SOURCES.get(k)
            if k in ("nim_reported", "roa_reported", "ci_reported", "gnpa", "nnpa"):
                hit = rep[(rep.bank == b) & (rep.period == p) & (rep.metric == {"ci_reported": "cost_income_reported"}.get(k, k))]
                src = (f"{hit.iloc[0].source_file} p{int(hit.iloc[0].page)}" + (f" | {hit.iloc[0].note}" if isinstance(hit.iloc[0].note, str) else "")) if len(hit) and pd.notna(hit.iloc[0].page) else "Screener quarterly table"
            if k == "provisions":
                hit = rep[(rep.bank == b) & (rep.period == p) & (rep.metric.isin(["provisions_ex_tax", "ppop"]))]
                if len(hit):
                    h = hit.iloc[0]
                    src = f"{h.source_file} p{h.page if pd.notna(h.page) else '-'} | {h.note if isinstance(h.note, str) else ''}"
            if src:
                ws.write_comment(r, first_col + j, src, {"x_scale": 2.5, "y_scale": 1.2})
    ws.freeze_panes(4, 2)
    wb.define_name("BankLabels", f"='1_Inputs_Raw'!${xl_col_to_name(first_col)}$3:${xl_col_to_name(first_col+ncol-1)}$3")

    def inp(k, j):
        return f"'1_Inputs_Raw'!{xl_rowcol_to_cell(row_of[k], first_col + j)}"

    # ---------------- 2_Definitions
    df = wb.add_worksheet("2_Definitions")
    df.set_column("A:A", 30); df.set_column("B:B", 100)
    defs = [
        ("Average assets", "(Opening + closing total assets) / 2. Q2 FY27 uses Mar-26 and Sep-26 (half-year proxy)."),
        ("Annualisation", "Quarterly flows x 4. Seasonality (Q4 fee and treasury spikes) is not adjusted."),
        ("NII % assets", "Net interest income / average total assets. Not the same as reported NIM, which divides by interest-earning assets (except HDFC, which reports on total assets)."),
        ("Other income % assets", "Fees + treasury + misc. / average assets. SBI FY26 includes a Rs 4,593 cr Yes Bank stake gain; HDFC FY26 includes transaction gains."),
        ("Opex % assets", "Operating expenses (incl. depreciation) / average assets."),
        ("Provisions % assets", "Provisions & contingencies excluding tax / average assets. SBI's 'Total Provisions' line includes tax: excluded here."),
        ("Tax % assets", "(PBT - PAT) / average assets."),
        ("RoA", "PAT / average assets. Equals the tree sum by construction; reconciles to reported RoA in 8_Checks."),
        ("RoE", "PAT / average net worth (equity capital + reserves)."),
        ("Cost-to-income", "Opex / (NII + other income). Reported C/I can exclude one-offs (HDFC 'core')."),
        ("Leverage", "Average assets / average net worth. RoE = RoA x leverage."),
        ("Shapley attribution", "Each factor's marginal contribution averaged over all orderings; sums exactly to the gap and does not depend on bridge order."),
        ("Standalone only", "No consolidated figures. Insurance/AMC subsidiaries are excluded, which matters most for HDFC, ICICI and Kotak."),
    ]
    df.write(0, 0, "Term", F["hdr"]); df.write(0, 1, "Definition and caveat", F["hdr"])
    for i, (a, b2) in enumerate(defs):
        df.write(1 + i, 0, a, F["lbl"]); df.write(1 + i, 1, b2, F["wrap"])

    # ---------------- 3_Calc_Ratios
    cr = wb.add_worksheet("3_Calc_Ratios")
    cr.set_column("A:A", 34); cr.set_column(first_col - 1, first_col + ncol - 1, 13)
    cr.write("A1", "DuPont ratios (% of average assets unless stated)", F["title"])
    cr.write(2, 0, "Metric", F["hdr"]); cr.write(2, 1, "Unit", F["hdr"])
    for j, lab in enumerate(labels):
        cr.write_formula(2, first_col + j, f"='1_Inputs_Raw'!{xl_rowcol_to_cell(2, first_col + j)}", F["hdr"])
    calc = [  # key, label, unit, formula(j) , fmt
        ("avg_assets", "Average assets", "INR cr", lambda j: f"=IF({inp('assets_close',j)}=\"\",\"\",({inp('assets_open',j)}+{inp('assets_close',j)})/2)", "num"),
        ("avg_equity", "Average net worth", "INR cr", lambda j: f"=IF({inp('equity_close',j)}=\"\",\"\",({inp('equity_open',j)}+{inp('equity_close',j)})/2)", "num"),
        ("nii_pct", "NII", "%", None, "pct"),
        ("oi_pct", "Other income", "%", None, "pct"),
        ("rev_pct", "Total revenue", "%", None, "pct"),
        ("opex_pct", "Opex", "%", None, "pct"),
        ("ppop_pct", "Pre-provision operating profit", "%", None, "pct"),
        ("prov_pct", "Provisions", "%", None, "pct"),
        ("pbt_pct", "PBT", "%", None, "pct"),
        ("tax_pct", "Tax", "%", None, "pct"),
        ("roa", "RoA (computed)", "%", None, "bold_pct"),
        ("roe", "RoE (computed)", "%", None, "bold_pct"),
        ("ci", "Cost-to-income", "%", None, "pct"),
        ("tax_rate", "Effective tax rate", "%", None, "pct"),
        ("leverage", "Leverage (assets / net worth)", "x", None, "x"),
    ]
    crow = {}
    for i, (k, lab, unit, _, _) in enumerate(calc):
        crow[k] = 3 + i

    def c(k, j):
        return xl_rowcol_to_cell(crow[k], first_col + j)

    def pct_of_assets(field, j):
        return f"=IF({c('avg_assets',j)}=\"\",\"\",100*{inp(field,j)}*{inp('annualise',j)}/{c('avg_assets',j)})"

    formulas = {
        "nii_pct": lambda j: pct_of_assets("nii", j),
        "oi_pct": lambda j: pct_of_assets("other_income", j),
        "rev_pct": lambda j: f"=IF({c('nii_pct',j)}=\"\",\"\",{c('nii_pct',j)}+{c('oi_pct',j)})",
        "opex_pct": lambda j: pct_of_assets("opex", j),
        "ppop_pct": lambda j: f"=IF({c('rev_pct',j)}=\"\",\"\",{c('rev_pct',j)}-{c('opex_pct',j)})",
        "prov_pct": lambda j: pct_of_assets("provisions", j),
        "pbt_pct": lambda j: f"=IF({c('ppop_pct',j)}=\"\",\"\",{c('ppop_pct',j)}-{c('prov_pct',j)})",
        "tax_pct": lambda j: pct_of_assets("tax", j),
        "roa": lambda j: f"=IF({c('pbt_pct',j)}=\"\",\"\",{c('pbt_pct',j)}-{c('tax_pct',j)})",
        "roe": lambda j: f"=IF({c('avg_equity',j)}=\"\",\"\",100*{inp('pat',j)}*{inp('annualise',j)}/{c('avg_equity',j)})",
        "ci": lambda j: f"=IF({inp('nii',j)}=\"\",\"\",100*{inp('opex',j)}/({inp('nii',j)}+{inp('other_income',j)}))",
        "tax_rate": lambda j: f"=IF({inp('pbt',j)}=\"\",\"\",100*{inp('tax',j)}/{inp('pbt',j)})",
        "leverage": lambda j: f"=IF({c('avg_equity',j)}=\"\",\"\",{c('avg_assets',j)}/{c('avg_equity',j)})",
    }
    for k, lab, unit, f0, fmt in calc:
        r = crow[k]
        cr.write(r, 0, lab, F["lbl"]); cr.write(r, 1, unit, F["lbl"])
        for j in range(ncol):
            cr.write_formula(r, first_col + j, (f0 or formulas[k])(j), F[fmt])
    cr.freeze_panes(3, 2)
    for k in crow:
        wb.define_name(f"r_{k}", f"='3_Calc_Ratios'!${xl_col_to_name(first_col)}${crow[k]+1}:${xl_col_to_name(first_col+ncol-1)}${crow[k]+1}")

    # ---------------- 4_RoA_Tree (transposed view + stacked chart)
    tr = wb.add_worksheet("4_RoA_Tree")
    tr.set_column("A:A", 22); tr.set_column("B:H", 12)
    tr.write("A1", "RoA tree: NII + other income - opex - provisions - tax = RoA (% of avg assets)", F["title"])
    heads = ["Bank-period", "NII", "Other income", "-Opex", "-Provisions", "-Tax", "RoA"]
    for i, h in enumerate(heads):
        tr.write(2, i, h, F["hdr"])
    for j in range(ncol):
        r = 3 + j
        col = xl_col_to_name(first_col + j)
        tr.write_formula(r, 0, f"='3_Calc_Ratios'!{col}3", F["lbl"])
        tr.write_formula(r, 1, f"='3_Calc_Ratios'!{col}{crow['nii_pct']+1}", F["pct"])
        tr.write_formula(r, 2, f"='3_Calc_Ratios'!{col}{crow['oi_pct']+1}", F["pct"])
        for ci_, k in [(3, "opex_pct"), (4, "prov_pct"), (5, "tax_pct")]:
            tr.write_formula(r, ci_, f"=IF('3_Calc_Ratios'!{col}{crow[k]+1}=\"\",\"\",-'3_Calc_Ratios'!{col}{crow[k]+1})", F["pct"])
        tr.write_formula(r, 6, f"='3_Calc_Ratios'!{col}{crow['roa']+1}", F["bold_pct"])
    ch = wb.add_chart({"type": "column", "subtype": "stacked"})
    colors = ["#1D4ED8", "#60A5FA", "#9CA3AF", "#F59E0B", "#D1D5DB"]
    for i, (h, colr) in enumerate(zip(heads[1:6], colors)):
        ch.add_series({"name": ["4_RoA_Tree", 2, 1 + i], "categories": ["4_RoA_Tree", 3, 0, 7, 0],
                       "values": ["4_RoA_Tree", 3, 1 + i, 7, 1 + i], "fill": {"color": colr}, "gap": 60})
    line = wb.add_chart({"type": "scatter"})
    line.add_series({"name": "RoA", "categories": ["4_RoA_Tree", 3, 0, 7, 0], "values": ["4_RoA_Tree", 3, 6, 7, 6],
                     "marker": {"type": "diamond", "size": 9, "fill": {"color": "#111827"}}, "data_labels": {"value": True, "num_format": "0.00"}})
    ch.combine(line)
    ch.set_title({"name": "FY26: margin builds RoA, opex and provisions consume it (% of avg assets)"})
    ch.set_legend({"position": "bottom"}); ch.set_size({"width": 820, "height": 420})
    tr.insert_chart("I3", ch)

    # ---------------- 5_PBT_Bridge
    br = wb.add_worksheet("5_PBT_Bridge")
    br.set_column("A:A", 30); br.set_column("B:E", 14)
    br.write("A1", "Bridge: subject bank vs benchmark (per Rs 100 of average assets)", F["title"])
    br.write("A3", "Subject bank-period", F["lbl"]); br.write("B3", "SBIN_FY26", F["sel"])
    br.write("A4", "Benchmark bank-period", F["lbl"]); br.write("B4", "ICICIBANK_FY26", F["sel"])
    for cell in ("B3", "B4"):
        br.data_validation(cell, {"validate": "list", "source": "=BankLabels"})
    br.write_row(5, 0, ["Line (per Rs 100 assets)", "Subject", "Benchmark", "Gap (bp)", "Read"], F["hdr"])
    blines = [("NII", "nii_pct", 1), ("Other income", "oi_pct", 1), ("Opex", "opex_pct", -1),
              ("Provisions", "prov_pct", -1), ("Tax", "tax_pct", -1), ("RoA", "roa", 1)]
    for i, (lab, k, sign) in enumerate(blines):
        r = 6 + i
        br.write(r, 0, lab, F["lbl"])
        br.write_formula(r, 1, f"=INDEX(r_{k},MATCH($B$3,BankLabels,0))", F["pct"])
        br.write_formula(r, 2, f"=INDEX(r_{k},MATCH($B$4,BankLabels,0))", F["pct"])
        br.write_formula(r, 3, f"=IFERROR(100*{sign}*(B{r+1}-C{r+1}),\"\")", F["bp"])
        br.write_formula(r, 4, f"=IF(D{r+1}=\"\",\"\",IF(D{r+1}>=0,\"helps subject\",\"hurts subject\"))", F["lbl"])
    br.write(13, 0, "Sign convention: positive bp = line raises the subject's RoA relative to the benchmark. Lines sum to the RoA gap.", F["sub"])
    br.write_formula(14, 0, "=\"Check: sum of lines minus RoA gap = \"&TEXT(SUM(D7:D11)-D12,\"0.0\")&\" bp\"", F["sub"])

    # ---------------- 6_History
    hs = wb.add_worksheet("6_History")
    hist = facts[facts.metric.str.startswith("hist_")]
    hs.write("A1", "FY17-FY26 trend (% of average assets; Screener standalone history, opex and provisions combined)", F["title"])
    piv = hist.pivot_table(index=["metric", "entity"], columns="period", values="value").reset_index()
    pcols = sorted([c_ for c_ in piv.columns if str(c_).startswith("FY")], key=lambda s: int(s[2:]))
    hs.write_row(2, 0, ["Metric", "Bank"] + pcols, F["hdr"])
    hs.set_column("A:A", 30); hs.set_column("B:B", 12)
    for i, rr in enumerate(piv.itertuples(index=False)):
        d = rr._asdict()
        hs.write(3 + i, 0, d["metric"].replace("hist_", "").replace("_", " "), F["lbl"])
        hs.write(3 + i, 1, d["entity"], F["lbl"])
        for jj, pc in enumerate(pcols):
            v = getattr(rr, pc) if hasattr(rr, pc) else d.get(pc)
            v = d.get(pc)
            if pd.notna(v):
                hs.write_number(3 + i, 2 + jj, float(v), F["pct"])
    roa_rows = [i for i, rr in enumerate(piv.itertuples(index=False)) if rr[0] == "hist_roa"]
    hch = wb.add_chart({"type": "line"})
    for i in roa_rows:
        hch.add_series({"name": ["6_History", 3 + i, 1], "categories": ["6_History", 2, 2, 2, 1 + len(pcols)],
                        "values": ["6_History", 3 + i, 2, 3 + i, 1 + len(pcols)], "marker": {"type": "circle"}})
    hch.set_title({"name": "RoA FY17-FY26: SBI's recovery stalls below private peers"})
    hch.set_size({"width": 820, "height": 380}); hch.set_legend({"position": "bottom"})
    hs.insert_chart(4 + len(piv), 0, hch)

    # ---------------- 7_Sensitivity
    sn = wb.add_worksheet("7_Sensitivity")
    sn.set_column("A:A", 30); sn.set_column("B:H", 11)
    sn.write("A1", "Sensitivity: RoA (%) for the subject bank selected in 5_PBT_Bridge", F["title"])
    sn.write("A3", "Subject", F["lbl"]); sn.write_formula("B3", "='5_PBT_Bridge'!B3", F["sel"])
    sn.write("A4", "Base RoA", F["lbl"]); sn.write_formula("B4", "=INDEX(r_roa,MATCH($B$3,BankLabels,0))", F["pct"])
    sn.write("A5", "Tax rate (%)", F["lbl"]); sn.write_formula("B5", "=INDEX(r_tax_rate,MATCH($B$3,BankLabels,0))", F["pct"])
    sn.write("A6", "Leverage (x)", F["lbl"]); sn.write_formula("B6", "=INDEX(r_leverage,MATCH($B$3,BankLabels,0))", F["x"])
    sn.write("A8", "RoA: rows = NII shock (bp of assets), columns = credit-cost shock (bp of assets)", F["sub"])
    nim = [-20, -10, -5, 0, 5, 10, 20]; cc = [-25, -10, 0, 10, 25]
    sn.write(8, 0, "NII shock \\ provisions shock", F["hdr"])
    for jj, d in enumerate(cc):
        sn.write_number(8, 1 + jj, d, F["hdr"])
    for ii, d in enumerate(nim):
        sn.write_number(9 + ii, 0, d, F["hdr"])
        for jj in range(len(cc)):
            colL = xl_col_to_name(1 + jj)
            sn.write_formula(9 + ii, 1 + jj, f"=$B$4+($A{10+ii}-{colL}$9)/100*(1-$B$5/100)", F["pct"])
    sn.write(17, 0, "RoE (%) for the same grid", F["sub"])
    sn.write(18, 0, "NII shock \\ provisions shock", F["hdr"])
    for jj, d in enumerate(cc):
        sn.write_number(18, 1 + jj, d, F["hdr"])
    for ii, d in enumerate(nim):
        sn.write_number(19 + ii, 0, d, F["hdr"])
        for jj in range(len(cc)):
            sn.write_formula(19 + ii, 1 + jj, f"={xl_rowcol_to_cell(9+ii,1+jj)}*$B$6", F["pct"])
    sn.conditional_format(9, 1, 15, 5, {"type": "3_color_scale", "min_color": "#FCA5A5", "mid_color": "#FFFFFF", "max_color": "#86EFAC"})
    sn.conditional_format(19, 1, 25, 5, {"type": "3_color_scale", "min_color": "#FCA5A5", "mid_color": "#FFFFFF", "max_color": "#86EFAC"})
    sn.write(27, 0, "Pass-through: a 10 bp NIM change moves RoA by roughly 10 bp x (assets / interest-earning assets) x (1 - tax). This grid shocks NII as a share of total assets.", F["sub"])

    # ---------------- 8_Checks
    ck = wb.add_worksheet("8_Checks")
    ck.set_column("A:A", 52); ck.set_column(first_col - 1, first_col + ncol - 1, 13)
    ck.write("A1", "Reconciliation checks (green pass / amber explained / red fail)", F["title"])
    ck.write(2, 0, "Check", F["hdr"]); ck.write(2, 1, "Tolerance", F["hdr"])
    for j, lab in enumerate(labels):
        ck.write(2, first_col + j, lab, F["hdr"])
    def cq(k, j):
        return f"'3_Calc_Ratios'!{c(k, j)}"

    checks = [
        ("PBT tie: NII + OI - opex - provisions - PBT (INR cr)", "±2",
         lambda j: f"=IF({inp('pbt',j)}=\"\",\"n/a\",{inp('nii',j)}+{inp('other_income',j)}-{inp('opex',j)}-{inp('provisions',j)}-{inp('pbt',j)})", 2, None),
        ("Tree sum vs PAT/avg assets (bp)", "±0.5",
         lambda j: f"=IF({cq('roa',j)}=\"\",\"n/a\",100*({cq('roa',j)}-100*{inp('pat',j)}*{inp('annualise',j)}/{cq('avg_assets',j)}))", 0.5, None),
        ("Computed RoA - reported RoA (bp)", "±10 (amber ±20)",
         lambda j: f"=IF(OR({inp('roa_reported',j)}=\"\",{cq('roa',j)}=\"\"),\"n/a\",100*({cq('roa',j)}-{inp('roa_reported',j)}))", 10, 20),
        ("Computed C/I - reported C/I (pp)", "±1.5 (amber ±7)",
         lambda j: f"=IF(OR({inp('ci_reported',j)}=\"\",{cq('ci',j)}=\"\"),\"n/a\",{cq('ci',j)}-{inp('ci_reported',j)})", 1.5, 7),
    ]
    for i, (lab, tol, fn, lim, amber) in enumerate(checks):
        r = 3 + i
        ck.write(r, 0, lab, F["lbl"]); ck.write(r, 1, tol, F["lbl"])
        for j in range(ncol):
            ck.write_formula(r, first_col + j, fn(j), F["pct"])
        rng = (r, first_col, r, first_col + ncol - 1)
        ck.conditional_format(*rng, {"type": "formula", "criteria": f"=AND(ISNUMBER({xl_rowcol_to_cell(r, first_col)}),ABS({xl_rowcol_to_cell(r, first_col)})<={lim})", "format": F["ok"]})
        if amber:
            ck.conditional_format(*rng, {"type": "formula", "criteria": f"=AND(ISNUMBER({xl_rowcol_to_cell(r, first_col)}),ABS({xl_rowcol_to_cell(r, first_col)})<={amber})", "format": F["warn"]})
        ck.conditional_format(*rng, {"type": "formula", "criteria": f"=ISNUMBER({xl_rowcol_to_cell(r, first_col)})", "format": F["bad"]})
    r0 = 3 + len(checks) + 1
    ck.write(r0, 0, "Data traps (single-cell tests)", F["hdr"])
    gn = labels.index("HDFCBANK_FY26")
    ck.write(r0 + 1, 0, "HDFC FY26 GNPA = 1.15% (secondary sites show NNPA 0.38% as GNPA)", F["lbl"])
    ck.write_formula(r0 + 1, 1, f"=IF({inp('gnpa',gn)}=1.15,\"PASS\",\"FAIL\")", F["lbl"])
    sb = labels.index("SBIN_FY26")
    ck.write(r0 + 2, 0, "SBI FY26 provisions exclude tax (must be < 'Total Provisions' 42,983)", F["lbl"])
    ck.write_formula(r0 + 2, 1, f"=IF({inp('provisions',sb)}<42983,\"PASS\",\"FAIL\")", F["lbl"])
    ck.write(r0 + 4, 0, "Why amber is acceptable: banks compute RoA on daily-average assets and C/I on 'core' income (HDFC excludes transaction gains; Kotak/Axis bases differ). Differences are definitional, not errors.", F["wrap"])
    ck.set_row(r0 + 4, 45)

    # ---------------- 9_Shapley
    sh = wb.add_worksheet("9_Shapley")
    sh.set_column("A:C", 14); sh.set_column("D:J", 11)
    sh.write("A1", "Shapley attribution of FY26 gap to benchmark (pp of RoA / RoE). Python output: pipeline/shapley.py", F["title"])
    cols = ["metric", "bank", "benchmark", "gap", "nii", "oi", "opex", "prov", "tax_rate", "leverage"]
    sh.write_row(2, 0, cols, F["hdr"])
    for i, rr in enumerate(shap[cols].itertuples(index=False)):
        for jj, v in enumerate(rr):
            if isinstance(v, str):
                sh.write(3 + i, jj, v, F["lbl"])
            elif pd.notna(v):
                sh.write_number(3 + i, jj, float(v), F["pct"])
        sh.write_formula(3 + i, 10, f"=ROUND(SUM(E{4+i}:J{4+i})-D{4+i},6)", F["pct"])
    sh.write(2, 10, "sum-gap", F["hdr"])
    sh.write(4 + len(shap), 0, "Reading: positive = the factor explains part of why the bank trails the benchmark. Negative = the factor works in the bank's favour.", F["sub"])

    # ---------------- 10_Chart_Data (flat, Tableau-ready)
    cd = wb.add_worksheet("10_Chart_Data")
    cd.write_row(0, 0, ["row_id", "entity", "period", "metric", "value", "unit", "source", "page", "status"], F["hdr"])
    for i, rr in enumerate(facts.itertuples(index=False)):
        cd.write_row(1 + i, 0, [("" if pd.isna(v) else v) for v in rr])
    wb.close()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
