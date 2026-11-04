# Project state: HDFC Bank, the path back to 2% RoA

Last updated: **4 Nov 2026**, after the step-1 valuation consistency pack (roadmap in section 6). Data is as of 3 Nov 2026 (financials to Q2 FY27; price ₹700 on 2 Nov 2026).

Standing rules are in `/CLAUDE.md`. This file covers state, numbers, decisions and what is open.

---

## 1. The answer (headline numbers; all from `data/tidy/hdfc_model_outputs.json`)
| Metric | Downside | Base | Upside |
|---|---|---|---|
| RoA FY29E, before levers | 1.31% | **1.89%** | 2.27% |
| RoA FY29E, with six levers | 1.45% | **2.03%** | 2.40% |
| RoE FY29E, before levers | 10.6% | 14.9% | 17.6% |
| Value per share at 2 Nov 2026 (residual income to sum of the parts) | ₹254-273 | **₹506-576** | ₹671-781 |
| Break-even Ke (sum of the parts = ₹700) | 9.49% | **12.11%** | 13.81% |

**Thesis:** HDFC Bank's RoA problem is a **funding** problem created by the July 2023 merger, not a cost problem. Run-off of legacy borrowings gets RoA to 1.89%. Six funding-led moves (+14.0 bp, risk-adjusted) get it to 2.03%, only 3 bp of headroom, and the optimistic CASA path alone puts 8 bp at risk. The ₹700 price implies a **16.7% core-bank RoE**, and the base case gives 14.9%. **Caveat:** this rests on the 13.13% CAPM Ke. At 12.1% or less the base case alone supports ₹700, and peer prices imply 10.6-11.1%.

**Key facts used throughout:**
- **Merger effects:**
  - NII / average assets fell from 3.83% (FY23) to 3.11% (FY26); opex fell from 2.10% to 1.76%.
  - Shapley RoA walk, FY23 to Q2 FY27: −20 bp in total (NII −55, other income −11, opex +31, provisions +16).
- **Gap to ICICI Bank, FY26:** 43 bp (NII 63, provisions 25; HDFC Bank ahead by 27 bp on opex).
- **Borrowings and funding cost:**
  - ₹1.93 lakh cr of borrowings mature within a year; base case replaces 60% with deposits.
  - Borrowings fall from 19% of funding (FY25) to 7% (FY29E); NIM rises to 3.56%.
  - Cost of borrowings 7.80% vs cost of deposits 4.76% (FY26).
  - **Marginal funding (step 3):** new term deposits cost the fresh rate, not the book rate.
    - The system fresh rate was 5.61% in Sep-26 (RBI press release 2026-2027/1416), against 6.55% outstanding; HDFC's implied book TD rate is about 6.1%.
    - Base fresh rate paid is 5.7-6.0% FY27-29E, so the marginal term adds about +3 bp to FY29E RoA.
    - A deposit war (+50 bp over system, Downside) costs 6.8 bp of FY29E RoA.
    - The base CASA path implies 37% of new deposits as CASA in FY28-29, against 21% delivered in the last four quarters: an optimistic input.
- **Credit cost:** 0.48% recent vs 0.69% through the cycle; normalisation costs about 10 bp of RoA.
- **Six levers, bp of FY29E RoA:**
  - re-mix advances 2.65 (was 5.3 before step 4: now net of a 2 pp credit-cost gap on the book moved; economic profit after a Ke charge on the ₹14k cr extra Tier 1 is −₹342 cr);
  - productivity 3.8;
  - CASA 3.4;
  - retire borrowings 1.9 (was 3.0 before step 3: priced against the fresh TD rate, not the average cost of deposits);
  - fees 1.9;
  - UPI 0.4.

  Peer anchors close 28-49% of the gap to a named peer.
