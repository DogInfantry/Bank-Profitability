"""Write the data the front end (site/) needs, all read from existing outputs; nothing typed by hand.

site/public/data/model.json     engine inputs: FY26 opening state, scenario driver tables, fee, lever and valuation inputs
site/public/data/story.json     history, scenario outputs, walk, tornado, beta, peers, anchors, call topics, checks, sources
The browser engine (site/src/lib/engine.ts) recomputes FY27E-FY29E from model.json; site/tests/engine.test.ts proves it
matches data/tidy/hdfc_model_outputs.json (the recalculated Excel) for all three scenarios.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T, I = ROOT / "data" / "tidy", ROOT / "data" / "inputs"
OUT = ROOT / "site" / "public" / "data"
XL = ROOT / "models" / "HDFC_RoA_Path_FY29.xlsx"
YEARS = ["FY20A", "FY21A", "FY22A", "FY23A", "FY24A", "FY25A", "FY26A", "FY27E", "FY28E", "FY29E"]
SCN = ["Base", "Upside", "Downside"]
DRIVERS = {  # engine key: Inputs-tab label prefix
    "repo": "Policy repo rate, fiscal-year average", "b_loan": "Yield beta: loans", "b_inv": "Yield beta: investments and liquidity",
    "b_dep": "Cost beta: deposits", "b_bor": "Cost beta: borrowings", "g_loan": "Advances growth", "g_dep": "Deposit growth",
    "casa": "CASA ratio, year end", "runoff": "Share of maturing borrowings retired", "g_fee": "Core fee income growth",
    "oi_pct": "Treasury and other non-fee income", "irdai": "IRDAI cap severity on bank fees", "g_opex": "Operating expense growth",
    "cc": "Credit cost", "td_prem": "Premium over the system fresh rate",
}
FIXED = {"matur": "Borrowings maturing in year", "spread_td": "Term deposit cost premium over CASA", "tax": "Effective tax rate",
         "payout": "Dividend payout (paid on prior-year PAT)"}


def clean(x):
    if isinstance(x, float):
        return round(x, 10)
    return x


def ten_year() -> list[dict]:
    """FY18-FY26 RoA tree from HDFC Bank IR26 p234 (ten-year highlights), simple-average total assets."""
    h = pd.read_csv(I / "hdfc_10yr_highlights.csv").set_index("metric")
    fys = [c for c in h.columns if c.startswith("FY")]
    out = []
    for prev, fy in zip(fys, fys[1:]):
        a = (h.loc["total_assets", fy] + h.loc["total_assets", prev]) / 2
        r = lambda m: float(h.loc[m, fy] / a)  # noqa: E731
        out.append(dict(fy=fy, nii=r("nii"), oi=r("other_income"), opex=r("opex"), prov=r("provisions_total"), tax=r("tax"), roa=r("pat"),
                        cc=float(h.loc["loan_loss_provisions", fy] / ((h.loc["loans", fy] + h.loc["loans", prev]) / 2)),
                        pb=float(h.loc["price", fy] / h.loc["bvps", fy])))
    return out


def main():
    O = json.loads((T / "hdfc_model_outputs.json").read_text())
    b = O["Base"]
    col = lambda key, y, s="Base": O[s][key][2 + YEARS.index(y)]  # noqa: E731
    sc = lambda key, s="Base": O[s][key][2]  # noqa: E731   column-E scalar

    wb = openpyxl.load_workbook(XL)                 # inputs are hard-coded values, so formulas are not needed
    ws = wb["Inputs"]
    rows = {ws.cell(r, 2).value: r for r in range(1, ws.max_row + 1) if isinstance(ws.cell(r, 2).value, str)}
    drivers = {}
    for k, lab in DRIVERS.items():
        drivers[k] = {s: [ws.cell(rows[f"{lab}: {s}"], c).value for c in (12, 13, 14)] for s in SCN}
    fixed = {k: [ws.cell(rows[lab], c).value for c in (12, 13, 14)] for k, lab in FIXED.items()}
    fixed |= {k: ws.cell(rows[lab], 5).value for k, lab in {  # scalars for the marginal term-deposit rate
        "fresh0": "Fresh term-deposit rate, system, Sep-26", "repo_ref": "Repo rate when the fresh rate was observed",
        "b_fresh": "Fresh term-deposit rate beta to repo"}.items()}
    # FY26 repo: the live repo row's K column (FY26A); same value in every scenario
    live = rows["Policy repo rate, fiscal-year average: live"]
    repo_fy26 = ws.cell(live, 11).value
    if isinstance(repo_fy26, str):  # live row in K may be a link formula; fall back to the Base row's K
        repo_fy26 = ws.cell(rows["Policy repo rate, fiscal-year average: Base"], 11).value

    lev_ws = wb["Levers"]
    levers = []
    for r in range(1, lev_ws.max_row + 1):
        nm, size, unit, mech, feas, months = (lev_ws.cell(r, c).value for c in range(2, 8))
        if isinstance(nm, str) and isinstance(size, (int, float)) and isinstance(feas, (int, float)) and isinstance(months, (int, float)):
            levers.append(dict(name=nm, size=size, unit=unit, mechanism=mech, feasibility=feas, months=months))

    fy26 = {k: col(f"Model|{lab}", "FY26A") for k, lab in {
        "loans": "Advances", "fixed": "Fixed assets", "dep": "Deposits", "bor": "Borrowings", "ol": "Other liabilities and provisions",
        "eq": "Net worth, closing", "liq": "Investments, liquidity and other assets", "ta": "Total assets",
        "y_loan": "Yield on advances", "y_liq": "Yield on investments and liquidity", "casa": "CASA ratio, year end",
        "c_dep": "Cost of deposits", "c_bor": "Cost of borrowings", "fee": "Core fee income", "opex": "Operating expenses",
        "pat": "Profit after tax", "pat_core": "Profit after tax, core", "a_ta": "Average total assets"}.items()}
    fy26["cash_ret"] = 0.0
    fy26["roa_core_bp"] = b["Levers|RoA FY26A, core"][2]

    fees = dict(hlife_bank_reset=sc("Fees|HDFC Life bank-channel first-year commission above proposed caps"),
                other_ins_mult=sc("Fees|Uplift for other insurers distributed (HDFC ERGO, partners)"),
                pool=sc("Fees|Annual MDR pool at current run-rate"), p2m_g=sc("Fees|P2M value growth, Apr-Oct 2026 vs Apr-Oct 2025"),
                hd_share=sc("Fees|HDFC Bank share of payee volume"), acq_share=sc("Fees|Acquiring bank's share of MDR"),
                mdr_frac=[col("Fees|Share of year MDR is live", y) for y in YEARS[7:]])
    vk = {"rf": "Risk-free rate: 10-year G-sec", "beta": "Equity beta", "erp": "Equity risk premium, India", "g": "Long-term growth",
          "subs_cost": "Investment in subsidiaries at cost", "hold_disc": "Holding-company discount", "ri_g": "Residual income growth after FY29",
          "price": "Current share price", "life_m": "HDFC Life: market capitalisation", "life_s": "HDFC Life: HDFC Bank stake",
          "hdb_m": "HDB Financial Services: market capitalisation", "hdb_s": "HDB Financial Services: HDFC Bank stake",
          "amc_m": "HDFC AMC: market capitalisation", "amc_s": "HDFC AMC: HDFC Bank stake",
          "sdiv_sh": "Share of FY26 treasury and other income", "t_roll": "Years from 31 Mar 2026 to 2 Nov 2026", "bvps_now": "Book value per share, latest"}
    val = {k: sc(f"Valuation|{lab}") for k, lab in vk.items()}
    val["mcap"] = ws.cell(rows["Market capitalisation"], 5).value
    val["shares"] = val["mcap"] / ws.cell(rows["Share price"], 5).value
    val["target_bp"] = b["Levers|Target"][2]

    remix = dict(ygap=sc("Levers|Re-mix: yield gap, target segments over mortgages"), ccgap=sc("Levers|Re-mix: credit-cost gap"))
    model = dict(years=YEARS[7:], scenarios=SCN, fy26=fy26, repo_fy26=repo_fy26, drivers=drivers, fixed=fixed, fees=fees,
                 levers=levers, remix=remix, valuation=val, model_sha256=hashlib.sha256(XL.read_bytes()).hexdigest())

    # ------------------------------------------------------------- story
    hist_keys = {"roa": "Model|Return on average assets", "roe": "Model|Return on average net worth", "nim": "Model|Net interest margin on interest-earning assets",
                 "nii_a": "Model|NII / average assets", "oi_a": "Model|Other income / average assets", "opex_a": "Model|Opex / average assets",
                 "prov_a": "Model|Provisions / average assets", "tax_a": "Model|Tax / average assets", "casa": "Model|CASA ratio, year end",
                 "cc": "Model|Credit cost", "ci": "Model|Cost to income", "bor_share": "Margin|Borrowings / (deposits + borrowings), average"}
    series = {s: {k: [clean(col(v, y, s)) for y in YEARS] for k, v in hist_keys.items()} for s in SCN}
    outputs = {s: dict(before_bp=O[s]["Levers|RoA FY29E, scenario before levers"][2], levers_bp=O[s]["Levers|Levers"][2],
                       with_bp=O[s]["Levers|RoA FY29E with levers"][2], drift_bp=O[s]["Levers|Scenario drift to FY29E (margin, fees, cost, credit, mix)"][2],
                       sotp_ps=sc("Valuation|Sum of the parts per share", s), ri_ps=sc("Valuation|Residual income per share", s)) for s in SCN}
    lev_out = [dict(name=k.split("|")[1], pretax=v[0], pat=v[1], bp=v[2], roe=v[3], value=v[4], per_share=v[5], score=v[6])
               for k, v in b.items() if k.startswith("Levers|") and len(v) > 6 and isinstance(v[6], float)]
    anchors = [dict(lever=k.split("|")[1], hdfc=v[0], bench=v[1], source=v[2], gap=v[3], closes=v[4], share=v[5])
               for k, v in b.items() if k.startswith("Levers|") and len(v) > 5 and isinstance(v[2], str) and isinstance(v[5], float)]
    peers = [dict(bank=k.split("|")[1], avg_assets=v[2], roa=v[4], roe=v[5], mcap=v[6], pb=v[7], fit=v[8])
             for k, v in b.items() if k.startswith("Peers|") and len(v) >= 9 and isinstance(v[4], float) and isinstance(v[7], float)]
    walk = pd.read_csv(T / "hdfc_roa_walk.csv").drop(columns="source").to_dict("records")
    torn = pd.read_csv(T / "hdfc_tornado.csv").drop(columns="source").to_dict("records")
    beta = pd.read_csv(T / "hdfc_deposit_beta.csv").set_index("term")
    cof = pd.read_csv(T / "hdfc_cost_of_funds.csv")
    topics = pd.read_csv(T / "hdfc_call_topics.csv").to_dict("records")
    topics_latest = pd.read_csv(T / "hdfc_call_topics_latest.csv").fillna("").to_dict("records")
    checks = json.loads((T / "checks_summary.json").read_text()) if (T / "checks_summary.json").exists() else {}
    facts = pd.read_csv(T / "bank_facts.csv")
    q = facts[(facts.entity == "HDFCBANK") & (facts.period == "Q2FY27")].set_index("metric").value
    alm = dict(ear=sc("ALM|Earnings at risk, +100 bp"), ear_pct=sc("ALM|As % of FY26 NII"))
    story = dict(
        as_of="2026-11-03", years=YEARS, series=series, outputs=outputs, levers=lev_out, anchors=anchors, peers=peers,
        q2fy27_roa=float(q["pat"] * 4 / ((q["assets_open"] + q["assets_close"]) / 2)), price=val["price"],
        roe_implied=sc("Valuation|RoE the market is pricing"), ke=sc("Valuation|Cost of equity"), v10=sc("Valuation|Value of +10 bp RoA (equity value)"),
        ke_be={s: sc("Valuation|Cost of equity at which sum of the parts equals the price", s) for s in SCN},
        remix_capital=dict(shift=sc("Levers|Share of the book moved"), rwa=sc("Levers|Extra risk-weighted assets"),
                           equity=sc("Levers|Extra Tier 1 capital at the projected ratio"), ep=sc("Levers|Re-mix PAT less a Ke charge on that capital")),
        regulation=dict(ecl_gross=sc("Regulation|Day-one top-up on FY27E advances"), ecl_buffer=sc("Regulation|Floating and contingent provisions already held"),
                        ecl_cet1=sc("Regulation|CET1 effect of the gross top-up"), ecl_bp=sc("Regulation|FY29E RoA effect, recurring ECL"),
                        crr_bp=sc("Regulation|FY29E RoA effect, freed reserves earning the liquidity yield"), lcr_head=sc("Regulation|Headroom"),
                        net_bp=sc("Regulation|FY29E RoA effect of the rule changes"), roa_after=sc("Regulation|RoA FY29E with levers, after the overlay")),
        capital_return=dict(excess=sc("Levers|Excess Tier 1 capital, FY29E"), roe_uplift=sc("Levers|RoE uplift"), value=sc("Levers|Value effect of returning it")),
        casa_test=dict(observed=sc("Levers|Incremental CASA share delivered, Q2 FY26 to Q2 FY27"), path=sc("Levers|Incremental CASA share the path needs, FY27E-FY29E"),
                       casa29=sc("Levers|CASA ratio FY29E at the delivered share"), roa_bp=sc("Levers|FY29E RoA at risk if the delivered share persists")),
        peer_ke={nm: sc(f"Valuation|Implied Ke: {nm}") for nm in ("HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "State Bank of India")},
        roa_norm=dict(core=sc("Valuation|RoA FY26A, core"), sdiv=sc("Valuation|Less dividends from subsidiaries"),
                      cc=sc("Valuation|Less credit cost at through-the-cycle level"), norm=sc("Valuation|Normalised core-bank RoA, FY26")),
        norm_roa_bp=sc("Opex_Credit|RoA at risk if credit cost normalises"),
        ttc_cc=sc("Opex_Credit|Through-the-cycle credit cost, FY21-FY26 average"), recent_cc=sc("Opex_Credit|Recent credit cost, FY24-FY26 average"),
        irdai_fy29=col("Fees|Bank fee lost to caps", "FY29E"), mdr_fy29=col("Fees|HDFC Bank MDR revenue", "FY29E"), mdr_pool=fees["pool"],
        dvnb=sc("Fees|Net change in annual VNB"), alm=alm, walk=walk, tornado=torn,
        beta=dict(same_year=float(beta.loc["beta_same_year", "estimate"]), same_year_se=float(beta.loc["beta_same_year", "std_error"]),
                  lag=float(beta.loc["beta_lag_1y", "estimate"]), long_run=float(beta.loc["long_run_beta", "estimate"]),
                  long_run_se=float(beta.loc["long_run_beta", "std_error"]), r2=float(beta.loc["beta_same_year", "r_squared"]),
                  n=int(beta.loc["beta_same_year", "observations"]),
                  points=cof[["fy_end", "cost_of_funds_pct", "repo_avg_pct", "d_cof", "d_repo"]].dropna().to_dict("records")),
        topics=topics, topics_latest=topics_latest, checks=dict(total=checks.get("total"), fail=checks.get("fail"), explained=checks.get("explained")),
        model_sha=model["model_sha256"][:7],
        history=ten_year(), maturity=pd.read_csv(I / "hdfc_borrowing_maturity_mar26.csv")[["bucket", "amount_cr"]].to_dict("records"),
        icici_gap=pd.read_csv(T / "bank_shapley_FY26.csv").query("metric == 'RoA' and bank == 'HDFCBANK' and benchmark == 'ICICIBANK'")
            .drop(columns=["metric", "bank", "benchmark", "leverage"]).iloc[0].to_dict(),
        # Funding mix (closing balance sheet, ₹ cr): what the run-off does to the liability side, base case
        funding_mix=[dict(fy=y, **{k: col(f"Model|{lab}", y) for k, lab in {
            "dep": "Deposits", "bor": "Borrowings", "eq": "Net worth, closing", "ol": "Other liabilities and provisions"}.items()})
            for y in ("FY23A", "FY26A", "FY29E")],
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "model.json").write_text(json.dumps(model, default=clean))
    (OUT / "story.json").write_text(json.dumps(story, default=clean))
    print(f"wrote {OUT.relative_to(ROOT)}/model.json ({len(levers)} levers, {len(drivers)} drivers) and story.json")


if __name__ == "__main__":
    main()
