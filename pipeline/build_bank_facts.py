"""Build the bank data asset: tidy long facts + a wide model-input table.

Inputs
  data/raw/screener/<SYM>_tables.csv   (standalone P&L, BS, quarters; secondary aggregator)
  data/inputs/bank_reported.csv        (page-cited figures from bank decks / NSE XBRL)
Outputs
  data/tidy/bank_facts.csv            entity|period|metric|value|unit|source|page|status|row_id
  data/tidy/bank_model_inputs.csv     one row per bank-period, INR cr, used by build_bank_xlsx.py

Rules (see docs/methodology.md)
  * Standalone only. NII = Screener Revenue - Interest. Other income = Screener Other Income.
  * Screener 'Expenses + Depreciation' = opex + provisions (ex-tax). Provisions come from filings;
    opex = (Expenses + Depreciation) - provisions, cross-checked against the deck's opex where cited.
  * If only PPOP is cited (HDFC Q2FY27, NSE XBRL): provisions = PPOP - PBT; opex = NII + OI - PPOP.
  * Tax = PBT - PAT.  Average assets: FY = (opening + closing)/2; Q2FY27 = (Mar-26 + Sep-26)/2, annualised x4.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "data" / "raw" / "screener"
TIDY = ROOT / "data" / "tidy"
BANKS = ["SBIN", "HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK"]
NAMES = {"SBIN": "SBI", "HDFCBANK": "HDFC Bank", "ICICIBANK": "ICICI Bank",
         "AXISBANK": "Axis Bank", "KOTAKBANK": "Kotak Mahindra Bank"}
PERIODS = {"FY26": ("profit-loss", "Mar 2026", "Mar 2025", "Mar 2026", 1),
           "Q2FY27": ("quarters", "Sep 2026", "Mar 2026", "Sep 2026", 4)}


def screener() -> pd.DataFrame:
    return pd.concat(pd.read_csv(SCR / f"{b}_tables.csv") for b in BANKS)


def val(s: pd.DataFrame, sym, sec, item, period):
    m = s[(s.symbol == sym) & (s.section == sec) & (s.line_item == item) & (s.period == period)]
    return float(m.value.iloc[0]) if len(m) else None


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    s = screener()
    rep = pd.read_csv(ROOT / "data" / "inputs" / "bank_reported.csv")
    facts, wide = [], []

    def add(bank, period, metric, value, unit, source, page="", status="primary"):
        facts.append(dict(entity=bank, period=period, metric=metric, value=value, unit=unit,
                          source=source, page=page, status=status))

    for b in BANKS:
        for per, (sec, col, bs_open, bs_close, ann) in PERIODS.items():
            rev = val(s, b, sec, "Revenue", col)
            if rev is None:
                print(f"skip {b} {per}: not yet reported")
                continue
            r = {k: v for k, v in rep[(rep.bank == b) & (rep.period == per)][["metric", "value"]].values}
            g = lambda item: val(s, b, sec, item, col)  # noqa: E731
            nii = rev - g("Interest")
            oi, pbt, pat = g("Other Income"), g("Profit before tax"), g("Net Profit")
            exp_dep = g("Expenses") + g("Depreciation")
            if "provisions_ex_tax" in r:
                prov = r["provisions_ex_tax"]
                opex = exp_dep - prov
            else:  # PPOP route
                ppop = r["ppop"]
                prov, opex = ppop - pbt, nii + oi - ppop
            a0, a1 = val(s, b, "balance-sheet", "Total Assets", bs_open), val(s, b, "balance-sheet", "Total Assets", bs_close)
            e0 = val(s, b, "balance-sheet", "Equity Capital", bs_open) + val(s, b, "balance-sheet", "Reserves", bs_open)
            e1 = val(s, b, "balance-sheet", "Equity Capital", bs_close) + val(s, b, "balance-sheet", "Reserves", bs_close)
            dep1 = val(s, b, "balance-sheet", "Deposits", bs_close)
            row = dict(bank=b, name=NAMES[b], period=per, annualise=ann, nii=nii, other_income=oi,
                       opex=opex, provisions=prov, pbt=pbt, tax=pbt - pat, pat=pat,
                       assets_open=a0, assets_close=a1, equity_open=e0, equity_close=e1, deposits=dep1,
                       opex_cited=r.get("opex"), nim_reported=r.get("nim_reported"),
                       roa_reported=r.get("roa_reported"), ci_reported=r.get("cost_income_reported"),
                       gnpa=r.get("gnpa") if "gnpa" in r else g("Gross NPA %"),
                       nnpa=r.get("nnpa") if "nnpa" in r else g("Net NPA %"), casa=r.get("casa"))
            wide.append(row)
            src = f"Screener standalone {sec} '{col}'"
            for k in ["nii", "other_income", "pbt", "pat"]:
                add(b, per, k, row[k], "INR cr", src, status="secondary-tied")
            add(b, per, "provisions", prov, "INR cr", "bank_reported.csv", status="primary")
            add(b, per, "opex", opex, "INR cr", "derived: (Expenses+Depreciation)-provisions", status="derived")
            for k in ["assets_open", "assets_close", "equity_open", "equity_close", "deposits"]:
                add(b, per, k, row[k], "INR cr", "Screener standalone balance-sheet", status="secondary-tied")
    for _, x in rep.iterrows():
        add(x.bank, x.period, x.metric, x.value, x.unit, x.source_file, x.page if pd.notna(x.page) else "", "primary")

    # 10-year history (FY17-FY26) for trend charts: pre-split opex+provisions only
    for b in BANKS:
        for yr in range(2017, 2027):
            col, prev = f"Mar {yr}", f"Mar {yr-1}"
            rev = val(s, b, "profit-loss", "Revenue", col)
            a0, a1 = val(s, b, "balance-sheet", "Total Assets", prev), val(s, b, "balance-sheet", "Total Assets", col)
            if rev is None or a0 is None or a1 is None:
                continue
            avg = (a0 + a1) / 2
            nii = rev - val(s, b, "profit-loss", "Interest", col)
            per = f"FY{str(yr)[-2:]}"
            for m, v in {"hist_nii_pct_assets": nii / avg,
                         "hist_oi_pct_assets": val(s, b, "profit-loss", "Other Income", col) / avg,
                         "hist_cost_prov_pct_assets": (val(s, b, "profit-loss", "Expenses", col) + val(s, b, "profit-loss", "Depreciation", col)) / avg,
                         "hist_roa": val(s, b, "profit-loss", "Net Profit", col) / avg}.items():
                add(b, per, m, round(100 * v, 4), "% of avg assets", "Screener standalone (computed)", status="derived")

    f = pd.DataFrame(facts)
    f.insert(0, "row_id", [f"B{i:04d}" for i in range(1, len(f) + 1)])
    return f, pd.DataFrame(wide)


if __name__ == "__main__":
    TIDY.mkdir(parents=True, exist_ok=True)
    f, w = build()
    f.to_csv(TIDY / "bank_facts.csv", index=False)
    w.to_csv(TIDY / "bank_model_inputs.csv", index=False)
    print(f"facts: {len(f)} rows; model inputs: {len(w)} bank-periods")
    w2 = w.copy()
    w2["avg_assets"] = (w2.assets_open + w2.assets_close) / 2
    for c in ["nii", "other_income", "opex", "provisions", "tax", "pat"]:
        w2[c + "_pct"] = 100 * w2[c] * w2.annualise / w2.avg_assets
    print(w2[["bank", "period", "nii_pct", "other_income_pct", "opex_pct", "provisions_pct", "tax_pct", "pat_pct", "roa_reported", "opex", "opex_cited"]].round(2).to_string())
