"""One-at-a-time sensitivity (tornado) of FY29E RoA on the live Excel model.

For each driver, overwrite its Base input row (Inputs tab, FY27E-FY29E) with a low and a high value, recalculate the
whole workbook headlessly (LibreOffice) and read Model RoA FY29E. Ranges are the element-wise min and max across the
Base, Upside and Downside rows already on the Inputs tab, so no new assumptions are introduced. One exception: the
deposit beta range runs from 0.25 to the long-run beta estimated in pipeline/deposit_beta.py.
Output: data/tidy/hdfc_tornado.csv. The model build writes it to a Tornado tab (values, labelled as such).
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "models" / "HDFC_RoA_Path_FY29.xlsx"
PROJ = ["L", "M", "N"]
DRIVERS = [
    "Policy repo rate, fiscal-year average", "Yield beta: loans", "Cost beta: deposits", "Advances growth", "Deposit growth",
    "CASA ratio, year end", "Share of maturing borrowings retired", "Core fee income growth", "Operating expense growth",
    "Credit cost", "IRDAI cap severity on bank fees", "Treasury and other non-fee income", "Premium over the system fresh rate",
]


def find_rows(ws, label):
    rows = {}
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, 2).value
        if isinstance(v, str) and v.startswith(label + ": "):
            rows[v.split(": ")[-1]] = r
    return rows


def roa_fy29(path: Path, tmp: str) -> float:
    subprocess.run([sys.executable, "-I", str(ROOT / "pipeline/recalc.py"), str(path), tmp + "/o", tmp + "/p"], check=True, capture_output=True)
    ws = openpyxl.load_workbook(Path(tmp) / "o" / path.name, data_only=True)["Model"]
    for r in range(1, ws.max_row + 1):
        if ws.cell(r, 2).value == "Return on average assets":
            return float(ws[f"N{r}"].value)
    raise KeyError("RoA row not found")


def main():
    beta = pd.read_csv(ROOT / "data" / "tidy" / "hdfc_deposit_beta.csv").set_index("term").estimate
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        base_path = Path(tmp) / "base.xlsx"
        wb = openpyxl.load_workbook(SRC); wb["Dashboard"]["E5"].value = "Base"; wb.save(base_path)
        base = roa_fy29(base_path, tmp)
        for d in DRIVERS:
            wb = openpyxl.load_workbook(SRC); wb["Dashboard"]["E5"].value = "Base"
            ws = wb["Inputs"]; rows = find_rows(ws, d)
            vals = {k: [float(ws[f"{c}{r}"].value) for c in PROJ] for k, r in rows.items() if k in ("Base", "Upside", "Downside")}
            lo = [min(v[i] for v in vals.values()) for i in range(3)]
            hi = [max(v[i] for v in vals.values()) for i in range(3)]
            note = "min / max of scenario inputs"
            if d == "Cost beta: deposits":
                lo, hi = [0.25] * 3, [round(float(beta["long_run_beta"]), 2)] * 3
                note = "0.25 to the regression long-run beta"
            res = {}
            for tag, vv in (("low", lo), ("high", hi)):
                for c, x in zip(PROJ, vv):
                    ws[f"{c}{rows['Base']}"].value = x
                pth = Path(tmp) / f"t_{len(out)}_{tag}.xlsx"; wb.save(pth)
                res[tag] = roa_fy29(pth, tmp)
            out.append(dict(driver=d, low_input_fy29=lo[2], high_input_fy29=hi[2], base_input_fy29=vals["Base"][2],
                            roa_low_input_pct=100 * res["low"], roa_high_input_pct=100 * res["high"], roa_base_pct=100 * base,
                            swing_bp=abs(res["high"] - res["low"]) * 1e4, range_basis=note))
            print(f"{d:45s} {100 * res['low']:.3f} {100 * res['high']:.3f}")
    df = pd.DataFrame(out).sort_values("swing_bp", ascending=False)
    df["source"] = "pipeline/tornado.py: LibreOffice recalculation of models/HDFC_RoA_Path_FY29.xlsx, Base scenario"
    df.to_csv(ROOT / "data" / "tidy" / "hdfc_tornado.csv", index=False)
    print(df[["driver", "swing_bp"]].round(1).to_string(index=False))


if __name__ == "__main__":
    main()
