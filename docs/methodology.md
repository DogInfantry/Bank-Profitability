# Methodology

## Principles
- **Standalone, primary-first.** Bank figures are standalone. Every input row carries a source file, page and status (`primary`, `secondary-tied`, `derived`). Screener.in is a secondary aggregator, used only after its figures tie to the bank's own filing.
- **Live models.** Hard-coded numbers exist only on input tabs, each with a cell comment naming its source. Everything else is a formula. Python outputs that cannot be formulas (Shapley, Monte Carlo) are labelled as such, and the seed is given where one is used.
- **Reconcile, then publish.** `python -I pipeline/checks.py` recalculates all three workbooks headlessly and fails on any FAIL. Differences that are definitional are marked EXPLAINED, with the reason.
- **Label inference.** Anything that is a judgement or rests on an assumption (PPT mix, MDR value split, a cap extension) is labelled on the slide or tab.

## P1: bank RoA benchmark
| Item | Definition |
|---|---|
| NII | Screener `Revenue - Interest` (ties to deck NII) |
| Opex | Screener `Expenses + Depreciation - provisions`. Screener's Expenses line combines opex and provisions for banks. |
| Provisions | From the bank deck or NSE XBRL, excluding tax. SBI's "Total Provisions" line includes tax, so it is derived as operating profit - PBT. |
| HDFC Q2 FY27 | Parent PPOP from NSE XBRL Integrated Filing. Provisions = PPOP - PBT. |
| Average assets | (opening + closing) / 2. Q2 FY27 uses Mar-26 and Sep-26 and is annualised x4. |
| RoA tree | NII + other income - opex - provisions - tax = PAT, all as % of average assets. Reconciles exactly. |
| Shapley | RoA = (NII + OI - opex - prov) x (1 - t). RoE adds leverage. Each factor's contribution is its marginal effect averaged over all 2^n orderings, so contributions sum exactly to the gap regardless of order. A sequential bridge would hand the tax-rate interaction to whichever line moves last. |
| Sensitivity | ΔRoA = shock x (1 - effective tax rate). ΔRoE = ΔRoA x leverage. |
| Say vs do | FactIQ quote-anchored earnings-call claims, scored against the NIM the bank later reported (in its own deck). The table shows paraphrases, each linking to its verbatim quote. |

Known gaps: computed RoA runs 0-16 bp below reported because banks use daily-average assets. One-offs are flagged but not stripped: SBI's Yes Bank stake gain, Axis's one-time provision, HDFC's transaction gains. NIM bases differ: HDFC reports on total assets, the others on interest-earning assets.

## P2: insurance distribution under the proposed caps
1. **Sector economics** (IRDAI AR 2024-25, Tables I.9-I.10):
   - commission vs premium growth;
   - new-business commission intensity = (first-year + single-premium commission) / (first-year + single premium);
   - EoM proxy = (commission + opex) / premium.
2. **Cap rules** (consultation Part 1, Box 2/4A/4B) are kept as a parameter table. They are proposals, not final rules.
3. **Channel gap:** Part 2 Annexure 3 Table 4 average first-year commission by channel, minus the cap blended at an assumed PPT mix. The default mix is 50% at ≥10 years and 8% pure term; both are editable orange cells.
4. **Rupee reset:** gap x first-year premium allocated to channels by their share of individual new-business premium (Handbook T99). This is a lower bound, because it compares averages against the cap while channel maxima reach 62-92%.
5. **Insurer exposure:** Handbook T100 channel mix x channel gap, scaled to the insurer's share of FYP. Also expressed as % of FY25 PAT (listed insurers only, Screener).
6. **Monte Carlo:** 10,000 draws, seed 20261102.
   - PPT mix ~ Dirichlet(base x 25)
   - term share ~ U(4%, 14%)
   - channel rate ~ Triangular(0.85 x avg, avg, avg + 0.25 x (max - avg))
7. **Promoter-bank link to P1:** bank-channel reset vs the promoter bank's FY26 other income.

Limits: IRDAI does not publish commission by PPT or by insurer x channel, so the cap test is directional.

## P3: UPI
- **Monthly data:** NPCI product statistics. Average ticket = value / volume.
- **App shares:** NPCI app-wise file. App names are normalised by our own rules in `normalise_app()`; the method is credited to koushikxy/upi-payments-dashboard, from which no files were copied (that repo has no licence).
- **Market concentration:** HHI = Σ(share%)², cross-checked against the reference value of 3,211.
- **30% cap:** the required monthly share loss = (share - 30) / months left, compared with an OLS trend over the last 13 months.
- **MDR pool:** trailing-12-month value x 29% P2M share (PIB FY26) x share of P2M value above ₹2,000 x (1 - exempt share) x 0.4% x 0.95 haircut for the ₹300 cap. It is shown as a grid because the split of value above and below ₹2,000 is not published.

## HDFC Bank: the path back to 2% RoA (integrated model)
`models/HDFC_RoA_Path_FY29.xlsx`, built by `pipeline/build_hdfc_model.py` on the framework in `pipeline/xlmodel.py`.

