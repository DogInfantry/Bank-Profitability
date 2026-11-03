"""P3: UPI's first fee and the 30% market-share cap.

Inputs (user uploads, hashed in manifest):
  data/raw/manual/npci_upi_monthly_FY26.xlsx, npci_upi_monthly_FY27ytd.xlsx   NPCI product statistics
  data/raw/manual/npci_upi_apps_monthly.csv                                   NPCI app-wise statistics (Dec-20 to Aug-26)
Rules: DFS FAQ on MDR (15 Sep 2026), data/raw/web/DFS_UPI_MDR_FAQ_Sep2026.pdf
Outputs: data/tidy/upi_monthly.csv, upi_app_share.csv, upi_concentration.csv, models/03_UPI_MDR_Cap.xlsx

App-name normalisation follows the approach described in koushikxy/upi-payments-dashboard (method only; no code or
files copied - that repo has no licence). Our own rules are in normalise_app().
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
import xlsxwriter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "manual"
TIDY = ROOT / "data" / "tidy"
OUT = ROOT / "models" / "03_UPI_MDR_Cap.xlsx"

# MDR rules (DFS FAQ, 15 Sep 2026): Q3, Q33, Q22, Q24
MDR_RATE, MDR_THRESHOLD, MDR_CAP_RS, FLAT_RS = 0.004, 2000, 300, 5
# Share inputs (PIB 24 Aug 2026 FY26 release): P2M = 63% of volume; P2P = 71% of value -> P2M = 29% of value
P2M_VALUE_SHARE = 0.29


def normalise_app(raw: str) -> tuple[str, str]:
    n = re.sub(r"\s*#\s*", " ", raw).strip()
    n = re.sub(r"\s*\((OCL|Livquik)\)\s*", " ", n, flags=re.I).strip()
    n = re.sub(r"\s+(apps?|App|Apps)$", "", n, flags=re.I).strip()
    low = n.lower()
    if low.startswith("paytm"):
        n = "Paytm"
    elif low.replace(" ", "").startswith("phonepe"):
        n = "PhonePe"
    elif low.startswith("google pay") or low == "gpay":
        n = "Google Pay"
    elif low.startswith("navi"):
        n = "Navi"
    elif low.startswith("super.money") or low.startswith("supermoney"):
        n = "super.money"
    elif low.startswith("cred"):
        n = "CRED"
    elif low.startswith("amazon pay"):
        n = "Amazon Pay"
    elif low.startswith("bhim"):
        n = "BHIM"
    kind = "Bank app" if ("bank" in low and not low.startswith(("paytm", "airtel payments"))) else "Third-party app"
    return n, kind


def monthly() -> pd.DataFrame:
    rows = []
    for f in ["npci_upi_monthly_FY26.xlsx", "npci_upi_monthly_FY27ytd.xlsx"]:
        ws = openpyxl.load_workbook(RAW / f, read_only=True, data_only=True).worksheets[0]
        for r in list(ws.iter_rows(values_only=True))[1:]:
            if r[0]:
                rows.append(dict(month=pd.to_datetime(r[0], format="%B-%Y"), volume_mn=float(r[1]),
                                 value_cr=float(r[3]), source=f"NPCI product statistics ({f})"))
    m = pd.DataFrame(rows).sort_values("month").reset_index(drop=True)
    m["avg_ticket_rs"] = m.value_cr * 1e7 / (m.volume_mn * 1e6)
    m["days"] = m.month.dt.days_in_month
    m["daily_volume_mn"] = m.volume_mn / m.days
    m["mom_volume_pct"] = 100 * m.volume_mn.pct_change()
    return m


def app_shares() -> pd.DataFrame:
    d = pd.read_csv(RAW / "npci_upi_apps_monthly.csv")
    recs = []
    for c in d.columns:
        m = re.match(r"^(.*), all transactions \((number|value)\)$", c)
        if m:
            app, kind = normalise_app(m.group(1))
            vals = pd.to_numeric(d[c], errors="coerce")
            for dt, v in zip(d["date"], vals):
                if pd.notna(v) and v > 0:
                    recs.append((dt, app, kind, m.group(2), v))
    long = pd.DataFrame(recs, columns=["month", "app", "app_type", "measure", "v"])
    w = long.pivot_table(index=["month", "app", "app_type"], columns="measure", values="v", aggfunc="sum").reset_index()
    w = w.dropna(subset=["number"])
    w["month"] = pd.to_datetime(w.month)
    w["volume_share"] = w["number"] / w.groupby("month")["number"].transform("sum")
    return w.rename(columns={"number": "volume", "value": "value_rs"})


def concentration(w: pd.DataFrame) -> pd.DataFrame:
    g = w.groupby("month")
    out = pd.DataFrame({
        "hhi": g.volume_share.apply(lambda s: float(((100 * s) ** 2).sum())),
        "top2_share": g.apply(lambda x: x.nlargest(2, "volume").volume_share.sum(), include_groups=False),
        "phonepe": g.apply(lambda x: x[x.app == "PhonePe"].volume_share.sum(), include_groups=False),
        "google_pay": g.apply(lambda x: x[x.app == "Google Pay"].volume_share.sum(), include_groups=False),
        "paytm": g.apply(lambda x: x[x.app == "Paytm"].volume_share.sum(), include_groups=False),
        "navi": g.apply(lambda x: x[x.app == "Navi"].volume_share.sum(), include_groups=False),
        "bank_apps": g.apply(lambda x: x[x.app_type == "Bank app"].volume_share.sum(), include_groups=False),
        "apps_total_volume": g.volume.sum(),
    }).reset_index()
    return out


def cap_math(c: pd.DataFrame, deadline="2026-12-31") -> pd.DataFrame:
    last = c.iloc[-1]
    months_left = (pd.Timestamp(deadline).to_period("M") - pd.Timestamp(last.month).to_period("M")).n
    rows = []
    for app in ["phonepe", "google_pay"]:
        s = c.set_index("month")[app].tail(13)
        slope = np.polyfit(np.arange(len(s)), 100 * s.values, 1)[0]  # pp per month, last 12m
        need = (100 * last[app] - 30) / months_left
        months_at_trend = (100 * last[app] - 30) / -slope if slope < 0 else np.inf
        rows.append(dict(app=app, share_latest_pct=100 * last[app], months_to_deadline=months_left,
                         required_pp_per_month=need, trend_pp_per_month=slope,
                         months_to_30pct_at_trend=months_at_trend))
    return pd.DataFrame(rows)


def mdr_pool(m: pd.DataFrame) -> pd.DataFrame:
    """Sensitivity grid: annual MDR pool (INR cr) on trailing-12m UPI value."""
    v12 = m.tail(12).value_cr.sum()
    grid = []
    for above in [0.40, 0.50, 0.60, 0.70]:          # share of P2M value in tickets > Rs 2,000 (unknown; DFS: >95% of P2M VOLUME is <= 2,000)
        for exempt in [0.10, 0.20, 0.30, 0.40]:     # share of that value exempt (P2PM small merchants, AutoPay, flat-fee sectors at Rs 5)
            pool = v12 * P2M_VALUE_SHARE * above * (1 - exempt) * MDR_RATE * 0.95  # 0.95 haircut for the Rs 300 cap on >= Rs 75k tickets
            grid.append(dict(p2m_value_above_2000=above, exempt_share=exempt, pool_cr=pool))
    return pd.DataFrame(grid), v12


def main():
    TIDY.mkdir(exist_ok=True)
    m = monthly(); w = app_shares(); c = concentration(w); cm = cap_math(c); grid, v12 = mdr_pool(m)
    m.to_csv(TIDY / "upi_monthly.csv", index=False)
    w.to_csv(TIDY / "upi_app_share.csv", index=False)
    c.to_csv(TIDY / "upi_concentration.csv", index=False)
    cm.to_csv(TIDY / "upi_cap_math.csv", index=False)
    grid.to_csv(TIDY / "upi_mdr_grid.csv", index=False)
    # reconciliation: app sum vs NPCI product total
    rec = m.merge(c[["month", "apps_total_volume"]], on="month")
    rec["diff_pct"] = 100 * (rec.apps_total_volume / 1e6 / rec.volume_mn - 1)
    write_xlsx(m, c, cm, grid, v12, rec)
    peak = m.loc[m.volume_mn.idxmax()]
    print(f"record month: {peak.month:%b-%Y} {peak.volume_mn:,.0f} mn; latest {m.iloc[-1].month:%b-%Y} {m.iloc[-1].volume_mn:,.0f} mn / Rs {m.iloc[-1].value_cr/1e5:.2f} lakh cr")
    print(c.tail(3)[["month", "hhi", "top2_share", "phonepe", "google_pay", "navi", "bank_apps"]].to_string(index=False))
    print(cm.round(2).to_string(index=False))
    print("app-vs-NPCI volume diff % (overlap):", rec.diff_pct.round(2).tolist())
    print(f"T12M value Rs {v12/1e5:.1f} lakh cr; MDR pool range Rs {grid.pool_cr.min():,.0f}-{grid.pool_cr.max():,.0f} cr")


def write_xlsx(m, c, cm, grid, v12, rec):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb = xlsxwriter.Workbook(OUT)
    H = wb.add_format({"bold": True, "bg_color": "#1F2937", "font_color": "white", "border": 1, "text_wrap": True})
    T = wb.add_format({"bold": True, "font_size": 15}); S = wb.add_format({"italic": True, "font_color": "#6B7280", "text_wrap": True})
    N = wb.add_format({"num_format": "#,##0", "border": 1}); P = wb.add_format({"num_format": "0.0%", "border": 1})
    D = wb.add_format({"num_format": "mmm-yy", "border": 1}); I = wb.add_format({"num_format": "#,##0.00", "font_color": "#1D4ED8", "bg_color": "#EFF6FF", "border": 1})
    A = wb.add_format({"num_format": "0%", "font_color": "#9A3412", "bg_color": "#FFEDD5", "border": 1}); F2 = wb.add_format({"num_format": "0.00", "border": 1})
    peak = m.loc[m.volume_mn.idxmax()]
    a = wb.add_worksheet("0_Answer"); a.set_column("B:B", 120)
    a.write("B2", "UPI's first fee: a value-driven pool from a small slice of volume; the 30% cap is out of reach by Dec-26", T)
    pp = cm.set_index("app")
    lines = [
        f"1. Record month is {peak.month:%b-%Y} ({peak.volume_mn/1e3:.2f} bn txns); Oct-26 was {m.iloc[-1].volume_mn/1e3:.2f} bn / Rs {m.iloc[-1].value_cr/1e5:.2f} lakh cr (NPCI). Secondary reports of 25.47 bn for Oct-26 do not match NPCI's file.",
        f"2. MDR applies to P2M tickets above Rs 2,000: under 5% of P2M volume but a large share of value. On trailing-12m value of Rs {v12/1e5:.0f} lakh cr the annual pool is Rs {grid.pool_cr.min():,.0f}-{grid.pool_cr.max():,.0f} cr across the sensitivity grid (assumption-driven; see 3_MDR_Pool).",
        f"3. PhonePe ({pp.loc['phonepe','share_latest_pct']:.1f}%) and Google Pay ({pp.loc['google_pay','share_latest_pct']:.1f}%) would need to lose {pp.loc['phonepe','required_pp_per_month']:.1f} pp and {pp.loc['google_pay','required_pp_per_month']:.1f} pp a month to reach 30% by 31 Dec 2026; the last-12-month trend is {pp.loc['phonepe','trend_pp_per_month']:+.2f} and {pp.loc['google_pay','trend_pp_per_month']:+.2f} pp a month.",
        f"4. Concentration is easing (HHI {c.iloc[-1].hhi:,.0f} in {c.iloc[-1].month:%b-%y}, down from {c.hhi.max():,.0f} peak) as Navi ({100*c.iloc[-1].navi:.1f}%) and super.money take share; bank apps carry only {100*c.iloc[-1].bank_apps:.1f}% of volume.",
        "5. Judgement (not reported fact): another extension or a phased glide path is more likely than hard enforcement on 1 Jan 2027.",
    ]
    for i, t in enumerate(lines):
        a.write(3 + i, 1, t, S if i == 4 else wb.add_format({"text_wrap": True}))
    s1 = wb.add_worksheet("1_Monthly"); s1.set_column("A:H", 14)
    cols = ["month", "volume_mn", "value_cr", "avg_ticket_rs", "daily_volume_mn", "mom_volume_pct", "source"]
    s1.write_row(0, 0, cols, H)
    for i, r in enumerate(m[cols].itertuples(index=False)):
        s1.write_datetime(1 + i, 0, r.month.to_pydatetime(), D)
        for j, v in enumerate(r[1:6]):
            if pd.notna(v):
                s1.write_number(1 + i, 1 + j, float(v), N if j < 2 else F2)
        s1.write(1 + i, 6, r.source)
    ch = wb.add_chart({"type": "column"})
    ch.add_series({"name": "Volume (mn)", "categories": f"='1_Monthly'!$A$2:$A${len(m)+1}", "values": f"='1_Monthly'!$B$2:$B${len(m)+1}", "fill": {"color": "#1D4ED8"}})
    ch.set_title({"name": "Volume plateaued after the Aug-26 record (mn transactions)"}); ch.set_size({"width": 760, "height": 340}); ch.set_legend({"none": True})
    s1.insert_chart("I2", ch)
    ln = wb.add_chart({"type": "line"})  # separate chart: one y-axis per chart, never dual-axis
    ln.add_series({"name": "Avg ticket (Rs)", "categories": f"='1_Monthly'!$A$2:$A${len(m)+1}", "values": f"='1_Monthly'!$D$2:$D${len(m)+1}", "line": {"color": "#2a78d6", "width": 2.25}, "marker": {"type": "circle", "size": 6}})
    ln.set_title({"name": "Average ticket drifting down (Rs per transaction)"}); ln.set_size({"width": 760, "height": 300}); ln.set_legend({"none": True})
    s1.insert_chart("I20", ln)
    s2 = wb.add_worksheet("2_Concentration"); s2.set_column("A:J", 13)
    cc = ["month", "hhi", "top2_share", "phonepe", "google_pay", "paytm", "navi", "bank_apps"]
    s2.write_row(0, 0, cc, H)
    for i, r in enumerate(c[cc].itertuples(index=False)):
        s2.write_datetime(1 + i, 0, pd.Timestamp(r.month).to_pydatetime(), D)
        s2.write_number(1 + i, 1, float(r.hhi), N)
        for j, v in enumerate(r[2:]):
            s2.write_number(1 + i, 2 + j, float(v), P)
    s2.write(0, 9, "30% cap", H)
    for i in range(len(c)):
        s2.write_number(1 + i, 9, 0.30, P)
    ac = wb.add_chart({"type": "line"})
    for col, name, colr in [(3, "PhonePe", "#5B21B6"), (4, "Google Pay", "#1D4ED8"), (5, "Paytm", "#0EA5E9"), (6, "Navi", "#10B981"), (9, "30% cap", "#DC2626")]:
        ac.add_series({"name": name, "categories": f"='2_Concentration'!$A$2:$A${len(c)+1}", "values": ["2_Concentration", 1, col, len(c), col],
                       "line": {"color": colr, "width": 2 if name != "30% cap" else 1.5, "dash_type": "dash" if name == "30% cap" else "solid"}})
    ac.set_title({"name": "Top-two shares remain far above the 30% cap"}); ac.set_size({"width": 760, "height": 380}); ac.set_y_axis({"num_format": "0%"})
    s2.insert_chart("L2", ac)
    s3 = wb.add_worksheet("3_MDR_Pool"); s3.set_column("A:A", 54); s3.set_column("B:F", 14)
    s3.write("A1", "MDR pool sensitivity (INR cr per year) - live formulas; orange = assumptions", T)
    s3.write("A3", "Trailing-12m UPI value (INR cr, NPCI)", wb.add_format({"border": 1})); s3.write_number("B3", v12, I)
    s3.write("A4", "P2M share of value (PIB FY26: P2P = 71% of value)", wb.add_format({"border": 1})); s3.write_number("B4", P2M_VALUE_SHARE, A)
    s3.write("A5", "MDR rate (DFS FAQ Q3)", wb.add_format({"border": 1})); s3.write_number("B5", MDR_RATE, wb.add_format({"num_format": "0.00%", "font_color": "#1D4ED8", "bg_color": "#EFF6FF", "border": 1}))
    s3.write("A6", "Haircut for Rs 300 cap on tickets >= Rs 75,000 (ASSUMPTION)", wb.add_format({"border": 1})); s3.write_number("B6", 0.95, A)
    s3.write("A8", "Rows: share of P2M value in tickets > Rs 2,000 | Columns: exempt share (P2PM, AutoPay, Rs 5 flat sectors)", S)
    ex = [0.10, 0.20, 0.30, 0.40]; ab = [0.40, 0.50, 0.60, 0.70]
    s3.write(8, 0, "Above-2,000 share \\ exempt share", H)
    for j, e in enumerate(ex):
        s3.write_number(8, 1 + j, e, A)
    for i, x in enumerate(ab):
        s3.write_number(9 + i, 0, x, A)
        for j in range(len(ex)):
            col = chr(ord("B") + j)
            s3.write_formula(9 + i, 1 + j, f"=$B$3*$B$4*$A{10+i}*(1-{col}$9)*$B$5*$B$6", N)
    s3.conditional_format(9, 1, 12, 4, {"type": "2_color_scale", "min_color": "#FFFFFF", "max_color": "#93C5FD"})
    s3.write(14, 0, "DFS FAQ Q2: tickets up to Rs 2,000 are >95% of P2M VOLUME. Their share of VALUE is not published - hence a grid, not a point estimate.", S)
    s4 = wb.add_worksheet("4_Cap_Math"); s4.set_column("A:G", 18)
    s4.write_row(0, 0, list(cm.columns), H)
    for i, r in enumerate(cm.itertuples(index=False)):
        s4.write(1 + i, 0, r.app)
        for j, v in enumerate(r[1:]):
            s4.write_number(1 + i, 1 + j, float(v) if np.isfinite(v) else 999, F2)
    s4.write(4, 0, "Trend = OLS slope of monthly volume share over the last 13 months. 999 = share not falling at trend.", S)
    s5 = wb.add_worksheet("5_Checks"); s5.set_column("A:A", 60); s5.set_column("B:C", 14)
    s5.write_row(0, 0, ["Check", "Value", "Result"], H)
    worst = float(rec.diff_pct.abs().max())
    hhi_sep = c[c.month == c.month.max()].hhi.iloc[0]
    for i, (lab, v, ok) in enumerate([
        ("Max |sum of app volumes / NPCI monthly total - 1| (%) over overlap months (PASS <=2; EXPLAINED <=3: app file omits small apps, NPCI revises totals)", worst, "PASS" if worst <= 2 else ("EXPLAINED" if worst <= 3 else "FAIL")),
        ("Months reconciled", float(len(rec)), len(rec) >= 12),
        (f"Latest HHI ({c.month.max():%b-%y}) within 150 of reference 3,211 (Sep-26, koushikxy dashboard)", float(hhi_sep), abs(hhi_sep - 3211) <= 150),
        ("Value per txn in band Rs 1,000-1,500 (sanity)", float(m.iloc[-1].avg_ticket_rs), 1000 <= m.iloc[-1].avg_ticket_rs <= 1500),
    ]):
        s5.write(1 + i, 0, lab); s5.write_number(1 + i, 1, v, F2); s5.write(1 + i, 2, ok if isinstance(ok, str) else ("PASS" if ok else "CHECK"))
    wb.close()


if __name__ == "__main__":
    main()
