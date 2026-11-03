"""Flip the Dashboard scenario selector, recalculate headlessly and export every labelled output to JSON.
Deck and memo numbers are read from this file, so each one traces to a model cell."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "models/HDFC_RoA_Path_FY29.xlsx"
SHEETS = ["Model", "Levers", "Valuation", "Fees", "ALM", "Opex_Credit", "Peers", "Margin", "Capital", "Checks"]


def main():
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for scn in ["Base", "Upside", "Downside"]:
            wb = openpyxl.load_workbook(SRC); wb["Dashboard"]["E5"].value = scn
            x = Path(tmp) / f"scn_{scn}.xlsx"; wb.save(x)
            subprocess.run([str(ROOT / "pipeline/recalc.sh"), str(x), tmp + "/o", tmp + "/p"], check=True)
            r = openpyxl.load_workbook(Path(tmp) / "o" / x.name, data_only=True)
            d = {}
            for name in SHEETS:
                for row in r[name].iter_rows(values_only=True):
                    if isinstance(row[1], str) and any(isinstance(v, (int, float)) for v in row[2:14]):
                        d[f"{name}|{row[1]}"] = list(row[2:14])
            out[scn] = d
    (ROOT / "data/tidy/hdfc_model_outputs.json").write_text(json.dumps(out, indent=0, default=str))
    print("exported", {k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    sys.exit(main())
