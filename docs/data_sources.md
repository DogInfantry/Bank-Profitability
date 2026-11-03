# Data sources

Every raw file is hashed in `data/raw/manifest.csv` (url, sha256, bytes, fetch time, status). Large PDFs and the Handbook workbooks are gitignored; re-create them with `pipeline/fetch.py` and `pipeline/fetch_docs.py`, or re-upload the manual files.

| Source | What | How obtained | Status |
|---|---|---|---|
| Bank investor presentations / press releases (SBI, HDFC, ICICI, Axis, Kotak) Q4 FY26, Q2 FY27 | P&L, NIM, GNPA, RoA, C/I | `fetch.py`, `fetch_docs.py` (links harvested from Screener's Concalls block, BSE AttachHis fallback) | primary |
| Screener.in standalone pages | 10-yr P&L / balance sheet, quarterlies, concall links | `screener.py` (3 s throttle, cached) | secondary, tied to filings |
| NSE XBRL Integrated Filing (Banking) via FactIQ | HDFC Q2 FY27 parent PPOP | FactIQ MCP | primary |
| FactIQ earnings-call claim graph | Management margin guidance (quote-anchored) | FactIQ MCP | primary transcripts, structured by FactIQ |
| IRDAI Annual Report 2024-25 | Life/non-life premium, commission, opex, ICR | `fetch.py` (Life Insurance Council mirror) | primary |
| IRDAI Handbook on Indian Insurance Statistics 2024-25 | Insurer-wise premium, commission, channel mix (T2, T3, T13, T99, T100) | user upload | primary |
| IRDAI consultation 'Recalibrating Economics of Insurance Distribution' Parts 1-2 + press note (Sep 2026) | Cap rules, EoM glide path, Annexure 3 commission data | user upload | primary (proposal) |
| NPCI UPI product statistics FY26, FY27 YTD | Monthly volume/value | user upload | primary |
| NPCI UPI app-wise statistics Dec-20 to Aug-26 | App volumes/values | user upload | primary |
| DFS FAQ on MDR (15 Sep 2026) | MDR rules, exemptions | `fetch.py` | primary |
| PIB release (24 Aug 2026) | FY26 P2M/P2P split | cited | primary |
| Crunchbase | Funding for UPI apps and insurance distributors | Crunchbase MCP, request id in CSV | secondary |
| data.gov.in (OGD) | Optional extra series | `datagov.py`, run locally (API blocks cloud egress); key in gitignored `.env` | optional |
| public-apis/public-apis | API discovery | `mine_public_apis.py` -> `public_apis_shortlist.md` (58 APIs) | reference |

**Corrections to the original brief, found from primary data:**
- **UPI, Oct-26:** 23.83 bn transactions / ₹29.25 lakh cr. The 25.47 bn in the secondary press does not match NPCI's file. The record month is Aug-26 at 24.51 bn.
- **IRDAI EoM path:** general-insurance EoM falls from 25% of GDPI (year 2) to 20% (year 5). The life path is 15% then 12.5%, and insurers already below that must reach 10%.
- **SBI provisions:** "Total Provisions" includes tax. Ex-tax provisions are ₹17,538 cr, not ₹42,983 cr.
- **Corporate-agent remuneration:** +125% vs new-business premium +28% over FY23-25. Verified in consultation Part 1, p19.
