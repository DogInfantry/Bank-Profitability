# Project state: HDFC Bank, the path back to 2% RoA

Last updated: **3 Nov 2026**, after commit `9fc0e3e` ("Site: one page grid and a visual for every argument"). Data is as of 3 Nov 2026 (financials to Q2 FY27; price ₹700 on 2 Nov 2026).

Standing rules are in `/CLAUDE.md`. This file covers state, numbers, decisions and what is open.

---

## 1. The answer (headline numbers; all from `data/tidy/hdfc_model_outputs.json`)
| Metric | Downside | Base | Upside |
|---|---|---|---|
| RoA FY29E, before levers | 1.32% | **1.86%** | 2.25% |
| RoA FY29E, with six levers | 1.50% | **2.04%** | 2.43% |
| RoE FY29E, before levers | 10.6% | 14.6% | 17.5% |
| Value per share (residual income to sum of the parts) | ₹254-269 | **₹471-533** | ₹632-733 |

**Thesis:** HDFC Bank's RoA problem is a **funding** problem created by the July 2023 merger, not a cost problem. Run-off of legacy borrowings gets RoA to 1.86%. Six funding-led moves (+17.8 bp) get it to 2.04%. The ₹700 price already implies a **17.9% RoE**, and the base case gives 14.6%.

**Key facts used throughout:**
- **Merger effects:**
  - NII / average assets fell from 3.83% (FY23) to 3.11% (FY26); opex fell from 2.10% to 1.76%.
  - Shapley RoA walk, FY23 to Q2 FY27: −20 bp in total (NII −55, other income −11, opex +31, provisions +16).
- **Gap to ICICI Bank, FY26:** 43 bp (NII 63, provisions 25; HDFC Bank ahead by 27 bp on opex).
- **Borrowings and funding cost:**
  - ₹1.93 lakh cr of borrowings mature within a year; base case replaces 60% with deposits.
  - Borrowings fall from 19% of funding (FY25) to 7% (FY29E); NIM rises to 3.51%.
  - Cost of borrowings 7.80% vs cost of deposits 4.76% (FY26).
- **Credit cost:** 0.48% recent vs 0.69% through the cycle; normalisation costs about 10 bp of RoA.
- **Six levers, bp of FY29E RoA:**
  - re-mix advances 5.3;
  - productivity 3.8;
  - CASA 3.4;
  - retire borrowings 3.0;
  - fees 1.9;
  - UPI 0.4.

  Peer anchors close 28-49% of the gap to a named peer.
- **Valuation:**
  - CAPM Ke 13.13%, g 8%; each 10 bp of RoA ≈ ₹84k cr of equity value; price P/B 1.92×.
  - Total value of the six levers ≈ ₹1.5 lakh cr.
- **Tornado (FY29E RoA swing):** repo 20 bp, advances growth 15, credit cost 13, opex growth 11; regulation about 1 bp.
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
  - 08 Plan: Exhibit 13 `Roadmap` (Gantt) + KPI tiles;
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
  - **Not** data.gov.in.
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
1. **Valuation roll-forward (decision pending from the user).** Values are struck at 31 Mar 2026 but compared with the 2 Nov 2026 price. Rolling forward at Ke, less the FY26 dividend, lifts the base case to about ₹492-559. The conclusion is unchanged (still below ₹700). It is audit finding 1, "Open".
2. **Steerco deck refresh**, only when the user takes it off hold: add the tornado, RoA walk, peer anchors and beta.
3. **Minor site polish:** at 390 px, two pre-existing SVG labels overhang the gutter by about 4 px:
   - "₹1.93 lakh cr" in `charts/Ladder.svelte`;
   - "same year 0.37" in `charts/BetaScatter.svelte`.
4. **Optional:** a custom domain for the site (user action in Vercel).
5. **Optional:** README screenshots or a GIF of the site.

## 7. Session log (newest first)
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