| Block | Method |
|---|---|
| Spreading | FY20-FY26 standalone P&L and balance sheet from IR26 schedules and ten-year highlights; one-offs isolated (FY26 ₹12,861 cr gain on sale of investments, ₹10,700 cr floating and contingent provisions). |
| Projection | FY27E-FY29E. Advances and deposits grow at scenario rates; borrowings run off from the IR26 maturity schedule at a scenario retirement share. Investments and liquidity balance the sheet. In-year retained profit is held as cash and deployed the next year, and treasury income runs on average assets excluding it, so the model has no circular reference and needs no iteration switch. |
| Rates | Yields and costs move with the fiscal-year average repo through betas (loans 0.55, deposits 0.35 base). Repo path from RBI actuals and the SPF round 102. |
| Margin | NII walk: volume effect = change in average interest-earning assets x prior NIM; margin effect = change in NIM x current assets; residual zero by construction. |
| ALM | Repricing gap from the IR26 maturity pattern; earnings at risk for +100 bp over 12 months, adding floating-rate advances beyond one year at an assumed 55% external-benchmark share (range 45-65%, not disclosed). Realised deposit beta = change in cost of deposits / change in average repo. |
| Fees | IRDAI: HDFC Life bank-channel first-year commission above the proposed caps x 1.3 for other insurers distributed, phased by a scenario severity. HDFC Life: half the commission saving kept as margin, 15% of bancassurance APE lost; value at the market-implied VNB multiple x 50.2% stake. UPI: P2M value above ₹2,000 (NPCI bands, 67.7%) x (1 - 30% exempt) x 0.4% x 0.95, times HDFC's payee share and a 30% acquirer share. |
| Credit | Through-the-cycle credit cost = FY21-FY26 average of loan-loss provisions / average advances (0.69%) vs FY24-FY26 (0.48%). |
| Capital | Tier 1 proxy on implied RWA density; internal capital generation = RoE x (1 - payout). |
| Valuation | Ke by CAPM (6.96% + 0.95 x 6.5% = 13.13%), g 8%. Justified P/B = (RoE - g)/(Ke - g) on FY29E core-bank RoE (PAT less subsidiary dividends after tax, over average net worth less subsidiaries at cost), applied to core book. Sum of the parts adds HDFC Life, HDB Financial and HDFC AMC at market value x stake less a 20% holding-company discount. Residual income FY27E-FY29E plus a terminal value growing at 5%. Both values are struck at 31 Mar 2026 and rolled forward to the 2 Nov 2026 price date (grown at Ke, less the FY26 dividend paid in between). Market-implied RoE solves the justified P/B for the current core-bank P/B: market cap less the listed stakes, over the latest (Sep-26) core book. Break-even Ke solves sum of the parts = price (two fixed-point passes). Peer-implied Ke = g + (RoE - g)/P/B on trailing FY26 figures. Peer P/B-RoE regression is reported but not used (R-squared about 0.001 on the five clean private banks). |
| Levers | Six driver changes on top of the selected scenario in FY29E, each converted to pre-tax, PAT, bp of RoA, RoE and equity value (at justified P/B). Priority score = RoA x feasibility / months to impact. |
| Scenarios | Base, Upside, Downside on every driver, chosen with a single selector (Dashboard!E5, named `Scenario`). `pipeline/export_scenarios.py` flips the selector, recalculates headlessly and writes `data/tidy/hdfc_model_outputs.json`; the deck, memo and cockpit read only that file. |

| RoA walk | Shapley attribution of HDFC's own RoA change (FY23 to FY24, FY24 to FY26, FY26 to Q2 FY27 annualised) across NII, other income, opex, provisions and tax rate; reuses `pipeline/shapley.py`. |
| Funding-cost beta | Annual cost of funds = interest expended / average (deposits + borrowings), FY16-FY26. Fiscal-year average repo is time-weighted from RBI Bank Rate change dates less the MSF spread (100 bp to Mar 2016, 50 bp to Mar 2017, 25 bp after). OLS of the change in cost of funds on the change in repo, same year and one-year lag, with a merger dummy for FY24. Nine observations, so it is used as a range-finder for the beta input. |
| Tornado | One driver at a time, the Base input row (FY27E-FY29E) is set to the element-wise min and max of the three scenario rows. The deposit beta instead runs 0.25 to the regression long-run beta. The whole workbook is recalculated in LibreOffice and FY29E RoA is read back. |
| Peer anchors | For CASA, borrowings share of funding, asset yield and UPI payee share, the share of the gap to a named benchmark (SBI, ICICI Bank, Axis Bank) that each lever closes. Lever sizes are unchanged. |
| Call topics | FactIQ earnings-call claim search per topic over the last eight calls. Retrieval is lexical and capped at 50 claims, so counts indicate emphasis, not completeness. |

**Excel standard.** Garamond throughout, no italics; blue inputs, black formulas, green cross-sheet links, red checks; grey fill only on inputs and historical columns; no merged cells; one formula pattern per row per block; no numbers inside formulas other than 0, 1 and 2. `pipeline/xlsx_lint.py --strict` enforces all of these and runs inside `checks.py`.

## Visual standards
- **Chart choice:** FT Visual Vocabulary.
- **Bridges:** IBCS-style fixed variance colours.
- **Storytelling:** Storytelling with Data decluttering. Decks use a pyramid / SCQA structure with the answer on the first slide.
- **Dashboard:** validated categorical palette, light and dark tokens, one y-axis per chart (no dual axes), a table view behind every chart, and hover on every mark.
