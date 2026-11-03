# HDFC Bank: the path back to 2% RoA

An outside-in consulting case built on public data only. It answers one question for a bank CEO, then shows what each answer is worth, in a driver-based Excel model, a steering-committee deck, a two-page memo and a cockpit dashboard. Data as of 3 November 2026.

> Independent outside-in case study using public data only; not commissioned by, or affiliated with, HDFC Bank or Bain & Company.

**Open first:** `decks/pdf/HDFC_RoA_Steerco.pdf` (31 slides), `decks/pdf/HDFC_CEO_Memo.pdf` (2 pages), then `models/HDFC_RoA_Path_FY29.xlsx`. The cockpit is `viz/dashboard.html`: download it and open it in a browser.

## Live site: The 2% Question
**https://site-two-eta-4o267upa77.vercel.app**

An argued long-read built from `site/`. It leads with the answer, then proves it in twelve numbered, annotated exhibits, then lays out the six moves and the plan. An appendix runs the FY27E-FY29E model in the browser, tested against the Excel to within 0.1 bp, so a reader can stress-test the recommendation. Stack: Svelte 5, Vite, D3, Scrollama. Vercel redeploys on every push. To run it locally: `make site`, then `cd site && npx vite preview`.

## The problem
HDFC Bank delivered 1.8-2.0% RoA for a decade. Since the July 2023 merger with HDFC Ltd it has sat at the bottom of that range: 1.80% in FY26 and 1.75% annualised in Q2 FY27. Three things are moving at once:
- margins absorbed the merger's mortgage book and its wholesale borrowings;
- IRDAI's proposed commission caps threaten bancassurance fees and HDFC Life's economics;
- a new UPI MDR opens a fee pool.

**Question:** what combination of moves gets standalone RoA back to 2.0% or more by FY29, what is each move worth (bp of RoA, ₹ cr of PAT, ₹ of value per share), and what should management start in the next 12 months?

Why HDFC Bank? It is the largest private bank, and every 10 bp of RoA there is worth about ₹84,000 cr of equity value. Its gap to ICICI Bank is structural, it missed its own margin guidance, and it sits on both the IRDAI and UPI changes. It also owns 50.2% of HDFC Life.

## The answer
**HDFC Bank can be back above 2% RoA by FY29, but only by pulling six levers. The share price already assumes it.**

| | Downside | Base | Upside |
|---|---|---|---|
| RoA FY29E, before levers | 1.32% | 1.86% | 2.25% |
| RoA FY29E, with levers | 1.50% | 2.04% | 2.43% |
| RoE FY29E, before levers | 10.6% | 14.6% | 17.5% |
| Value per share, residual income to sum of the parts | ₹254-269 | ₹471-533 | ₹632-733 |

The share price was ₹700 on 2 Nov 2026.

1. **The problem is margin, not cost.**
   - NII fell from 3.83% of average assets (FY23) to 3.11% (FY26).
   - The 43 bp RoA gap to ICICI Bank is 63 bp of NII plus 25 bp of FY26's one-off provisions. HDFC Bank is already ahead on opex, other income and tax.
2. **The base case helps but stops short.**
   - ₹1.93 lakh cr of legacy borrowings mature within a year. Replacing 60% of them with deposits lifts NIM from 3.12% to 3.51% by FY29E.
   - Credit cost normalising from 0.48% to its through-the-cycle 0.69% costs about 10 bp of RoA.
3. **Regulation is small for the bank, not for the group.**
   - The IRDAI caps cost the bank ₹873 cr of fees by FY29E (1.3% of other income).
   - UPI MDR adds ₹564 cr.
   - HDFC Life's value of new business rises by a net ₹279 cr, but only if the bank keeps distributing.
4. **Six levers add 17.8 bp and about ₹1.5 lakh cr of equity value.** Four carry the plan:
   - re-mix advances (5.3 bp);
   - branch and operations productivity (3.8 bp);
   - rebuild CASA (3.4 bp);
   - retire legacy borrowings faster (3.0 bp).
