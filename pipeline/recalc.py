"""Recalculate an xlsxwriter workbook with headless LibreOffice so cached values exist (for QA reads).
Works on Linux (CI) and Windows. Usage: python -I pipeline/recalc.py <in.xlsx> <outdir> [profile_dir]
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

XCU = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""
WIN_DEFAULT = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")


def office() -> str:
    exe = shutil.which("libreoffice") or shutil.which("soffice") or (str(WIN_DEFAULT) if WIN_DEFAULT.exists() else None)
    if not exe:
        sys.exit("recalc: LibreOffice not found (libreoffice or soffice on PATH)")
    return exe


def main(argv: list[str]) -> None:
    src, out = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    prof = Path(argv[2] if len(argv) > 2 else Path(tempfile.gettempdir()) / "lo_recalc_profile").resolve()
    (prof / "user").mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    (prof / "user" / "registrymodifications.xcu").write_text(XCU, encoding="utf-8")
    subprocess.run([office(), f"-env:UserInstallation={prof.as_uri()}", "--headless", "--calc", "--convert-to", "xlsx",
                    "--outdir", str(out), str(src)], check=True, timeout=240, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main(sys.argv[1:])
