"""Quarterly KPI panel from HDFC Bank investor decks (data/raw/ir/HDFCBANK_<Q>_ppt.pdf, gitignored).

Run LOCALLY after `pipeline/fetch_docs.py --symbols HDFCBANK --kinds PPT`; CI uses the committed output.
  highlights page    NIM, NIM on interest-earning assets, GNPA, GNPA ex-agri, CET1, RoA (that quarter only)
  abridged balance   net advances, deposits, borrowings, total assets, equity (INR bn, every dated column)
  balance-sheet mix  CASA ratio and borrowings share (any deck); advances mix only from the FY26 "new format"
                     tables (from FY26 the bank reclassified segments: Mar-25 retail is 50% old basis, 55% new)
A value is taken from its own quarter's deck when that deck reports it, otherwise from the latest deck that
restates it; the note says which. Chart-only series (LCR, NSFR, yields, cost of funds, slippages) are read
by eye into data/inputs/hdfc_quarterly_chart_reads.csv. Output: data/inputs/hdfc_quarterly_kpis.csv
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
IR, OUT = ROOT / "data/raw/ir", ROOT / "data/inputs/hdfc_quarterly_kpis.csv"
NUM = r"\(?[\d,]+(?:\.\d+)?\)?"
DATE = r"(?:Q[1-4]FY\d{2}|(?:Mar|Jun|Sep|Dec)['’]\d{2})"
SCALARS = {  # highlights: metric -> (regex, unit)
    "nim": (r"Net interest margin\s*\^?\s*(?:\(NIM\))?\s*of\s*(\d\.\d{1,2})%", "%"),
    "nim_iea": (r"Net interest margin \(IEA\) of (\d\.\d{2})%", "%"),
    "gnpa": (r"(?:Gross NPA|GNPA ratio) at (\d\.\d{2})%", "%"),
    "gnpa_ex_agri": (r"ex-agri at (\d\.\d{2})%", "%"),
    "cet1": (r"CET1 at (\d+\.\d)%", "%"),
    "roa": (r"Return on assets of (\d\.\d+)%", "%"),
}
BS = {"Net Advances": "net_advances", "Loans and advances": "net_advances", "Deposits": "deposits", "Borrowings": "borrowings",
      "Total assets": "total_assets", "Equity & reserves": "equity"}
MIX = {"Retail": "mix_retail", "Mortgage": "mix_mortgage", "Small and mid-market": "mix_smm", "Corporate & other wholesale": "mix_wholesale"}
ORDER = [f"Q{q}FY{y}" for y in range(23, 28) for q in (1, 2, 3, 4)]


def quarter(label: str) -> str:
    if label.startswith("Q"):
        return label
    mon, yy = label[:3], int(label[-2:])
    return {"Mar": f"Q4FY{yy}", "Jun": f"Q1FY{yy + 1}", "Sep": f"Q2FY{yy + 1}", "Dec": f"Q3FY{yy + 1}"}[mon]


def num(s: str) -> float:
    v = float(s.strip("()").replace(",", ""))
    return -v if s.startswith("(") else v


def candidates(pdf: Path) -> list[dict]:
    deck = pdf.stem.split("_")[1]
    out = []
    add = lambda per, m, v, u, p: out.append(dict(period=per, metric=m, value=v, unit=u, deck=deck, page=p, source_file=pdf.name))  # noqa: E731
    with pdfplumber.open(pdf) as doc:
        pages = [(i, pg.extract_text() or "") for i, pg in enumerate(doc.pages, 1)]
    for m, (rx, unit) in SCALARS.items():
        hit = next(((i, h) for i, t in pages[:6] if (h := re.search(rx, t))), None)
        if hit:
            add(deck, m, float(hit[1].group(1)), unit, hit[0])

    def table(i: int, lines: list[str], hdr_rx: str, rows: dict, unit: str, pct: bool):
        hdr = next((ln for ln in lines if re.match(hdr_rx, ln)), None)
        if not hdr:
            return
        dates = [quarter(d) for d in re.findall(DATE, hdr)]
        for j, line in enumerate(lines):
            text = line.lstrip("* ")
            for lab, m in rows.items():
                if text.startswith(lab + " ") and re.match(r"^[\d(]", text[len(lab) + 1:]):
                    vals = re.findall(r"(\d+)%", text) if pct else re.findall(NUM, text[len(lab):])
                    for d, v in zip(dates, vals):
                        add(d, m, float(v) if pct else num(v), unit, i)
            if pct and text.startswith("Borrowings as a % of Total"):
                vals = re.findall(r"(\d+)%", text + " " + (lines[j + 1] if j + 1 < len(lines) else ""))
                for d, v in zip(dates, vals):
                    add(d, "borrowings_share_liab", float(v), "%", i)

    for i, t in pages:
        lines = t.splitlines()
        if "Balance sheet (" in t:
            table(i, lines, r"^Balance sheet \(", BS, "INR bn", pct=False)
        if "CASA ratio" in t and re.search(r"Particulars|Q[1-4] (?:Mar|Jun|Sep|Dec)", t):
            table(i, lines, rf"^(?:Particulars|.*{DATE} .*{DATE})", {"CASA ratio": "casa_ratio"}, "%", pct=True)
            if "Small and mid-market" in t:  # new-format advances mix only
                table(i, lines, r"^Particulars", MIX, "%", pct=True)
    return out


def main() -> None:
    cands = [c for pdf in sorted(IR.glob("HDFCBANK_*_ppt.pdf")) for c in candidates(pdf)]
    best = {}
    for c in cands:  # own-quarter deck wins; otherwise the latest deck that restates the value
        k = (c["period"], c["metric"])
        rank = (c["deck"] == c["period"], ORDER.index(c["deck"]))
        if k not in best or rank > best[k][0]:
            best[k] = (rank, c)
    rows = []
    for (per, m), (_, c) in sorted(best.items(), key=lambda kv: (ORDER.index(kv[0][0]) if kv[0][0] in ORDER else -1, kv[0][1])):
        note = "own-quarter deck" if c["deck"] == per else f"restated in {c['deck']} deck"
        rows.append(dict(bank="HDFCBANK", period=per, metric=m, value=c["value"], unit=c["unit"],
                         source_file=c["source_file"], page=c["page"], note=note))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["bank", "period", "metric", "value", "unit", "source_file", "page", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} rows")


if __name__ == "__main__":
    main()
