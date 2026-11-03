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

## Visual standards
- **Chart choice:** FT Visual Vocabulary.
- **Bridges:** IBCS-style fixed variance colours.
- **Storytelling:** Storytelling with Data decluttering. Decks use a pyramid / SCQA structure with the answer on the first slide.
- **Dashboard:** validated categorical palette, light and dark tokens, one y-axis per chart (no dual axes), a table view behind every chart, and hover on every mark.
