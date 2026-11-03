"""Are management talking about the levers? Topic tracker over HDFC Bank's last eight earnings calls.

Input: FactIQ earnings-call claim search (search_earnings_transcripts, ticker HDFCBANK.NS, limit 50) for five topic
queries, cached as JSON in data/raw/factiq/hdfc_calls_<topic>.json (gitignored: it holds verbatim quotes).
Queries: casa = "CASA"; deposits = "deposits deposit cost of funds"; borrowings = "borrowings"; margin = "margin NIM";
credit = "credit cost provisions".
Retrieval is lexical and capped at 50 claims per topic, so counts are indicative of emphasis, not complete.
Output: data/tidy/hdfc_call_topics.csv (claims per topic per call) and hdfc_call_topics_latest.csv (latest claim per
topic: FactIQ's normalised statement, a paraphrase, with a link to the verbatim quote).
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, T = ROOT / "data" / "raw" / "factiq", ROOT / "data" / "tidy"
TOPICS = {"casa": "CASA", "deposits": "Deposits and cost of funds", "borrowings": "Borrowings", "margin": "Margin / NIM", "credit": "Credit cost"}
CALLS = ["FY2025Q3", "FY2025Q4", "FY2026Q1", "FY2026Q2", "FY2026Q3", "FY2026Q4", "FY2027Q1", "FY2027Q2"]


def label(fp: str) -> str:
    return f"Q{fp[-1]} FY{fp[4:6]}"


def main():
    # The cache is gitignored, so a clean checkout (CI) has none: keep the committed tidy outputs rather than
    # overwriting them. A partial cache is treated the same way, so the outputs are never a partial table.
    missing = [k for k in TOPICS if not (RAW / f"hdfc_calls_{k}.json").exists()]
    if missing:
        print(f"call_topics: no cached FactIQ search for {', '.join(missing)}; keeping committed "
              f"{T.relative_to(ROOT)}/hdfc_call_topics*.csv (re-run the queries in the docstring to refresh)")
        return
    counts, latest = [], []
    for key, name in TOPICS.items():
        f = RAW / f"hdfc_calls_{key}.json"
        d = json.loads(f.read_text()); df = pd.DataFrame(d["results"], columns=d["columns"])
        df = df[df.fiscal_period.isin(CALLS)].copy(); df["relevance_score"] = df.relevance_score.astype(float)
        for fp in CALLS:
            counts.append(dict(topic=name, call=label(fp), fiscal_period=fp, claims=int((df.fiscal_period == fp).sum())))
        top = df.sort_values(["fiscal_period", "relevance_score"], ascending=[False, False]).iloc[0]
        sl = top.source_link
        link = (sl if isinstance(sl, dict) else ast.literal_eval(sl)).get("source_url", "")
        latest.append(dict(topic=name, call=label(top.fiscal_period), speaker_role=top.speaker_role, paraphrase=top.canonical_statement, verbatim_url=link))
    pd.DataFrame(counts).to_csv(T / "hdfc_call_topics.csv", index=False)
    pd.DataFrame(latest).to_csv(T / "hdfc_call_topics_latest.csv", index=False)
    print(pd.DataFrame(counts).pivot(index="topic", columns="fiscal_period", values="claims").to_string())
    for x in latest:
        print("-", x["topic"], x["call"], ":", x["paraphrase"][:140])


if __name__ == "__main__":
    main()
