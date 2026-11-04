"""Post-merger quarterly panel, Q2 FY24 to Q2 FY27, from the investor-deck inputs.

Inputs (committed, page-cited): data/inputs/hdfc_quarterly_kpis.csv (text extract, pipeline/extract_hdfc_quarterly.py)
and data/inputs/hdfc_quarterly_chart_reads.csv (chart labels read by eye). Text wins where both exist.
Output: data/tidy/hdfc_quarterly_panel.csv, one row per quarter, plus derived ratios:
  cd_ratio            net advances / deposits
  bor_share_funding   borrowings / (deposits + borrowings)
  slippage_ratio_ann  slippages x 4 / average net advances (net, not gross, advances: the decks do not tabulate gross)
  gnpa_bridge_diff    opening + slippages - upgrades - write-offs - closing (INR bn; rounding only)
  deposit_share       deposits / RBI aggregate deposits of residents (data/inputs/rbi_system_deposits_credit.csv)
  credit_share        net advances / RBI bank credit to the commercial sector (broader than advances: a proxy)
Also writes data/tidy/hdfc_segments.csv from data/inputs/hdfc_ir26_segments.csv (IR26 segment note): pre-tax
segment return on segment assets and provisions / segment assets, FY25 and FY26.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
I, T = ROOT / "data/inputs", ROOT / "data/tidy"
Q = [f"Q{q}FY{y}" for y in (24, 25, 26, 27) for q in (1, 2, 3, 4)][1:-2]  # Q2FY24 .. Q2FY27


def main() -> None:
    kp = pd.read_csv(I / "hdfc_quarterly_kpis.csv")
    ch = pd.read_csv(I / "hdfc_quarterly_chart_reads.csv")
    long = pd.concat([kp.assign(rank=0), ch.assign(rank=1)]).sort_values("rank").drop_duplicates(["period", "metric"])
    p = long[long.period.isin(Q)].pivot(index="period", columns="metric", values="value").reindex(Q)
    p["cd_ratio"] = p.net_advances / p.deposits
    p["bor_share_funding"] = p.borrowings / (p.deposits + p.borrowings)
    p["slippage_ratio_ann"] = p.slippages * 4 / ((p.net_advances + p.net_advances.shift()) / 2)
    p["gnpa_bridge_diff"] = p.gnpa_open + p.slippages - p.upgrades_recoveries - p.write_offs - p.gnpa_close
    sysd = pd.read_csv(I / "rbi_system_deposits_credit.csv").pivot(index="period", columns="metric", values="value").reindex(Q)
    p["deposit_share"] = p.deposits / sysd.system_deposits
    p["credit_share"] = p.net_advances / sysd.system_credit
    p.index.name = "period"
    p.round(6).to_csv(T / "hdfc_quarterly_panel.csv")
    seg = pd.read_csv(I / "hdfc_ir26_segments.csv")
    s = seg[seg.segment.isin(["treasury", "retail", "wholesale", "other"])].pivot_table(index=["fy", "segment"], columns="metric", values="value")
    s["pretax_return_on_assets"] = s.segment_result / s.segment_assets
    s["provisions_to_assets"] = s.segment_provisions / s.segment_assets
    s["share_of_assets"] = s.segment_assets / s.groupby(level="fy").segment_assets.transform("sum")
    s.round(6).to_csv(T / "hdfc_segments.csv")
    print(s[["pretax_return_on_assets", "provisions_to_assets", "share_of_assets"]].round(4).to_string())
    print(p[["nim", "casa_ratio", "cd_ratio", "bor_share_funding", "cost_of_funds", "slippage_ratio_ann", "credit_cost_bp", "lcr_avg", "cet1", "deposit_share", "credit_share"]]
          .round(3).to_string())


if __name__ == "__main__":
    main()
