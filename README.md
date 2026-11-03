# India FS profit pools: bank RoA, insurance distribution caps, UPI's first fee

A financial-services research portfolio built on primary data: three analyses, one reproducible data pipeline, live Excel models, a client dashboard and board-style decks. Data as of 3 Nov 2026.

> **Open first:** `viz/dashboard.html` (download it and open it in a browser), then `decks/pdf/`. The models are in `models/`.

## The answers

**1. Why Indian bank RoA diverges** (`models/01_Bank_RoA_Benchmark.xlsx`, `decks/01_Bank_RoA_Divergence.pptx`)

ICICI Bank has the peer-best FY26 standalone RoA (2.23%). A Shapley attribution shows the banks behind it trail for **different** reasons:

| Bank | Gap to ICICI | Main cause |
|---|---|---|
| SBI | 111 bp | Almost entirely margin: net interest income explains 114 bp. SBI's opex per rupee of assets is the *lowest* in the set. |
| Axis | 83 bp | Margin (57 bp) plus credit cost (41 bp, including a ₹2,001 cr one-off provision). |
| Kotak | 34 bp | Cost: it has the best margin, but opex absorbs 41 bp. |

Every reported Q2 FY27 NIM is 14–36 bp below Q4 FY26. A "say vs do" tracker scores management's margin guidance from earnings calls against the margins the banks later reported.

**2. Who loses under IRDAI's proposed commission caps** (`models/02_Insurance_Distribution.xlsx`, `decks/02_Insurance_Distribution_Caps.pptx`)
- In FY25, private life commission grew 38.8% against premium growth of 12.1%.
- Private insurers' expense of management is 19.5% of premium, against proposed limits of 15% (year 2) and 12.5% (year 5). That means removing ₹17.9k cr (year 2) and ₹27.8k cr (year 5) on the FY25 base.
- First-year commission above the proposed caps is about ₹10.75k cr a year (Monte Carlo P10–P90: ₹8.6k–13.2k cr). This is a lower bound.
- That sum is roughly 74% of SBI Life's FY25 profit and 70% of HDFC Life's, versus about 6% of LIC's. Bank-promoted private insurers carry the renegotiation risk; their promoter banks lose only 0.8–1.7% of other income.

**3. UPI's first fee and the 30% app cap** (`models/03_UPI_MDR_Cap.xlsx`, `decks/03_UPI_MDR_and_Cap.pptx`)
- NPCI's own file puts the record month at Aug-26 (24.51 bn transactions). Oct-26 was 23.83 bn, not the 25.47 bn widely reported.
- The 0.4% MDR on merchant payments above ₹2,000 creates a ₹9k–24k cr annual pool (sensitivity grid).
- PhonePe (45.9% share) would need to lose 4 pp a month to reach the 30% cap by December 2026. Its 12-month trend is flat.

## What is in the repo
| Layer | Files |
|---|---|
| Data asset | `data/tidy/*.csv`: long facts table with `source`, `page` and `status` on every row. `data/inputs/*.csv`: page-cited manual inputs. `data/raw/manifest.csv`: sha256 hash of every raw file. |
| Pipeline | `pipeline/`: `fetch.py`, `screener.py`, `fetch_docs.py`, `build_bank_facts.py`, `shapley.py`, `build_bank_xlsx.py`, `extract_irdai.py`, `insurance_model.py`, `upi_model.py`, `checks.py`, `datagov.py`, `mine_public_apis.py` |
| Models | `models/*.xlsx`: live formulas, a source comment on every input, checks tabs |
| Dashboard | `viz/dashboard.html`: single file, light/dark, a table behind every chart. `viz/tableau/`: long-format extracts and a field dictionary |
| Decks | `decks/*.pptx` (native, editable charts) and `decks/pdf/` |
| Docs | `docs/methodology.md`, `docs/data_sources.md`, `docs/public_apis_shortlist.md` |

## Reproduce
```bash
pip install -r requirements.txt            # plus LibreOffice for headless recalculation
python -I pipeline/fetch.py && python -I pipeline/screener.py && python -I pipeline/fetch_docs.py
python -I pipeline/build_bank_facts.py && python -I pipeline/shapley.py && python -I pipeline/build_bank_xlsx.py
python -I pipeline/extract_irdai.py && python -I pipeline/insurance_model.py && python -I pipeline/upi_model.py
python -I viz/build_dashboard.py && python -I decks/build_decks.py
python -I pipeline/checks.py               # 18 reconciliations; exits non-zero on any FAIL
```
The NPCI files and the IRDAI Handbook and consultation papers block automated download, so they are user-supplied (see `docs/data_sources.md`). A quarterly refresh means re-running the commands above; the SBI Q2 FY27 column fills automatically once its results appear on Screener.

## Caveats
- The IRDAI caps are a **September 2026 proposal**, not final. The premium-paying-term mix is an assumption; it is stress-tested by the Monte Carlo and editable in the workbook.
- Screener.in is a secondary source, used only after tying to the banks' filings. Crunchbase figures are as reported by Crunchbase.
- Judgements are labelled as judgements, for example the expectation that the 30% cap deadline will be extended again.
- Bain publications are referenced for framing only. No Bain charts, data or wording are reproduced.

Prepared by Anklesh.