5. **The market is paying for 17.9% RoE.** The base case gives 14.6%. Only the upside case supports ₹700.
6. **Decisions for the steering committee:**
   - make deposits the binding constraint;
   - retire ₹75,000 cr of borrowings ahead of plan;
   - re-price the HDFC Life partnership before the caps land.

## What else the analysis shows
- **What the merger changed.** HDFC's own RoA walk from FY23 to Q2 FY27 is -20 bp. Net interest income took 55 bp off, and lower opex gave 31 bp back (Shapley, `data/tidy/hdfc_roa_walk.csv`).
- **What matters most for FY29.** A tornado on the live model, one driver at a time, ranks the swings:
  - repo path: 20 bp;
  - advances growth: 15 bp;
  - credit cost: 13 bp;
  - opex growth: 11 bp;
  - every other driver: 10 bp or less.
- **The levers are conservative against named peers.** Each one closes only 28-49% of the gap to best demonstrated practice:
  - CASA vs SBI's 38.3%;
  - borrowings share vs ICICI Bank's 6.5%;
  - asset yield vs ICICI Bank;
  - UPI payee share vs Axis Bank's 18.9%.
  - HDFC already leads on opex and fees, so those two are sized on its own operating leverage.
- **Funding-cost beta.** A regression over FY17-FY26 gives 0.37 in the same year, which supports the model's 0.35. It rises to 0.62 once the year-two catch-up is included, which is the risk case in the tornado.
- **What management talks about.** In Q2 FY27, ₹1.3 of ₹1.57 lakh cr of new deposits were term deposits, the reason CASA is lever one. Topic counts over eight calls are in the cockpit.

## How the analysis is done
| Layer | What | Where |
|---|---|---|
| Consulting | Issue tree with five hypotheses, lever tree, impact x feasibility x time prioritisation, 12-month roadmap, KPI tree, risk register | `decks/HDFC_RoA_Steerco.pptx` |
| Bank model | IR26-schedule spreading, driver-based FY27E-FY29E projection on average balances, NII rate/volume walk, repricing gap and earnings at risk, legacy-borrowing run-off, fee pools (IRDAI, HDFC Life, UPI MDR), credit normalisation, Tier 1 capacity | `models/HDFC_RoA_Path_FY29.xlsx` |
| Valuation | CAPM cost of equity, justified P/B, residual income, sum of the parts (listed stakes less a 20% holding discount), market-implied RoE, Ke x g and RoE x Ke grids, 12-bank P/B-RoE cross-check | same workbook, Valuation and Sensitivities tabs |
| Sensitivity and evidence | Tornado (24 headless recalculations of the live model); HDFC RoA walk (Shapley); funding-cost beta regression with a one-year lag; peer anchors per lever; earnings-call topic tracker | `pipeline/tornado.py`, `hdfc_walk.py`, `deposit_beta.py`, `call_topics.py`; Tornado, Margin, ALM and Levers tabs |
| SQL | DuckDB warehouse over every tidy and input file, the Screener harvest and the scenario export, plus six analyst queries (peer league, DuPont history, credit cycle, MDR pool, insurer exposure, scenario compare) | `pipeline/warehouse.py`, `sql/*.sql`, `data/tidy/sql_results/` |
| Quality | Strict Excel lint, 29 reconciliation checks, 19 pytest tests (model invariants, traceability of every memo and cockpit headline to the export, SQL ties), ruff code lint, CI on every push, independent model audit | `tests/`, `.github/workflows/ci.yml`, `docs/model_audit.md` |
| Sector modules | Shapley RoA attribution across banks; IRDAI cap model with Monte Carlo; NPCI UPI concentration and MDR pool; say-versus-do tracker of management guidance | `models/01-03_*.xlsx`, `decks/0*.pptx` |

The Excel follows investment-banking hygiene:
- Garamond throughout, no italics;
- blue inputs, black formulas, green links, red checks;
- grey fill only on inputs and historical columns;
- no merged cells;
- one formula pattern per row;
- no hard-coded numbers inside formulas;
- a Base / Upside / Downside selector that drives every driver;
- nine checks that roll up to a master check on the Cover.

