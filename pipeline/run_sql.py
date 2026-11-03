"""Run every query in sql/ against data/fs.duckdb and write data/tidy/sql_results/<name>.csv."""
from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT / "data" / "tidy" / "sql_results"
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(ROOT / "data" / "fs.duckdb"), read_only=True)
    for q in sorted((ROOT / "sql").glob("*.sql")):
        df = con.sql(q.read_text()).df()
        df.to_csv(out / f"{q.stem}.csv", index=False)
        print(f"== {q.stem} ({len(df)} rows)\n{df.head(12).to_string(index=False)}")


if __name__ == "__main__":
    main()
