import subprocess
import sys

import openpyxl


def test_hdfc_model_passes_strict_lint(root):
    r = subprocess.run([sys.executable, "-I", str(root / "pipeline/xlsx_lint.py"), "--strict", str(root / "models/HDFC_RoA_Path_FY29.xlsx")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_sector_workbooks_garamond_no_italics(root):
    for f in sorted((root / "models").glob("0*.xlsx")):
        wb = openpyxl.load_workbook(f)
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if c.value is not None:
                        assert c.font.name == "Garamond" and not c.font.i, f"{f.name} {ws.title}!{c.coordinate}"
