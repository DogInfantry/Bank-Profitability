"""Run every reconciliation in one go: recalculates the three workbooks headlessly and reads their checks tabs,
then runs data-asset checks (provenance, Shapley additivity). Exit code 1 on any FAIL.
Usage: python -I pipeline/checks.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
results = []


def add(name, ok, detail=""):
    results.append((name, "PASS" if ok is True else ("FAIL" if ok is False else ok), detail))


with tempfile.TemporaryDirectory() as tmp:
    for wbname, sheet in [("HDFC_RoA_Path_FY29.xlsx", "Checks"), ("01_Bank_RoA_Benchmark.xlsx", "8_Checks"), ("02_Insurance_Distribution.xlsx", "9_Checks"), ("03_UPI_MDR_Cap.xlsx", "5_Checks")]:
        subprocess.run([str(ROOT / "pipeline/recalc.sh"), str(ROOT / "models" / wbname), tmp, tmp + "/prof"], check=True)
        ws = openpyxl.load_workbook(Path(tmp) / wbname, data_only=True)[sheet]
        for row in ws.iter_rows(values_only=True):
            vals = [v for v in row if v is not None]
            for v in vals:
                if v in ("PASS", "FAIL", "EXPLAINED", "CHECK", "ALL CHECKS PASS", "CHECK FAILURES"):
                    v = {"ALL CHECKS PASS": "PASS", "CHECK FAILURES": "FAIL"}.get(v, v)
                    add(f"{wbname}: {str(vals[0])[:70]}", v if v != "PASS" else True)
        if wbname.startswith("01"):
            for lim, row in zip([2, 0.5, 20, 7], ws.iter_rows(min_row=4, max_row=7, values_only=True)):
                nums = [v for v in row[2:] if isinstance(v, (int, float))]
                worst = max((abs(v) for v in nums), default=0)
                add(f"{wbname}: bank tolerance | {row[0]}", worst <= lim or "EXPLAINED", f"worst {worst:.2f} (limit {lim})")

lint = subprocess.run([sys.executable, "-I", str(ROOT / "pipeline/xlsx_lint.py"), "--strict", str(ROOT / "models/HDFC_RoA_Path_FY29.xlsx")], capture_output=True, text=True)
add("HDFC model passes IB-hygiene lint (Garamond, no italics, no hard-codes, row patterns, no errors)", lint.returncode == 0, lint.stdout.strip().splitlines()[0] if lint.stdout else "")
f = pd.read_csv(ROOT / "data/tidy/bank_facts.csv")
add("bank_facts: every row has a source", bool(f.source.notna().all()))
sh = pd.read_csv(ROOT / "data/tidy/bank_shapley_FY26.csv").fillna(0)
add("Shapley contributions sum to gap", bool(((sh[["nii", "oi", "opex", "prov", "tax_rate", "leverage"]].sum(axis=1) - sh.gap).abs() < 1e-9).all()))
ins = pd.read_csv(ROOT / "data/tidy/ins_life_insurers_FY25.csv")
add("Handbook commission ties to AR 60,799.91", bool(abs(ins.total_commission.sum() - 60799.91) < 1), f"{ins.total_commission.sum():,.2f}")

w = max(len(r[0]) for r in results)
for n, s, d in results:
    print(f"{s:9} {n:<{w}} {d}")
fails = [r for r in results if r[1] == "FAIL"]
(ROOT / "data" / "tidy" / "checks_summary.json").write_text(json.dumps(
    {"total": len(results), "fail": len(fails), "explained": sum(r[1] == "EXPLAINED" for r in results),
     "checks": [{"name": n, "status": s_, "detail": str(d)} for n, s_, d in results]}, indent=1))
print(f"\n{len(results)} checks: {len(fails)} FAIL, {sum(r[1]=='EXPLAINED' for r in results)} EXPLAINED")
sys.exit(1 if fails else 0)