- **Valuation:**
  - CAPM Ke 13.13%, g 8% (implies a 45% long-run payout); each 10 bp of RoA ≈ ₹84k cr of equity value.
  - P/B: 1.92× standalone (Mar-26 book, reference only); **1.70× core bank** (market cap less listed stakes after the 20% discount, over Sep-26 core book).
  - Values are struck at 31 Mar 2026 and rolled forward to 2 Nov 2026 (grown at Ke, less the FY26 dividend).
  - Peer-implied Ke (FY26 trailing): ICICI 10.7%, Axis 10.6%, Kotak 8.9%, SBI 12.9%, HDFC Bank 11.1%.
  - Subsidiary dividends (₹2,242 cr FY26) are stripped from core RoE. The effect is about 0 bp, because removing the investment at cost offsets it (core 14.61% vs 14.62%).
  - Normalised FY26 core RoA is 166 bp: core 180, less 4 for subsidiary dividends, less 10 for through-the-cycle credit cost.
  - Total value of the six levers ≈ ₹1.18 lakh cr; ₹0.79 lakh cr weighted by feasibility (illustrative).
  - **Lever 7, capital return:** Tier 1 above 15% is ≈ ₹1.09 lakh cr FY29E.
    - Returning it lifts RoE by 1.9 pp, to 16.8%, about what the price implies (16.7%).
    - RoA is unchanged.
    - Value falls ≈ ₹36k cr, because RoE exceeds Ke (justified P/B > 1). It is an RoE optic, not value creation.
  - **CASA reasonableness:** the Base path needs 32% of FY27-29 new deposits to be CASA, against 21% delivered in the last four quarters. At 21%, FY29E CASA is 29.9% (path 33.5%) and RoA is 8.2 bp lower, which is more than the 3 bp headroom.
- **Tornado (FY29E RoA swing):** repo 16 bp, advances growth 15, credit cost 13, opex growth 11, deposit-war premium 7; regulation about 1 bp.
- **Funding-cost beta:** 0.37 same year, 0.62 long run (R² 0.94, n = 9).
- **Regulation:**
  - IRDAI commission caps cost the bank ₹873 cr of fees by FY29E; UPI MDR adds ₹564 cr.
  - HDFC Life VNB +₹279 cr net.

