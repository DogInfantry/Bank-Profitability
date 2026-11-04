# Model audit: `models/HDFC_RoA_Path_FY29.xlsx`

Audit date 3 Nov 2026. Scope: whole workbook, model-integrity level (bank operating model with scenarios, levers and valuation). Method: the audit-xls checklist. Checks were run programmatically on a LibreOffice-recalculated copy of all three scenarios (`data/tidy/hdfc_model_outputs.json`) and on the formulas themselves (`pipeline/xlsx_lint.py`).

> Model type: bank operating model (driver-based, average-balance) with residual-income and sum-of-the-parts valuation. Overall: **Minor issues**. 0 critical, 2 warnings, 5 info.

## Findings
| # | Sheet | Cell / range | Severity | Category | Issue | Status |
|---|---|---|---|---|---|---|
| 1 | Valuation | Residual income and sum-of-the-parts per share | Warning | Timing | Values are struck at the valuation date (31 Mar 2026) but compared with the 2 Nov 2026 share price, 0.59 years later. Rolling equity value forward at Ke and deducting the FY26 dividend paid in between would lift both per-share values by about 4-5% (₹471 to about ₹492; ₹533 to about ₹559). It does not change the conclusion: the base case is still below ₹700. | **Closed 4 Nov 2026:** values now rolled forward on the Valuation tab (base ₹492-558). The tab also reports the break-even Ke (11.96%) at which the base case supports the price |
| 2 | Valuation | Present value of terminal residual income | Warning | Reasonableness | The terminal value is 86% of the residual-income excess over book, so the answer is sensitive to Ke, g and the 5% fade rate. The Sensitivities tab shows the Ke x g and RoE x Ke grids. | Accepted; disclosed |
| 3 | Model | Credit-deposit ratio, FY27E-FY29E | Info | Logic | The CD ratio is an output of the advances and deposit growth inputs, not a constraint. Scenario inputs keep it near 93%, which matches the "deposits are the binding constraint" recommendation. A user who flexes advances growth alone will see the CD ratio drift. | Noted on the Inputs tab |
| 4 | Model | L31:N31 (CASA), L41:N41 (UPI MDR) | Info | Colour code | Pure cross-sheet links were black instead of green. | **Fixed** |
| 5 | Levers | Rebuild CASA pre-tax uplift | Info | Assumption | The uplift uses a 4% term-deposit premium over CASA. This is an input, not disclosed by the bank; the cost of deposits is 4.76% (FY26). | Labelled as an assumption |
| 6 | Tornado | Whole tab | Info | Structure | Holds values from a Python recalculation, not live formulas. A one-at-a-time sensitivity of a full model cannot be done in cell formulas without iteration. | Labelled on the tab |
| 7 | Peers | Slope / intercept / R-squared | Info | Method | The P/B-RoE regression (R-squared 0.0006 on five clean private banks) is reported but not used for valuation; justified P/B is used instead. | Disclosed |

## Checks that passed
| Check | Result |
|---|---|
| Balance sheet balances, FY27E-FY29E, all three scenarios | Difference below ₹1 cr in every period |
| Net-worth roll-forward: prior + PAT - dividends = closing | Exact, all periods and scenarios |
| Tax = PBT x 25.17% | Exact |
| Dividends = 30% of prior-year PAT | Exact; FY26 actual payout was 31.9% |
| Formula errors (#REF!, #VALUE!, #DIV/0!, #N/A, Err:) | None after recalculation |
| Numbers inside formulas other than 0, 1, 2 | None (lint) |
| Formula pattern breaks within the historical and projection blocks | None (lint) |
| Pasted-over values in projection rows | None |
| Circular references | None. Treasury income runs on average assets excluding in-year retained profit, so the loop is removed structurally and no iteration switch is needed. |
| Hidden sheets or rows | None |
| Fonts | Garamond only, no italics, no merged cells (lint) |
| Colour convention | Inputs blue, formulas black, cross-sheet links green (after fix 4), checks red |
| Lever bridge: FY26 core + drift + levers = FY29E with levers | Exact (pytest `test_lever_bridge_adds_up`) |
| Model Checks tab | All PASS; the master flag on the Cover is green |
