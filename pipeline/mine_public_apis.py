"""Shortlist APIs relevant to Indian FS research from the public-apis/public-apis README (fetched by fetch.py)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = {"Finance", "Government", "Open Data", "Cryptocurrency", "Currency Exchange", "Business"}
KEEP = re.compile(r"india|indian|\brbi\b|\bnse\b|\bbse\b|\bbank|ifsc|upi|mutual fund|insur|world bank|\bimf\b|\bfred\b|federal reserve|edgar|sec filings|exchange rates?\b|inflation|gdp", re.I)

text = (ROOT / "data/raw/web/public_apis_README.md").read_text()
out, sec = [], None
for line in text.splitlines():
    m = re.match(r"^###\s+(.*)", line)
    if m:
        sec = m.group(1).strip(); continue
    if sec in SECTIONS and line.startswith("| [") and KEEP.search(line):
        cells = [c.strip() for c in line.strip("|").split("|")]
        name_url = re.match(r"\[(.*?)\]\((.*?)\)", cells[0])
        if name_url:
            out.append((sec, name_url.group(1), name_url.group(2), cells[1], cells[2] if len(cells) > 2 else ""))
md = ["# APIs shortlisted from public-apis/public-apis", "",
      "Mined by `pipeline/mine_public_apis.py` from the public-apis README (MIT licence). Filter: Finance, Government, Open Data, Currency Exchange, Business sections, keyword match on India / banking / markets / macro. Use = how it could extend this project.", "",
      "| Section | API | Description | Auth |", "|---|---|---|---|"]
md += [f"| {s} | [{n}]({u}) | {d} | {a} |" for s, n, u, d, a in out]
(ROOT / "docs/public_apis_shortlist.md").write_text("\n".join(md) + "\n")
print(len(out), "APIs shortlisted")
