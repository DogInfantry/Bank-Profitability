"""HDFC Bank's own RoA walk over time: what the merger changed, by factor.

Order-independent (Shapley) attribution of the change in RoA between periods, reusing pipeline/shapley.py.
Periods: FY23 (last pre-merger year), FY24 (merger year, 1 July 2023), FY26, Q2 FY27 annualised.
FY figures from HDFC Bank IR26 p234 (ten-year highlights, standalone); Q2 FY27 from data/tidy/bank_model_inputs.csv.
Output: data/tidy/hdfc_roa_walk.csv (bp of RoA per factor; each step sums exactly to the RoA change).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shapley import FACTORS_ROA, bank_vector, roa, shapley  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
I, T = ROOT / "data" / "inputs", ROOT / "data" / "tidy"


def fy_row(h: pd.DataFrame, fy: str, prev: str) -> dict:
    g = lambda m, c: float(h.loc[m, c])  # noqa: E731
    return dict(annualise=1, nii=g("nii", fy), other_income=g("other_income", fy), opex=g("opex", fy),
                provisions=g("provisions_total", fy), tax=g("tax", fy), pbt=g("pbt", fy),
                assets_open=g("total_assets", prev), assets_close=g("total_assets", fy),
                equity_open=g("equity", prev), equity_close=g("equity", fy))


def periods() -> dict[str, dict]:
    h = pd.read_csv(I / "hdfc_10yr_highlights.csv").set_index("metric")
    out = {fy: bank_vector(fy_row(h, fy, prev)) for fy, prev in (("FY23", "FY22"), ("FY24", "FY23"), ("FY26", "FY25"))}
    w = pd.read_csv(T / "bank_model_inputs.csv")
    q = w[(w.bank == "HDFCBANK") & (w.period == "Q2FY27")].iloc[0].to_dict()
    out["Q2 FY27"] = bank_vector(q)
    return out


def main():
    p = periods()
    rows = []
    for a, b in (("FY23", "FY24"), ("FY24", "FY26"), ("FY26", "Q2 FY27"), ("FY23", "Q2 FY27")):
        c = shapley(roa, p[a], p[b], FACTORS_ROA)
        chg = roa(p[b]) - roa(p[a])
        assert abs(sum(c.values()) - chg) < 1e-12
        rows.append(dict(step=f"{a} to {b}", roa_from_pct=roa(p[a]), roa_to_pct=roa(p[b]), change_bp=100 * chg,
                         **{f"{k}_bp": 100 * v for k, v in c.items()}))
    out = pd.DataFrame(rows)
    out["source"] = "HDFC Bank IR26 p234 (FY); Screener standalone Q2 FY27 tied to the Q2 FY27 presentation; Shapley attribution"
    out.to_csv(T / "hdfc_roa_walk.csv", index=False)
    print(out.drop(columns="source").round(1).to_string(index=False))


if __name__ == "__main__":
    main()