`pipeline/xlsx_lint.py` enforces the standard and fails the build on any breach. Full method: `docs/methodology.md`.

## What is in the repo
| Path | Contents |
|---|---|
| `models/` | `HDFC_RoA_Path_FY29.xlsx` (integrated model); `01_Bank_RoA_Benchmark.xlsx`, `02_Insurance_Distribution.xlsx`, `03_UPI_MDR_Cap.xlsx` (sector modules) |
| `decks/` | `HDFC_RoA_Steerco.pptx`, `HDFC_CEO_Memo.docx`, the three sector decks, and PDFs in `decks/pdf/` |
| `viz/dashboard.html` | CEO cockpit with a scenario switch, plus sector tabs; light and dark, phone-width safe, a table behind every chart |
| `data/inputs/` | Page-cited manual inputs (IR26 schedules, borrowing maturities, RBI rate path, NPCI bands and payee banks, valuation inputs) |
| `data/tidy/` | Long facts table with source, page and status on every row; `hdfc_model_outputs.json` (all three scenarios, recalculated) |
| `pipeline/` | Fetch, Screener harvest, model builders, `export_scenarios.py`, `tornado.py`, `hdfc_walk.py`, `deposit_beta.py`, `call_topics.py`, `warehouse.py`, `run_sql.py`, `xlsx_lint.py`, `checks.py` |
| `sql/`, `tests/`, `Makefile` | Analyst SQL queries; pytest suite; one entrypoint for the pipeline |
| `docs/` | `methodology.md`, `data_sources.md`, `model_audit.md`, `public_apis_shortlist.md` |

## Reproduce
LibreOffice is needed for headless recalculation.
```bash
pip install -r requirements.txt
```
```bash
make data sector
```
```bash
make all
```
`make data sector` fetches public sources and rebuilds the sector modules; the NPCI app-wise files, the IRDAI Handbook and the consultation papers are user-supplied (see `docs/data_sources.md`). `make all` rebuilds the HDFC model (twice, so the Tornado tab carries the latest recalculation), the scenario export, the SQL warehouse and queries, the memo, the cockpit and the Tableau extracts. It then runs the checks, the tests and the lint. The steerco deck is built separately with `make deck`.

Before pushing, run `make ci-local`. It clones the last commit into a temporary folder and runs `make all` on committed files only, which is exactly what CI sees. Gitignored caches, such as the FactIQ transcript searches in `data/raw/factiq/`, are absent there; the scripts that use them keep the committed outputs instead.

## Corrections to earlier versions
- **UPI, October 2026.** An earlier version said Oct-26 was 23.83 bn transactions and that the 25.47 bn widely reported was wrong. That was our error: the NPCI file row was a 29-day partial. The full month is 25.47 bn transactions and ₹31.53 lakh cr, a record.
- **Q2 FY27 margins.** An earlier version said every reported Q2 FY27 NIM fell. SBI's whole-bank NIM rose 13 bp to 2.94% (press release, 3 Nov 2026).

## Caveats
- The IRDAI caps are a September 2026 proposal, not final.
- Lever sizes, feasibility and timing are judgements for discussion, not forecasts. Each one is an explicit driver change in the model, so it can be challenged and re-run.
- HDFC Bank does not disclose its external-benchmark (floating-rate) share of advances. The model assumes 55% (range 45-65%).
- Screener.in is a secondary source, used only after tying to the bank's filings.
- The steerco deck was built before the tornado, the RoA walk, the peer anchors and the beta regression. It is on hold and does not yet show them; its numbers still match the model.
- The workbooks specify Garamond. If Garamond is not installed, the viewer substitutes a serif font.
- No Bain engagement with HDFC Bank is known or implied. Bain publications are referenced for framing only; no Bain charts, data or wording are reproduced.

Prepared by Anklesh.
