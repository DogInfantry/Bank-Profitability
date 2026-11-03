"""Regenerate the Tableau-ready long extracts from data/tidy (no Tableau workbook is built here).

banks_long.csv <- tidy/bank_facts.csv; upi_monthly.csv <- tidy/upi_monthly.csv; upi_app_share_long.csv <- tidy/upi_app_share.csv;
insurers_exposure.csv <- tidy/ins_insurer_exposure.csv; hdfc_scenarios_long.csv <- the hdfc_scenarios table in data/fs.duckdb
(run pipeline/warehouse.py first). Usage: python -I viz/tableau/build_extracts.py
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
T, OUT = ROOT / "data" / "tidy", Path(__file__).resolve().parent


def main():
    pd.read_csv(T / "bank_facts.csv").to_csv(OUT / "banks_long.csv", index=False)
    pd.read_csv(T / "upi_monthly.csv").to_csv(OUT / "upi_monthly.csv", index=False)
    pd.read_csv(T / "upi_app_share.csv").to_csv(OUT / "upi_app_share_long.csv", index=False)
    pd.read_csv(T / "ins_insurer_exposure.csv").to_csv(OUT / "insurers_exposure.csv", index=False)
    con = duckdb.connect(str(ROOT / "data" / "fs.duckdb"), read_only=True)
    con.sql("SELECT * FROM hdfc_scenarios ORDER BY scenario, sheet, line, period").df().to_csv(OUT / "hdfc_scenarios_long.csv", index=False)
    for f in sorted(OUT.glob("*.csv")):
        print(f"{f.name}: {sum(1 for _ in f.open()) - 1} rows")


if __name__ == "__main__":
    main()
