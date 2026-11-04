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
| data.gov.in (OGD) | Allowed from 4 Nov 2026, no series used yet. RBI and NPCI series still come from FactIQ. `datagov.py` runs locally only (the API resets non-Indian cloud egress); key in a gitignored `.env`; raw pulls in gitignored `data/raw/datagov/`; GODL-India licence | not used yet |
| HDFC Bank Integrated Annual Report 2025-26 | Schedules 3, 4, 8, 9, 13-16 (pp359-366); maturity pattern (p384); ten-year highlights (p234); stakes (p52); branches (p18); employees (p420) | `fetch_docs.py` (PDF gitignored); extracts in `data/inputs/hdfc_*.csv` | primary |
| RBI via FactIQ | Policy repo path, 10-year G-sec, Survey of Professional Forecasters round 102 | FactIQ MCP -> `data/inputs/rbi_policy_path.csv` | primary |
| NPCI via FactIQ | P2M value by ticket band (Apr-25 to Oct-26), payee-bank volumes (Sep-26) | FactIQ MCP -> `data/inputs/npci_p2m_monthly.csv`, `npci_payee_banks_sep26.csv` | primary |
| HDFC Life public disclosures FY26, Q2 FY27 | VNB, APE, VNB margin, embedded value, bancassurance share | cited in `data/inputs/hdfc_group_valuation_inputs.csv` | primary |
| Screener valuation block (12 banks + HDFC Life, HDFC AMC, HDB Financial) | Market cap, price, book value | `screener.py` -> `data/raw/screener/*_valuation.csv` | secondary |
| SBI Q2 FY27 press release (3 Nov 2026) | NII, operating profit, PAT, NIM, CASA, credit cost | user upload | primary |
| RBI Bank Rate change dates via FactIQ (2012-2026) | Repo history for the funding-cost beta (Bank Rate less the MSF spread) | FactIQ MCP -> `data/inputs/rbi_repo_history.csv` | primary, derived |
| HDFC Bank earnings-call claims via FactIQ (eight calls to Q2 FY27) | Topic counts and the latest claim per topic | FactIQ MCP, cached in gitignored `data/raw/factiq/` -> `data/tidy/hdfc_call_topics*.csv` | primary transcripts, structured by FactIQ |
| public-apis/public-apis | API discovery | `mine_public_apis.py` -> `public_apis_shortlist.md` (58 APIs) | reference |

**Corrections to the original brief, found from primary data:**
- **UPI, Oct-26 (our own error, corrected):** an earlier version read the NPCI file's Oct-26 row (23.83 bn) as the full month. It was a 29-day partial (821.7 mn a day x 29). The full month, from NPCI's P2P/P2M table via FactIQ, is 25.47 bn transactions / ₹31.53 lakh cr, so October 2026 is the record month. `upi_model.py` now replaces any month-to-date row with the full month.
- **SBI Q2 FY27 NIM:** an earlier version said every reported Q2 FY27 NIM fell. SBI's press release (3 Nov 2026) shows whole-bank NIM up 13 bp to 2.94%.
- **IRDAI EoM path:** general-insurance EoM falls from 25% of GDPI (year 2) to 20% (year 5). The life path is 15% then 12.5%, and insurers already below that must reach 10%.
- **SBI provisions:** "Total Provisions" includes tax. Ex-tax provisions are ₹17,538 cr, not ₹42,983 cr.
- **Corporate-agent remuneration:** +125% vs new-business premium +28% over FY23-25. Verified in consultation Part 1, p19.