## 2. Deliverables and where they live
| Deliverable | Path | Status |
|---|---|---|
| Integrated Excel model | `models/HDFC_RoA_Path_FY29.xlsx` (built by `pipeline/build_hdfc_model.py`) | Done; IB-hygiene lint 0 issues; 29 reconciliation checks pass |
| Sector modules | `models/01-03_*.xlsx`, `decks/0*.pptx` | Done (bank RoA Shapley, IRDAI caps with Monte Carlo, UPI/MDR) |
| Steerco deck | `decks/HDFC_RoA_Steerco.pptx` + PDF | **ON HOLD**: do not touch. Built before the tornado, walk, anchors and beta; numbers still match |
| CEO memo | `decks/HDFC_CEO_Memo.docx` + PDF (2 pages) | Done |
| Cockpit | `viz/dashboard.html` (single file, Plotly) | Done (legacy; the site supersedes it) |
| SQL | `pipeline/warehouse.py` (DuckDB), `sql/01-06_*.sql`, outputs in `data/tidy/sql_results/` | Done |
| Tests and CI | `tests/` (19 pytest), `site/tests/engine.test.ts` (15 vitest), `.github/workflows/ci.yml`, `Makefile` | Green (CI run #7 on `9fc0e3e`) |
| Model audit | `docs/model_audit.md` | 0 critical, 2 warnings (1 open, see section 6) |
| Website | `site/` (Svelte 5 + Vite + D3 + Scrollama) | **Live**: https://site-two-eta-4o267upa77.vercel.app |

## 3. Pipeline (one entrypoint: `Makefile`)
- `make data sector` fetches public sources and rebuilds the sector modules.
- `make all`:
  - rebuilds the HDFC model (twice, so the Tornado tab carries the recalculation; LibreOffice headless);
  - runs `export_scenarios.py` → `data/tidy/hdfc_model_outputs.json`, then the SQL warehouse and queries, memo, cockpit and Tableau extracts;
  - runs `pipeline/export_site_data.py` → `site/public/data/model.json` and `story.json`;
  - then the checks, pytest, ruff, xlsx lint and the site build plus vitest.
- `make ci-local` runs a clean clone of HEAD through `make all`; run it before every push.
- `make deck` builds the steerco deck (on hold).
- **Gitignored caches:** `data/raw/factiq/` (verbatim call quotes). `pipeline/call_topics.py` keeps the committed outputs when the cache is absent, which is why CI passes on a clean checkout.

## 4. Website ("The 2% Question")
- **Stack:**
  - Svelte 5 (runes), Vite 6, TypeScript, D3 v7, Scrollama, KaTeX;
  - @primer/octicons (UI icons only);
  - @fontsource EB Garamond and IBM Plex Sans/Mono;
  - Vitest. Bundle about 163 KB gzipped.
- **Hosting:**
  - Vercel project `site`, team `anklesh-s-projects`, rootDirectory `site`, `site/vercel.json` (vite, `npm ci`, `npm run build`, output `dist`).
  - Production auto-deploys on every push to `claude/wonderful-noether-vgfm7p`.
  - The public alias is the one above; other `*.vercel.app` URLs sit behind Vercel SSO, which is expected.
  - A custom domain is optional (user action in Vercel → Domains).
- **Engine:**
  - `site/src/lib/engine.ts` is a line-by-line port of the Excel FY27E-FY29E projection.
  - Parity tests prove RoA within 0.1 bp and value per share within ₹0.5 for all three scenarios.
  - Do not change it without re-running the tests.
- **State:** `site/src/lib/store.svelte.ts` (AppState: model, story, preset, shift, leverOn; derived drivers, result, scenarioResults; URL hash `#w=` for workbench state).
- **Layout (v2.1):**
  - A 12-column grid, `--wide` 1080 px. Prose sits in columns 1-8 (`--main` 700 px); the right rail is columns 9-12; wide exhibits span all 12.
  - Primitives in `site/src/lib/`:
    - `Row.svelte` (main plus `rail` snippet);
    - `Exhibit.svelte` (numbered frame: title, units, source, Data toggle; `wide` prop);
    - `Stat.svelte` (stat tile);
    - `Spot.svelte` (line-style spot illustrations: vault, ladder, steps, scales, gears, receipt, qr, coins, shield, eye, stop, flow);
    - `BankGlyph.svelte` (neutral bank emblem);
    - `ChapterHead.svelte`, `Note.svelte` (on-chart annotation), `Palette.svelte` (⌘K menu).
  - Global helpers in `app.css`: `.pair` (two exhibits side by side) and `.rnote` (rail note).
- **Page order (`site/src/App.svelte`):**
  - masthead: bank glyph, thesis headline, standfirst, the `AtAGlance` panel;
  - 01 Answer: `AnswerTiles` + Exhibit 1 `HeroRoa`;
  - 02 Merger: `RupeeOfAssets`, Exhibit 2 `SmallMultiples`, Exhibit 3 `Waterfall` with stat tiles;
  - 03 Peers: stat tiles, Exhibit 4 `PeerGap` + Exhibit 5 `Beeswarm`;
  - 04 Run-off: `FundingMix`, Exhibit 6 `Ladder`, `CreditCycle`;
  - 05 Moves: scrolly with Exhibit 7 `Waterfall` and step cards, Exhibit 8 `Dumbbell`, moves table with bars and feasibility dots;
  - 06 Value: `PbEquation`, Exhibit 9 `RoeBars` + Exhibit 10 `ValueBullet`, 10 bp tile;
  - 07 Risks: Exhibit 11 `Tornado`, Exhibit 12 `BetaScatter` with beta tiles, `RiskCards`;
  - 07 also carries Exhibit 13 (break-evens table), Exhibit 14 `StressGrid` (live engine, repo × credit cost) and the pre-registered Q3 FY27 calls;
  - 08 Plan: Exhibit 15 `Roadmap` (Gantt) + KPI tiles;
  - Appendix A: "Test the answer yourself", `ModelFlow` + the collapsible `sections/Workbench.svelte` (live model);
  - Appendix B: `sections/Changelog.svelte` (release notes, formulas, source register, caveats), then reproducibility and footer.
- **Palette:** tokens in `site/src/app.css`, light and dark, validated with the dataviz validator.

  | Token | Light | Dark |
  |---|---|---|
  | s1 | #1C68AE | #4A8BD4 |
  | s2 | #B26F0E | #C58516 |
  | s3 | #0E9A7E | #19A585 |

  Brand #004C8F; target red #ED232A; paper #F7F5F0.
- **QA script pattern:**
  - Playwright at 1440, 1024 and 390 px;
  - assert equal left edges for h1, h2, `.prose` and `.exhibit`;
  - no element past the grid's right edge, `scrollWidth == viewport`, no console errors.

## 5. Decisions already made (do not re-open unless the user asks)
- **The real bank, HDFC Bank,** was chosen because the case has a stake: the largest private bank, a structural gap to ICICI Bank, a missed margin guide, exposure to both the IRDAI and UPI changes, and a 50.2% stake in HDFC Life.
- **Data sources:**
  - Public data only. Screener.in is secondary, tied to filings. FactIQ is used for RBI, NPCI and call transcripts.
  - **data.gov.in allowed from 4 Nov 2026** (ban lifted by the user), local runs only via `pipeline/datagov.py`; raw cache gitignored, derived CSVs committed. No dataset chosen yet; use it only where FactIQ or filings lack the series.
- **Steerco deck** on hold. **Tableau:** ignore for now (extracts are kept, not deleted).
- **Site:**
  - Audience is a consulting partner or case jury. The analysis and recommendation lead; the workbench sits in an appendix ("people pay for analysis, not the bench").
  - Neutral bank glyph, not the HDFC logo. Deployed on Vercel.
  - The site must look different from the user's other repos (Next.js/Vercel dashboards); Svelte was chosen for that reason.
- **Resources reviewed and not used:**
  - shadcn admin, Tremor, Aceternity, React Bits, fintech dashboard UI: they give a SaaS look, and they are React;
  - Superset, Redash, Panel, Vizro, Perspective, Glue: BI tools, not editorial;
  - WebGPU; Observable Framework.

  Used as references: Reuters Graphics, FT, Salt DS, Midday, Scrollama.
- **Earlier choices:** "Neither for now" to GitHub Pages and to a scheduled re-run.

## 6. Open items (pick up here)
1. **Roadmap from the 4 Nov 2026 gap audit** (7-agent review, 6 dimensions plus a case-jury critic). Step 1 is done; do the rest in order, pausing for review after each:
   - **2. Quarterly primary-source pull: deck panel DONE (4 Nov 2026).** Output `data/tidy/hdfc_quarterly_panel.csv`, Q2 FY24-Q2 FY27, every value cited to deck and page:
     - balance sheet; NIM; yield and cost of funds; CASA; new-format advances mix;
     - GNPA bridge (ties exactly every quarter); credit cost (gross, net, INR); provisions and specific PCR;
     - CRAR, Tier 1, CET1; LCR; NSFR.
     - Readings so far:
       - borrowings fell from 25% to 13% of funding;
       - the CD ratio fell from 110% to 96%;
       - cost of funds fell from 4.9% to 4.4%;
       - NIM still fell, from 3.46% (Q2 FY25) to 3.16%, because asset yields fell faster (8.4% to 7.6%);
       - CASA slid from 38% to 32%;
       - LCR fell from a 128% peak to 113%.

     Rest of step 2, also done:
     - **IR26 segment note** → `data/tidy/hdfc_segments.csv`. Pre-tax return on segment assets, FY25 → FY26:
       - wholesale 3.6% → 2.3%;
       - retail 1.8% → 2.0%;
       - treasury 0.5% → 1.8%.
     - **Sch 4:** legacy bonds ₹2.39 → ₹2.08 lakh cr; foreign borrowings ₹1.17 lakh cr.
     - **PSLCs:** bought ₹76k cr of small and marginal farmer certificates (a sub-target shortfall cost); sold ₹2.0 lakh cr of micro and general certificates.
     - **Floating provisions:** ₹9,000 cr built in FY26.
     - **Pillar 3 Sep-26:** RWA ≈ ₹33.8 lakh cr, split 89% credit, 1% market, 10% operational. That confirms the model's net worth / Tier 1 proxy (₹34.0 lakh cr); RWA density is about 74% of assets.
     - **Market share:** deposits 10.8% → 11.5% (ties to the bank's disclosure); credit (proxy) 14.7% → 13.2%.
     - **Merger-synergy metrics are not disclosed** by the bank, so they are not estimated.
     - **RIDF deposits** are not broken out in the standalone notes; the PSLC purchases stand in as the PSL cost proxy.

     Not yet used by the model or site; steps 3-6 consume it.
   - **3. Marginal funding cost: DONE (4 Nov 2026).** The cost of deposits now prices the term-deposit share of new deposits at the fresh rate:
     - fresh rate = system rate 5.61% + 0.75 × repo change since Sep-26 + scenario premium;
     - the incremental CASA share is implied by the CASA path;
     - with the new term at zero, the formula is exactly the old one;
     - lever 2 is now priced against the fresh rate.

     CRR and DICGC are left out on purpose: CRR is already in the liquidity yield and DICGC in opex, so adding them would double count.
   - **4. Defensible levers: DONE (4 Nov 2026).**
     - Re-mix is net of the credit-cost gap, with the capital consumed and its economic profit.
     - A feasibility-weighted value column.
     - Capital return added as lever 7 (RoE, not RoA).
     - CASA path tested against the share delivered.
     - Joint vs sum and phasing are documented rather than modelled: the levers are linear in FY29E, and all land by mid-2028.
     - Not done: cost to achieve, because there is no public basis for it; the feasibility weight stands in.
   - **5. Regulatory overlay: DONE (4 Nov 2026).** New Regulation tab (an overlay, not in the scenario path):
     - **Net effect −1.0 bp of FY29E RoA:**
       - ECL recurring −2.7 bp;
       - CRR +1.6 bp;
       - LCR 0 (RBI: the package is about +6 pp net; headroom 13 pp);
       - PSL 0 (already in the base).
     - **ECL day one:** a ₹33.2k cr top-up = 0.71 pp CET1 gross, covered by ₹36.8k cr of floating and contingent provisions if they can be applied.
     - **Exhibit 11:** retitled, plus a bound paragraph.
     - **Not sourced:** the ECL transition relief (Reuters is paywalled; not claimed) and PSLC trading fees (not disclosed).
   - **6. "What would change our answer": DONE except say-do (4 Nov 2026).**
     - **Break-evens** (`pipeline/breakevens.py` → `data/tidy/hdfc_breakevens.csv`, from the tornado recalculations). Base headroom is 2.4 bp over 2.0% (with levers and the overlay). The base case falls below 2% at:
       - repo 5.56% (base 5.75%);
       - credit cost 0.73% (0.68%);
       - opex growth 10.7% (10.0%);
       - CASA 32.4% (33.5%);
       - deposit premium +18 bp;
       - borrowings retired 45% (60%).

       Ke break-even for value = ₹700 is 12.11%.
     - **2D stress grid:** live on the site, computed by the engine.
     - **Q3 FY27 calls**, frozen in `data/inputs/hdfc_q3fy27_predictions.csv` (registered 4 Nov 2026), each halfway from the Sep-26 actual to the model's FY27E:
       - CD ratio 94.5%;
       - borrowings / funding 11.1%;
       - CASA 32.3%;
       - deposits ₹34,492 bn;
       - credit cost 50 bp;
       - NIM 3.20% (±0.05).

       **Score them when the Q3 FY27 deck is out (mid-Jan 2027):** fill `actual_q3fy27` and `verdict`.
     - **Not done:** the say-do extension beyond NIM (needs new FactIQ transcript claims). It is the next item if wanted.
   - **7. One-page trading comps** (core P/B, P/E, RoA, RoE, CASA, CD ratio, CET1, growth) plus merger precedents (ICICI 2002, IDFC First).
   - **8. CEO "so what" page:**
     - three decisions with trade-offs;
     - variant view (management / consensus / we say);
     - "is 2% the right target" mix check;
     - stakeholder map;
     - first-100-days KPI tree.
   - **9. Packaging:**
     - README order;
     - OG image and screenshot;
     - bind hand-typed site numbers to story.json;
     - clickable sources;
     - source confidence column;
     - evidence-to-decision table.
   - **Skipped on purpose:** full ECL stage model, Monte Carlo, sentiment analysis, macro transmission, profit pool, backtest, bigger workbench, sell-side deliverables, DDM, peer P/B regression, new front-end libraries.
   - **Thesis decision pending:** the Ke caveat (break-even 11.96% vs peer-implied 10.6-11.1%) may warrant reframing chapter 06's title "The share price already assumes success". The user decides.
2. **Steerco deck refresh**, only when the user takes it off hold: add the tornado, RoA walk, peer anchors and beta. Deck numbers are now stale (pre-roll-forward).
3. **Minor site polish:** at 390 px, two pre-existing SVG labels overhang the gutter by about 4 px:
   - "₹1.93 lakh cr" in `charts/Ladder.svelte`;
   - "same year 0.37" in `charts/BetaScatter.svelte`.
4. **Optional:** a custom domain for the site (user action in Vercel).
5. **Optional:** README screenshots or a GIF of the site.

## 7. Session log (newest first)
- **4 Nov 2026, roadmap step 6 (what would change our answer):**
  - New `pipeline/breakevens.py` (in the Makefile and Windows runner), with 3 tests in `tests/test_answer_tests.py`.
  - Frozen Q3 FY27 predictions.
  - Site chapter 07: Exhibits 13-14 (break-evens and the stress grid, `charts/StressGrid.svelte`) and the predictions table; the Plan exhibit is renumbered to 15.
  - Story gains `breakevens` and `predictions`.
- **4 Nov 2026, roadmap step 5 (regulatory overlay):**
  - New Regulation sheet: ECL, CRR, LCR and PSL blocks, each with the FY29E RoA effect and the net overlay. It is also in the export and the Cover table of contents.
  - Story gains a `regulation` dict. Chapter 07 is reworded, and its "recalculated N times" figure is now bound.
  - Headline RoA with levers after the overlay: 2.02% Base.
- **4 Nov 2026, roadmap step 4 (defensible levers):**
  - Levers tab gains:
    - re-mix risk inputs (yield gap 4.0 pp, credit-cost gap 2.0 pp, risk-weight gap 0.75; all labelled assumptions);
    - a capital-consumed block;
    - a feasibility-weighted value column;
    - lever 7 (capital return);
    - a CASA reasonableness block.
  - The engine ports the re-mix change, and parity still holds (18 vitest).
  - Headline: with levers 2.06% → 2.03% (levers 16.7 → 14.0 bp); lever value ₹1.4 → ₹1.18 lakh cr. Values per share are unchanged (the levers sit outside the valuation).
- **4 Nov 2026, roadmap step 3 (marginal funding cost):**
  - New inputs: fresh rate, repo at the observation date, fresh beta, and the `td_prem` scenario driver (in the tornado).
  - New Model lines: incremental CASA share, book TD rate, fresh TD rate; cost of deposits gains the marginal term.
  - Engine ported, with 2 new parity checks per year.
  - Headline moves: Base 1.86% → 1.89% (with levers 2.04% → 2.06%); value ₹492-558 → ₹506-576; break-even Ke 11.96% → 12.11%; lever 2 3.0 → 1.9 bp.
  - The site masthead, the Ch04 title and the Ch08 RoA KPI are now bound to the engine (no longer hand-typed).
- **4 Nov 2026, roadmap step 2 (deck panel):**
  - Downloaded 12 HDFC decks; the old hdfcbank.com links had moved to hdfc.bank.in.
  - `fetch_docs.py` gained `--symbols`/`--kinds` filters, creates `data/raw/ir/`, and reads `data/inputs/ir_url_overrides.csv`.
  - New `extract_hdfc_quarterly.py` (header-aware text extract, local only) and `hdfc_quarterly.py` (tidy panel, in CI), with 8 tests in `tests/test_quarterly_panel.py`.
  - Then the rest of step 2:
    - fetched IR26 and Pillar 3 Sep-26 (`fetch.py --only ...`);
    - hand-transcribed the segment note, Sch 4, PSLCs and Pillar 3 into `data/inputs/hdfc_ir26_segments.csv`;
    - added RBI system deposits and credit (FactIQ);
    - the panel gained deposit and credit share, plus `hdfc_segments.csv`;
    - 10 tests now.
  - Gotcha: from FY26 the bank reclassified the advances mix (Mar-25 retail 50% old basis vs 55% new), so only new-format tables feed the mix.
- **4 Nov 2026, local resume and roadmap step 1:**
  - Moved from the cloud session to a local clone (nothing lost; resumed at `c38ab6d`).
  - Commit identity changed to `DogInfantry <ankleshrawat5@gmail.com>`; still no AI attribution.
  - data.gov.in ban lifted (local runs only); `data/raw/datagov/` added to `.gitignore`. Rules updated in `CLAUDE.md`, `docs/data_sources.md` and `docs/NEW_CHAT_PROMPT.md`.
  - Local Windows build works without `make` or WSL: LibreOffice installed via winget; the Linux-only `pipeline/recalc.sh` was replaced by the cross-platform `pipeline/recalc.py`; Python runs from the gitignored `.venv` with `-X utf8` (the Windows default encoding breaks ₹ otherwise). The baseline reproduced CI's committed outputs, differing only by 15th-digit float noise.
  - Gap audit, plus a triage of 28 ChatGPT suggestions (9 do, 11 partial, 8 skip), produced the roadmap in section 6.
  - Step 1, valuation consistency pack (closes open item 1 / audit finding 1):
    - core-bank RoE ex subsidiary dividends;
    - roll-forward to the price date;
    - core-bank P/B and implied RoE (17.9% → 16.7%);
    - break-even Ke 11.96%;
    - peer-implied Ke table;
    - normalised FY26 RoA 166 bp;
    - 0.76%/0.69% credit-cost label fixed.
  - Base value ₹471-533 → ₹492-558. Engine ported, with 3 new parity tests (18 vitest). Chapter 06 rail note now states the Ke caveat.
- **3 Nov 2026, v2.1 (`9fc0e3e`):**
  - Feedback was "placement off, too much pure text". Fixed it with one 12-column grid with aligned edges, a right rail, and a visual for every argument (components listed in section 4).
  - The export added `funding_mix`. Exhibit 13 (roadmap) added.
- **3 Nov 2026, v2.0 (`2f6ca67`, `a52bc60`):**
  - Feedback (user plus a GPT audit) was "amateurish and vague". Rebuilt as an argued editorial long-read: answer first, 12 numbered annotated exhibits, workbench moved to an appendix, bank glyph in the masthead.
  - Public URL added to the README.
- **3 Nov 2026, v1.0 (`5377d0d`, `204e1ef`):** first Svelte site; engine port with parity tests; Vercel config (the user imported the repo into Vercel themselves).
- **Before that:**
  - data v2;
  - HDFC model and lint;
  - deck, memo and cockpit;
  - the v3 analytics: tornado, Shapley walk, peer anchors, beta regression, call tracker, DuckDB SQL, pytest, CI, Makefile, model audit;
  - CI fix for the gitignored FactIQ cache.
