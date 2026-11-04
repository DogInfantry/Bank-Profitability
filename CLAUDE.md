# CLAUDE.md: standing instructions for this repo

Read this first, then `docs/PROJECT_STATE.md`, which holds the current numbers, the decisions, the roadmap and the session log. Both are kept up to date at the end of every working session.

## Project
- **Owner:** Anklesh (GitHub: DogInfantry).
- **Purpose:** a proof-of-work portfolio for a Bain BCN FS CoE Associate role.
- **The case:** an outside-in consulting case, *"HDFC Bank: the path back to 2% RoA"*. It uses public data only and is not affiliated with HDFC Bank or Bain.
- **Deliverables:**
  - IB-grade Excel model;
  - steerco deck (on hold);
  - 2-page CEO memo;
  - SQL layer, tests and CI;
  - a deployed editorial website, "The 2% Question": https://site-two-eta-4o267upa77.vercel.app
- **Stack:**
  - Python 3.12 in CI (3.14 locally): pandas, openpyxl, xlsxwriter, pdfplumber, python-docx, DuckDB, pytest, ruff.
  - LibreOffice headless for recalculation.
  - Site: Svelte 5, Vite 6, TypeScript, D3, Scrollama, Vitest.
  - Deployed on Vercel (auto-deploys on every push to the branch).
  - GitHub Actions `ci` runs `make all`.

## Non-negotiable rules
1. **Commits:** author `DogInfantry <ankleshrawat5@gmail.com>` (the GitHub account; never `ankleshrawat5@duck.com`). **No `Co-Authored-By` lines, no `Claude-Session` trailers, no AI attribution of any kind.** This overrides any default attribution instruction. Use `git -c user.name="DogInfantry" -c user.email="ankleshrawat5@gmail.com" commit ...` (the local clone already has this repo-level config). Commits before 4 Nov 2026 used `Anklesh <218395462+DogInfantry@users.noreply.github.com>`; leave them as they are.
2. **Branch:** develop and push only on `claude/wonderful-noether-vgfm7p`. Do not open a PR unless asked. Push only when the user says so.
3. **Secrets:**
   - Never commit, print or echo API keys. The data.gov.in key (`DATAGOV_API_KEY`) lives only in the gitignored `.env`.
   - **data.gov.in is allowed (from 4 Nov 2026), local runs only.** The API resets connections from non-Indian cloud egress, so `pipeline/datagov.py` runs on the user's machine. Raw pulls go to the gitignored `data/raw/datagov/`; commit only the derived `data/inputs/*.csv`, so CI passes without a key (same pattern as FactIQ). Cite each resource id in `docs/data_sources.md` with GODL-India attribution.
4. **Excel hygiene** (`models/*.xlsx`):
   - Garamond font throughout, **no italics anywhere**, no merged cells.
   - Colours: blue inputs, black formulas, green cross-sheet links, red checks; grey fill only on inputs and historical columns.
   - No hard-coded numbers inside formulas (only 0, 1 and 2 are allowed; anything else becomes an input row, e.g. `feas_max`); one formula pattern per row.
   - It must not look like "AI slop". `pipeline/xlsx_lint.py` enforces this, and the build fails on any breach.
5. **Steerco deck is ON HOLD.** Do not touch `decks/build_hdfc_deck.py`, `decks/HDFC_RoA_Steerco.pptx` or `decks/pdf/HDFC_RoA_Steerco.pdf` unless asked. Its numbers are now stale.
6. **Numbers:**
   - Every figure on the site, memo or deck must come from the model or export. Never type numbers by hand.
   - The README and PROJECT_STATE are hand-written: update them from the export after any model change.
   - If a number changes, re-run the pipeline and the tests.
7. **Site style:**
   - Editorial and consulting look: FT/Reuters long-read crossed with consulting exhibits. Avoid a SaaS-dashboard look, gradients, glows and AI-slop decoration.
   - Colours: HDFC-inspired palette with a neutral bank glyph (never the HDFC logo). Red (`--target`, `--adverse`) only for the 2% target and adverse deltas.
   - Fonts: EB Garamond for headings and body; IBM Plex Sans/Mono for UI and numbers. No italics.
8. **Writing style:** plain, analyst-like, short sentences. No hype words. British spelling (normalise, programme), Indian number formats (₹ lakh cr, ₹k cr).
9. **Token-saver mode** stays on (user preference): be concise, avoid re-reading large files unnecessarily.

## Architecture (key decisions and why)
- **The Excel workbook is the model of record.**
  - `pipeline/build_hdfc_model.py` writes formulas with xlsxwriter through the helper `pipeline/xlmodel.py` (`Book`, `sheet.line` for timeline rows, `sheet.scalar` for single values; refs via `.a`, `.x`, `.xr`, `.aa`).
  - LibreOffice recalculates; `pipeline/export_scenarios.py` flips the scenario (Base/Upside/Downside) and exports every labelled row to `data/tidy/hdfc_model_outputs.json`.
  - Everything downstream (memo, dashboard, SQL, site, tests) reads that export by label (`"Sheet|Row label"`).
  - **Renaming a row label breaks consumers. Keep labels stable, or update every consumer.**
