"""Download public primary sources into data/raw/<bucket>/ and record a manifest.

Usage: python -I pipeline/fetch.py [--only KEY ...]
Every file gets a row in data/raw/manifest.csv: key, bucket, url, path, sha256, bytes, fetched_utc, status.
Files already present with a matching manifest row are skipped (idempotent re-runs).
"""
from __future__ import annotations

import csv
import hashlib
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "manifest.csv"
UA = "Mozilla/5.0 (portfolio-research; contact via github.com/DogInfantry)"

# key, bucket, filename, url
SOURCES = [
    ("sbi_q4fy26_pr", "ir", "SBI_Q4FY26_press_release.pdf",
     "https://sbi.bank.in/documents/17836/53469043/SBI+Press+Release+Q4FY26.pdf"),
    ("hdfc_q4fy26_pres", "ir", "HDFC_Q4FY26_earnings_presentation.pdf",
     "https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/pdf/about-us/financial-results/2025-2026/quarter-4/q4fy26-earnings-presentation.pdf"),
    ("hdfc_q2fy27_pres", "ir", "HDFC_Q2FY27_earnings_presentation.pdf",
     "https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/pdf/about-us/financial-results/2026-2027/quarter-2/q2fy27-earnings-presentation.pdf"),
    ("icici_q4fy26_pres", "ir", "ICICI_Q4FY26_investor_presentation.pdf",
     "https://www.icici.bank.in/content/dam/icicibank/india/managed-assets/docs/about-us/2026/2026-04-Q4-2026-investor-presentation.pdf"),
    ("kotak_q4fy26_pr", "ir", "Kotak_Q4FY26_press_release.pdf",
     "https://www.kotak.bank.in/content/dam/Kotak/investor-relation/Financial-Result/QuarterlyReport/FY-2026/q4/PressRelease/Q4FY26_Press-Release.pdf"),
    ("irdai_ar_2024_25", "web", "IRDAI_Annual_Report_2024-25.pdf",
     "https://lifeinscouncil.org/component/IRDAI%20Annual%20Report%202024-25.pdf"),
    ("dfs_mdr_faq", "web", "DFS_UPI_MDR_FAQ_Sep2026.pdf",
     "https://financialservices.gov.in/sites/default/files/2026-09/FAQs---Merchant-Discount-Rate--MDR--on-Select-UPI--P2M--Transactions_0.pdf"),
    ("public_apis_readme", "web", "public_apis_README.md",
     "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open() as f:
        return {r["key"]: r for r in csv.DictReader(f)}


def save_manifest(rows: dict[str, dict]) -> None:
    fields = ["key", "bucket", "url", "path", "sha256", "bytes", "fetched_utc", "status"]
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for k in sorted(rows):
            w.writerow({x: rows[k].get(x, "") for x in fields})


def download(url: str, dest: Path, tries: int = 3) -> None:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r, dest.open("wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            return
        except Exception as e:  # noqa: BLE001 - report and retry
            last = e
            time.sleep(2 ** (i + 1))
    raise RuntimeError(f"{url}: {last}")


def register(rows: dict, key: str, bucket: str, url: str, dest: Path, status: str) -> None:
    rows[key] = {
        "key": key, "bucket": bucket, "url": url,
        "path": str(dest.relative_to(ROOT)),
        "sha256": sha256(dest) if dest.exists() else "",
        "bytes": dest.stat().st_size if dest.exists() else 0,
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
    }


def main(only: set[str] | None = None) -> None:
    rows = load_manifest()
    for key, bucket, name, url in SOURCES:
        if only and key not in only:
            continue
        dest = RAW / bucket / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and key in rows and rows[key].get("status") == "ok":
            print(f"skip  {key}")
            continue
        try:
            download(url, dest)
            register(rows, key, bucket, url, dest, "ok")
            print(f"ok    {key} ({dest.stat().st_size/1e6:.1f} MB)")
        except RuntimeError as e:
            register(rows, key, bucket, url, dest, "failed")
            print(f"FAIL  {key}: {e}")
    # register user-supplied manual files too, so every raw input is hashed
    for p in sorted((RAW / "manual").rglob("*")):
        if p.is_file():
            key = "manual_" + p.stem.lower().replace(" ", "_")
            register(rows, key, "manual", "user upload", p, "ok")
    save_manifest(rows)


if __name__ == "__main__":
    args = sys.argv[1:]
    main(set(args[1:]) if args[:1] == ["--only"] else None)
