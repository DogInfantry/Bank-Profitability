"""Funding-cost beta for HDFC Bank: how much of a repo move passes into its cost of funds, and how fast.

Annual cost of funds FY16-FY26 = interest expended / average (deposits + borrowings), Screener standalone (tied to IR26).
Fiscal-year average repo (time-weighted, April-March) from data/inputs/rbi_repo_history.csv (RBI Bank Rate less the MSF spread).
OLS: d(cost of funds)_t = a + b0 * d(repo)_t + b1 * d(repo)_t-1 + c * merger_FY24 + e.  Long-run beta = b0 + b1.
Ten annual observations: the result is a range-finder for the model's beta input, not a precise estimate.
Output: data/tidy/hdfc_deposit_beta.csv (coefficients, standard errors, fit) and hdfc_cost_of_funds.csv (the series).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
I, T, S = ROOT / "data" / "inputs", ROOT / "data" / "tidy", ROOT / "data" / "raw" / "screener"


def fy_avg_repo() -> pd.Series:
    r = pd.read_csv(I / "rbi_repo_history.csv", parse_dates=["effective_month"]).sort_values("effective_month")
    months = pd.date_range("2012-02-01", "2026-09-01", freq="MS")
    m = pd.Series(np.nan, index=months)
    for _, x in r.iterrows():
        m[m.index >= x.effective_month] = x.repo_pct
    fy = m.groupby(lambda d: d.year + (1 if d.month >= 4 else 0)).agg(["mean", "count"])
    return fy[fy["count"] == 12]["mean"]          # complete fiscal years only; index = FY end year


def cost_of_funds() -> pd.DataFrame:
    t = pd.read_csv(S / "HDFCBANK_tables.csv")
    pick = lambda sec, item: t[(t.section == sec) & (t.line_item == item) & t.period.str.startswith("Mar")].set_index("period").value  # noqa: E731
    d = pd.DataFrame({"interest": pick("profit-loss", "Interest"), "deposits": pick("balance-sheet", "Deposits"), "borrowings": pick("balance-sheet", "Borrowing")})
    d.index = [int(p.split()[1]) for p in d.index]
    d = d.sort_index()
    d["funding"] = d.deposits + d.borrowings
    d["cost_of_funds_pct"] = 100 * d.interest / ((d.funding + d.funding.shift()) / 2)
    return d.dropna()


def main():
    cf = cost_of_funds()
    rp = fy_avg_repo()
    df = cf.join(rp.rename("repo_avg_pct"), how="inner")
    df["d_cof"] = df.cost_of_funds_pct.diff()
    df["d_repo"] = df.repo_avg_pct.diff()
    df["d_repo_l1"] = df.d_repo.shift()
    df["merger"] = (df.index == 2024).astype(float)
    est = df.dropna()
    X = np.column_stack([np.ones(len(est)), est.d_repo, est.d_repo_l1, est.merger])
    y = est.d_cof.values
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ b
    dof = len(y) - X.shape[1]
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r2 = 1 - resid @ resid / ((y - y.mean()) @ (y - y.mean()))
    lr = b[1] + b[2]
    lr_se = np.sqrt(s2 * np.array([0, 1, 1, 0]) @ np.linalg.inv(X.T @ X) @ np.array([0, 1, 1, 0]))
    names = ["intercept", "beta_same_year", "beta_lag_1y", "merger_FY24"]
    out = pd.DataFrame({"term": names + ["long_run_beta"], "estimate": list(b) + [lr], "std_error": list(se) + [lr_se]})
    out["observations"] = len(y); out["r_squared"] = r2
    out["fy_range"] = f"FY{est.index.min() % 100:02d}-FY{est.index.max() % 100:02d} (changes)"
    out["source"] = "Screener standalone (Interest; Deposits; Borrowing) tied to IR26; repo from RBI Bank Rate via FactIQ"
    out.to_csv(T / "hdfc_deposit_beta.csv", index=False)
    df.reset_index(names="fy_end").to_csv(T / "hdfc_cost_of_funds.csv", index=False)
    print(df[["cost_of_funds_pct", "repo_avg_pct", "d_cof", "d_repo"]].round(2).to_string())
    print(out[["term", "estimate", "std_error"]].round(3).to_string(index=False), f"\nR2 {r2:.2f}, n={len(y)}")


if __name__ == "__main__":
    main()
