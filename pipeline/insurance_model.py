"""P2: who loses under IRDAI's proposed commission caps and EoM glide path.

Builds models/02_Insurance_Distribution.xlsx (live formulas for the deterministic model; Monte Carlo
results pasted as values with the seed) and data/tidy/ins_*.csv for the dashboard.

Method (all FY25 base; every input is cited in data/inputs/irdai_*.csv):
  1. Sector economics: commission vs premium growth, NB commission intensity, EoM = (commission + opex) / premium.
  2. Cap gap by channel: Annexure 3 Table 4 average first-year commission by channel vs the Box 4B cap,
     weighted by an assumed premium-paying-term (PPT) mix (input cells, labelled ASSUMPTION).
  3. Rupee reset: channel gap x first-year premium allocated by channel (Handbook Table 99 shares).
     Average-vs-cap is a lower bound: within-channel dispersion (Table 4 maxima) means more premium sits above the cap.
  4. Insurer exposure: Handbook Table 100 channel mix x channel gap, scaled to each insurer's share of FYP.
  5. Monte Carlo (seeded) over PPT mix, channel commission rates and term share, for a P10-P90 range.
  6. EoM glide path: rupee expense reduction needed to reach 15% (Y2) and 12.5% (Y5) on the FY25 base.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell

ROOT = Path(__file__).resolve().parents[1]
INP = ROOT / "data" / "inputs"
TIDY = ROOT / "data" / "tidy"
OUT = ROOT / "models" / "02_Insurance_Distribution.xlsx"
SEED = 20261102

# ASSUMPTIONS (not in any public table): PPT mix of non-term individual first-year premium.
PPT_BASE = {"<5y": 0.10, "5y": 0.15, "6-8y": 0.20, "9y": 0.05, ">=10y": 0.50}
TERM_SHARE_BASE = 0.08  # pure-term share of individual first-year premium (assumption; protection ~ high-single-digit % of NB)
CHANNEL_MAP = {  # Annexure 3 channel -> (Table 99 rows, cap type)
    "Agents": (["Individual Agents"], "agent"),
    "Corporate agents - banks": (["Corporate Agents-Banks"], "entity"),
    "Corporate agents - others": (["Corporate Agents- Others*"], "entity"),
    "Brokers": (["Brokers"], "entity"),
}


def load():
    ir = pd.read_csv(INP / "irdai_inputs.csv")
    caps = pd.read_csv(INP / "irdai_life_caps.csv")
    ins = pd.read_csv(TIDY / "ins_life_insurers_FY25.csv")
    rs = list(openpyxl.load_workbook(ROOT / "data/raw/manual/irdai_handbook_2024_25/Part V.xlsx",
                                     read_only=True, data_only=True)["99"].iter_rows(values_only=True))
    t99 = {str(r[1]).strip(): float(r[23]) for r in rs[3:40] if r[1] and isinstance(r[23], (int, float))}
    return ir, caps, ins, t99


def g(ir, block, key, seg):
    return float(ir[(ir.block == block) & (ir.key == key) & (ir.segment == seg)].value.iloc[0])


def weighted_cap(caps, mix, kind):
    col = "entity_first_year" if kind == "entity" else "agent_first_year"
    c = caps[caps.product_class == "Individual non-linked/linked"].set_index("ppt_band")[col]
    return sum(mix[b] * c[b] for b in mix)


def channel_gap(ir, caps, mix, term_share, rates=None):
    term_cap = caps[caps.product_class == "Pure term multi-year"].iloc[0]
    out = {}
    for ch, (_, kind) in CHANNEL_MAP.items():
        rate = (rates or {}).get(ch, g(ir, "annex3", "channel_fyp_commission_avg", ch))
        cap = (1 - term_share) * weighted_cap(caps, mix, kind) + term_share * (
            term_cap.entity_first_year if kind == "entity" else term_cap.agent_first_year)
        out[ch] = (rate, cap, max(0.0, rate - cap))
    return out


def rupee_reset(ir, t99, gaps):
    fyp = g(ir, "sector", "fy_premium", "Public") + g(ir, "sector", "fy_premium", "Private")
    total_nb = t99["Total"]
    rows = []
    for ch, (rate, cap, gap) in gaps.items():
        prem = sum(t99[r] for r in CHANNEL_MAP[ch][0])
        fyp_ch = fyp * prem / total_nb
        rows.append(dict(channel=ch, indiv_nb_premium=prem, fyp_allocated=fyp_ch, avg_rate=rate, cap=cap,
                         gap_pp=gap, reset_cr=fyp_ch * gap / 100))
    return pd.DataFrame(rows)


def monte_carlo(ir, caps, t99, n=10000):
    rng = np.random.default_rng(SEED)
    keys = list(PPT_BASE)
    alpha = np.array([PPT_BASE[k] for k in keys]) * 25
    res = []
    for _ in range(n):
        mix = dict(zip(keys, rng.dirichlet(alpha)))
        term = rng.uniform(0.04, 0.14)
        rates = {}
        for ch in CHANNEL_MAP:
            avg = g(ir, "annex3", "channel_fyp_commission_avg", ch)
            mx = g(ir, "annex3", "channel_fyp_commission_max", ch)
            rates[ch] = rng.triangular(0.85 * avg, avg, avg + 0.25 * (mx - avg))
        res.append(rupee_reset(ir, t99, channel_gap(ir, caps, mix, term, rates)).reset_cr.sum())
    return np.array(res)


def insurer_exposure(ins, gaps, ir):
    fyp = g(ir, "sector", "fy_premium", "Public") + g(ir, "sector", "fy_premium", "Private")
    col = {"Agents": "indiv_nb_agents", "Corporate agents - banks": "indiv_nb_ca_banks",
           "Corporate agents - others": "indiv_nb_ca_others", "Brokers": "indiv_nb_brokers"}
    d = ins.dropna(subset=["indiv_nb_total_indiv_nb"]).copy()
    d = d[d.indiv_nb_total_indiv_nb > 0]
    k = fyp / d.indiv_nb_total_indiv_nb.sum()
    d["reset_cr"] = sum(d[c].fillna(0) * gaps[ch][2] / 100 * k for ch, c in col.items())
    d["reset_pct_total_premium"] = 100 * d.reset_cr / d.total_premium
    d["blended_gap_pp"] = 100 * d.reset_cr / (d.indiv_nb_total_indiv_nb * k)
    return d.sort_values("reset_cr", ascending=False)


PROMOTERS = {"SBI Life": "SBIN", "HDFC Life": "HDFCBANK", "ICICI Prudential": "ICICIBANK",
             "Axis MaxLife": "AXISBANK", "Kotak Mahindra Life": "KOTAKBANK"}


def promoter_bank_hit(expo, gaps, ir):
    """Bank-channel share of each bank-promoted insurer's reset, vs the promoter bank's FY26 other income (P1 data)."""
    fyp = g(ir, "sector", "fy_premium", "Public") + g(ir, "sector", "fy_premium", "Private")
    k = fyp / expo.indiv_nb_total_indiv_nb.sum()
    bank = pd.read_csv(TIDY / "bank_model_inputs.csv").query("period == 'FY26'").set_index("bank")
    rows = []
    for ins_name, sym in PROMOTERS.items():
        m = expo[expo.insurer.str.contains(ins_name, case=False, regex=False)]
        if m.empty:
            continue
        r = m.iloc[0]
        hit = r.indiv_nb_ca_banks * gaps["Corporate agents - banks"][2] / 100 * k
        oi = bank.loc[sym, "other_income"]
        rows.append(dict(insurer=r.insurer, promoter_bank=sym, bank_channel_reset_cr=hit,
                         bank_other_income_fy26=oi, pct_of_bank_other_income=100 * hit / oi,
                         pct_of_bank_pbt=100 * hit / bank.loc[sym, "pbt"]))
    return pd.DataFrame(rows)


def main():
    ir, caps, ins, t99 = load()
    gaps = channel_gap(ir, caps, PPT_BASE, TERM_SHARE_BASE)
    reset = rupee_reset(ir, t99, gaps)
    mc = monte_carlo(ir, caps, t99)
    expo = insurer_exposure(ins, gaps, ir)
    pat = {}
    for sym, name in [("SBILIFE", "SBI Life"), ("HDFCLIFE", "HDFC Life"), ("LICI", "Life Insurance Corporation")]:
        s = pd.read_csv(ROOT / f"data/raw/screener/{sym}_tables.csv")
        v = s[(s.section == "profit-loss") & (s.line_item == "Net Profit") & (s.period == "Mar 2025")].value
        pat[name] = float(v.iloc[0]) if len(v) else None
    expo["pat_fy25"] = expo.insurer.map(lambda n: next((v for k, v in pat.items() if k.lower() in n.lower()), None))
    expo["reset_pct_pat"] = 100 * expo.reset_cr / expo.pat_fy25
    TIDY.mkdir(exist_ok=True)
    reset.to_csv(TIDY / "ins_channel_reset.csv", index=False)
    expo.to_csv(TIDY / "ins_insurer_exposure.csv", index=False)
    promo = promoter_bank_hit(expo, gaps, ir)
    promo.to_csv(TIDY / "ins_promoter_bank_hit.csv", index=False)
    print(promo.round(2).to_string(index=False))
    pd.DataFrame({"reset_cr": mc}).describe(percentiles=[.1, .5, .9]).to_csv(TIDY / "ins_mc_summary.csv")
    write_xlsx(ir, caps, t99, reset, mc, expo)
    p10, p50, p90 = np.percentile(mc, [10, 50, 90])
    print(reset.round(1).to_string(index=False))
    print(f"MC distributor-income reset (INR cr): P10 {p10:,.0f}  P50 {p50:,.0f}  P90 {p90:,.0f}")
    print(expo[["insurer", "bank_ca_share", "blended_gap_pp", "reset_cr", "reset_pct_total_premium", "reset_pct_pat"]].head(10).round(2).to_string(index=False))


def write_xlsx(ir, caps, t99, reset, mc, expo):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(OUT, {"default_format_properties": {"font_name": "Garamond"}})
    F = {
        "title": wb.add_format({"bold": True, "font_size": 15}),
        "sub": wb.add_format({"font_color": "#6B7280", "text_wrap": True}),
        "hdr": wb.add_format({"bold": True, "bg_color": "#1F2937", "font_color": "white", "border": 1, "text_wrap": True}),
        "lbl": wb.add_format({"border": 1}),
        "inp": wb.add_format({"num_format": "#,##0.00", "font_color": "#1D4ED8", "bg_color": "#EFF6FF", "border": 1}),
        "asm": wb.add_format({"num_format": "0%", "font_color": "#9A3412", "bg_color": "#FFEDD5", "border": 1}),
        "num": wb.add_format({"num_format": "#,##0", "border": 1}),
        "pct1": wb.add_format({"num_format": "0.0", "border": 1}),
        "pctf": wb.add_format({"num_format": "0.0%", "border": 1}),
        "bold": wb.add_format({"num_format": "#,##0", "border": 1, "bold": True, "bg_color": "#F3F4F6"}),
        "wrap": wb.add_format({"text_wrap": True, "valign": "top"}),
    }
    p10, p50, p90 = np.percentile(mc, [10, 50, 90])
    tot = reset.reset_cr.sum()
    # 0_Answer
    a = wb.add_worksheet("0_Answer"); a.set_column("B:B", 120)
    a.write("B2", "Commission caps would reset distributor economics; private, bancassurance-led life insurers are most exposed", F["title"])
    a.write("B3", "IRDAI consultation (23 Sep 2026) is a PROPOSAL. FY25 base. Prepared by Anklesh, 2 Nov 2026.", F["sub"])
    priv_g = 100 * (g(ir, 'sector', 'total_commission', 'Private') / g(ir, 'sector', 'total_commission_PY', 'Private') - 1)
    priv_pg = 100 * (g(ir, 'sector', 'total_premium', 'Private') / g(ir, 'sector', 'total_premium_PY', 'Private') - 1)
    eom_priv = 100 * (g(ir, 'sector', 'total_commission', 'Private') + g(ir, 'sector', 'opex', 'Private')) / g(ir, 'sector', 'total_premium', 'Private')
    lines = [
        f"1. Distribution captured the growth: private life commission rose {priv_g:.0f}% in FY25 against {priv_pg:.0f}% premium growth (IRDAI AR Table I.9/I.10).",
        f"2. Private insurers' expense of management is {eom_priv:.1f}% of premium vs the proposed 15% (Y2) and 12.5% (Y5); LIC is already ~12.4%.",
        f"3. On average rates, first-year commission above the proposed caps is ~INR {tot:,.0f} cr a year (base PPT mix); Monte Carlo P10-P90 INR {p10:,.0f}-{p90:,.0f} cr.",
        "4. Every channel pays above its blended cap, but entities more so: gap ~11 pp for banks, ~27 pp brokers, ~45 pp 'other' corporate agents vs ~6.5 pp for agents (base PPT mix).",
        "4a. The reset is DISTRIBUTOR income. For bank-promoted insurers it equals ~70-75% of FY25 PAT (SBI Life, HDFC Life) vs ~6% for LIC: that is the bargaining-power risk if distributors shift shelf space.",
        "4b. Promoter banks lose fee income directly (see 5b_Promoter_Banks); the hit is small relative to bank other income, so insurers carry more of the renegotiation risk than banks.",
        "5. Pure term is the outlier: 51% average first-year commission vs a 25-30% cap. Protection-heavy distributors face the sharpest cut.",
        "6. Averages understate the hit: Annexure 3 maxima reach 62-92% by channel, so premium above the cap is larger than the average gap implies (treat as a lower bound).",
        "",
        "Tabs: 1_Inputs (cited) | 2_Sector_Economics | 3_Cap_Rules | 4_Cap_Gap (orange cells = assumptions you can change) | 5_Insurer_Exposure | 6_Monte_Carlo | 7_EoM_Glide | 8_NonLife | 9_Checks",
    ]
    for i, t in enumerate(lines):
        a.write(4 + i, 1, t, F["wrap"])
    # 1_Inputs
    s1 = wb.add_worksheet("1_Inputs"); s1.set_column("A:C", 26); s1.set_column("D:D", 14); s1.set_column("E:H", 30)
    s1.write_row(0, 0, ["block", "key", "segment", "value", "unit", "source", "page", "note"], F["hdr"])
    ref = {}
    for i, r in enumerate(ir.itertuples(index=False)):
        s1.write_row(1 + i, 0, [r.block, r.key, r.segment], F["lbl"])
        s1.write_number(1 + i, 3, float(r.value), F["inp"])
        s1.write_row(1 + i, 4, [r.unit, r.source, str(r.page), "" if pd.isna(r.note) else r.note], F["lbl"])
        ref[(r.block, r.key, r.segment)] = f"'1_Inputs'!$D${2+i}"
    R = lambda b, k, s: ref[(b, k, s)]  # noqa: E731
    # 2_Sector_Economics (formulas)
    s2 = wb.add_worksheet("2_Sector_Economics"); s2.set_column("A:A", 50); s2.set_column("B:D", 14)
    s2.write("A1", "Life sector economics FY25 (formulas over 1_Inputs)", F["title"])
    s2.write_row(2, 0, ["Metric (%)", "Public (LIC)", "Private", "Industry"], F["hdr"])
    rows = [
        ("Commission growth YoY", lambda s: f"=100*({R('sector','total_commission',s)}/{R('sector','total_commission_PY',s)}-1)"),
        ("Premium growth YoY", lambda s: f"=100*({R('sector','total_premium',s)}/{R('sector','total_premium_PY',s)}-1)"),
        ("Total commission / total premium", lambda s: f"=100*{R('sector','total_commission',s)}/{R('sector','total_premium',s)}"),
        ("First-year commission / first-year premium", lambda s: f"=100*{R('sector','fy_commission',s)}/{R('sector','fy_premium',s)}"),
        ("NB commission / NB premium (FY+single)", lambda s: f"=100*({R('sector','fy_commission',s)}+{R('sector','single_commission',s)})/({R('sector','fy_premium',s)}+{R('sector','single_premium',s)})"),
        ("Renewal commission / renewal premium", lambda s: f"=100*{R('sector','renewal_commission',s)}/{R('sector','renewal_premium',s)}"),
        ("EoM proxy: (commission + opex) / premium", lambda s: f"=100*({R('sector','total_commission',s)}+{R('sector','opex',s)})/{R('sector','total_premium',s)}"),
    ]
    for i, (lab, fn) in enumerate(rows):
        s2.write(3 + i, 0, lab, F["lbl"])
        for j, s in enumerate(["Public", "Private"]):
            s2.write_formula(3 + i, 1 + j, fn(s), F["pct1"])
        ind = fn("Public").replace("=", "", 1)
        both = fn("Private").replace("=", "", 1)
        # industry = sum-based recompute
        s2.write_formula(3 + i, 3, "=" + _industry(fn), F["pct1"])
    s2.write(12, 0, "Reading: private first-year commission (~27%) already exceeds the 20% entity cap for >=10y PPT before any rewards or 'other' payouts.", F["sub"])
    # 3_Cap_Rules
    s3 = wb.add_worksheet("3_Cap_Rules"); s3.set_column("A:B", 28); s3.set_column("C:H", 14)
    s3.write("A1", "Proposed life commission caps, % of premium (IRDAI Consultation Part 1, Box 4B, p51) - PROPOSED, not final", F["title"])
    s3.write_row(2, 0, list(caps.columns), F["hdr"])
    caprow = {}
    for i, r in enumerate(caps.itertuples(index=False)):
        for j, v in enumerate(r):
            (s3.write_number if isinstance(v, (int, float)) and not pd.isna(v) else s3.write)(3 + i, j, "" if (isinstance(v, float) and pd.isna(v)) else v, F["inp"] if isinstance(v, (int, float)) else F["lbl"])
        caprow[(r.product_class, r.ppt_band)] = 3 + i
    # 4_Cap_Gap (live: PPT mix + term share are editable assumptions)
    s4 = wb.add_worksheet("4_Cap_Gap"); s4.set_column("A:A", 30); s4.set_column("B:I", 14)
    s4.write("A1", "Cap gap by channel and rupee reset (edit orange assumption cells)", F["title"])
    s4.write("A3", "PPT mix of non-term FYP (ASSUMPTION)", F["hdr"])
    bands = list(PPT_BASE)
    for i, b in enumerate(bands):
        s4.write(3 + i, 0, b, F["lbl"]); s4.write_number(3 + i, 1, PPT_BASE[b], F["asm"])
    s4.write(8, 0, "Sum (must be 100%)", F["lbl"]); s4.write_formula(8, 1, "=SUM(B4:B8)", F["pctf"])
    s4.write(9, 0, "Pure-term share of FYP (ASSUMPTION)", F["lbl"]); s4.write_number(9, 1, TERM_SHARE_BASE, F["asm"])
    ent = "+".join(f"B{4+i}*'3_Cap_Rules'!C{caprow[('Individual non-linked/linked', b)]+1}" for i, b in enumerate(bands))
    agt = "+".join(f"B{4+i}*'3_Cap_Rules'!E{caprow[('Individual non-linked/linked', b)]+1}" for i, b in enumerate(bands))
    tr = caprow[("Pure term multi-year", "all")] + 1
    s4.write(10, 0, "Blended entity cap (%)", F["lbl"]); s4.write_formula(10, 1, f"=(1-B10)*({ent})+B10*'3_Cap_Rules'!C{tr}", F["pct1"])
    s4.write(11, 0, "Blended agent cap (%)", F["lbl"]); s4.write_formula(11, 1, f"=(1-B10)*({agt})+B10*'3_Cap_Rules'!E{tr}", F["pct1"])
    s4.write(12, 0, "Industry first-year premium (INR cr)", F["lbl"])
    s4.write_formula(12, 1, f"={R('sector','fy_premium','Public')}+{R('sector','fy_premium','Private')}", F["num"])
    s4.write(13, 0, "Individual NB premium, all channels (Handbook T99)", F["lbl"]); s4.write_number(13, 1, t99["Total"], F["inp"])
    s4.write_row(15, 0, ["Channel", "Indiv NB premium (T99)", "FYP allocated", "Avg FY commission % (Annex 3 T4)", "Cap %", "Gap pp", "Reset INR cr", "Max FY commission %"], F["hdr"])
    for i, ch in enumerate(CHANNEL_MAP):
        r = 16 + i
        rows99, kind = CHANNEL_MAP[ch]
        s4.write(r, 0, ch, F["lbl"])
        s4.write_number(r, 1, sum(t99[x] for x in rows99), F["inp"])
        s4.write_formula(r, 2, f"=$B$13*B{r+1}/$B$14", F["num"])
        s4.write_formula(r, 3, f"={R('annex3','channel_fyp_commission_avg',ch)}", F["pct1"])
        s4.write_formula(r, 4, "=$B$11" if kind == "entity" else "=$B$12", F["pct1"])
        s4.write_formula(r, 5, f"=MAX(0,D{r+1}-E{r+1})", F["pct1"])
        s4.write_formula(r, 6, f"=C{r+1}*F{r+1}/100", F["num"])
        s4.write_formula(r, 7, f"={R('annex3','channel_fyp_commission_max',ch)}", F["pct1"])
    s4.write(20, 0, "Total reset (lower bound)", F["lbl"]); s4.write_formula(20, 6, "=SUM(G17:G20)", F["bold"])
    s4.write(21, 0, "As % of FY25 life commission", F["lbl"])
    s4.write_formula(21, 6, f"=100*G21/({R('sector','total_commission','Public')}+{R('sector','total_commission','Private')})", F["pct1"])
    s4.write(23, 0, "Allocation note: FYP is split by each channel's share of FY25 individual new-business premium (T99), which includes individual single premium. Direct, online and other channels are excluded (no Annexure 3 rate).", F["sub"])
    ch = wb.add_chart({"type": "bar"})
    ch.add_series({"name": "Avg FY commission %", "categories": "='4_Cap_Gap'!$A$17:$A$20", "values": "='4_Cap_Gap'!$D$17:$D$20", "fill": {"color": "#1D4ED8"}})
    ch.add_series({"name": "Proposed cap %", "categories": "='4_Cap_Gap'!$A$17:$A$20", "values": "='4_Cap_Gap'!$E$17:$E$20", "fill": {"color": "#F59E0B"}})
    ch.set_title({"name": "Every non-agent channel pays above the proposed cap"}); ch.set_size({"width": 720, "height": 340})
    s4.insert_chart("J3", ch)
    # 5_Insurer_Exposure (values: python, documented)
    s5 = wb.add_worksheet("5_Insurer_Exposure"); s5.set_column("A:A", 46); s5.set_column("B:J", 13)
    s5.write("A1", "Insurer exposure at base assumptions (pipeline/insurance_model.py: T100 channel mix x channel gap)", F["title"])
    cols = ["insurer", "sector", "total_premium", "bank_ca_share", "agent_share", "blended_gap_pp", "reset_cr", "reset_pct_total_premium", "pat_fy25", "reset_pct_pat"]
    s5.write_row(2, 0, cols, F["hdr"])
    for i, r in enumerate(expo[cols].itertuples(index=False)):
        for j, v in enumerate(r):
            if isinstance(v, str):
                s5.write(3 + i, j, v, F["lbl"])
            elif pd.notna(v):
                s5.write_number(3 + i, j, float(v), F["pctf"] if cols[j].endswith("share") else (F["pct1"] if "pct" in cols[j] or "gap" in cols[j] else F["num"]))
    s5.write(4 + len(expo), 0, "reset_pct_pat uses FY25 standalone PAT from Screener (secondary) for listed insurers only. Insurer FYP is proxied by its share of individual NB premium.", F["sub"])
    # 5b_Promoter_Banks
    promo = pd.read_csv(TIDY / "ins_promoter_bank_hit.csv")
    s5b = wb.add_worksheet("5b_Promoter_Banks"); s5b.set_column("A:A", 46); s5b.set_column("B:F", 16)
    s5b.write("A1", "Link to P1: bank-channel commission reset vs promoter bank FY26 other income and PBT", F["title"])
    s5b.write_row(2, 0, list(promo.columns), F["hdr"])
    for i, r in enumerate(promo.itertuples(index=False)):
        for j, v in enumerate(r):
            (s5b.write(3 + i, j, v, F["lbl"]) if isinstance(v, str) else s5b.write_number(3 + i, j, float(v), F["pct1"] if "pct" in promo.columns[j] else F["num"]))
    s5b.write(4 + len(promo), 0, "Assumes the promoter bank is the bank channel for its insurer (approximation: SBI Life/HDFC Life also sell via other banks).", F["sub"])
    # 6_Monte_Carlo
    s6 = wb.add_worksheet("6_Monte_Carlo"); s6.set_column("A:A", 40); s6.set_column("B:B", 14)
    s6.write("A1", f"Monte Carlo, n={len(mc):,}, seed {SEED} (values)", F["title"])
    for i, (lab, v) in enumerate([("P10", p10), ("P50", p50), ("P90", p90), ("Mean", mc.mean()), ("Std dev", mc.std())]):
        s6.write(2 + i, 0, f"Reset INR cr - {lab}", F["lbl"]); s6.write_number(2 + i, 1, float(v), F["num"])
    s6.write(8, 0, "Draws: PPT mix ~ Dirichlet(base x 25); term share ~ U(4%,14%); channel rate ~ Triangular(0.85 x avg, avg, avg + 0.25 x (max - avg)).", F["sub"])
    hist, edges = np.histogram(mc, bins=20)
    s6.write_row(10, 0, ["Bin lower (INR cr)", "Count"], F["hdr"])
    for i, (h, e) in enumerate(zip(hist, edges)):
        s6.write_number(11 + i, 0, float(e), F["num"]); s6.write_number(11 + i, 1, int(h), F["num"])
    hc = wb.add_chart({"type": "column"})
    hc.add_series({"categories": f"='6_Monte_Carlo'!$A$12:$A${11+len(hist)}", "values": f"='6_Monte_Carlo'!$B$12:$B${11+len(hist)}", "gap": 5, "fill": {"color": "#1D4ED8"}})
    hc.set_title({"name": "Distribution of annual distributor-income reset (INR cr)"}); hc.set_legend({"none": True})
    s6.insert_chart("D3", hc)
    # 7_EoM_Glide
    s7 = wb.add_worksheet("7_EoM_Glide"); s7.set_column("A:A", 46); s7.set_column("B:D", 14)
    s7.write("A1", "EoM glide path (Box 2): expense reduction needed on FY25 base", F["title"])
    s7.write_row(2, 0, ["Metric", "Public (LIC)", "Private", "Industry"], F["hdr"])
    for i, (lab, tgt) in enumerate([("EoM FY25 (%)", None), ("Cut to 15% by Y2 (INR cr)", "eom_life_y2"), ("Cut to 12.5% by Y5 (INR cr)", "eom_life_y5")]):
        s7.write(3 + i, 0, lab, F["lbl"])
        for j, s in enumerate(["Public", "Private"]):
            e = f"({R('sector','total_commission',s)}+{R('sector','opex',s)})"
            p = R('sector', 'total_premium', s)
            if tgt is None:
                s7.write_formula(3 + i, 1 + j, f"=100*{e}/{p}", F["pct1"])
            else:
                s7.write_formula(3 + i, 1 + j, f"=MAX(0,{e}-{R('cap',tgt,'Life')}/100*{p})", F["num"])
        s7.write_formula(3 + i, 3, "=SUM(B{0}:C{0})".format(4 + i) if tgt else f"=100*({R('sector','total_commission','Public')}+{R('sector','opex','Public')}+{R('sector','total_commission','Private')}+{R('sector','opex','Private')})/({R('sector','total_premium','Public')}+{R('sector','total_premium','Private')})", F["num"] if tgt else F["pct1"])
    s7.write(7, 0, "LIC is below 15%/12.5% on this proxy but must reach 10% in 5 years (Box 2 A(ii)). Proxy excludes rewards paid outside commission.", F["sub"])
    # 8_NonLife
    s8 = wb.add_worksheet("8_NonLife"); s8.set_column("A:A", 18); s8.set_column("B:E", 14)
    s8.write("A1", "Non-life: commission intensity vs claims ratio by line, FY25 (IRDAI AR I.12-I.14)", F["title"])
    s8.write_row(2, 0, ["Line", "GDPI INR cr", "Commission INR cr", "Commission % GDPI", "ICR %"], F["hdr"])
    for i, ln in enumerate(["motor", "health", "fire", "marine", "others"]):
        r = 3 + i
        s8.write(r, 0, ln.title(), F["lbl"])
        s8.write_formula(r, 1, f"={R('gi','gdpi_'+ln,'Total')}", F["num"])
        s8.write_formula(r, 2, f"={R('gi','commission_'+ln,'Total')}", F["num"])
        s8.write_formula(r, 3, f"=100*C{r+1}/B{r+1}", F["pct1"])
        s8.write_formula(r, 4, f"={R('gi','icr_'+ln,'Total')}", F["pct1"])
    s8.write(9, 0, "GI EoM proxy", F["lbl"])
    s8.write_formula(9, 3, f"=100*({R('gi','commission_total','Total')}+{R('gi','opex_total','Total')})/{R('gi','gdpi','Total')}", F["pct1"])
    s8.write(10, 0, "Cut to 25% (Y2)", F["lbl"]); s8.write_formula(10, 3, f"=MAX(0,{R('gi','commission_total','Total')}+{R('gi','opex_total','Total')}-{R('cap','eom_gi_y2','General')}/100*{R('gi','gdpi','Total')})", F["num"])
    s8.write(11, 0, "Cut to 20% (Y5)", F["lbl"]); s8.write_formula(11, 3, f"=MAX(0,{R('gi','commission_total','Total')}+{R('gi','opex_total','Total')}-{R('cap','eom_gi_y5','General')}/100*{R('gi','gdpi','Total')})", F["num"])
    bub = wb.add_chart({"type": "scatter"})
    bub.add_series({"name": "Lines (marker = line of business)", "categories": "='8_NonLife'!$D$4:$D$8", "values": "='8_NonLife'!$E$4:$E$8",
                    "marker": {"type": "circle", "size": 11}, "data_labels": {"value": False, "custom": [{"value": n} for n in ["Motor", "Health", "Fire", "Marine", "Others"]]}})
    bub.set_x_axis({"name": "Commission % GDPI"}); bub.set_y_axis({"name": "ICR %"})
    bub.set_title({"name": "Motor: highest commission intensity with an 85% claims ratio"})
    s8.insert_chart("G3", bub)
    # 9_Checks
    s9 = wb.add_worksheet("9_Checks"); s9.set_column("A:A", 70); s9.set_column("B:C", 16)
    s9.write_row(0, 0, ["Check", "Value", "Result"], F["hdr"])
    sumcom = float(pd.read_csv(TIDY / "ins_life_insurers_FY25.csv").total_commission.sum())
    checks = [
        ("Handbook T13 insurer commission sum = AR Table I.10 total (60,799.91)", f"={sumcom}", f"=IF(ABS(B2-({R('sector','total_commission','Public')}+{R('sector','total_commission','Private')}))<1,\"PASS\",\"FAIL\")"),
        ("AR FY+single+renewal premium = total premium (private)", f"={R('sector','fy_premium','Private')}+{R('sector','single_premium','Private')}+{R('sector','renewal_premium','Private')}-{R('sector','total_premium','Private')}", "=IF(ABS(B3)<1,\"PASS\",\"FAIL\")"),
        ("AR commission components sum to total (private)", f"={R('sector','fy_commission','Private')}+{R('sector','single_commission','Private')}+{R('sector','renewal_commission','Private')}-{R('sector','total_commission','Private')}", "=IF(ABS(B4)<1,\"PASS\",\"FAIL\")"),
        ("PPT mix sums to 100%", "='4_Cap_Gap'!B9", "=IF(ABS(B5-1)<0.0001,\"PASS\",\"FAIL\")"),
        ("GI segment commission sums to total", f"={'+'.join(R('gi','commission_'+x,'Total') for x in ['motor','health','fire','marine','others'])}-{R('gi','commission_total','Total')}", "=IF(ABS(B6)<1,\"PASS\",\"FAIL\")"),
    ]
    for i, (lab, v, res) in enumerate(checks):
        s9.write(1 + i, 0, lab, F["lbl"]); s9.write_formula(1 + i, 1, v, F["num"]); s9.write_formula(1 + i, 2, res, F["lbl"])
    wb.close()
    print(f"wrote {OUT.relative_to(ROOT)}")


def _industry(fn):
    """Recompute an industry ratio by summing public+private numerators/denominators inside a formula string."""
    pub, priv = fn("Public").lstrip("="), fn("Private").lstrip("=")
    # replace each Public ref with (Public+Private) ref pair; refs are '1_Inputs'!$D$n
    import re
    pr = re.findall(r"'1_Inputs'!\$D\$\d+", pub)
    vr = re.findall(r"'1_Inputs'!\$D\$\d+", priv)
    out = pub
    for a, b in zip(pr, vr):
        out = out.replace(a, f"@@{a[-6:]}@@", 1)
    for a, b in zip(pr, vr):
        out = out.replace(f"@@{a[-6:]}@@", f"({a}+{b})", 1)
    return out


if __name__ == "__main__":
    main()
