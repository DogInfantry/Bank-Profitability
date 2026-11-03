"""Order-independent (Shapley) attribution of RoA and RoE gaps between two banks.

RoA = (NII + OI - Opex - Prov) / A  x  (1 - t)          factors: nii, oi, opex, prov, tax_rate
RoE = RoA x Leverage (A/E)                              adds factor: leverage

A sequential bridge assigns the tax-rate and leverage interaction terms to whichever factor is
moved last, so its answer depends on the order chosen. Shapley averages each factor's marginal
contribution over every ordering (2^n subsets), which is order-independent and sums exactly to the gap.
"""
from __future__ import annotations

from itertools import combinations
from math import factorial

FACTORS_ROA = ["nii", "oi", "opex", "prov", "tax_rate"]
FACTORS_ROE = FACTORS_ROA + ["leverage"]


def roa(x: dict) -> float:
    return (x["nii"] + x["oi"] - x["opex"] - x["prov"]) * (1 - x["tax_rate"])


def roe(x: dict) -> float:
    return roa(x) * x["leverage"]


def shapley(f, base: dict, target: dict, factors: list[str]) -> dict[str, float]:
    """Contribution of each factor to f(target) - f(base)."""
    n = len(factors)
    out = {k: 0.0 for k in factors}
    for k in factors:
        others = [o for o in factors if o != k]
        for r in range(n):
            w = factorial(r) * factorial(n - r - 1) / factorial(n)
            for subset in combinations(others, r):
                x = {o: (target[o] if o in subset else base[o]) for o in factors}
                without = f(x)
                x[k] = target[k]
                out[k] += w * (f(x) - without)
    return out


def bank_vector(row: dict) -> dict:
    """row: one bank-period from bank_model_inputs.csv (INR cr). Returns % of avg assets."""
    avg_a = (row["assets_open"] + row["assets_close"]) / 2
    avg_e = (row["equity_open"] + row["equity_close"]) / 2
    k = 100 * row["annualise"] / avg_a
    return dict(nii=row["nii"] * k, oi=row["other_income"] * k, opex=row["opex"] * k,
                prov=row["provisions"] * k, tax_rate=row["tax"] / row["pbt"], leverage=avg_a / avg_e)


if __name__ == "__main__":
    from pathlib import Path

    import pandas as pd

    root = Path(__file__).resolve().parents[1]
    w = pd.read_csv(root / "data" / "tidy" / "bank_model_inputs.csv")
    fy = {r.bank: bank_vector(r._asdict()) for r in w[w.period == "FY26"].itertuples()}
    rows = []
    for bench in ["ICICIBANK", "HDFCBANK"]:
        for b in fy:
            if b == bench:
                continue
            for metric, f, facs in [("RoA", roa, FACTORS_ROA), ("RoE", roe, FACTORS_ROE)]:
                c = shapley(f, fy[b], fy[bench], facs)
                gap = f(fy[bench]) - f(fy[b])
                assert abs(sum(c.values()) - gap) < 1e-9
                rows.append(dict(metric=metric, bank=b, benchmark=bench, gap=gap, **c))
    out = pd.DataFrame(rows)
    out.to_csv(root / "data" / "tidy" / "bank_shapley_FY26.csv", index=False)
    print(out[out.metric == "RoA"].round(3).to_string(index=False))
