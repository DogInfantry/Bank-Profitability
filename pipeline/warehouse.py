"""Build data/fs.duckdb: one SQL warehouse over every tidy and input file, the Screener harvest and the model export.

Tables are named after their files (data/tidy/bank_facts.csv -> tidy_bank_facts; data/inputs/x.csv -> in_x).
screener_tables and screener_valuation union the per-bank Screener files. hdfc_scenarios is the long form of
data/tidy/hdfc_model_outputs.json (scenario, sheet, line, period, value). Views add bank-year ratios and a peer league.
The file is gitignored and rebuilt on demand: python -I pipeline/warehouse.py
"""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "fs.duckdb"
TIMELINE = {"Model", "Margin", "Fees", "Opex_Credit", "Capital"}
YEARS = ["FY20A", "FY21A", "FY22A", "FY23A", "FY24A", "FY25A", "FY26A", "FY27E", "FY28E", "FY29E"]

VIEWS = """
CREATE OR REPLACE VIEW v_bank_year AS
WITH p AS (
  SELECT symbol, CAST(substr(period, 5, 4) AS INT) AS fy_end,
         max(CASE WHEN line_item = 'Revenue' THEN value END) AS interest_earned,
         max(CASE WHEN line_item = 'Interest' THEN value END) AS interest_expended,
         max(CASE WHEN line_item = 'Other Income' THEN value END) AS other_income,
         max(CASE WHEN line_item = 'Net Profit' THEN value END) AS pat
  FROM screener_tables WHERE section = 'profit-loss' AND period LIKE 'Mar %' GROUP BY 1, 2),
b AS (
  SELECT symbol, CAST(substr(period, 5, 4) AS INT) AS fy_end,
         max(CASE WHEN line_item = 'Total Assets' THEN value END) AS total_assets,
         max(CASE WHEN line_item = 'Deposits' THEN value END) AS deposits,
         max(CASE WHEN line_item = 'Borrowing' THEN value END) AS borrowings,
         max(CASE WHEN line_item = 'Equity Capital' THEN value END) + max(CASE WHEN line_item = 'Reserves' THEN value END) AS net_worth
  FROM screener_tables WHERE section = 'balance-sheet' AND period LIKE 'Mar %' GROUP BY 1, 2)
SELECT p.symbol, p.fy_end, p.interest_earned, p.interest_expended, p.other_income, p.pat,
       b.total_assets, b.deposits, b.borrowings, b.net_worth,
       (b.total_assets + lag(b.total_assets) OVER w) / 2 AS avg_assets,
       (b.net_worth + lag(b.net_worth) OVER w) / 2 AS avg_net_worth
FROM p JOIN b USING (symbol, fy_end)
WINDOW w AS (PARTITION BY p.symbol ORDER BY p.fy_end);

CREATE OR REPLACE VIEW v_bank_ratios AS
SELECT symbol, fy_end,
       pat / avg_assets AS roa,
       pat / avg_net_worth AS roe,
       (interest_earned - interest_expended) / avg_assets AS nii_to_assets,
       other_income / avg_assets AS other_income_to_assets,
       borrowings / (borrowings + deposits) AS borrowings_share_of_funding
FROM v_bank_year WHERE avg_assets IS NOT NULL;

CREATE OR REPLACE VIEW v_peer_league AS
WITH f AS (
  SELECT r.symbol, u.ownership, r.roa, r.roe, v.value / y.net_worth AS price_to_book
  FROM v_bank_ratios r
  JOIN bank_universe u ON u.symbol = r.symbol
  JOIN v_bank_year y ON y.symbol = r.symbol AND y.fy_end = r.fy_end
  JOIN screener_valuation v ON v.symbol = r.symbol AND v.metric = 'Market Cap'
  WHERE r.fy_end = 2026)
SELECT *, rank() OVER (ORDER BY roa DESC) AS roa_rank, (max(roa) OVER () - roa) * 1e4 AS roa_gap_to_best_bp FROM f;
"""


def main():
    if DB.exists():
        DB.unlink()
    con = duckdb.connect(str(DB))
    n = 0
    for folder, prefix in ((ROOT / "data" / "tidy", "tidy_"), (ROOT / "data" / "inputs", "in_")):
        for f in sorted(folder.glob("*.csv")):
            con.execute(f"CREATE TABLE {prefix}{f.stem} AS SELECT * FROM read_csv_auto('{f.as_posix()}', header=true, sample_size=-1)")
            n += 1
    scr = ROOT / "data" / "raw" / "screener"
    con.execute(f"CREATE TABLE screener_tables AS SELECT * FROM read_csv_auto('{(scr / '*_tables.csv').as_posix()}', union_by_name=true)")
    con.execute(f"CREATE TABLE screener_valuation AS SELECT * FROM read_csv_auto('{(scr / '*_valuation.csv').as_posix()}', union_by_name=true)")
    O = json.loads((ROOT / "data" / "tidy" / "hdfc_model_outputs.json").read_text())
    rows = []
    for scn, d in O.items():
        if scn.startswith("_"):
            continue
        for key, vals in d.items():
            sheet, line = key.split("|", 1)
            if sheet in TIMELINE and any(isinstance(v, (int, float)) for v in vals[3:12]):   # E..N = FY20A..FY29E
                rows += [(scn, sheet, line, y, v) for y, v in zip(YEARS, vals[2:12]) if isinstance(v, (int, float))]
            else:                    # scalar and table rows: period = spreadsheet column letter (C, D, E, ...)
                rows += [(scn, sheet, line, "CDEFGHIJKLMN"[i], v) for i, v in enumerate(vals[:12]) if isinstance(v, (int, float))]
    hs = pd.DataFrame(rows, columns=["scenario", "sheet", "line", "period", "value"])
    con.register("hs", hs); con.execute("CREATE TABLE hdfc_scenarios AS SELECT * FROM hs")
    uni = pd.DataFrame({"symbol": ["HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK", "INDUSINDBK", "YESBANK", "IDFCFIRSTB", "FEDERALBNK",
                                   "SBIN", "BANKBARODA", "PNB", "CANBK"], "ownership": ["private"] * 8 + ["public"] * 4})
    con.register("uni", uni); con.execute("CREATE TABLE bank_universe AS SELECT * FROM uni")
    con.execute(VIEWS)
    print(f"wrote {DB.relative_to(ROOT)}: {n} csv tables + screener_tables, screener_valuation, hdfc_scenarios ({len(hs)} rows) and 3 views")
    con.close()


if __name__ == "__main__":
    main()
