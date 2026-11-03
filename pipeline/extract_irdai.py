"""Extract insurer-wise FY25 life data from the IRDAI Handbook on Indian Insurance Statistics 2024-25.

Tables used (Part I / Part V workbooks, user-uploaded; hashes in data/raw/manifest.csv):
  T2   Total premium of life insurers (insurer-wise, INR cr)
  T3   New business premium of life insurers
  T13  Linked and non-linked commission (total commission and % of total premium)
  T100 Channel-wise insurer-wise individual new business FY25 (policies, premium)
Output: data/tidy/ins_life_insurers_FY25.csv
"""
from __future__ import annotations

import difflib
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HB = ROOT / "data" / "raw" / "manual" / "irdai_handbook_2024_25"
CHANNELS = ["agents", "ca_banks", "ca_others", "brokers", "direct", "mi_agents", "csc",
            "web_aggregators", "imf", "online", "pos", "others", "total_indiv_nb"]


def rows(book: str, sheet: str) -> list[tuple]:
    wb = openpyxl.load_workbook(HB / book, read_only=True, data_only=True)
    return list(wb[sheet].iter_rows(values_only=True))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def insurer_rows(rs: list[tuple]):
    """Yield (sector, sno, name, row) for insurer rows; skips share/percentage rows."""
    sector = None
    for r in rs:
        lab = str(r[1]).strip() if len(r) > 1 and r[1] is not None else ""
        first = str(r[0]).strip() if r[0] is not None else ""
        if first.lower().startswith("public") or lab.lower().startswith("public sector"):
            sector = "Public"; continue
        if first.lower().startswith("private") or lab.lower().startswith("private sector"):
            sector = "Private"; continue
        if isinstance(r[0], (int, float)) and lab and sector:
            yield sector, int(r[0]), lab.rstrip("."), r


def norm(name: str) -> str:
    n = name.lower().replace("ltd", "").replace("limited", "").replace(".", "").replace(",", "")
    for w in ["company", "co", "insurance", "life", "india", "of", "the", "&", "and"]:
        n = n.replace(f" {w} ", " ")
    return " ".join(n.split())[:18]


def build() -> pd.DataFrame:
    t2 = {norm(n): (s, n, num(r[11])) for s, _, n, r in insurer_rows(rows("Part I.xlsx", "2"))}
    t3 = {norm(n): num(r[11]) for s, _, n, r in insurer_rows(rows("Part I.xlsx", "3"))}
    t13 = {norm(n): (num(r[71]), num(r[81])) for s, _, n, r in insurer_rows(rows("Part I.xlsx", "13"))}
    t100 = {}
    for s, _, n, r in insurer_rows(rows("Part V.xlsx", "100")):
        prem = [num(r[3 + 2 * i]) for i in range(len(CHANNELS))]
        t100[norm(n)] = dict(zip(CHANNELS, prem))
    def look(d: dict, k: str):
        if k in d:
            return d[k]
        m = difflib.get_close_matches(k, list(d), n=1, cutoff=0.55)
        return d[m[0]] if m else None

    out = []
    for k, (sector, name, tot) in t2.items():
        rec = dict(insurer=name, sector=sector, total_premium=tot, nbp=look(t3, k),
                   total_commission=(look(t13, k) or (None, None))[0],
                   commission_pct_total_premium=(look(t13, k) or (None, None))[1])
        rec.update({f"indiv_nb_{c}": v for c, v in (look(t100, k) or {}).items()})
        out.append(rec)
    df = pd.DataFrame(out)
    tot = df["indiv_nb_total_indiv_nb"]
    df["bank_ca_share"] = df["indiv_nb_ca_banks"] / tot
    df["agent_share"] = df["indiv_nb_agents"] / tot
    df["broker_ca_other_share"] = (df["indiv_nb_brokers"] + df["indiv_nb_ca_others"]) / tot
    df["direct_online_share"] = (df["indiv_nb_direct"] + df["indiv_nb_online"] + df["indiv_nb_web_aggregators"]) / tot
    return df


if __name__ == "__main__":
    df = build()
    out = ROOT / "data" / "tidy" / "ins_life_insurers_FY25.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} insurers -> {out.relative_to(ROOT)}")
    print("sum total premium:", round(df.total_premium.sum()), " sum commission:", round(df.total_commission.sum(skipna=True)))
    show = df.sort_values("total_premium", ascending=False).head(12)
    print(show[["insurer", "total_premium", "nbp", "total_commission", "commission_pct_total_premium", "bank_ca_share", "agent_share"]].round(3).to_string(index=False))
