"""Harvest Screener.in standalone tables + concall document links for the peer set.

Usage: python -I pipeline/screener.py [SYMBOL ...]
Outputs:
  data/raw/screener/<SYM>_tables.csv   long table: symbol, section, line_item, period, value
  data/raw/screener/<SYM>_docs.csv     concall docs: symbol, period, kind, url
Polite: one request every 3 s, cached HTML in data/raw/screener/cache/ (gitignored).
Screener is a secondary aggregator; every figure is tied out against company filings in checks.py.
"""
from __future__ import annotations

import csv
import html as htmllib
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "screener"
CACHE = OUT / "cache"
UA = "Mozilla/5.0 (portfolio-research; github.com/DogInfantry)"
PEERS = ["SBIN", "HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK"]
SECTIONS = ["quarters", "profit-loss", "balance-sheet", "ratios"]
_last = [0.0]


def get(url: str, cache_name: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    cp = CACHE / cache_name
    if cp.exists():
        return cp.read_text()
    wait = 3 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8", "replace")
    _last[0] = time.time()
    cp.write_text(text)
    return text


def clean(cell: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", cell))).replace("+", "").strip()


def to_num(s: str):
    s = s.replace(",", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse_section(page: str, sec: str) -> list[tuple[str, str, float]]:
    i = page.find(f'id="{sec}"')
    if i < 0:
        return []
    block = page[i:]
    block = block[: block.find("</table>")]
    heads = [clean(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", block, re.S)]
    periods = heads[1:]
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", block, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 2:
            continue
        item = clean(tds[0])
        for p, v in zip(periods, tds[1:]):
            n = to_num(clean(v))
            if n is not None:
                rows.append((item, p, n))
    return rows


def parse_docs(page: str) -> list[tuple[str, str, str]]:
    i = page.find("Concalls")
    if i < 0:
        return []
    block = page[i: i + 40000]
    block = block[: block.find("</ul>")] if "</ul>" in block else block
    out = []
    for li in re.findall(r"<li[^>]*>(.*?)</li>", block, re.S):
        m = re.search(r"([A-Z][a-z]{2} \d{4})", clean(li))
        if not m:
            continue
        for href, label in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', li, re.S):
            kind = clean(label)
            if kind in {"Transcript", "PPT", "REC", "Notes"}:
                out.append((m.group(1), kind, htmllib.unescape(href)))
    return out


def harvest(sym: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    page = get(f"https://www.screener.in/company/{sym}/", f"{sym}.html")
    if "View Consolidated" not in page:
        print(f"WARN {sym}: page does not look standalone")
    with (OUT / f"{sym}_tables.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symbol", "section", "line_item", "period", "value"])
        n = 0
        for sec in SECTIONS:
            for item, period, val in parse_section(page, sec):
                w.writerow([sym, sec, item, period, val])
                n += 1
    docs = parse_docs(page)
    with (OUT / f"{sym}_docs.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symbol", "period", "kind", "url"])
        w.writerows([(sym, *d) for d in docs])
    print(f"ok {sym}: {n} values, {len(docs)} docs")


if __name__ == "__main__":
    for s in sys.argv[1:] or PEERS:
        harvest(s)
