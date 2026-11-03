"""Lint workbooks against the IB-hygiene standard used in this repo.

Fails (exit 1) on, for workbooks passed with --strict:
  * any font other than Garamond, or any italic font
  * merged cells
  * error values in the recalculated copy (#REF!, #DIV/0!, #VALUE!, Err:...)
  * numeric literals inside formulas other than 0, 1 and 2 (hard-codes belong on input rows)
  * a row whose formulas break pattern within the historical block (E-K) or the projection block (L-N)
Usage: python -I pipeline/xlsx_lint.py --strict models/HDFC_RoA_Path_FY29.xlsx [--advisory other.xlsx ...]
Recalculation uses pipeline/recalc.sh (LibreOffice headless).
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
from openpyxl.utils import column_index_from_string, get_column_letter

ROOT = Path(__file__).resolve().parents[1]
REF = re.compile(r"(\$?)([A-Z]{1,3})(\$?)(\d+)")
STR = re.compile(r'"[^"]*"')
SHEETREF = re.compile(r"'[^']*'!|[A-Za-z_][A-Za-z0-9_]*!")
NUMLIT = re.compile(r"(?<![A-Za-z0-9_$.])(\d+\.?\d*)(?![A-Za-z0-9_(])")
ALLOWED = {"0", "1", "2"}
HIST_COLS = [get_column_letter(i) for i in range(5, 12)]   # E..K
PROJ_COLS = [get_column_letter(i) for i in range(12, 15)]  # L..N


def relative(formula: str, col: str) -> str:
    """Express column references relative to the cell's own column (R1C1-style for columns)."""
    c0 = column_index_from_string(col)

    def sub(m):
        d1, c, d2, r = m.groups()
        cc = c if d1 else f"C[{column_index_from_string(c) - c0}]"
        return f"{cc}{d2}{r}"
    return REF.sub(sub, formula)


def literals(formula: str) -> list[str]:
    f = STR.sub("", formula)
    f = SHEETREF.sub("", f)
    f = REF.sub("", f)
    return [n for n in NUMLIT.findall(f) if n not in ALLOWED]


def lint(path: Path, strict: bool) -> list[str]:
    issues = []
    wb = openpyxl.load_workbook(path)
    for ws in wb.worksheets:
        if ws.merged_cells.ranges:
            issues.append(f"{ws.title}: merged cells {list(ws.merged_cells.ranges)[:3]}")
        for row in ws.iter_rows():
            for c in row:
                if c.value is None:
                    continue
                if c.font is not None:
                    if c.font.name not in ("Garamond",):
                        issues.append(f"{ws.title}!{c.coordinate}: font {c.font.name}")
                    if c.font.i:
                        issues.append(f"{ws.title}!{c.coordinate}: italic")
                if isinstance(c.value, str) and c.value.startswith("="):
                    lits = literals(c.value)
                    if lits:
                        issues.append(f"{ws.title}!{c.coordinate}: hard-coded {lits} in {c.value[:70]}")
        # row-pattern consistency on timeline sheets
        header = None
        for r in range(1, 12):
            vals = [ws.cell(r, j).value for j in range(5, 15)]
            if "FY27E" in vals:
                header = r; break
        if header:
            for r in range(header + 1, ws.max_row + 1):
                for block in (HIST_COLS, PROJ_COLS):
                    pats = {relative(ws[f"{col}{r}"].value, col) for col in block
                            if isinstance(ws[f"{col}{r}"].value, str) and ws[f"{col}{r}"].value.startswith("=")}
                    if len(pats) > 1:
                        issues.append(f"{ws.title} row {r} ({ws.cell(r, 2).value}): {len(pats)} formula patterns in {block[0]}-{block[-1]}")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([str(ROOT / "pipeline/recalc.sh"), str(path), tmp, tmp + "/p"], check=True)
        rc = openpyxl.load_workbook(Path(tmp) / path.name, data_only=True)
        for ws in rc.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str) and (c.value.startswith("#") and c.value.endswith(("!", "?", "A")) or c.value.startswith("Err:")):
                        issues.append(f"{ws.title}!{c.coordinate}: error value {c.value}")
    return issues


def main(argv):
    mode, failed = "--strict", False
    for a in argv:
        if a in ("--strict", "--advisory"):
            mode = a; continue
        issues = lint(Path(a), mode == "--strict")
        tag = "STRICT" if mode == "--strict" else "ADVISORY"
        print(f"{tag} {a}: {len(issues)} issue(s)")
        for i in issues[:25]:
            print("   ", i)
        if mode == "--strict" and issues:
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
