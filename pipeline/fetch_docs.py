"""Download concall PPTs and transcripts harvested by screener.py.

Maps Screener's call month to the fiscal quarter reported (Indian FY ends March):
  Jan/Feb -> Q3, Apr/May -> Q4, Jul/Aug -> Q1 of next FY, Oct/Nov -> Q2 of next FY.
Usage: python -I pipeline/fetch_docs.py [--since 2025-07] [--ppt-quarters Q4FY26,Q2FY27] [--symbols HDFCBANK] [--kinds PPT]
Writes data/raw/ir/<SYM>_<QTR>_<kind>.pdf and registers each in data/raw/manifest.csv.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime

from fetch import RAW, download, load_manifest, register, save_manifest

MONTH_Q = {1: 3, 2: 3, 4: 4, 5: 4, 7: 1, 8: 1, 10: 2, 11: 2}


def fiscal_quarter(period: str) -> str | None:
    d = datetime.strptime(period, "%b %Y")
    q = MONTH_Q.get(d.month)
    if q is None:
        return None
    fy = d.year + 1 if q in (1, 2) else d.year
    return f"Q{q}FY{str(fy)[-2:]}"


def candidates(url: str) -> list[str]:
    """BSE's AnnPdfOpen viewer sometimes serves an HTML shell; the same file lives under AttachHis."""
    out = [url]
    if "AnnPdfOpen.aspx?Pname=" in url:
        out.append("https://www.bseindia.com/xml-data/corpfiling/AttachHis/" + url.split("Pname=")[1])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-07")
    ap.add_argument("--ppt-quarters", default="Q4FY26,Q2FY27")
    ap.add_argument("--symbols", default="", help="comma-separated, e.g. HDFCBANK (default: every bank)")
    ap.add_argument("--kinds", default="PPT,Transcript")
    a = ap.parse_args()
    since = datetime.strptime(a.since, "%Y-%m")
    ppt_q = set(a.ppt_quarters.split(","))
    syms, kinds = set(filter(None, a.symbols.split(","))), set(a.kinds.split(","))
    rows = load_manifest()
    moved = {r["key"]: r["url"] for r in csv.DictReader((RAW.parent / "inputs/ir_url_overrides.csv").open())}
    seen = set()
    for f in sorted((RAW / "screener").glob("*_docs.csv")):
        if syms and f.name.removesuffix("_docs.csv") not in syms:
            continue
        for r in csv.DictReader(f.open()):
            if datetime.strptime(r["period"], "%b %Y") < since:
                continue
            q = fiscal_quarter(r["period"])
            kind = r["kind"]
            if q is None or kind not in kinds:
                continue
            if kind == "PPT" and q not in ppt_q:
                continue
            key = f"{r['symbol']}_{q}_{kind.lower()}"
            if key in seen:  # first link per bank-quarter-kind wins
                continue
            seen.add(key)
            r["url"] = moved.get(key, r["url"])
            dest = RAW / "ir" / f"{key}.pdf"
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and rows.get(key, {}).get("status") == "ok":
                continue
            try:
                ok = False
                for url in candidates(r["url"]):
                    download(url, dest)
                    if dest.read_bytes()[:5] == b"%PDF-":
                        ok = True
                        r["url"] = url
                        break
                register(rows, key, "ir", r["url"], dest, "ok" if ok else "not_pdf")
                print(f"{'ok ' if ok else 'BAD'} {key} {dest.stat().st_size/1e6:.1f} MB")
            except RuntimeError as e:
                register(rows, key, "ir", r["url"], dest, "failed")
                print(f"FAIL {key}: {e}")
    save_manifest(rows)


if __name__ == "__main__":
    main()
