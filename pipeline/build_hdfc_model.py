"""Build models/HDFC_RoA_Path_FY29.xlsx: driver-based bank operating model, levers and valuation.

Outside-in case study on public data only. Every hard-coded number sits on an input row (blue, grey fill)
with its source in column D; everything else is a live formula. Run: python -I pipeline/build_hdfc_model.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xlmodel import BLACK, BLUE, COLS, GREEN, GREY, HIST, PROJ, RED, YEARS, Book, prev

ROOT = Path(__file__).resolve().parents[1]
I, T, S = ROOT / "data/inputs", ROOT / "data/tidy", ROOT / "data/raw/screener"
OUT = ROOT / "models/HDFC_RoA_Path_FY29.xlsx"
FYMAP = {"FY20A": "FY20", "FY21A": "FY21", "FY22A": "FY22", "FY23A": "FY23", "FY24A": "FY24", "FY25A": "FY25", "FY26A": "FY26"}
SCMAP = {"FY20A": "Mar 2020", "FY21A": "Mar 2021", "FY22A": "Mar 2022", "FY23A": "Mar 2023", "FY24A": "Mar 2024", "FY25A": "Mar 2025", "FY26A": "Mar 2026"}


# ------------------------------------------------------------------ data
def load():
    h = pd.read_csv(I / "hdfc_10yr_highlights.csv").set_index("metric")
    sch = pd.read_csv(I / "hdfc_ir26_schedules.csv").set_index("line")
    scr = pd.read_csv(S / "HDFCBANK_tables.csv")
    bs = scr[scr.section == "balance-sheet"].pivot(index="line_item", columns="period", values="value")
    grp = pd.read_csv(I / "hdfc_group_valuation_inputs.csv").set_index("item")
    mat = pd.read_csv(I / "hdfc_borrowing_maturity_mar26.csv")
    p2m = pd.read_csv(I / "npci_p2m_monthly.csv")
    payee = pd.read_csv(I / "npci_payee_banks_sep26.csv")
    promo = pd.read_csv(T / "ins_promoter_bank_hit.csv")
    expo = pd.read_csv(T / "ins_insurer_exposure.csv")
    return h, sch, bs, grp, mat, p2m, payee, promo, expo


def hist_series(h, metric):
    return [float(h.loc[metric, FYMAP[y]]) if pd.notna(h.loc[metric, FYMAP[y]]) else None for y in YEARS[:7]]


def sched(sch, line):
    v = [None] * 7
    v[5], v[6] = float(sch.loc[line, "fy25_cr"]), float(sch.loc[line, "fy26_cr"])
    return v


def peers():
    rows = []
    names = {"HDFCBANK": "HDFC Bank", "ICICIBANK": "ICICI Bank", "AXISBANK": "Axis Bank", "KOTAKBANK": "Kotak Mahindra Bank",
             "INDUSINDBK": "IndusInd Bank", "YESBANK": "Yes Bank", "IDFCFIRSTB": "IDFC First Bank", "FEDERALBNK": "Federal Bank",
             "SBIN": "State Bank of India", "BANKBARODA": "Bank of Baroda", "PNB": "Punjab National Bank", "CANBK": "Canara Bank"}
    for sym, nm in names.items():
        t = pd.read_csv(S / f"{sym}_tables.csv"); v = pd.read_csv(S / f"{sym}_valuation.csv").set_index("metric")["value"]
        g = lambda sec, item, per: float(t[(t.section == sec) & (t.line_item == item) & (t.period == per)].value.iloc[0])  # noqa: E731
        rows.append(dict(sym=sym, name=nm, pat=g("profit-loss", "Net Profit", "Mar 2026"),
                         ta0=g("balance-sheet", "Total Assets", "Mar 2025"), ta1=g("balance-sheet", "Total Assets", "Mar 2026"),
                         eq0=g("balance-sheet", "Equity Capital", "Mar 2025") + g("balance-sheet", "Reserves", "Mar 2025"),
                         eq1=g("balance-sheet", "Equity Capital", "Mar 2026") + g("balance-sheet", "Reserves", "Mar 2026"),
                         mcap=float(v["Market Cap"]), price=float(v["Current Price"]), bvps=float(v["Book Value"]),
                         sector="Private" if sym not in ("SBIN", "BANKBARODA", "PNB", "CANBK") else "PSU"))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ build
def build():
    h, sch, bs, grp, mat, p2m, payee, promo, expo = load()
    B = Book(str(OUT))
    wb = B.wb

    cover = B.sheet("Cover", "HDFC Bank: the path back to 2% RoA", "Driver-based standalone operating model, value levers and valuation. Outside-in, public data only.", timeline=False, widths=(2, 34, 18, 90))
    dash = B.sheet("Dashboard", "Dashboard", "Select the scenario in E5; every tab recalculates.", timeline=False, widths=(2, 40, 10, 30))
    inp = B.sheet("Inputs", "Inputs and scenarios", "Blue = hard-coded input. Live rows pick Base / Upside / Downside via the Dashboard selector.")
    hs = B.sheet("Hist", "Historical spreading (standalone, RBI schedule basis)", "Source: HDFC Bank Integrated Annual Report FY2025-26 (IR26) and Screener.in standalone balance sheet.")
    md = B.sheet("Model", "Projections: balance sheet, P&L and ratios", "Historical columns link to Hist; projections are driver-based. No circular references.")
    mg = B.sheet("Margin", "Margin analytics", "Volume / rate decomposition of NII and the NIM bridge to FY29E.")
    alm = B.sheet("ALM", "ALM: repricing gap and earnings at risk", "Contractual maturity buckets, IR26 p384, as at 31 March 2026.", timeline=False, widths=(2, 34, 12, 30))
    fee = B.sheet("Fees", "Fee pools: IRDAI caps, HDFC Life and UPI MDR", "Bank fee at risk from proposed commission caps; value effect at HDFC Life; new UPI MDR pool.")
    opc = B.sheet("Opex_Credit", "Cost-to-serve and credit normalisation", "Productivity and through-the-cycle credit cost.")
    cap = B.sheet("Capital", "Capital and growth capacity", "Tier 1 proxy, risk-weight density and internal capital generation.")
    lev = B.sheet("Levers", "Value levers: FY29E impact on RoA, PAT and equity value", "Each lever is a driver change on top of the selected scenario.", timeline=False, widths=(2, 44, 12, 46))
    val = B.sheet("Valuation", "Valuation: justified P/B, residual income and sum of the parts", "Cost of equity by CAPM; terminal assumptions are inputs.", timeline=False, widths=(2, 44, 12, 46))
    sen = B.sheet("Sensitivities", "Sensitivities", "Explicit formula grids (no Data Tables), so they recalculate in any spreadsheet.", timeline=False, widths=(2, 30, 12, 12))
    peer = B.sheet("Peers", "Peer set: twelve listed banks, FY26 standalone", "P/B against RoE across the peer set gives the market's price for an extra point of return.", timeline=False, widths=(2, 26, 10, 12))
    chk = B.sheet("Checks", "Checks", "Any FAIL turns the master flag on the Cover red.", timeline=False, widths=(2, 70, 14, 12))
    src = B.sheet("Sources", "Sources", "Every input row cites one of these.", timeline=False, widths=(2, 12, 70, 60))

    # ================================================================ Inputs
    inp.section("Scenario control")
    inp.ws.write(inp.r, 1, "Scenario list", B.f())
    for j, nm in enumerate(["Base", "Upside", "Downside"]):
        inp.ws.write(inp.r, 4 + j, nm, B.f(color=BLUE, fill=True))
    inp.rows["sc_list"] = inp.r; inp.r += 1
    inp.scalar("scn", "Active scenario number", "=MATCH(Scenario,$E${0}:$G${0},0)".format(inp.rows["sc_list"] + 1), "1-3", "Driven by Dashboard!E5", num="int", kind="calc")
    wb.define_name("ScenarioNum", f"=Inputs!$E${inp.rows['scn'] + 1}")

    def driver(key, label, unit, note, base, up, down, num="pct1", hist=None):
        inp.line(f"{key}_b", f"{label}: Base", unit, note, hist=None, proj=base, num=num)
        inp.line(f"{key}_u", f"{label}: Upside", unit, "", proj=up, num=num)
        inp.line(f"{key}_d", f"{label}: Downside", unit, "", proj=down, num=num)
        inp.line(key, f"{label}: live", unit, "Selected by scenario", hist=hist,
                 proj=lambda c: f"=CHOOSE(ScenarioNum,{inp.a(key + '_b', c)},{inp.a(key + '_u', c)},{inp.a(key + '_d', c)})",
                 num=num, bold=True, hist_kind="input")

    inp.section("Rates")
    driver("repo", "Policy repo rate, fiscal-year average", "%", "S3 RBI Bank Rate less 25 bp; S4 SPF round 102 mean (Base) / max (Upside); Downside: no further hikes, cuts in FY28-29",
           [0.0542, 0.0578, 0.0575], [0.0556, 0.0625, 0.0625], [0.05375, 0.0525, 0.0500], num="pct2",
           hist=[None, None, None, None, None, 0.06458, 0.0550])
    driver("b_loan", "Yield beta: loans", "x", "Assumption: share of loans on external benchmarks (not disclosed) 45-65%", [0.55] * 3, [0.60] * 3, [0.60] * 3, num="num")
    driver("b_inv", "Yield beta: investments and liquidity", "x", "Assumption", [0.40] * 3, [0.40] * 3, [0.40] * 3, num="num")
    driver("b_dep", "Cost beta: deposits", "x", "ALM tab: FY26 realised beta about 0.17 (term-deposit lag); rises as deposits reprice", [0.35] * 3, [0.30] * 3, [0.25] * 3, num="num")
    driver("b_bor", "Cost beta: borrowings", "x", "Assumption: legacy bonds largely fixed-rate", [0.30] * 3, [0.30] * 3, [0.30] * 3, num="num")
    inp.section("Balance sheet")
    driver("g_loan", "Advances growth", "%", "S1 Q2 FY27 deck: average advances +14.1% YoY", [0.13, 0.14, 0.14], [0.15, 0.16, 0.16], [0.11, 0.11, 0.12])
    driver("g_dep", "Deposit growth", "%", "S1 Q2 FY27 deck: deposits +18.8% YoY (Sep-26 vs Sep-25)", [0.15, 0.14, 0.14], [0.17, 0.16, 0.16], [0.12, 0.12, 0.12])
    driver("casa", "CASA ratio, year end", "%", "S1 Q2 FY27 deck: 32% (Sep-26) vs 38% pre-merger", [0.325, 0.33, 0.335], [0.33, 0.345, 0.36], [0.315, 0.315, 0.32])
    driver("runoff", "Share of maturing borrowings retired", "%", "Remainder is refinanced", [0.60] * 3, [0.80] * 3, [0.30] * 3)
    inp.line("matur", "Borrowings maturing in year", "INR cr", "S2 IR26 p384: <=1y 1,93,209; 1-3y 78,306 split evenly", proj=[193209.0, 39153.0, 39153.0])
    inp.line("spread_td", "Term deposit cost premium over CASA", "%", "Assumption: TD ~6.5-7% vs SA ~2.5-3%, CA nil", proj=[0.040] * 3, num="pct2")
    inp.section("Income and cost")
    driver("g_fee", "Core fee income growth", "%", "S2 IR26 Sch 14: FY26 +9.3%", [0.11, 0.12, 0.12], [0.13, 0.14, 0.14], [0.08, 0.09, 0.09])
    driver("oi_pct", "Treasury and other non-fee income", "% avg assets", "Normalised; FY25 0.36%, FY26 0.41% ex HDB stake-sale gain", [0.0035] * 3, [0.0040] * 3, [0.0030] * 3, num="pct2")
    driver("irdai", "IRDAI cap severity on bank fees", "x", "Phase-in from FY2027-28 (year 1); 1.0 = full modelled reset", [0.0, 0.5, 1.0], [0.0, 0.25, 0.5], [0.0, 0.75, 1.5], num="num")
    driver("g_opex", "Operating expense growth", "%", "S2 IR26: FY26 +6.6%; branch adds continue", [0.10] * 3, [0.09] * 3, [0.12] * 3)
    driver("cc", "Credit cost", "% avg advances", "Opex_Credit tab: through-the-cycle 0.76% vs FY24-26 0.48%; Downside adds ECL transition", [0.0055, 0.0062, 0.0068], [0.0050, 0.0055, 0.0060], [0.0065, 0.0076, 0.0085], num="pct2")
    inp.line("tax", "Effective tax rate", "%", "Section 115BAA rate 25.17%", proj=[0.2517] * 3)
    inp.line("payout", "Dividend payout (paid on prior-year PAT)", "%", "S2 IR26: FY26 31.9%", proj=[0.30] * 3)
    inp.section("Per share and valuation inputs")
    inp.scalar("price", "Share price", float(grp.loc["hdfcbank_price", "value"]), "INR", "S5 Screener, 2 Nov 2026", num="rs")
    inp.scalar("mcap", "Market capitalisation", float(grp.loc["hdfcbank_mcap", "value"]), "INR cr", "S5 Screener, 2 Nov 2026", num="cr")
    inp.scalar("shares", "Shares outstanding", "=E{0}/E{1}".format(inp.rows["mcap"] + 1, inp.rows["price"] + 1), "crore", "Market cap / price", num="num", kind="calc")
    inp.scalar("bp", "Basis points per unit", 10000, "bp", "Unit conversion", num="int")

    # ================================================================ Hist
    hs.section("Profit and loss")
    hs.line("ii", "Interest earned", "INR cr", "S2 IR26 p234", hist=hist_series(h, "interest_income"))
    hs.line("ii_adv", "  of which interest on advances", "INR cr", "S2 IR26 Sch 13, p365", hist=sched(sch, "Interest on advances / bills"))
    hs.line("ie", "Interest expended", "INR cr", "S2 IR26 p234", hist=hist_series(h, "interest_expense"))
    hs.line("ie_dep", "  of which interest on deposits", "INR cr", "S2 IR26 Sch 15, p365", hist=sched(sch, "Interest on deposits"))
    hs.line("nii", "Net interest income", "INR cr", "", hist=lambda c: f"={hs.a('ii', c)}-{hs.a('ie', c)}", hist_kind="calc", bold=True)
    hs.line("oi", "Other income", "INR cr", "S2 IR26 p234", hist=hist_series(h, "other_income"))
    hs.line("fee", "  of which commission, exchange and brokerage", "INR cr", "S2 IR26 Sch 14", hist=sched(sch, "Commission exchange and brokerage"))
    hs.line("tsy", "  of which profit on sale of investments", "INR cr", "S2 IR26 Sch 14", hist=sched(sch, "Profit on sale of investments"))
    hs.line("opex", "Operating expenses", "INR cr", "S2 IR26 p234", hist=hist_series(h, "opex"))
    hs.line("emp", "  of which employee cost", "INR cr", "S2 IR26 Sch 16", hist=sched(sch, "Employee cost"))
    hs.line("prov", "Provisions and contingencies", "INR cr", "S2 IR26 p234", hist=hist_series(h, "provisions_total"))
    hs.line("llp", "  of which loan loss provisions", "INR cr", "S2 IR26 p234", hist=hist_series(h, "loan_loss_provisions"))
    hs.line("taxh", "Provision for taxation", "INR cr", "S2 IR26 p234", hist=hist_series(h, "tax"))
    hs.line("pat_rep", "Profit after tax, reported", "INR cr", "S2 IR26 p234", hist=hist_series(h, "pat"), bold=True)
    hs.line("pat_calc", "Profit after tax, rebuilt", "INR cr", "NII + other income - opex - provisions - tax",
            hist=lambda c: f"={hs.a('nii', c)}+{hs.a('oi', c)}-{hs.a('opex', c)}-{hs.a('prov', c)}-{hs.a('taxh', c)}", hist_kind="calc")
    hs.section("Balance sheet, 31 March")
    hs.line("loans", "Advances", "INR cr", "S2 IR26 p234", hist=hist_series(h, "loans"))
    hs.line("inv", "Investments", "INR cr", "S2 IR26 p234", hist=hist_series(h, "investments"))
    hs.line("fixed", "Fixed assets", "INR cr", "S5 Screener standalone", hist=[float(bs.loc["Fixed Assets", SCMAP[y]]) for y in YEARS[:7]])
    hs.line("ta", "Total assets", "INR cr", "S2 IR26 p234", hist=hist_series(h, "total_assets"), bold=True)
    hs.line("dep", "Deposits", "INR cr", "S2 IR26 p234", hist=hist_series(h, "deposits"))
    casa = [None] * 7
    casa[5] = float(sch.loc["Demand deposits", "fy25_cr"] + sch.loc["Savings deposits", "fy25_cr"])
    casa[6] = float(sch.loc["Demand deposits", "fy26_cr"] + sch.loc["Savings deposits", "fy26_cr"])
    hs.line("casa_cr", "  of which current and savings deposits", "INR cr", "S2 IR26 Sch 3", hist=casa)
    hs.line("bor", "Borrowings", "INR cr", "S5 Screener standalone; ties to IR26 Sch 4", hist=[float(bs.loc["Borrowing", SCMAP[y]]) for y in YEARS[:7]])
    hs.line("ol", "Other liabilities and provisions", "INR cr", "S5 Screener standalone", hist=[float(bs.loc["Other Liabilities", SCMAP[y]]) for y in YEARS[:7]])
    hs.line("eq", "Net worth", "INR cr", "S2 IR26 p234", hist=hist_series(h, "equity"))
    hs.line("bs_diff", "Assets less liabilities and net worth", "INR cr", "Should be nil",
            hist=lambda c: f"={hs.a('ta', c)}-{hs.a('dep', c)}-{hs.a('bor', c)}-{hs.a('ol', c)}-{hs.a('eq', c)}", hist_kind="calc")
    hs.section("Capital, per share and franchise")
    hs.line("t1", "Tier 1 capital ratio", "%", "S2 IR26 p234", hist=[v / 100 if v else None for v in hist_series(h, "tier1_pct")], num="pct1")
    hs.line("bvps_rep", "Book value per share (bonus-adjusted)", "INR", "S2 IR26 p234", hist=hist_series(h, "bvps"), num="rs")
    hs.line("px", "Share price, 31 March (bonus-adjusted)", "INR", "S2 IR26 p234", hist=hist_series(h, "price"), num="rs")
    br = [None] * 7; br[6] = 9689.0
    emp = [None] * 7; emp[5], emp[6] = 214308.0, 210969.0
    hs.line("branches", "Branches including digital banking units", "number", "S2 IR26 p18", hist=br, num="cr")
    hs.line("employees", "Employees", "number", "S2 IR26 p420", hist=emp, num="cr")
    hs.section("FY26 one-off items (for core RoA)")
    one = [None] * 7; one[6] = float(sch.loc["Profit on sale of investments", "fy26_cr"] - sch.loc["Profit on sale of investments", "fy25_cr"])
    hs.line("oneoff_gain", "Treasury gain above FY25 run-rate (HDB stake sale)", "INR cr", "S2 IR26 Sch 14: FY26 less FY25 sale-of-investments profit", hist=one)
    onep = [None] * 7; onep[6] = 10700.0
    hs.line("oneoff_prov", "Floating and contingent provisions created in Q1 FY26", "INR cr", "S1 Q4 FY26 deck p19: INR 90 bn floating + 17 bn contingent", hist=onep)

    # ================================================================ Model
    L = lambda key: (lambda c: f"={hs.xr(key, c)}")  # noqa: E731  link to Hist
    md.section("Balance sheet")
    md.line("loans", "Advances", "INR cr", "Hist; projection = prior x (1 + growth)", hist=L("loans"), hist_kind="link",
            proj=lambda c: f"={md.a('loans', prev(c))}*(1+{inp.xr('g_loan', c)})")
    md.line("fixed", "Fixed assets", "INR cr", "Grows with operating expenses", hist=L("fixed"), hist_kind="link",
            proj=lambda c: f"={md.a('fixed', prev(c))}*(1+{inp.xr('g_opex', c)})")
    md.line("dep", "Deposits", "INR cr", "", hist=L("dep"), hist_kind="link", proj=lambda c: f"={md.a('dep', prev(c))}*(1+{inp.xr('g_dep', c)})")
    md.line("bor", "Borrowings", "INR cr", "Prior less maturities retired", hist=L("bor"), hist_kind="link",
            proj=lambda c: f"={md.a('bor', prev(c))}-{inp.xr('matur', c)}*{inp.xr('runoff', c)}")
    md.line("ol", "Other liabilities and provisions", "INR cr", "Held at FY26 share of deposits", hist=L("ol"), hist_kind="link",
            proj=lambda c: f"={md.a('dep', c)}*{md.aa('ol', 'K')}/{md.aa('dep', 'K')}")
    md.line("div", "Dividends paid in year", "INR cr", "Payout x prior-year PAT", proj=lambda c: f"={inp.xr('payout', c)}*{md.a('pat', prev(c))}")
    md.line("eq", "Net worth, closing", "INR cr", "Prior + PAT - dividends", hist=L("eq"), hist_kind="link",
            proj=lambda c: f"={md.a('eq', prev(c))}+{md.a('pat', c)}-{md.a('div', c)}", bold=True)
    md.line("liq", "Investments, liquidity and other assets", "INR cr", "Balancing item; in-year retained profit deployed next year",
            hist=lambda c: f"={hs.xr('ta', c)}-{hs.xr('loans', c)}-{hs.xr('fixed', c)}", hist_kind="link",
            proj=lambda c: f"={md.a('dep', c)}+{md.a('bor', c)}+{md.a('ol', c)}+{md.a('eq', prev(c))}-{md.a('div', c)}-{md.a('loans', c)}-{md.a('fixed', c)}")
    md.line("cash_ret", "In-year retained profit held as cash", "INR cr", "Earns from the following year", hist=[0.0] * 7,
            proj=lambda c: f"={md.a('pat', c)}")
    md.line("ta", "Total assets", "INR cr", "", hist=L("ta"), hist_kind="link",
            proj=lambda c: f"={md.a('loans', c)}+{md.a('fixed', c)}+{md.a('liq', c)}+{md.a('cash_ret', c)}", bold=True, top=True)
    md.line("tle", "Total liabilities and net worth", "INR cr", "", hist=lambda c: f"={md.a('dep', c)}+{md.a('bor', c)}+{md.a('ol', c)}+{md.a('eq', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('dep', c)}+{md.a('bor', c)}+{md.a('ol', c)}+{md.a('eq', c)}")
    md.section("Average balances")
    avg = lambda k: (lambda c: f"=({md.a(k, prev(c))}+{md.a(k, c)})/2")  # noqa: E731
    hcols_avg = lambda k: (lambda c: None if c == "E" else f"=({md.a(k, prev(c))}+{md.a(k, c)})/2")  # noqa: E731
    md.line("a_loans", "Average advances", "INR cr", "", hist=hcols_avg("loans"), hist_kind="calc", proj=avg("loans"))
    md.line("a_liq", "Average investments, liquidity and other assets", "INR cr", "Prior closing includes retained cash",
            hist=lambda c: None if c == "E" else f"=({md.a('liq', prev(c))}+{md.a('cash_ret', prev(c))}+{md.a('liq', c)})/2", hist_kind="calc",
            proj=lambda c: f"=({md.a('liq', prev(c))}+{md.a('cash_ret', prev(c))}+{md.a('liq', c)})/2")
    md.line("a_dep", "Average deposits", "INR cr", "", hist=hcols_avg("dep"), hist_kind="calc", proj=avg("dep"))
    md.line("a_bor", "Average borrowings", "INR cr", "", hist=hcols_avg("bor"), hist_kind="calc", proj=avg("bor"))
    md.line("a_ta", "Average total assets", "INR cr", "", hist=hcols_avg("ta"), hist_kind="calc", proj=avg("ta"))
    md.line("a_eq", "Average net worth", "INR cr", "", hist=hcols_avg("eq"), hist_kind="calc", proj=avg("eq"))
    md.line("a_ta_x", "Average assets before in-year retained profit", "INR cr", "Driver base for treasury income (avoids circularity)",
            hist=hcols_avg("ta"), hist_kind="calc", proj=lambda c: f"=({md.a('ta', prev(c))}+{md.a('loans', c)}+{md.a('fixed', c)}+{md.a('liq', c)})/2")
    md.section("Yields and costs")
    ylo = lambda c: f"={hs.xr('ii_adv', c)}/{md.a('a_loans', c)}" if c in ("J", "K") else None  # noqa: E731
    md.line("y_loan", "Yield on advances", "%", "Hist FY25-26 from Sch 13; projection = prior + beta x change in repo", hist=ylo, hist_kind="calc", num="pct2",
            proj=lambda c: f"={md.a('y_loan', prev(c))}+{inp.xr('b_loan', c)}*({inp.xr('repo', c)}-{inp.xr('repo', prev(c))})")
    md.line("y_liq", "Yield on investments and liquidity", "%", "", num="pct2", hist_kind="calc",
            hist=lambda c: f"=({hs.xr('ii', c)}-{hs.xr('ii_adv', c)})/{md.a('a_liq', c)}" if c in ("J", "K") else None,
            proj=lambda c: f"={md.a('y_liq', prev(c))}+{inp.xr('b_inv', c)}*({inp.xr('repo', c)}-{inp.xr('repo', prev(c))})")
    md.line("casa", "CASA ratio, year end", "%", "", num="pct1", hist_kind="calc",
            hist=lambda c: f"={hs.xr('casa_cr', c)}/{hs.xr('dep', c)}" if c in ("J", "K") else None, proj=lambda c: f"={inp.xr('casa', c)}")
    md.line("c_dep", "Cost of deposits", "%", "Prior + beta x change in repo + CASA mix effect", num="pct2", hist_kind="calc",
            hist=lambda c: f"={hs.xr('ie_dep', c)}/{md.a('a_dep', c)}" if c in ("J", "K") else None,
            proj=lambda c: f"={md.a('c_dep', prev(c))}+{inp.xr('b_dep', c)}*({inp.xr('repo', c)}-{inp.xr('repo', prev(c))})+({md.a('casa', prev(c))}-{md.a('casa', c)})*{inp.xr('spread_td', c)}")
    md.line("c_bor", "Cost of borrowings", "%", "", num="pct2", hist_kind="calc",
            hist=lambda c: f"=({hs.xr('ie', c)}-{hs.xr('ie_dep', c)})/{md.a('a_bor', c)}" if c in ("J", "K") else None,
            proj=lambda c: f"={md.a('c_bor', prev(c))}+{inp.xr('b_bor', c)}*({inp.xr('repo', c)}-{inp.xr('repo', prev(c))})")
    md.section("Profit and loss")
    md.line("ii", "Interest earned", "INR cr", "", hist=L("ii"), hist_kind="link",
            proj=lambda c: f"={md.a('y_loan', c)}*{md.a('a_loans', c)}+{md.a('y_liq', c)}*{md.a('a_liq', c)}")
    md.line("ie", "Interest expended", "INR cr", "", hist=L("ie"), hist_kind="link",
            proj=lambda c: f"={md.a('c_dep', c)}*{md.a('a_dep', c)}+{md.a('c_bor', c)}*{md.a('a_bor', c)}")
    md.line("nii", "Net interest income", "INR cr", "", hist=lambda c: f"={md.a('ii', c)}-{md.a('ie', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('ii', c)}-{md.a('ie', c)}", bold=True, top=True)
    md.line("fee", "Core fee income", "INR cr", "Commission, exchange and brokerage", hist=L("fee"), hist_kind="link",
            proj=lambda c: f"={md.a('fee', prev(c))}*(1+{inp.xr('g_fee', c)})")
    md.line("irdai", "IRDAI commission caps: bank fee lost", "INR cr", "Fees tab", proj=lambda c: f"=-{fee.xr('bank_hit', c)}")
    md.line("mdr", "UPI MDR revenue", "INR cr", "Fees tab", proj=lambda c: f"={fee.xr('mdr_hdfc', c)}")
    md.line("oth", "Treasury and other non-fee income", "INR cr", "Hist: other income less fees; projection: % of average assets",
            hist=lambda c: f"={hs.xr('oi', c)}-{hs.xr('fee', c)}" if c in ("J", "K") else None, hist_kind="link",
            proj=lambda c: f"={inp.xr('oi_pct', c)}*{md.a('a_ta_x', c)}")
    md.line("oi", "Other income", "INR cr", "", hist=L("oi"), hist_kind="link",
            proj=lambda c: f"={md.a('fee', c)}+{md.a('irdai', c)}+{md.a('mdr', c)}+{md.a('oth', c)}")
    md.line("rev", "Net revenue", "INR cr", "", hist=lambda c: f"={md.a('nii', c)}+{md.a('oi', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('nii', c)}+{md.a('oi', c)}", bold=True)
    md.line("opex", "Operating expenses", "INR cr", "", hist=L("opex"), hist_kind="link", proj=lambda c: f"={md.a('opex', prev(c))}*(1+{inp.xr('g_opex', c)})")
    md.line("ppop", "Pre-provision operating profit", "INR cr", "", hist=lambda c: f"={md.a('rev', c)}-{md.a('opex', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('rev', c)}-{md.a('opex', c)}", bold=True)
    md.line("prov", "Provisions and contingencies", "INR cr", "Projection: credit cost x average advances", hist=L("prov"), hist_kind="link",
            proj=lambda c: f"={inp.xr('cc', c)}*{md.a('a_loans', c)}")
    md.line("pbt", "Profit before tax", "INR cr", "", hist=lambda c: f"={md.a('ppop', c)}-{md.a('prov', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('ppop', c)}-{md.a('prov', c)}")
    md.line("tax", "Tax", "INR cr", "", hist=L("taxh"), hist_kind="link", proj=lambda c: f"={inp.xr('tax', c)}*{md.a('pbt', c)}")
    md.line("pat", "Profit after tax", "INR cr", "", hist=lambda c: f"={md.a('pbt', c)}-{md.a('tax', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('pbt', c)}-{md.a('tax', c)}", bold=True, top=True)
    md.line("pat_core", "Profit after tax, core", "INR cr", "FY26 excludes one-off treasury gain and one-off provisions, after tax",
            hist=lambda c: f"={md.a('pat', c)}-({hs.xr('oneoff_gain', c)}-{hs.xr('oneoff_prov', c)})*(1-{inp.x('tax', 'L')})",
            hist_kind="calc", proj=lambda c: f"={md.a('pat', c)}")
    md.section("Returns and ratios")
    rat = lambda num_k, den_k: (lambda c: None if c == "E" else f"={md.a(num_k, c)}/{md.a(den_k, c)}")  # noqa: E731
    md.line("roa", "Return on average assets", "%", "", hist=rat("pat", "a_ta"), hist_kind="calc", proj=rat("pat", "a_ta"), num="pct2", bold=True)
    md.line("roa_core", "Return on average assets, core", "%", "", hist=rat("pat_core", "a_ta"), hist_kind="calc", proj=rat("pat_core", "a_ta"), num="pct2")
    md.line("roe", "Return on average net worth", "%", "", hist=rat("pat", "a_eq"), hist_kind="calc", proj=rat("pat", "a_eq"), num="pct1")
    md.line("nim", "Net interest margin on interest-earning assets", "%", "IEA = advances + investments, liquidity and other assets",
            hist=lambda c: None if c == "E" else f"={md.a('nii', c)}/({md.a('a_loans', c)}+{md.a('a_liq', c)})", hist_kind="calc",
            proj=lambda c: f"={md.a('nii', c)}/({md.a('a_loans', c)}+{md.a('a_liq', c)})", num="pct2")
    for k, lab, n in [("nii", "NII / average assets", "nii"), ("oi", "Other income / average assets", "oi"), ("opex", "Opex / average assets", "opex"),
                      ("prov", "Provisions / average assets", "prov"), ("tax", "Tax / average assets", "tax")]:
        md.line(f"{k}_a", lab, "%", "RoA tree", hist=rat(n, "a_ta"), hist_kind="calc", proj=rat(n, "a_ta"), num="pct2")
    md.line("ci", "Cost to income", "%", "", hist=lambda c: f"={md.a('opex', c)}/{md.a('rev', c)}", hist_kind="calc", proj=lambda c: f"={md.a('opex', c)}/{md.a('rev', c)}", num="pct1")
    md.line("ccost", "Credit cost", "% avg advances", "Loan loss provisions in history",
            hist=lambda c: None if c == "E" else f"={hs.xr('llp', c)}/{md.a('a_loans', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('prov', c)}/{md.a('a_loans', c)}", num="pct2")
    md.line("cd", "Credit-deposit ratio", "%", "", hist=lambda c: f"={md.a('loans', c)}/{md.a('dep', c)}", hist_kind="calc",
            proj=lambda c: f"={md.a('loans', c)}/{md.a('dep', c)}", num="pct1")
    md.line("eps", "Earnings per share", "INR", "Current share count", hist=lambda c: f"={md.a('pat', c)}/{inp.x('shares')}", hist_kind="calc",
            proj=lambda c: f"={md.a('pat', c)}/{inp.x('shares')}", num="rs")
    md.line("bvps", "Book value per share", "INR", "", hist=lambda c: f"={md.a('eq', c)}/{inp.x('shares')}", hist_kind="calc",
            proj=lambda c: f"={md.a('eq', c)}/{inp.x('shares')}", num="rs")

    # ================================================================ Margin
    mg.section("NII walk, volume and rate (total balance sheet)")
    mg.line("iea", "Average interest-earning assets", "INR cr", "", hist=lambda c: None if c == "E" else f"={md.xr('a_loans', c)}+{md.xr('a_liq', c)}", hist_kind="link",
            proj=lambda c: f"={md.xr('a_loans', c)}+{md.xr('a_liq', c)}", proj_kind="link")
    mg.line("nim", "Net interest margin", "%", "", hist=lambda c: None if c == "E" else f"={md.xr('nim', c)}", hist_kind="link", proj=lambda c: f"={md.xr('nim', c)}", proj_kind="link", num="pct2")
    mg.line("dnii", "Change in NII", "INR cr", "", hist=lambda c: None if c in ("E", "F") else f"={md.xr('nii', c)}-{md.xr('nii', prev(c))}", hist_kind="calc",
            proj=lambda c: f"={md.xr('nii', c)}-{md.xr('nii', prev(c))}")
    mg.line("vol", "  Volume effect", "INR cr", "Change in IEA x prior NIM", hist=lambda c: None if c in ("E", "F") else f"=({mg.a('iea', c)}-{mg.a('iea', prev(c))})*{mg.a('nim', prev(c))}", hist_kind="calc",
            proj=lambda c: f"=({mg.a('iea', c)}-{mg.a('iea', prev(c))})*{mg.a('nim', prev(c))}")
    mg.line("rate", "  Margin effect", "INR cr", "Change in NIM x current IEA", hist=lambda c: None if c in ("E", "F") else f"=({mg.a('nim', c)}-{mg.a('nim', prev(c))})*{mg.a('iea', c)}", hist_kind="calc",
            proj=lambda c: f"=({mg.a('nim', c)}-{mg.a('nim', prev(c))})*{mg.a('iea', c)}")
    mg.line("vr_chk", "  Unexplained", "INR cr", "Should be nil", hist=lambda c: None if c in ("E", "F") else f"={mg.a('dnii', c)}-{mg.a('vol', c)}-{mg.a('rate', c)}", hist_kind="calc",
            proj=lambda c: f"={mg.a('dnii', c)}-{mg.a('vol', c)}-{mg.a('rate', c)}")
    mg.section("Spread decomposition")
    for k, lab in [("y_loan", "Yield on advances"), ("y_liq", "Yield on investments and liquidity"), ("c_dep", "Cost of deposits"), ("c_bor", "Cost of borrowings")]:
        mg.line(k, lab, "%", "", hist=lambda c, k=k: f"={md.xr(k, c)}" if c in ("J", "K") else None, hist_kind="link", proj=lambda c, k=k: f"={md.xr(k, c)}", proj_kind="link", num="pct2")
    mg.line("spread", "Loan-deposit spread", "%", "", hist=lambda c: f"={mg.a('y_loan', c)}-{mg.a('c_dep', c)}" if c in ("J", "K") else None, hist_kind="calc",
            proj=lambda c: f"={mg.a('y_loan', c)}-{mg.a('c_dep', c)}", num="pct2")
    mg.line("bor_share", "Borrowings / (deposits + borrowings), average", "%", "Merger legacy funding mix",
            hist=lambda c: None if c == "E" else f"={md.xr('a_bor', c)}/({md.xr('a_dep', c)}+{md.xr('a_bor', c)})", hist_kind="calc",
            proj=lambda c: f"={md.xr('a_bor', c)}/({md.xr('a_dep', c)}+{md.xr('a_bor', c)})", num="pct1")
    mg.line("runoff_gain", "Run-off saving vs refinancing at borrowing cost", "INR cr", "Retired borrowings x (cost of borrowings - cost of deposits)",
            proj=lambda c: f"={inp.xr('matur', c)}*{inp.xr('runoff', c)}*({md.xr('c_bor', c)}-{md.xr('c_dep', c)})")

    # ================================================================ ALM
    alm.section("Repricing gap, 31 March 2026 (INR cr)")
    hdr = ["Bucket", "Mid-point (months)", "Advances", "Investments", "Deposits", "Borrowings", "Gap", "Cumulative gap"]
    for j, t in enumerate(hdr):
        alm.ws.write(alm.r, 1 + j, t, B.f(bold=True, bottom=True, align="right" if j else None))
    alm.ws.set_column(5, 9, 13)
    alm.r += 1
    mids = [0.03, 0.15, 0.35, 0.75, 1.5, 2.5, 4.5, 9.0, 24.0, 48.0, 84.0]
    inv_b = [214529.94, 30256.65, 14524.74, 42532.84, 34583.75, 35880.28, 31861.69, 66410.65, 185640.79, 19629.47, 208350.67]
    first = alm.r
    for i, rrow in enumerate(mat.itertuples()):
        r = alm.r
        alm.ws.write(r, 1, rrow.bucket, B.f())
        alm.ws.write_number(r, 2, mids[i], B.f(num="num", color=BLUE, fill=True))
        alm.ws.write_number(r, 3, rrow.advances_cr, B.f(num="cr", color=BLUE, fill=True))
        alm.ws.write_number(r, 4, inv_b[i], B.f(num="cr", color=BLUE, fill=True))
        alm.ws.write_number(r, 5, rrow.deposits_cr, B.f(num="cr", color=BLUE, fill=True))
        alm.ws.write_number(r, 6, rrow.amount_cr, B.f(num="cr", color=BLUE, fill=True))
        alm.ws.write_formula(r, 7, f"=D{r+1}+E{r+1}-F{r+1}-G{r+1}", B.f(num="cr"))
        alm.ws.write_formula(r, 8, f"=SUM($H${first+1}:H{r+1})", B.f(num="cr"))
        alm.r += 1
    last = alm.r - 1
    alm.rows["gap_first"], alm.rows["gap_last"] = first, last
    alm.ws.write(alm.r, 1, "Total", B.f(bold=True, top=True))
    for j in range(3, 8):
        col = "DEFGH"[j - 3]
        alm.ws.write_formula(alm.r, j, f"=SUM({col}{first+1}:{col}{last+1})", B.f(num="cr", bold=True, top=True))
    alm.rows["gap_tot"] = alm.r; alm.r += 2
    alm.note("Source: S2 IR26 p384 (maturity pattern, RBI ALM buckets). Contractual maturity, not repricing: floating-rate loans are adjusted below.")
    alm.section("Earnings at risk: +100 bp parallel shift, first 12 months")
    alm.scalar("shock", "Rate shock", 0.01, "%", "Parallel", num="pct2")
    alm.scalar("float_share", "Advances on external benchmarks (reprice within a month)", 0.55, "%", "Assumption: not disclosed; range 45-65%", num="pct1")
    alm.scalar("months", "Months in horizon", 12, "months", "", num="int")
    gap_1y = f"SUMPRODUCT(($C${first+1}:$C${last+1}<{alm.a('months')})*($H${first+1}:$H${last+1})*({alm.a('months')}-$C${first+1}:$C${last+1})/{alm.a('months')})"
    alm.scalar("ear_contract", "NII change on contractual gaps", f"={gap_1y}*{alm.a('shock')}", "INR cr", "Gap x shock x time remaining in year", num="cr", kind="calc")
    late_adv = f"SUMPRODUCT(($C${first+1}:$C${last+1}>={alm.a('months')})*($D${first+1}:$D${last+1}))"
    alm.scalar("ear_float", "Add: floating advances beyond 1 year that reprice now", f"={alm.a('float_share')}*{late_adv}*{alm.a('shock')}", "INR cr", "", num="cr", kind="calc")
    alm.scalar("ear", "Earnings at risk, +100 bp", f"={alm.a('ear_contract')}+{alm.a('ear_float')}", "INR cr", "Positive = asset-sensitive", num="cr", kind="calc")
    alm.scalar("ear_pct", "As % of FY26 NII", f"={alm.a('ear')}/{md.x('nii', 'K')}", "%", "", num="pct1", kind="calc")
    alm.section("Deposit beta, realised FY25 to FY26")
    alm.scalar("beta_real", "Change in cost of deposits / change in average repo", f"=({md.x('c_dep', 'K')}-{md.x('c_dep', 'J')})/({inp.x('repo', 'K')}-{inp.x('repo', 'J')})", "x",
               "Two-point estimate; term deposits reprice with a lag", num="num", kind="calc")

    # ================================================================ Fees
    fee.section("IRDAI proposed caps: bank fee at risk")
    fee.scalar("hlife_bank_reset", "HDFC Life bank-channel first-year commission above proposed caps", float(promo[promo.promoter_bank == "HDFCBANK"].bank_channel_reset_cr.iloc[0]), "INR cr",
               "data/tidy/ins_promoter_bank_hit.csv (insurance module, Base PPT mix)", num="cr")
    fee.scalar("other_ins_mult", "Uplift for other insurers distributed (HDFC ERGO, partners)", 1.30, "x", "Assumption", num="num")
    fee.line("bank_hit", "Bank fee lost to caps", "INR cr", "Reset x uplift x scenario severity",
             proj=lambda c: f"={fee.aa('hlife_bank_reset', 'E')}*{fee.aa('other_ins_mult', 'E')}*{inp.xr('irdai', c)}")
    fee.section("HDFC Life: value effect of the caps (50.2% owned)")
    hl = expo[expo.insurer.str.contains("HDFC Life")].iloc[0]
    fee.scalar("hl_reset", "HDFC Life distributor commission above caps, all channels", float(hl.reset_cr), "INR cr", "data/tidy/ins_insurer_exposure.csv", num="cr")
    fee.scalar("hl_ape", "HDFC Life APE FY26", float(grp.loc["hdfclife_ape_fy26", "value"]), "INR cr", "S6 HDFC Life Q4 FY26 deck p3", num="cr")
    fee.scalar("hl_vnb", "HDFC Life VNB FY26", float(grp.loc["hdfclife_vnb_fy26", "value"]), "INR cr", "S6 HDFC Life Q4 FY26 deck p2", num="cr")
    fee.scalar("hl_banca", "Bancassurance share of individual APE", float(grp.loc["hdfclife_banca_share_indiv_ape_h1fy27", "value"]) / 100, "%", "S6 HDFC Life Q2 FY27 deck p14", num="pct1")
    fee.scalar("hl_keep", "Share of commission saving kept as margin", 0.50, "%", "Assumption: rest passed to policyholders", num="pct1")
    fee.scalar("hl_volloss", "Bancassurance APE lost if bank distribution pulls back", 0.15, "%", "Assumption", num="pct1")
    fee.scalar("hl_dvnb", "Net change in annual VNB", f"={fee.a('hl_keep')}*{fee.a('hl_reset')}-{fee.a('hl_volloss')}*{fee.a('hl_banca')}*{fee.a('hl_vnb')}", "INR cr", "Margin gain less volume loss", num="cr", kind="calc")
    fee.scalar("hl_mcap", "HDFC Life market capitalisation", float(grp.loc["hdfclife_mcap", "value"]), "INR cr", "S5 Screener", num="cr")
    fee.scalar("hl_ev", "HDFC Life embedded value Q2 FY27", float(grp.loc["hdfclife_ev_q2fy27", "value"]), "INR cr", "S6 HDFC Life Q2 FY27 deck p3", num="cr")
    fee.scalar("hl_mult", "Market-implied VNB multiple", f"=({fee.a('hl_mcap')}-{fee.a('hl_ev')})/{fee.a('hl_vnb')}", "x", "(Market cap - EV) / VNB", num="x", kind="calc")
    fee.scalar("hl_stake", "HDFC Bank stake in HDFC Life", float(grp.loc["stake_hdfclife", "value"]), "%", "S2 IR26 p52", num="pct1")
    fee.scalar("hl_val", "Value effect to HDFC Bank shareholders", f"={fee.a('hl_dvnb')}*{fee.a('hl_mult')}*{fee.a('hl_stake')}", "INR cr", "", num="cr", kind="calc")
    fee.section("UPI merchant discount rate (from FY2026-27 Q4)")
    fee.ws.write(fee.r, 1, "Month", B.f(bold=True, bottom=True)); fee.ws.write(fee.r, 2, "P2M value", B.f(bold=True, bottom=True, align="right"))
    fee.ws.write(fee.r, 3, "Share of P2M value above INR 2,000", B.f(bold=True, bottom=True)); fee.r += 1
    m_first = fee.r
    for rr in p2m.itertuples():
        fee.ws.write(fee.r, 1, rr.month, B.f()); fee.ws.write_number(fee.r, 2, rr.p2m_value_cr, B.f(num="cr", color=BLUE, fill=True))
        if pd.notna(rr.p2m_value_share_above_2000_pct):
            fee.ws.write_number(fee.r, 3, rr.p2m_value_share_above_2000_pct / 100, B.f(num="pct1", color=BLUE, fill=True))
        fee.r += 1
    m_last = fee.r - 1
    fee.note("Source: S7 NPCI via FactIQ rbi-npci_upi (p2p and p2p_bands tables).")
    fee.scalar("p2m_t12", "P2M value, trailing 12 months", f"=SUM(C{m_last-10}:C{m_last+1})", "INR cr", "", num="cr", kind="calc")
    fee.scalar("p2m_g", "P2M value growth, Apr-Oct 2026 vs Apr-Oct 2025", f"=SUM(C{m_last-5}:C{m_last+1})/SUM(C{m_first+1}:C{m_first+7})-1", "%", "", num="pct1", kind="calc")
    fee.scalar("gt2k", "Share of P2M value above INR 2,000", f"=AVERAGE(D{m_last-10}:D{m_last+1})", "%", "Twelve-month average", num="pct1", kind="calc")
    fee.scalar("exempt", "Exempt or flat-fee share of that value", 0.30, "%", "Assumption: P2PM micro-merchants, AutoPay, INR 5 flat sectors", num="pct1")
    fee.scalar("mdr_rate", "MDR", 0.004, "%", "S8 DFS FAQ Q3", num="pct2")
    fee.scalar("cap_hc", "Haircut for INR 300 cap on tickets of INR 75,000 and above", 0.95, "x", "Assumption", num="num")
    fee.scalar("pool", "Annual MDR pool at current run-rate", f"={fee.a('p2m_t12')}*{fee.a('gt2k')}*(1-{fee.a('exempt')})*{fee.a('mdr_rate')}*{fee.a('cap_hc')}", "INR cr", "", num="cr", kind="calc")
    fee.scalar("hd_payee", "HDFC Bank payee volume, Sep-26", float(payee[payee.bank == 'HDFC Bank'].payee_volume_mn.iloc[0]), "mn", "S7 NPCI payee banks", num="cr1")
    fee.scalar("tot_payee", "Payee volume, top twelve banks, Sep-26", float(payee.payee_volume_mn.sum()), "mn", "S7 NPCI payee banks", num="cr1")
    fee.scalar("hd_share", "HDFC Bank share of payee volume", f"={fee.a('hd_payee')}/{fee.a('tot_payee')}", "%", "", num="pct1", kind="calc")
    fee.scalar("acq_share", "Acquiring bank's share of MDR", 0.30, "%", "Assumption: split with issuer, app provider, NPCI", num="pct1")
    fee.line("yr_idx", "Years after FY26", "number", "Timeline counter", proj=[1.0, 2.0, 3.0], num="int")
    fee.line("mdr_frac", "Share of year MDR is live", "%", "Assumption: start Jan-2027", proj=[0.25, 1.0, 1.0], num="pct1")
    fee.line("mdr_hdfc", "HDFC Bank MDR revenue", "INR cr", "Pool grown at P2M growth x share x acquirer share",
             proj=lambda c: f"={fee.aa('pool', 'E')}*(1+{fee.aa('p2m_g', 'E')})^({fee.a('yr_idx', c)}-1)*{fee.aa('hd_share', 'E')}*{fee.aa('acq_share', 'E')}*{fee.a('mdr_frac', c)}")

    # ================================================================ Opex and credit
    opc.section("Credit cost: current vs through the cycle")
    opc.line("cc_hist", "Credit cost (loan loss provisions / average advances)", "%", "", hist=lambda c: None if c == "E" else f"={md.xr('ccost', c)}", hist_kind="link", num="pct2")
    opc.scalar("ttc", "Through-the-cycle credit cost, FY21-FY26 average", f"=AVERAGE({md.x('ccost', 'F')}:{md.x('ccost', 'K')})", "%", "", num="pct2", kind="calc")
    opc.scalar("recent", "Recent credit cost, FY24-FY26 average", f"=AVERAGE({md.x('ccost', 'I')}:{md.x('ccost', 'K')})", "%", "", num="pct2", kind="calc")
    opc.scalar("cc_gap_bp", "Normalisation gap", f"=({opc.a('ttc')}-{opc.a('recent')})*{inp.x('bp')}", "bp", "", num="bp", kind="calc")
    opc.scalar("cc_roa_bp", "RoA at risk if credit cost normalises", f"={opc.a('cc_gap_bp')}*{md.x('a_loans', 'K')}/{md.x('a_ta', 'K')}*(1-{inp.x('tax', 'L')})", "bp", "After tax", num="bp", kind="calc")
    opc.section("Cost-to-serve")
    opc.line("opex_a", "Opex / average assets", "%", "", hist=lambda c: None if c == "E" else f"={md.xr('opex_a', c)}", hist_kind="link", proj=lambda c: f"={md.xr('opex_a', c)}", proj_kind="link", num="pct2")
    opc.line("ci", "Cost to income", "%", "", hist=lambda c: f"={md.xr('ci', c)}", hist_kind="link", proj=lambda c: f"={md.xr('ci', c)}", proj_kind="link", num="pct1")
    opc.line("jaws", "Jaws: revenue growth less cost growth", "%", "",
             hist=lambda c: None if c in ("E",) else f"=({md.xr('rev', c)}/{md.xr('rev', prev(c))})-({md.xr('opex', c)}/{md.xr('opex', prev(c))})", hist_kind="calc",
             proj=lambda c: f"=({md.xr('rev', c)}/{md.xr('rev', prev(c))})-({md.xr('opex', c)}/{md.xr('opex', prev(c))})", num="pct1")
    opc.line("emp_share", "Employee cost / opex", "%", "", hist=lambda c: f"={hs.xr('emp', c)}/{hs.xr('opex', c)}" if c in ("J", "K") else None, hist_kind="calc", num="pct1")
    opc.line("rev_br", "Net revenue per branch", "INR cr", "", hist=lambda c: f"={md.xr('rev', c)}/{hs.xr('branches', c)}" if c == "K" else None, hist_kind="calc", num="num")
    opc.line("rev_emp", "Net revenue per employee", "INR cr", "", hist=lambda c: f"={md.xr('rev', c)}/{hs.xr('employees', c)}" if c == "K" else None, hist_kind="calc", num="num")

    # ================================================================ Capital
    cap.line("t1", "Tier 1 capital ratio, reported", "%", "", hist=lambda c: f"={hs.xr('t1', c)}", hist_kind="link", num="pct1")
    cap.line("rwa", "Risk-weighted assets, implied", "INR cr", "Net worth / Tier 1 ratio (proxy)", hist=lambda c: f"={md.xr('eq', c)}/{cap.a('t1', c)}", hist_kind="calc",
             proj=lambda c: f"={md.xr('ta', c)}*{cap.aa('dens', 'K')}")
    cap.line("dens", "Risk-weight density", "%", "RWA / total assets", hist=lambda c: f"={cap.a('rwa', c)}/{md.xr('ta', c)}", hist_kind="calc",
             proj=lambda c: f"={cap.a('rwa', c)}/{md.xr('ta', c)}", num="pct1")
    cap.line("t1p", "Tier 1 ratio, projected (proxy)", "%", "", hist=lambda c: f"={md.xr('eq', c)}/{cap.a('rwa', c)}", hist_kind="calc",
             proj=lambda c: f"={md.xr('eq', c)}/{cap.a('rwa', c)}", num="pct1")
    cap.line("icg", "Internal capital generation", "%", "RoE x (1 - payout)", proj=lambda c: f"={md.xr('roe', c)}*(1-{inp.xr('payout', c)})", num="pct1")
    cap.line("sgr", "Asset growth fundable at constant Tier 1", "%", "", proj=lambda c: f"={cap.a('icg', c)}", num="pct1")

    # ================================================================ Peers
    pdf = peers()
    hd = ["Bank", "Sector", "PAT FY26", "Avg assets", "Avg net worth", "RoA", "RoE", "Market cap", "P/B", "Include in fit"]
    for j, t in enumerate(hd):
        peer.ws.write(peer.r, 1 + j, t, B.f(bold=True, bottom=True, align="right" if j > 1 else None))
    peer.ws.set_column(3, 11, 12)
    peer.r += 1; pf = peer.r
    for rr in pdf.itertuples():
        r = peer.r
        peer.ws.write(r, 1, rr.name, B.f()); peer.ws.write(r, 2, rr.sector, B.f(color=GREY))
        peer.ws.write_number(r, 3, rr.pat, B.f(num="cr", color=BLUE, fill=True))
        peer.ws.write_number(r, 4, (rr.ta0 + rr.ta1) / 2, B.f(num="cr", color=BLUE, fill=True))
        peer.ws.write_number(r, 5, (rr.eq0 + rr.eq1) / 2, B.f(num="cr", color=BLUE, fill=True))
        peer.ws.write_formula(r, 6, f"=D{r+1}/E{r+1}", B.f(num="pct2"))
        peer.ws.write_formula(r, 7, f"=D{r+1}/F{r+1}", B.f(num="pct1"))
        peer.ws.write_number(r, 8, rr.mcap, B.f(num="cr", color=BLUE, fill=True))
        peer.r += 1
    pl = peer.r - 1
    # closing net worth column for P/B (input), and fit flag
    peer.ws.write(pf - 1, 11, "Net worth FY26", B.f(bold=True, bottom=True, align="right"))
    peer.ws.write(pf - 1, 10, "Include in fit", B.f(bold=True, bottom=True, align="right"))
    for i, rr in enumerate(pdf.itertuples()):
        r = pf + i
        peer.ws.write_number(r, 11, rr.eq1, B.f(num="cr", color=BLUE, fill=True))
        peer.ws.write_formula(r, 9, f"=I{r+1}/L{r+1}", B.f(num="x"))
        flag = 0 if rr.sym in ("INDUSINDBK", "IDFCFIRSTB", "YESBANK") or rr.sector == "PSU" else 1
        peer.ws.write_number(r, 10, flag, B.f(num="int", color=BLUE, fill=True))
        peer.ws.write_formula(r, 12, f'=IF(K{r+1}=1,H{r+1},"")', B.f(num="pct1"))
        peer.ws.write_formula(r, 13, f'=IF(K{r+1}=1,J{r+1},"")', B.f(num="x"))
    peer.ws.write(pf - 1, 12, "RoE (fit)", B.f(bold=True, bottom=True, align="right")); peer.ws.write(pf - 1, 13, "P/B (fit)", B.f(bold=True, bottom=True, align="right"))
    peer.r += 1
    peer.note("Source: S5 Screener standalone financials and market data, 2-3 Nov 2026. Fit: private banks with normal earnings (excludes PSU banks and IndusInd, IDFC First, Yes).")
    peer.note("All twelve banks give a negative slope (R-squared about 0.1): PSU banks earn 16-18% RoE at below 1x book. Ownership and franchise dominate, so levers are valued by justified P/B.")
    peer.scalar("slope", "Slope: P/B per unit of RoE", f"=SLOPE(N{pf+1}:N{pl+1},M{pf+1}:M{pl+1})", "x", "", num="num", kind="calc")
    peer.scalar("icpt", "Intercept", f"=INTERCEPT(N{pf+1}:N{pl+1},M{pf+1}:M{pl+1})", "x", "", num="num", kind="calc")
    peer.scalar("rsq", "R-squared", f"=RSQ(N{pf+1}:N{pl+1},M{pf+1}:M{pl+1})", "", "", num="num", kind="calc")
    peer.scalar("n", "Banks in fit", f"=SUM(K{pf+1}:K{pl+1})", "", "", num="int", kind="calc")
    peer.rows["pf"], peer.rows["pl"] = pf, pl
    sc = wb.add_chart({"type": "scatter"})
    sc.add_series({"name": "Peers", "categories": ["Peers", pf, 7, pl, 7], "values": ["Peers", pf, 9, pl, 9],
                   "marker": {"type": "circle", "size": 7, "fill": {"color": "#7F7F7F"}, "border": {"color": "#7F7F7F"}},
                   "trendline": {"type": "linear", "line": {"color": "#1F3864", "width": 1.25}}})
    hdr_row = pf + list(pdf.sym).index("HDFCBANK")
    sc.add_series({"name": "HDFC Bank", "categories": ["Peers", hdr_row, 7, hdr_row, 7], "values": ["Peers", hdr_row, 9, hdr_row, 9],
                   "marker": {"type": "circle", "size": 9, "fill": {"color": "#1F3864"}, "border": {"color": "#1F3864"}}})
    sc.set_title({"name": "P/B rises with RoE across Indian banks", "name_font": {"name": "Garamond", "size": 12, "bold": True}})
    sc.set_x_axis({"name": "RoE FY26", "num_format": "0%", "num_font": {"name": "Garamond"}, "name_font": {"name": "Garamond", "bold": False}, "major_gridlines": {"visible": False}})
    sc.set_y_axis({"name": "P/B", "num_format": "0.0x", "num_font": {"name": "Garamond"}, "name_font": {"name": "Garamond", "bold": False}, "major_gridlines": {"visible": True, "line": {"color": "#E0E0E0"}}})
    sc.set_legend({"position": "bottom", "font": {"name": "Garamond"}}); sc.set_size({"width": 620, "height": 330})
    peer.ws.insert_chart(peer.r + 1, 1, sc)

    # ================================================================ Valuation
    val.section("Cost of equity")
    val.scalar("rf", "Risk-free rate: 10-year G-sec", float(grp.loc["gsec_10y", "value"]) / 100, "%", "S9 RBI via FactIQ, Aug-26", num="pct2")
    val.scalar("beta", "Equity beta", 0.95, "x", "Assumption: range 0.85-1.10 (no licensed price feed)", num="num")
    val.scalar("erp", "Equity risk premium, India", 0.065, "%", "Assumption: range 6.0-7.5%", num="pct2")
    val.scalar("ke", "Cost of equity", f"={val.a('rf')}+{val.a('beta')}*{val.a('erp')}", "%", "CAPM", num="pct2", kind="calc")
    val.scalar("g", "Long-term growth", 0.08, "%", "Assumption: nominal GDP-linked", num="pct2")
    val.section("Justified P/B (Gordon growth on sustainable RoE)")
    val.scalar("roe29", "Sustainable RoE: FY29E", f"={md.x('roe', 'N')}", "%", "Model, selected scenario", num="pct1", kind="link")
    val.scalar("pb_j", "Justified P/B", f"=({val.a('roe29')}-{val.a('g')})/({val.a('ke')}-{val.a('g')})", "x", "(RoE - g) / (Ke - g)", num="x", kind="calc")
    val.scalar("subs_cost", "Investment in subsidiaries at cost", 13348.7, "INR cr", "S2 IR26 Sch 8 I(v) and II(ii)", num="cr")
    val.scalar("bv_core", "Core book value, FY26", f"={md.x('eq', 'K')}-{val.a('subs_cost')}", "INR cr", "", num="cr", kind="calc")
    val.scalar("core_val", "Core bank value", f"={val.a('pb_j')}*{val.a('bv_core')}", "INR cr", "", num="cr", kind="calc")
    val.section("Listed subsidiaries at market value")
    for k, nm, mk, sk in [("v_life", "HDFC Life", "hdfclife_mcap", "stake_hdfclife"), ("v_hdb", "HDB Financial Services", "hdbfs_mcap", "stake_hdbfs"), ("v_amc", "HDFC AMC", "hdfcamc_mcap", "stake_hdfcamc")]:
        val.scalar(k + "_m", f"{nm}: market capitalisation", float(grp.loc[mk, "value"]), "INR cr", "S5 Screener", num="cr")
        val.scalar(k + "_s", f"{nm}: HDFC Bank stake", float(grp.loc[sk, "value"]), "%", "S2 IR26 p52", num="pct1")
    val.scalar("hold_disc", "Holding-company discount", 0.20, "%", "Assumption", num="pct1")
    val.scalar("subs_val", "Subsidiaries, after discount", f"=({val.a('v_life_m')}*{val.a('v_life_s')}+{val.a('v_hdb_m')}*{val.a('v_hdb_s')}+{val.a('v_amc_m')}*{val.a('v_amc_s')})*(1-{val.a('hold_disc')})", "INR cr", "", num="cr", kind="calc")
    val.scalar("sotp", "Sum of the parts equity value", f"={val.a('core_val')}+{val.a('subs_val')}", "INR cr", "", num="cr", kind="calc")
    val.scalar("sotp_ps", "Sum of the parts per share", f"={val.a('sotp')}/{inp.x('shares')}", "INR", "", num="rs", kind="calc")
    val.section("Residual income (standalone, including subsidiaries at book)")
    val.scalar("ri_g", "Residual income growth after FY29", 0.05, "%", "Assumption: fade", num="pct2")
    for i, (y, c) in enumerate(zip(["FY27E", "FY28E", "FY29E"], PROJ)):
        val.scalar(f"n_{c}", f"Discount periods to {y}", float(i + 1), "years", "Valuation date 31 March 2026", num="int")
        val.scalar(f"ri_{c}", f"Residual income {y}", f"={md.x('pat', c)}-{val.a('ke')}*{md.x('eq', prev(c))}", "INR cr", "PAT - Ke x opening book", num="cr", kind="calc")
    val.scalar("ri_pv", "Present value of FY27E-FY29E residual income",
               f"={val.a('ri_L')}/(1+{val.a('ke')})^{val.a('n_L')}+{val.a('ri_M')}/(1+{val.a('ke')})^{val.a('n_M')}+{val.a('ri_N')}/(1+{val.a('ke')})^{val.a('n_N')}", "INR cr", "", num="cr", kind="calc")
    val.scalar("ri_tv", "Present value of terminal residual income", f"={val.a('ri_N')}*(1+{val.a('ri_g')})/({val.a('ke')}-{val.a('ri_g')})/(1+{val.a('ke')})^{val.a('n_N')}", "INR cr", "", num="cr", kind="calc")
    val.scalar("ri_val", "Residual income equity value", f"={md.x('eq', 'K')}+{val.a('ri_pv')}+{val.a('ri_tv')}", "INR cr", "", num="cr", kind="calc")
    val.scalar("ri_ps", "Residual income per share", f"={val.a('ri_val')}/{inp.x('shares')}", "INR", "", num="rs", kind="calc")
    val.section("Market view")
    val.scalar("px", "Current share price", f"={inp.x('price')}", "INR", "", num="rs", kind="link")
    val.scalar("pb_now", "Current P/B (standalone)", f"={inp.x('mcap')}/{md.x('eq', 'K')}", "x", "", num="x", kind="calc")
    val.scalar("roe_impl", "RoE the market is pricing", f"={val.a('g')}+{val.a('pb_now')}*({val.a('ke')}-{val.a('g')})", "%", "g + P/B x (Ke - g)", num="pct1", kind="calc")
    val.scalar("pb_reg", "P/B implied by peer regression at FY29E RoE", f"={peer.x('icpt')}+{peer.x('slope')}*{val.a('roe29')}", "x", "Peers tab", num="x", kind="link")
    val.scalar("up_sotp", "Upside to sum of the parts", f"={val.a('sotp_ps')}/{val.a('px')}-1", "%", "", num="pct1", kind="calc")
    val.scalar("up_ri", "Upside to residual income", f"={val.a('ri_ps')}/{val.a('px')}-1", "%", "", num="pct1", kind="calc")
    val.scalar("roa_step", "RoA increment for value test", 10, "bp", "", num="bp")
    val.scalar("val_10bp", "Value of +10 bp RoA (equity value)", f"={val.a('roa_step')}/{inp.x('bp')}*{md.x('a_ta', 'N')}/{md.x('a_eq', 'N')}/({val.a('ke')}-{val.a('g')})*{val.a('bv_core')}",
               "INR cr", "Through justified P/B", num="cr", kind="calc")

    # ================================================================ Levers
    lev.section("Inputs per lever")
    hdr = ["Lever", "Size", "Unit", "Mechanism", "Feasibility (1-5)", "Months to impact"]
    for j, t in enumerate(hdr):
        lev.ws.write(lev.r, 1 + j, t, B.f(bold=True, bottom=True))
    lev.ws.set_column(5, 12, 13)
    lev.r += 1
    LV = [("l1", "Rebuild CASA", 0.015, "pct1", "% of deposits", "CASA ratio above scenario path", 3, 18),
          ("l2", "Retire legacy borrowings faster", 75000.0, "cr", "INR cr", "Extra borrowings replaced by deposits", 4, 12),
          ("l3", "Re-mix advances to higher-yield retail and SME", 0.0010, "pct2", "% yield", "Yield on advances above path", 3, 9),
          ("l4", "Branch and operations productivity", 0.03, "pct1", "% of opex", "Opex below path", 4, 12),
          ("l5", "Protect bancassurance and grow card fees", 0.03, "pct1", "% of fees", "Fees above path", 3, 12),
          ("l6", "Win UPI merchant acquiring share", 0.10, "pct1", "% payee share", "Payee share target", 2, 18)]
    for k, nm, size, nf, unit, mech, feas, mo in LV:
        r = lev.r
        lev.ws.write(r, 1, nm, B.f()); lev.ws.write_number(r, 2, size, B.f(num=nf, color=BLUE, fill=True)); lev.ws.write(r, 3, unit, B.f(color=GREY))
        lev.ws.write(r, 4, mech, B.f(color=GREY)); lev.ws.write_number(r, 5, feas, B.f(num="int", color=BLUE, fill=True)); lev.ws.write_number(r, 6, mo, B.f(num="int", color=BLUE, fill=True))
        lev.rows[k] = r; lev.r += 1
    lev.note("Assumptions: lever sizes, feasibility and timing are judgements for discussion, not forecasts.")
    lev.section("FY29E impact")
    hdr = ["Lever", "Pre-tax uplift", "PAT uplift", "RoA uplift", "RoE uplift", "Equity value", "Value per share", "Priority score"]
    for j, t in enumerate(hdr):
        lev.ws.write(lev.r, 1 + j, t, B.f(bold=True, bottom=True, align="right" if j else None))
    lev.r += 1
    N = "N"
    pre = {
        "l1": f"=C{lev.rows['l1']+1}*{inp.x('spread_td', N)}*{md.x('a_dep', N)}",
        "l2": f"=C{lev.rows['l2']+1}*({md.x('c_bor', N)}-{md.x('c_dep', N)})",
        "l3": f"=C{lev.rows['l3']+1}*{md.x('a_loans', N)}",
        "l4": f"=C{lev.rows['l4']+1}*{md.x('opex', N)}",
        "l5": f"=C{lev.rows['l5']+1}*{md.x('fee', N)}",
        "l6": f"=MAX(0,C{lev.rows['l6']+1}-{fee.x('hd_share')})*{fee.x('pool')}*(1+{fee.x('p2m_g')})^({fee.x('yr_idx', N)}-1)*{fee.x('acq_share')}",
    }
    out_first = lev.r
    for k, nm, *_ in LV:
        r = lev.r; ir = lev.rows[k] + 1
        lev.ws.write(r, 1, nm, B.f())
        lev.ws.write_formula(r, 2, pre[k], B.f(num="cr"))
        lev.ws.write_formula(r, 3, f"=C{r+1}*(1-{inp.x('tax', N)})", B.f(num="cr"))
        lev.ws.write_formula(r, 4, f"=D{r+1}/{md.x('a_ta', N)}*{inp.x('bp')}", B.f(num="bp"))
        lev.ws.write_formula(r, 5, f"=D{r+1}/{md.x('a_eq', N)}", B.f(num="pct2"))
        lev.ws.write_formula(r, 6, f"=F{r+1}/({val.x('ke')}-{val.x('g')})*{val.x('bv_core')}", B.f(num="cr"))
        lev.ws.write_formula(r, 7, f"=G{r+1}/{inp.x('shares')}", B.f(num="rs"))
        lev.ws.write_formula(r, 8, f"=E{r+1}*F{ir}/G{ir}", B.f(num="num"))
        lev.rows[f"o_{k}"] = r; lev.r += 1
    out_last = lev.r - 1
    lev.ws.write(lev.r, 1, "All levers", B.f(bold=True, top=True))
    for j, col in enumerate("CDEFGH"):
        lev.ws.write_formula(lev.r, 2 + j, f"=SUM({col}{out_first+1}:{col}{out_last+1})", B.f(num=["cr", "cr", "bp", "pct2", "cr", "rs"][j], bold=True, top=True))
    lev.rows["tot"] = lev.r; lev.r += 2
    lev.section("FY29E RoA bridge")
    lev.scalar("b0", "RoA FY26A, core", f"={md.x('roa_core', 'K')}*{inp.x('bp')}", "bp", "", num="bp", kind="link")
    lev.scalar("b1", "Scenario drift to FY29E (margin, fees, cost, credit, mix)", f"={md.x('roa', 'N')}*{inp.x('bp')}-{lev.a('b0')}", "bp", "", num="bp", kind="calc")
    lev.scalar("b2", "RoA FY29E, scenario before levers", f"={lev.a('b0')}+{lev.a('b1')}", "bp", "", num="bp", kind="calc")
    lev.scalar("b3", "Levers", f"=E{lev.rows['tot']+1}", "bp", "", num="bp", kind="calc")
    lev.scalar("b4", "RoA FY29E with levers", f"={lev.a('b2')}+{lev.a('b3')}", "bp", "", num="bp", kind="calc")
    lev.scalar("target", "Target", 200, "bp", "Problem statement: 2.0%", num="bp")
    lev.scalar("gap", "Shortfall (-) / headroom (+) to target", f"={lev.a('b4')}-{lev.a('target')}", "bp", "", num="bp", kind="calc")
    bc = wb.add_chart({"type": "bar"})
    bc.add_series({"name": "RoA uplift FY29E", "categories": ["Levers", out_first, 1, out_last, 1], "values": ["Levers", out_first, 4, out_last, 4],
                   "fill": {"color": "#1F3864"}, "gap": 80, "data_labels": {"value": True, "num_format": '0" bp"', "font": {"name": "Garamond"}}})
    bc.set_title({"name": "FY29E RoA uplift by lever", "name_font": {"name": "Garamond", "size": 12, "bold": True}})
    bc.set_x_axis({"num_font": {"name": "Garamond"}, "major_gridlines": {"visible": False}, "num_format": '0" bp"'})
    bc.set_y_axis({"num_font": {"name": "Garamond"}, "reverse": True}); bc.set_legend({"none": True}); bc.set_size({"width": 620, "height": 300})
    lev.ws.insert_chart(lev.r + 1, 1, bc)

    # ================================================================ Sensitivities
    sen.section("Value per share (sum of the parts): cost of equity (rows) x long-term growth (columns)")
    kes = [0.115, 0.12, 0.125, 0.13, 0.135, 0.14, 0.145]; gs = [0.07, 0.075, 0.08, 0.085, 0.09]
    sen.ws.write(sen.r, 1, "Ke \\ g", B.f(bold=True, bottom=True))
    for j, gv in enumerate(gs):
        sen.ws.write_number(sen.r, 2 + j, gv, B.f(num="pct1", color=BLUE, fill=True, bottom=True))
    hr = sen.r; sen.r += 1
    for kv in kes:
        r = sen.r
        sen.ws.write_number(r, 1, kv, B.f(num="pct1", color=BLUE, fill=True))
        for j in range(len(gs)):
            col = "CDEFG"[j]
            sen.ws.write_formula(r, 2 + j, f"=((({val.x('roe29')}-{col}${hr+1})/($B{r+1}-{col}${hr+1}))*{val.x('bv_core')}+{val.x('subs_val')})/{inp.x('shares')}", B.f(num="rs"))
        sen.r += 1
    sen.r += 1
    sen.section("Value per share (sum of the parts): FY29E RoE (rows) x cost of equity (columns)")
    roes = [0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18]; kes2 = [0.12, 0.125, 0.13, 0.135, 0.14]
    sen.ws.write(sen.r, 1, "RoE \\ Ke", B.f(bold=True, bottom=True))
    for j, kv in enumerate(kes2):
        sen.ws.write_number(sen.r, 2 + j, kv, B.f(num="pct1", color=BLUE, fill=True, bottom=True))
    hr2 = sen.r; sen.r += 1
    for rv in roes:
        r = sen.r
        sen.ws.write_number(r, 1, rv, B.f(num="pct1", color=BLUE, fill=True))
        for j in range(len(kes2)):
            col = "CDEFG"[j]
            sen.ws.write_formula(r, 2 + j, f"=((($B{r+1}-{val.x('g')})/({col}${hr2+1}-{val.x('g')}))*{val.x('bv_core')}+{val.x('subs_val')})/{inp.x('shares')}", B.f(num="rs"))
        sen.r += 1
    sen.note("Current share price for reference is on the Valuation tab. Grids hold the selected scenario's book value and subsidiaries constant.")

    # ================================================================ Dashboard
    dash.ws.write(4, 1, "Scenario", B.f(bold=True))
    dash.ws.write(4, 4, "Base", B.f(color=BLUE, fill=True, bold=True))
    dash.ws.data_validation(4, 4, 4, 4, {"validate": "list", "source": "=Inputs!$E${0}:$G${0}".format(inp.rows["sc_list"] + 1)})
    wb.define_name("Scenario", "=Dashboard!$E$5")
    dash.r = 6
    dash.timeline()
    for k, lab, n in [("roa", "Return on average assets", "pct2"), ("roa_core", "Return on average assets, core", "pct2"), ("roe", "Return on average net worth", "pct1"),
                      ("nim", "Net interest margin", "pct2"), ("ci", "Cost to income", "pct1"), ("ccost", "Credit cost", "pct2"), ("cd", "Credit-deposit ratio", "pct1"),
                      ("pat", "Profit after tax", "cr"), ("eps", "Earnings per share", "rs"), ("bvps", "Book value per share", "rs")]:
        dash.line(k, lab, "", "", hist=lambda c, k=k: None if (c == "E" and k not in ("pat", "eps", "bvps", "ci", "cd")) else f"={md.xr(k, c)}", hist_kind="link",
                  proj=lambda c, k=k: f"={md.xr(k, c)}", proj_kind="link", num=n)
    dash.section("Valuation and the answer")
    for k, lab, ref_, n in [("d_px", "Share price", val.x("px"), "rs"), ("d_sotp", "Sum of the parts per share", val.x("sotp_ps"), "rs"), ("d_ri", "Residual income per share", val.x("ri_ps"), "rs"),
                            ("d_roeimpl", "RoE the market is pricing", val.x("roe_impl"), "pct1"), ("d_b2", "RoA FY29E before levers", lev.x("b2"), "bp"),
                            ("d_b4", "RoA FY29E with levers", lev.x("b4"), "bp"), ("d_gap", "Headroom (+) / shortfall (-) to 2.0%", lev.x("gap"), "bp"),
                            ("d_val10", "Equity value of +10 bp RoA", val.x("val_10bp"), "cr")]:
        dash.scalar(k, lab, f"={ref_}", "", "", num=n, kind="link")
    ch = wb.add_chart({"type": "line"})
    ch.add_series({"name": "RoA", "categories": ["Dashboard", 6, 4, 6, 13], "values": ["Dashboard", dash.rows["roa"], 4, dash.rows["roa"], 13],
                   "line": {"color": "#1F3864", "width": 2}, "marker": {"type": "circle", "size": 6, "fill": {"color": "#1F3864"}, "border": {"color": "#1F3864"}}})
    ch.add_series({"name": "RoA, core", "categories": ["Dashboard", 6, 4, 6, 13], "values": ["Dashboard", dash.rows["roa_core"], 4, dash.rows["roa_core"], 13],
                   "line": {"color": "#A6A6A6", "width": 1.5, "dash_type": "dash"}})
    ch.set_title({"name": "RoA path, selected scenario", "name_font": {"name": "Garamond", "size": 12, "bold": True}})
    ch.set_y_axis({"num_format": "0.0%", "num_font": {"name": "Garamond"}, "major_gridlines": {"visible": True, "line": {"color": "#E0E0E0"}}})
    ch.set_x_axis({"num_font": {"name": "Garamond"}}); ch.set_legend({"position": "bottom", "font": {"name": "Garamond"}}); ch.set_size({"width": 620, "height": 300})
    dash.ws.insert_chart(dash.r + 1, 1, ch)

    # ================================================================ Checks
    chk.ws.write(chk.r, 1, "Check", B.f(bold=True, bottom=True)); chk.ws.write(chk.r, 2, "Value", B.f(bold=True, bottom=True, align="right")); chk.ws.write(chk.r, 3, "Result", B.f(bold=True, bottom=True))
    chk.ws.write(chk.r, 4, "Tolerance", B.f(bold=True, bottom=True, align="right"))
    chk.r += 1
    tests = [
        ("Model balance sheet balances, FY27E-FY29E (sum of absolute differences, INR cr)", f"=SUMPRODUCT(ABS('Model'!L{md.rows['ta']+1}:N{md.rows['ta']+1}-'Model'!L{md.rows['tle']+1}:N{md.rows['tle']+1}))", "<1"),
        ("Hist balance sheet ties within Screener whole-crore rounding (sum of absolute differences, INR cr)", f"=SUMPRODUCT(ABS('Hist'!E{hs.rows['bs_diff']+1}:K{hs.rows['bs_diff']+1}))", "<5"),
        ("Hist PAT rebuilt from components ties to reported (sum of absolute differences)", f"=SUMPRODUCT(ABS('Hist'!E{hs.rows['pat_calc']+1}:K{hs.rows['pat_calc']+1}-'Hist'!E{hs.rows['pat_rep']+1}:K{hs.rows['pat_rep']+1}))", "<1"),
        ("Borrowing maturities sum to FY26 borrowings (difference, INR cr)", f"='ALM'!G{alm.rows['gap_tot']+1}-{md.x('bor', 'K')}", "<1"),
        ("NII walk explains all of the change (sum of residuals, INR cr)", f"=SUMPRODUCT(ABS('Margin'!G{mg.rows['vr_chk']+1}:N{mg.rows['vr_chk']+1}))", "<1"),
        ("Scenario selector resolves to 1, 2 or 3", f"={inp.x('scn')}", "in"),
        ("Cost of equity exceeds long-term growth", f"={val.x('ke')}-{val.x('g')}", ">0"),
        ("Lever bridge adds up (difference, bp)", f"={lev.x('b4')}-{lev.x('b0')}-{lev.x('b1')}-{lev.x('b3')}", "<1"),
        ("No error values in Model, Valuation and Levers", f"=SUMPRODUCT(--ISERROR('Model'!E5:N120))+SUMPRODUCT(--ISERROR('Valuation'!E5:E80))+SUMPRODUCT(--ISERROR('Levers'!C5:I40))", "=0"),
    ]
    rows_chk = []
    for lab, f_, rule in tests:
        r = chk.r
        chk.ws.write(r, 1, lab, B.f())
        chk.ws.write_formula(r, 2, f_, B.f(num="num"))
        tol = {"<1": 1, "<5": 5, "in": None, ">0": 0, "=0": 0}[rule]
        if tol is not None:
            chk.ws.write_number(r, 4, tol, B.f(num="num", color=BLUE, fill=True))
        cond = {"<1": f"ABS(C{r+1})<E{r+1}", "<5": f"ABS(C{r+1})<E{r+1}", "in": f"AND(C{r+1}>=1,C{r+1}<=COUNTA(Inputs!$E${inp.rows['sc_list']+1}:$G${inp.rows['sc_list']+1}))",
                ">0": f"C{r+1}>E{r+1}", "=0": f"C{r+1}=E{r+1}"}[rule]
        chk.ws.write_formula(r, 3, f'=IF({cond},"PASS","FAIL")', B.f(color=RED, bold=True))
        rows_chk.append(r); chk.r += 1
    chk.r += 1
    chk.scalar("master", "Master check", f'=IF(COUNTIF(D{rows_chk[0]+1}:D{rows_chk[-1]+1},"FAIL")=0,"ALL CHECKS PASS","CHECK FAILURES")', "", "", num="gen", kind="check", col=3)

    # ================================================================ Sources
    srcs = [("S1", "HDFC Bank quarterly investor presentations, Q4 FY26 and Q2 FY27", "data/raw/ir/HDFCBANK_Q4FY26_ppt.pdf, HDFCBANK_Q2FY27_ppt.pdf (hashes in data/raw/manifest.csv)"),
            ("S2", "HDFC Bank Integrated Annual Report FY2025-26 (standalone schedules, ten-year highlights, maturity pattern)", "hdfc.bank.in annual report; pages cited per row"),
            ("S3", "RBI Bank Rate (repo + 25 bp), daily", "FactIQ rbi|bbe02280a1da51aa"),
            ("S4", "RBI Survey of Professional Forecasters, round 102 (Sep-2026)", "FactIQ rbi|905a6f3e95217459 (mean), rbi|bb554632b75f939c (max)"),
            ("S5", "Screener.in standalone financials and market data", "data/raw/screener/*_tables.csv, *_valuation.csv (2-3 Nov 2026)"),
            ("S6", "HDFC Life investor presentations, Q4 FY26 and Q2 FY27", "data/raw/ir/HDFCLIFE_*.pdf"),
            ("S7", "NPCI UPI statistics: P2P/P2M, ticket bands, payee banks", "FactIQ rbi-npci_upi; data/inputs/npci_*.csv"),
            ("S8", "Department of Financial Services FAQ on UPI MDR (15 Sep 2026)", "data/raw/web/DFS_UPI_MDR_FAQ_Sep2026.pdf"),
            ("S9", "RBI 10-year G-sec yield (SGL transactions)", "FactIQ rbi|9cbd58f9ab50a1de"),
            ("S10", "IRDAI consultation 'Recalibrating Economics of Insurance Distribution' and Handbook 2024-25", "Insurance module: models/02_Insurance_Distribution.xlsx")]
    for j, t in enumerate(["ID", "Source", "Location"]):
        src.ws.write(src.r, 1 + j, t, B.f(bold=True, bottom=True))
    src.r += 1
    for sid, d_, loc in srcs:
        src.ws.write(src.r, 1, sid, B.f(bold=True)); src.ws.write(src.r, 2, d_, B.f()); src.ws.write(src.r, 3, loc, B.f(color=GREY)); src.r += 1

    # ================================================================ Cover
    cv = cover.ws
    cover.r = 3
    for lab, v in [("Purpose", "Quantify the moves that restore HDFC Bank's standalone RoA to at least 2.0% by FY29, and what each is worth."),
                   ("Status", "Outside-in case study on public data only. Not commissioned by, or affiliated with, HDFC Bank or Bain & Company."),
                   ("Prepared by", "Anklesh"), ("Version", "v2.0, 3 November 2026"), ("Units", "INR crore unless stated; fiscal year ends 31 March")]:
        cv.write(cover.r, 1, lab, B.f(bold=True)); cv.write(cover.r, 3, v, B.f()); cover.r += 1
    cover.r += 1
    cv.write(cover.r, 1, "Master check", B.f(bold=True)); cv.write_formula(cover.r, 3, f"={chk.x('master', 'D')}", B.f(color=RED, bold=True)); cover.r += 1
    cv.write(cover.r, 1, "Active scenario", B.f(bold=True)); cv.write_formula(cover.r, 3, "=Scenario", B.f(color=GREEN)); cover.r += 2
    cv.write(cover.r, 1, "Tab", B.f(bold=True, bottom=True)); cv.write(cover.r, 3, "Contents", B.f(bold=True, bottom=True)); cover.r += 1
    toc = [("Dashboard", "Scenario selector, key outputs, valuation and the answer"), ("Inputs", "All drivers by scenario; per-share and unit inputs"),
           ("Hist", "Standalone financials FY20-FY26 spread from the annual report"), ("Model", "Balance sheet, P&L and ratios FY20A-FY29E"),
           ("Margin", "NII volume/rate walk, spreads, legacy borrowing run-off"), ("ALM", "Repricing gap and earnings at risk"),
           ("Fees", "IRDAI caps (bank and HDFC Life) and UPI MDR"), ("Opex_Credit", "Cost-to-serve and credit normalisation"),
           ("Capital", "Tier 1 proxy and growth capacity"), ("Levers", "Six value levers and the FY29E RoA bridge"),
           ("Valuation", "Justified P/B, sum of the parts, residual income"), ("Sensitivities", "Value per share grids"),
           ("Peers", "Twelve-bank P/B vs RoE"), ("Checks", "Integrity tests and master flag"), ("Sources", "Source register")]
    for n_, d_ in toc:
        cv.write_url(cover.r, 1, f"internal:'{n_}'!A1", string=n_, cell_format=B.f(color=BLACK))
        cv.write(cover.r, 3, d_, B.f(color=GREY)); cover.r += 1
    cover.r += 1
    cv.write(cover.r, 1, "Colour code", B.f(bold=True)); cv.write(cover.r, 3, "Blue: hard-coded input", B.f(color=BLUE)); cover.r += 1
    cv.write(cover.r, 3, "Black: formula", B.f()); cover.r += 1
    cv.write(cover.r, 3, "Green: link to another tab", B.f(color=GREEN)); cover.r += 1
    cv.write(cover.r, 3, "Red: check", B.f(color=RED)); cover.r += 1
    for s_ in B.sheets.values():
        s_.ws.set_tab_color("#1F3864" if s_.name in ("Cover", "Dashboard") else "#BFBFBF")
    cover.ws.activate()
    B.close()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