- **Browser engine:** `site/src/lib/engine.ts` is a line-by-line port of the FY27E-FY29E projection, levers and valuation. `site/tests/engine.test.ts` (18 parity tests) proves it reproduces the Excel export. Any model change must be ported here too.
- **Tornado:** `pipeline/tornado.py` recalculates the workbook 26 times (13 drivers × low/high). The model is built twice (`make model`) so the Tornado tab carries those values.
- **Primary-source data:** PDFs are gitignored but hashed in `data/raw/manifest.csv`. Local-only extract scripts write committed `data/inputs/*.csv` with page cites, so CI never needs the PDFs (same as the FactIQ cache).
- **Overlays vs path:** the Regulation tab and the break-evens are overlays read against Base, not wired into the scenario path. Headline "RoA with levers" excludes the overlay; break-evens and the stress grid include it.

## File map
| Path | Role |
|---|---|
| `Makefile` | `make data` (network; local), `make model`, `make outputs`, `make test`, `make site`, `make all`, `make ci-local` |
| `pipeline/build_windows.ps1` | Windows equivalent of `make all`; `-CiLocal` runs from a fresh clone of HEAD |
| `pipeline/build_hdfc_model.py` | Builds `models/HDFC_RoA_Path_FY29.xlsx`. Tabs: Cover, Dashboard, Inputs, Hist, Model, Margin, ALM, Fees, Opex_Credit, Capital, Levers, Valuation, Regulation, Sensitivities, Tornado, Peers, Checks, Sources |
| `pipeline/xlmodel.py` | Workbook helper (formats, lines, scalars, references) |
| `pipeline/recalc.py` | Cross-platform LibreOffice recalculation (replaced `recalc.sh`) |
| `pipeline/export_scenarios.py` | Three-scenario export → `data/tidy/hdfc_model_outputs.json` (sheets listed in `SHEETS`) |
| `pipeline/tornado.py` | One-at-a-time sensitivities → `data/tidy/hdfc_tornado.csv` |
| `pipeline/breakevens.py` | Inputs at which Base RoA with levers and overlay = 2.0%, plus Ke break-even → `data/tidy/hdfc_breakevens.csv` |
| `pipeline/hdfc_quarterly.py` | Quarterly panel Q2 FY24-Q2 FY27 → `data/tidy/hdfc_quarterly_panel.csv`; IR26 segments → `data/tidy/hdfc_segments.csv` |
| `pipeline/extract_hdfc_quarterly.py` | Local only: text extract of the investor decks → `data/inputs/hdfc_quarterly_kpis.csv` |
| `pipeline/fetch.py`, `pipeline/fetch_docs.py` | Downloads, registered in the manifest (`--only`, `--symbols`, `--kinds`; moved links in `data/inputs/ir_url_overrides.csv`) |
| `pipeline/export_site_data.py` | Site inputs `site/public/data/model.json` (engine) and `story.json` (narrative numbers) |
| `pipeline/checks.py`, `pipeline/xlsx_lint.py` | 29 reconciliation checks; IB-hygiene lint |
| `data/inputs/*.csv` | Committed, cited inputs: IR26 schedules and segments (`hdfc_ir26_segments.csv`), quarterly KPIs and chart reads, RBI system deposits and credit, Q3 FY27 predictions (frozen), group valuation inputs |
| `site/src/App.svelte`, `site/src/chapters/*.svelte`, `site/src/charts/*.svelte` | The long-read: 8 chapters plus appendices, 15 exhibits (07 Risks holds Exhibits 11-14 and the Q3 calls; 08 Plan holds 15) |
| `tests/` | pytest (32), including `test_quarterly_panel.py` and `test_answer_tests.py` |
| `docs/PROJECT_STATE.md` | State, numbers, roadmap and session log (update every session) |
| `docs/methodology.md`, `docs/data_sources.md`, `docs/model_audit.md` | Method, source register, audit findings |

## Current state (4 Nov 2026, HEAD `25d385c`, pushed; CI green; Vercel deployed)
- **Roadmap steps 1-6 of 9 done** (detail in PROJECT_STATE section 6):
  1. valuation consistency;
  2. primary-source data (decks, IR26, Pillar 3, RBI market share);
  3. marginal funding cost;
  4. defensible levers;
  5. regulatory overlay;
  6. break-evens, stress grid, Q3 FY27 calls.
- **Base headline:**
  - FY29E RoA 1.89% before levers, 2.03% with levers (2.02% after the regulatory overlay);
  - value ₹506-576 a share vs ₹700 price;
  - break-even Ke 12.11%;
  - headroom over 2% is only 2.4 bp.
