"""Pull a data.gov.in (OGD India) resource to data/raw/datagov/<resource_id>.csv. Run LOCALLY: the API resets
connections from non-Indian cloud egress. The key is read from the DATAGOV_API_KEY env var or a gitignored .env.
Usage: python pipeline/datagov.py <resource_id> [--limit 1000]
Find resource ids at https://data.gov.in (e.g. search 'scheduled commercial banks', 'UPI', 'insurance').
"""
import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def key() -> str:
    if os.getenv("DATAGOV_API_KEY"):
        return os.environ["DATAGOV_API_KEY"]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("DATAGOV_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("Set DATAGOV_API_KEY (copy .env.example to .env).")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("resource_id"); ap.add_argument("--limit", type=int, default=1000)
    a = ap.parse_args()
    rows, offset = [], 0
    while True:
        q = urllib.parse.urlencode({"api-key": key(), "format": "json", "limit": a.limit, "offset": offset})
        with urllib.request.urlopen(f"https://api.data.gov.in/resource/{a.resource_id}?{q}", timeout=60) as r:
            batch = json.load(r).get("records", [])
        rows += batch; offset += len(batch)
        if len(batch) < a.limit:
            break
    out = ROOT / "data/raw/datagov" / f"{a.resource_id}.csv"; out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False); print(f"{len(rows)} rows -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