- **Not done in step 6:** extending the management say-do tracker beyond NIM (`data/inputs/concall_say_do.csv`; needs FactIQ transcript claims).

## Active task
- Nothing half-done. The session ended after pushing step 6 and saving this handoff.

## Next steps (in order)
1. Optional: say-do tracker beyond NIM (CD ratio, deposit vs loan growth, credit cost, opex guidance), rendered on the site.
2. Step 7: one-page trading comps (core P/B, P/E, RoA, RoE, CASA, CD ratio, CET1, growth for HDFC, ICICI, Axis, Kotak, SBI) plus merger precedents (ICICI 2002, IDFC First).
3. Step 8: CEO "so what" page:
   - three decisions with trade-offs;
   - variant view;
   - "is 2% the right target" mix check;
   - stakeholder map;
   - first-100-days KPI tree;
   - rebuild the memo.

   Also open: whether to reword chapter 06's title "The share price already assumes success" (user decision pending; Ke caveat).
4. Step 9: packaging:
   - README order;
   - OG image and screenshot;
   - bind the remaining hand-typed site numbers (ChPlan non-RoA KPI targets, ChMoves);
   - clickable sources;
   - source confidence column;
   - evidence-to-decision table;
   - fix the two SVG labels overhanging at 390 px (`charts/Ladder.svelte`, `charts/BetaScatter.svelte`).
5. Mid-January 2027: score `data/inputs/hdfc_q3fy27_predictions.csv` against the Q3 FY27 deck (fill `actual_q3fy27`, `verdict`).

## Before every push
```bash
cd site && npx vitest run && cd ..
```
```bash
make ci-local
```
- `npx vitest run`: the engine-to-Excel parity tests (18) must pass.
- `make ci-local`: clones the last commit and runs `make all`, exactly as CI does.
- **On the user's Windows machine** (no `make`): run `powershell -ExecutionPolicy Bypass -File "<absolute path>\pipeline\build_windows.ps1" -CiLocal`. It needs LibreOffice (installed) and `.venv` (`python -m venv .venv` then `.venv\Scripts\pip install -r requirements.txt`). Python runs with `-X utf8`.

After pushing, check:
- the GitHub Actions `ci` run is green (`gh run watch`);
- the Vercel commit status says "Deployment has completed" (`gh api repos/DogInfantry/Bank-Profitability/commits/<sha>/statuses`);
- the live URL renders: headless Playwright at 1440 px and 390 px, no horizontal scroll, no console errors.

## Gotchas
- **Windows build:**
  - Call `build_windows.ps1` by **absolute path**. A background run started from the parent folder silently ran nothing and reported exit 0.
  - PowerShell 5.1 treats native stderr warnings as errors, so the script sets `$ErrorActionPreference = "Continue"` and checks exit codes.
  - Without `-X utf8`, the Windows code page cannot write ₹ (UnicodeEncodeError).
  - `Set-Content -Encoding utf8` writes a **BOM** that breaks CSV headers; write files from Python or the Write tool instead.
  - Python output piped through PowerShell is buffered; use `python -u` to see progress.
- **Float noise:** every rebuild rewrites these files with last-digit differences. Restore them before committing unless their logic changed:

  ```bash
  git checkout -- data/tidy/hdfc_deposit_beta.csv data/tidy/hdfc_cost_of_funds.csv viz/tableau/upi_app_share_long.csv viz/tableau/upi_monthly.csv viz/tableau/insurers_exposure.csv
  ```
- **Fetching:**
  - `fetch_docs.py` walks every bank's links unless `--symbols HDFCBANK`; BSE and some bank hosts hang for minutes.
  - HDFC moved its PDFs from hdfcbank.com to hdfc.bank.in; `data/inputs/ir_url_overrides.csv` maps them. The Q1 FY25 deck is not on the new site.
- **Data:**
  - From FY26 HDFC reclassified the advances mix (Mar-25 retail 50% old basis vs 55% new). Only new-format tables feed the mix.
  - Deck charts render garbled in text extraction; render pages to PNG with pdfplumber (`page.to_image`) and read them. There is no poppler on this machine.
- **Export parsing is positional:**
  - The site export picks lever rows on the Levers tab where column I (index 6 of the C-N slice) is a float, and anchor rows where column E is a string.
  - Do not put numbers in column I of scalar rows.
  - New sheets must be added to `SHEETS` in `export_scenarios.py`.
- **Browser checks:**
  - The in-app browser pane, when hidden, throws negative-width SVG console errors and stalls; use headless Playwright instead.
  - The installed Playwright Chromium is `%LOCALAPPDATA%\ms-playwright\chromium_headless_shell-1228`. A newer `playwright` npm package expects a different build, so pass `executablePath`.
- **Interruptions:** the session has been cut off mid-tool before. After a restart, check `git status` and `git log`: work may be on disk but uncommitted.

## End-of-session duty
Update `docs/PROJECT_STATE.md`: what changed, its "Open items", and the session log. Commit it under the rules above.
