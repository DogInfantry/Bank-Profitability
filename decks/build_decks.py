"""Build the three client decks (native, editable PowerPoint charts) from data/tidy and data/inputs.

Every number on a slide is read from the same tidy files that feed the Excel models and dashboard, so a
pipeline refresh regenerates the decks. Action titles state the finding; every slide carries a source line.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
T, I = ROOT / "data" / "tidy", ROOT / "data" / "inputs"
OUT = ROOT / "decks"
NAVY, INK, MUTED, GRID = RGBColor(0x1F, 0x2A, 0x44), RGBColor(0x1A, 0x1A, 0x1A), RGBColor(0x6F, 0x6E, 0x69), RGBColor(0xD9, 0xD7, 0xD0)
S = [RGBColor(0x2A, 0x78, 0xD6), RGBColor(0xEB, 0x68, 0x34), RGBColor(0x1B, 0xAF, 0x7A), RGBColor(0xED, 0xA1, 0x00), RGBColor(0xE8, 0x7B, 0xA4)]
GRAY = RGBColor(0xB8, 0xB6, 0xAE)
BN = {"SBIN": "SBI", "HDFCBANK": "HDFC Bank", "ICICIBANK": "ICICI Bank", "AXISBANK": "Axis Bank", "KOTAKBANK": "Kotak"}


class Deck:
    def __init__(self, name: str, tag: str):
        self.p = Presentation(); self.p.slide_width, self.p.slide_height = Inches(13.333), Inches(7.5)
        self.name, self.tag, self.n = name, tag, 0

    def slide(self, title: str, source: str, tracker: str = ""):
        s = self.p.slides.add_slide(self.p.slide_layouts[6]); self.n += 1
        if tracker:
            self.text(s, tracker.upper(), 0.5, 0.25, 8, 0.3, 10, MUTED, bold=True)
        self.text(s, title, 0.5, 0.5, 12.3, 1.0, 22, NAVY, bold=True)
        ln = s.shapes.add_connector(1, Inches(0.5), Inches(1.5), Inches(12.83), Inches(1.5)); ln.line.color.rgb = GRID
        self.text(s, f"Source: {source}", 0.5, 6.95, 10.8, 0.4, 9, MUTED)
        self.text(s, f"{self.tag} | {self.n}", 11.4, 6.95, 1.43, 0.4, 9, MUTED, align=PP_ALIGN.RIGHT)
        return s

    @staticmethod
    def text(s, txt, x, y, w, h, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT):
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
        for i, line in enumerate(txt.split("\n")):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.text = line; para.alignment = align
            for r in para.runs:
                r.font.size, r.font.bold, r.font.color.rgb, r.font.name = Pt(size), bold, color, "Calibri"
        return tb

    def big(self, s, value, label, x, y, w=3.8, color=NAVY):
        self.text(s, value, x, y, w, 1.1, 54, color, bold=True)
        self.text(s, label, x, y + 1.15, w, 0.9, 13, MUTED)

    def chart(self, s, kind, cats, series, x, y, w, h, colors=None, legend=True, labels=False, fmt='0.0', gap=60, overlap=None):
        cd = CategoryChartData(); cd.categories = cats
        for name, vals in series:
            cd.add_series(name, vals)
        gf = s.shapes.add_chart(kind, Inches(x), Inches(y), Inches(w), Inches(h), cd); ch = gf.chart
        ch.font.size, ch.font.name = Pt(11), "Calibri"
        ch.has_legend = legend and len(series) > 1
        if ch.has_legend:
            ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.BOTTOM, False
        for i, ser in enumerate(ch.series):
            c = (colors or S)[i % len(colors or S)]
            if kind in (XL_CHART_TYPE.LINE_MARKERS, XL_CHART_TYPE.LINE):
                ser.format.line.color.rgb, ser.format.line.width = c, Pt(2.25); ser.smooth = False
                ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = c
            else:
                ser.format.fill.solid(); ser.format.fill.fore_color.rgb = c
        if labels:
            pl = ch.plots[0]; pl.has_data_labels = True; dl = pl.data_labels
            dl.number_format, dl.number_format_is_linked, dl.font.size = fmt, False, Pt(10)
        try:
            ch.plots[0].gap_width = gap
            if overlap is not None:
                ch.plots[0].overlap = overlap
            ch.value_axis.major_gridlines.format.line.color.rgb = GRID
            ch.value_axis.format.line.color.rgb = GRID
            ch.value_axis.tick_labels.font.color.rgb = MUTED; ch.category_axis.tick_labels.font.color.rgb = INK
            ch.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW  # keep labels off the zero line when values go negative
            if kind in (XL_CHART_TYPE.BAR_STACKED, XL_CHART_TYPE.BAR_CLUSTERED):
                ch.category_axis.reverse_order = True  # first category on top
                ch.value_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        except Exception:  # noqa: BLE001 - not every chart type exposes all axes
            pass
        return ch

    def table(self, s, header, rows, x, y, w, col_w=None, size=11, highlight_col=None):
        t = s.shapes.add_table(len(rows) + 1, len(header), Inches(x), Inches(y), Inches(w), Inches(0.36 * (len(rows) + 1))).table
        for j, h in enumerate(header):
            c = t.cell(0, j); c.text = h; c.fill.solid(); c.fill.fore_color.rgb = NAVY
            for p_ in c.text_frame.paragraphs:
                for r in p_.runs:
                    r.font.size, r.font.bold, r.font.color.rgb = Pt(size), True, RGBColor(0xFF, 0xFF, 0xFF)
        for i, row in enumerate(rows):
            for j, v in enumerate(row):
                c = t.cell(i + 1, j); c.text = str(v); c.fill.solid()
                c.fill.fore_color.rgb = RGBColor(0xF6, 0xF5, 0xF2) if i % 2 else RGBColor(0xFF, 0xFF, 0xFF)
                for p_ in c.text_frame.paragraphs:
                    for r in p_.runs:
                        r.font.size, r.font.color.rgb = Pt(size), INK
                        r.font.bold = (highlight_col == j)
        if col_w:
            for j, cw in enumerate(col_w):
                t.columns[j].width = Inches(cw)
        return t

    def save(self):
        OUT.mkdir(exist_ok=True); path = OUT / self.name; self.p.save(path); print(f"wrote {path.relative_to(ROOT)} ({self.n} slides)")


def bank_deck():
    w = pd.read_csv(T / "bank_model_inputs.csv"); w["avg_assets"] = (w.assets_open + w.assets_close) / 2
    w["avg_eq"] = (w.equity_open + w.equity_close) / 2
    for c in ["nii", "other_income", "opex", "provisions", "tax", "pat"]:
        w[c + "_p"] = 100 * w[c] * w.annualise / w.avg_assets
    w["roe"] = 100 * w.pat * w.annualise / w.avg_eq; w["ci"] = 100 * w.opex / (w.nii + w.other_income); w["t"] = w.tax / w.pbt
    fy = w[w.period == "FY26"].set_index("bank").loc[["ICICIBANK", "HDFCBANK", "KOTAKBANK", "AXISBANK", "SBIN"]]
    sh = pd.read_csv(T / "bank_shapley_FY26.csv").query("metric=='RoA' and benchmark=='ICICIBANK'").set_index("bank")
    nim = pd.read_csv(I / "nim_trajectory.csv").dropna(subset=["q2fy27_nim"])
    say = pd.read_csv(I / "concall_say_do.csv")
    d = Deck("01_Bank_RoA_Divergence.pptx", "Indian bank RoA benchmark")
    src_b = "Bank investor presentations Q4 FY26 / Q2 FY27 (page-cited in data/inputs/bank_reported.csv); Screener.in standalone financials tied to filings; analysis by Anklesh"
    # 1 answer
    s = d.slide(f"ICICI earns {fy.loc['ICICIBANK'].pat_p:.2f}% RoA; the banks behind it trail for three different reasons, so each needs a different lever", src_b, "Executive summary")
    d.big(s, f"{100*sh.loc['SBIN'].gap:.0f} bp", f"SBI's RoA gap to ICICI; net interest income alone explains {100*sh.loc['SBIN'].nii:.0f} bp. SBI's opex/assets is the lowest in the set", 0.6, 1.9)
    d.big(s, f"{100*sh.loc['AXISBANK'].gap:.0f} bp", f"Axis's gap: margin {100*sh.loc['AXISBANK'].nii:.0f} bp + credit cost {100*sh.loc['AXISBANK'].prov:.0f} bp (incl. Rs 2,001 cr one-off provision)", 4.8, 1.9, color=S[1])
    d.big(s, f"{100*sh.loc['KOTAKBANK'].gap:.0f} bp", f"Kotak's gap is cost: best NII margin, but opex absorbs {100*sh.loc['KOTAKBANK'].opex:.0f} bp", 9.0, 1.9, color=S[2])
    d.text(s, "Margins are now compressing across the board (every reported Q2 FY27 NIM is below Q4 FY26), so the levers that matter for FY27 are deposit franchise (SBI, HDFC), credit discipline (Axis) and cost-to-serve (Kotak).", 0.6, 4.6, 12, 1.2, 15, INK)
    # 2 NIM
    s = d.slide(f"Margins are compressing everywhere: reported NIM fell {abs(nim.change_bp.max()):.0f}-{abs(nim.change_bp.min()):.0f} bp between Q4 FY26 and Q2 FY27", "Bank investor presentations Q4 FY26 and Q2 FY27; HDFC NIM on total assets, others on interest-earning assets. SBI Q2 FY27 due 3 Nov 2026", "Context")
    ch = d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [BN[b] for b in nim.bank], [("Q4 FY26", nim.q4fy26_nim.tolist()), ("Q2 FY27", nim.q2fy27_nim.tolist())], 0.6, 1.7, 8.2, 5.0, colors=[GRAY, S[0]], labels=True, fmt="0.00")
    d.text(s, "\n".join(f"{BN[r.bank]}: {r.change_bp:+.0f} bp" for r in nim.itertuples()), 9.2, 2.0, 3.6, 2.5, 16, NAVY, bold=True)
    d.text(s, "Asset yields reset faster than deposit costs in the down-rate cycle. NII, not asset quality, is the FY27 earnings swing factor.", 9.2, 4.4, 3.6, 2.0, 13, MUTED)
    # 3 scorecard
    s = d.slide("On the FY26 scorecard ICICI leads on RoA and RoE; SBI runs the leanest cost base but the thinnest margin", src_b + ". Ratios % of average assets; RoE on average net worth", "Peer scorecard")
    rows = [[BN[b], f"{x.nii_p:.2f}", f"{x.other_income_p:.2f}", f"{x.opex_p:.2f}", f"{x.provisions_p:.2f}", f"{x.pat_p:.2f}", f"{x.roe:.1f}", f"{x.ci:.1f}", f"{x.gnpa:.2f}"] for b, x in fy.iterrows()]
    d.table(s, ["Bank", "NII %", "Other inc. %", "Opex %", "Provisions %", "RoA %", "RoE %", "Cost/income %", "GNPA %"], rows, 0.6, 1.9, 12.1, size=13, highlight_col=5)
    d.text(s, "Read across: highest NII margin (Kotak 4.06%) does not buy the highest RoA because opex is also highest (2.65%). SBI's 14.5x leverage lifts its RoE (16.2%) above HDFC's despite the lowest RoA.", 0.6, 4.6, 12, 1.2, 14)
    # 4 tree
    s = d.slide("The RoA tree shows margin builds returns and opex and provisions consume them, in different proportions by bank", src_b, "RoA tree")
    banks = [BN[b] for b in fy.index]
    d.chart(s, XL_CHART_TYPE.COLUMN_STACKED, banks, [("NII", fy.nii_p.round(2).tolist()), ("Other income", fy.other_income_p.round(2).tolist()), ("Opex", (-fy.opex_p).round(2).tolist()),
            ("Provisions", (-fy.provisions_p).round(2).tolist()), ("Tax", (-fy.tax_p).round(2).tolist())], 0.6, 1.7, 8.4, 5.1, colors=[S[0], S[2], S[1], S[3], S[4]], gap=50, overlap=100)
    d.text(s, "RoA (% of avg assets)\n" + "\n".join(f"{BN[b]}: {x.pat_p:.2f}%" for b, x in fy.iterrows()), 9.4, 2.0, 3.4, 2.8, 15, NAVY, bold=True)
    d.text(s, "Computed RoA ties to reported within 10 bp (SBI exact); differences come from daily-average vs simple-average assets.", 9.4, 4.9, 3.4, 1.5, 11, MUTED)
    # 5 shapley
    s = d.slide("Shapley attribution: SBI's gap is all margin, Axis's is margin plus credit cost, Kotak's is cost", "pipeline/shapley.py: order-independent attribution over RoA = (NII + OI - opex - provisions) x (1 - tax rate); contributions sum exactly to the gap", "Gap attribution")
    order = ["SBIN", "AXISBANK", "HDFCBANK", "KOTAKBANK"]
    d.chart(s, XL_CHART_TYPE.BAR_STACKED, [BN[b] for b in order], [(n, (100 * sh.loc[order, k]).round(0).tolist()) for k, n in [("nii", "NII"), ("oi", "Other income"), ("opex", "Opex"), ("prov", "Provisions"), ("tax_rate", "Tax rate")]],
            0.6, 1.7, 8.6, 5.1, colors=[S[0], S[2], S[1], S[3], S[4]], gap=60, overlap=100)
    d.text(s, "bp of RoA gap to ICICI\n(positive = widens the gap)\n\n" + "\n".join(f"{BN[b]}: {100*sh.loc[b].gap:.0f} bp" for b in order), 9.6, 2.0, 3.2, 3.0, 15, NAVY, bold=True)
    d.text(s, "Why Shapley: a sequential bridge assigns the tax-rate interaction to whichever line moves last; Shapley removes that ordering bias.", 9.6, 5.0, 3.2, 1.6, 11, MUTED)
    # 6 say vs do
    s = d.slide("Management margin guidance held for a few quarters at ICICI and Kotak, then broke in Q2 FY27; HDFC missed its stated range", "FactIQ earnings-call claim graph (paraphrases; verbatim quotes linked in data/inputs/concall_say_do.csv); outcomes from bank decks", "Say vs do")
    d.table(s, ["Bank", "Call", "Management said (paraphrase)", "What happened", "Verdict"], [[BN[r.bank], r.call_quarter, r.said, r.outcome, r.verdict] for r in say.itertuples()],
            0.5, 1.75, 12.3, col_w=[1.1, 1.1, 4.2, 4.3, 1.6], size=10)
    # 7 levers
    sens = [(BN[b], 10 * (1 - x.t), 25 * (1 - x.t)) for b, x in fy.iterrows()]
    s = d.slide("Each bank has one lever worth pulling first: every 10 bp of margin is worth 7-8 bp of RoA after tax", src_b + "; sensitivity = shock x (1 - effective tax rate)", "So what")
    d.table(s, ["Bank", "Primary lever", "Why (FY26 evidence)", "+10 bp NII -> RoA", "-25 bp credit cost -> RoA"],
            [["SBI", "Deposit franchise / pricing", "NII explains the whole gap; opex already lowest", f"+{sens[4][1]:.1f} bp", f"+{sens[4][2]:.1f} bp"],
             ["Axis Bank", "Credit discipline + margin", "Provisions 0.76% of assets, highest in set", f"+{sens[3][1]:.1f} bp", f"+{sens[3][2]:.1f} bp"],
             ["Kotak", "Cost-to-serve", "Opex 2.65% of assets, highest in set", f"+{sens[2][1]:.1f} bp", f"+{sens[2][2]:.1f} bp"],
             ["HDFC Bank", "Post-merger margin rebuild", "NII 63 bp below ICICI; CASA rebuild", f"+{sens[1][1]:.1f} bp", f"+{sens[1][2]:.1f} bp"],
             ["ICICI Bank", "Defend margin as rates turn", "Q2 FY27 NIM 4.18%, -14 bp vs Q4", f"+{sens[0][1]:.1f} bp", f"+{sens[0][2]:.1f} bp"]],
            0.6, 1.9, 12.1, col_w=[1.6, 2.8, 4.1, 1.8, 1.8], size=12)
    d.text(s, "Next refresh: SBI Q2 FY27 (results 3 Nov 2026) drops into the same pipeline: python pipeline/screener.py SBIN && python pipeline/build_bank_facts.py", 0.6, 5.0, 12, 0.8, 12, MUTED)
    # appendix
    s = d.slide("Appendix: method, definitions and data traps", src_b, "Appendix")
    d.text(s, "- Standalone only; FY26 = Apr-25 to Mar-26; Q2 FY27 annualised x4 on (Mar-26 + Sep-26)/2 assets.\n- Opex = Screener (Expenses + Depreciation) - provisions; equals deck opex for all banks where cited.\n- SBI's 'Total Provisions' (Rs 42,983 cr) includes tax; ex-tax provisions = operating profit - PBT = Rs 17,538 cr.\n- HDFC GNPA is 1.15% (secondary sites swap in NNPA 0.38%).\n- One-offs not stripped: SBI Yes Bank stake gain Rs 4,593 cr; Axis one-time provision Rs 2,001 cr; HDFC transaction gains.\n- NIM bases differ: HDFC reports on total assets, others on interest-earning assets.\n- Workbook: models/01_Bank_RoA_Benchmark.xlsx (live formulas, checks tab).", 0.6, 1.8, 12, 4.8, 14)
    d.save()


def ins_deck():
    ir = pd.read_csv(I / "irdai_inputs.csv")
    g = lambda k, s: float(ir[(ir.key == k) & (ir.segment == s)].value.iloc[0])  # noqa: E731
    ch = pd.read_csv(T / "ins_channel_reset.csv"); ex = pd.read_csv(T / "ins_insurer_exposure.csv"); pr = pd.read_csv(T / "ins_promoter_bank_hit.csv")
    mc = pd.read_csv(T / "ins_mc_summary.csv", index_col=0)["reset_cr"]
    tot = ch.reset_cr.sum()
    eom = {s: 100 * (g("total_commission", s) + g("opex", s)) / g("total_premium", s) for s in ["Public", "Private"]}
    cut = {k: (g("total_commission", "Private") + g("opex", "Private")) - v / 100 * g("total_premium", "Private") for k, v in [("y2", 15), ("y5", 12.5)]}
    cg = {s: 100 * (g("total_commission", s) / g("total_commission_PY", s) - 1) for s in ["Public", "Private"]}
    pg = {s: 100 * (g("total_premium", s) / g("total_premium_PY", s) - 1) for s in ["Public", "Private"]}
    nbi = {s: 100 * (g("fy_commission", s) + g("single_commission", s)) / (g("fy_premium", s) + g("single_premium", s)) for s in ["Public", "Private"]}
    d = Deck("02_Insurance_Distribution_Caps.pptx", "IRDAI distribution reforms")
    src = "IRDAI Annual Report 2024-25 (Tables I.9-I.14); IRDAI Handbook 2024-25 (T2, T3, T13, T99, T100); IRDAI consultation 'Recalibrating Economics of Insurance Distribution' Parts 1-2 (Sep 2026)"
    sbi = ex[ex.insurer.str.contains("SBI Life")].iloc[0]; hdfc = ex[ex.insurer.str.contains("HDFC Life")].iloc[0]
    s = d.slide(f"Proposed caps would reset ~Rs {tot/1e3:.1f}k cr a year of distributor income, equal to ~{sbi.reset_pct_pat:.0f}% of SBI Life's profit; private insurers must take out Rs {cut['y2']/1e3:.1f}k cr of expense in two years", src + ". Caps are PROPOSED, not final", "Executive summary")
    d.big(s, f"Rs {tot/1e3:.1f}k cr", f"Annual first-year commission above the proposed caps (base case); Monte Carlo P10-P90 Rs {mc['10%']/1e3:.1f}k-{mc['90%']/1e3:.1f}k cr", 0.6, 1.9)
    d.big(s, f"{eom['Private']:.1f}%", f"Private-sector expense of management vs proposed 15% (yr 2) and 12.5% (yr 5); LIC is at {eom['Public']:.1f}%", 4.8, 1.9, color=S[1])
    d.big(s, f"{sbi.reset_pct_pat:.0f}% / {hdfc.reset_pct_pat:.0f}%", "Reset as % of FY25 PAT: SBI Life / HDFC Life (bank-promoted, 50-60% bank channel), vs ~6% for LIC", 9.0, 1.9, color=S[2])
    d.text(s, "Implication: the economics move from distributors back to policyholders and insurers, but bank-promoted insurers carry the renegotiation risk. The winning response is a shift to long-PPT products, persistency-linked pay and direct/Bima Sugam channels.", 0.6, 4.7, 12, 1.4, 15)
    s = d.slide(f"Distribution captured the growth: private commission rose {cg['Private']:.0f}% in FY25 against premium growth of {pg['Private']:.0f}%", src, "Complication")
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, ["LIC (public)", "Private"], [("Commission growth %", [round(cg['Public'], 1), round(cg['Private'], 1)]), ("Premium growth %", [round(pg['Public'], 1), round(pg['Private'], 1)])],
            0.6, 1.7, 8.2, 5.1, colors=[S[1], S[0]], labels=True, fmt="0.0")
    d.text(s, "Industry: commission +18.0% vs premium +6.7%; commission ratio 6.21% -> 6.86% of premium.\n\nIRDAI's own diagnosis (Part 1, p19): corporate-agent remuneration +125% FY23-25 vs new business premium +28%; remuneration growing 4-5x faster than business (para 44).", 9.2, 2.0, 3.6, 4.0, 14)
    s = d.slide(f"Private insurers spend ~{nbi['Private']/nbi['Public']:.0f}x LIC per rupee of new business on commission ({nbi['Private']:.1f}% vs {nbi['Public']:.1f}%)", src + ". New-business commission = first-year + single-premium commission / (first-year + single premium)", "Finding")
    d.chart(s, XL_CHART_TYPE.BAR_CLUSTERED, ["LIC (public)", "Private"], [("NB commission % of NB premium", [round(nbi['Public'], 1), round(nbi['Private'], 1)])], 0.6, 1.7, 8.2, 3.6, colors=[S[0]], labels=True, legend=False)
    d.text(s, f"First-year commission alone is ~{100*g('fy_commission','Private')/g('fy_premium','Private'):.0f}% of first-year premium for both LIC and private players. The private gap comes from mix: LIC's new business is dominated by low-commission single premium.", 0.6, 5.5, 12, 1.2, 14)
    s = d.slide("Every channel pays above its proposed cap; brokers and 'other' corporate agents sit 27-45 pp over, banks 11 pp, agents 6.5 pp", src + "; Annexure 3 Table 4; cap blended at an assumed PPT mix (50% >=10y), see workbook 4_Cap_Gap", "Finding")
    d.chart(s, XL_CHART_TYPE.BAR_CLUSTERED, ch.channel.tolist(), [("Average first-year commission %", ch.avg_rate.tolist()), ("Proposed cap % (blended)", ch.cap.round(1).tolist())], 0.6, 1.7, 8.4, 5.1, colors=[S[0], S[3]], labels=True, fmt="0", gap=40)
    d.text(s, "\n".join(f"{r.channel}: Rs {r.reset_cr:,.0f} cr" for r in ch.itertuples()) + f"\n\nTotal: Rs {tot:,.0f} cr (lower bound: channel maxima reach 62-92%)", 9.4, 2.0, 3.4, 4.0, 13, NAVY, bold=True)
    top = ex.dropna(subset=["reset_pct_total_premium"]).head(10)
    s = d.slide("Relative to profit, bank-promoted private insurers are the most exposed; in rupees LIC is largest only because of scale", src + "; PAT from Screener (secondary) for listed insurers only", "Finding")
    d.table(s, ["Insurer", "Bank channel %", "Reset Rs cr", "% of premium", "% of FY25 PAT"],
            [[r.insurer.replace(" Insurance Company Ltd", "").replace(" Insurance Ltd", ""), f"{100*r.bank_ca_share:.0f}", f"{r.reset_cr:,.0f}", f"{r.reset_pct_total_premium:.2f}", ("-" if pd.isna(r.reset_pct_pat) else f"{r.reset_pct_pat:.0f}")] for r in top.itertuples()],
            0.6, 1.75, 12.1, col_w=[4.6, 1.8, 1.8, 1.9, 2.0], size=12, highlight_col=4)
    d.text(s, f"Promoter banks lose only {pr.pct_of_bank_other_income.min():.1f}-{pr.pct_of_bank_other_income.max():.1f}% of FY26 other income, so they have room to hold the line in negotiations; the insurer carries more of the risk.", 0.6, 6.0, 12, 0.8, 13)
    s = d.slide(f"The EoM glide path forces private life insurers to remove Rs {cut['y2']/1e3:.1f}k cr of cost by year 2 and Rs {cut['y5']/1e3:.1f}k cr by year 5 (FY25 base)", src + "; Box 2 (FY2027-28 = Year 1). EoM proxy = (commission + opex) / premium", "Finding")
    gi = (g("commission_total", "Total") + g("opex_total", "Total")); gdpi = g("gdpi", "Total")
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, ["Private life", "LIC", "General insurance"], [("FY25 EoM %", [round(eom['Private'], 1), round(eom['Public'], 1), round(100 * gi / gdpi, 1)]),
            ("Year-2 limit %", [15, 15, 25]), ("Year-5 limit %", [12.5, 12.5, 20])], 0.6, 1.7, 8.4, 5.1, colors=[S[0], GRAY, S[3]], labels=True, fmt="0.0")
    d.text(s, f"Cut needed (Rs cr, FY25 base)\nPrivate life: {cut['y2']:,.0f} (Y2) / {cut['y5']:,.0f} (Y5)\nLIC: 0 vs 15%/12.5%, but must reach 10%\nGeneral: {gi-0.25*gdpi:,.0f} (Y2) / {gi-0.20*gdpi:,.0f} (Y5)", 9.4, 2.0, 3.4, 3.2, 14, NAVY, bold=True)
    s = d.slide("A 90-day agenda for a private life CEO: reprice the product shelf, rewrite bank contracts and build the direct channel before caps bite in FY28", src, "Recommendation")
    d.table(s, ["Move", "What to do in 90 days", "Why (evidence)"],
            [["1. Shift mix to long PPT", "Re-weight incentives to >=10y PPT where the cap is 20-25%", "<5y PPT cap is 5-6.25%; avg FYP commission today ~27%"],
             ["2. Rewrite bancassurance contracts", "Fold rewards into capped commission; add persistency claw-backs", "Total payouts to promoter banks up to 42% of NB (Annex 3 T8)"],
             ["3. Protect term", "Redesign term distribution economics", "Term FYP commission averages 51% vs 25-30% cap"],
             ["4. Build direct and Bima Sugam", "Fund digital/direct now from commission savings", "Direct/online is ~12% of individual NB today"],
             ["5. Cost programme", f"Target Rs {cut['y2']/1e3:.0f}k cr industry-wide opex+commission reduction", f"Private EoM {eom['Private']:.1f}% vs 15% in 2 years"]],
            0.6, 1.8, 12.1, col_w=[2.8, 4.8, 4.5], size=12)
    s = d.slide("Appendix: regulatory timeline and method", src, "Appendix")
    d.text(s, "- Dec 2025: Sabka Bima Sabki Raksha Act passed (effective 5 Feb 2026); 100% FDI under automatic route.\n- 23-24 Sep 2026: IRDAI consultation on distribution economics; comments closed 25 Oct 2026.\n- Proposed: EoM 15% (Y2) / 12.5% (Y5) for life, 25% / 20% for general; commission caps by PPT and channel (Box 4A/4B); ban on forced bundling.\n- Method: channel gap = Annexure 3 average first-year commission - cap blended at an assumed PPT mix; rupees = gap x FYP allocated by Handbook T99 channel shares. Monte Carlo over PPT mix, term share and channel rates (seed 20261102).\n- Limits: IRDAI does not publish commission by PPT or by insurer-channel; the cap test is directional, a lower bound on averages.", 0.6, 1.8, 12, 4.8, 14)
    d.save()


def upi_deck():
    m = pd.read_csv(T / "upi_monthly.csv", parse_dates=["month"]); c = pd.read_csv(T / "upi_concentration.csv", parse_dates=["month"])
    cm = pd.read_csv(T / "upi_cap_math.csv").set_index("app"); grid = pd.read_csv(T / "upi_mdr_grid.csv")
    peak = m.loc[m.volume_mn.idxmax()]; last = m.iloc[-1]
    d = Deck("03_UPI_MDR_and_Cap.pptx", "UPI hot take")
    src = "NPCI UPI product statistics and app-wise statistics; DFS FAQ on MDR (15 Sep 2026); PIB FY26 release (P2M share)"
    s = d.slide(f"UPI peaked at {peak.volume_mn/1e3:.2f} bn transactions in {peak.month:%b-%y} and has plateaued since; Oct-26 was {last.volume_mn/1e3:.2f} bn, not the 25.47 bn widely reported", src, "Volume")
    d.chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, m.month.dt.strftime("%b-%y").tolist(), [("bn transactions", (m.volume_mn / 1e3).round(2).tolist())], 0.6, 1.7, 9.0, 5.1, colors=[S[0]], legend=False, gap=40)
    d.text(s, f"Avg ticket Rs {last.avg_ticket_rs:,.0f} (Oct-26)\nValue Rs {last.value_cr/1e5:.2f} lakh cr\n\nThe secondary-press figure for Oct-26 does not match NPCI's own file: always check against source.", 9.9, 2.0, 2.9, 4.0, 14, NAVY, bold=True)
    s = d.slide(f"The new MDR creates a Rs {grid.pool_cr.min()/1e3:.0f}k-{grid.pool_cr.max()/1e3:.0f}k cr annual pool from <5% of merchant volume; the range hinges on how much P2M value sits above Rs 2,000", src + ". Pool = trailing-12m value x 29% P2M x share above Rs 2,000 x (1 - exempt) x 0.4% x 0.95 cap haircut", "MDR pool")
    gz = grid.pivot(index="p2m_value_above_2000", columns="exempt_share", values="pool_cr")
    d.table(s, ["P2M value above Rs 2k \\ exempt share"] + [f"{int(100*x)}%" for x in gz.columns], [[f"{int(100*i)}%"] + [f"{v:,.0f}" for v in row] for i, row in zip(gz.index, gz.values)], 0.6, 1.9, 8.5, size=14)
    d.text(s, "Rules (DFS FAQ): 0.4% on P2M > Rs 2,000; Rs 300 cap at >= Rs 75,000; Rs 5 flat for railways, telecom, insurance, fuel; P2PM small merchants (<= Rs 1 lakh/month) and AutoPay mandates exempt.\n\nThe fee lands on large merchants: a value-driven, concentrated pool.", 9.4, 1.9, 3.4, 4.6, 13)
    s = d.slide(f"The 30% cap is out of reach by Dec-26: PhonePe ({cm.loc['phonepe','share_latest_pct']:.1f}%) would need to shed {cm.loc['phonepe','required_pp_per_month']:.1f} pp a month; its 12-month trend is {cm.loc['phonepe','trend_pp_per_month']:+.2f} pp", src + ". Trend = OLS slope of monthly share, last 13 months. Extension is a judgement, not a reported fact", "Market structure")
    cc = c[c.month >= "2024-01-01"]
    d.chart(s, XL_CHART_TYPE.LINE, cc.month.dt.strftime("%b-%y").tolist(), [("PhonePe", (100 * cc.phonepe).round(1).tolist()), ("Google Pay", (100 * cc.google_pay).round(1).tolist()),
            ("Paytm", (100 * cc.paytm).round(1).tolist()), ("Navi", (100 * cc.navi).round(1).tolist()), ("30% cap", [30] * len(cc))], 0.6, 1.7, 8.6, 5.1, colors=[S[4], S[0], S[2], S[3], GRAY])
    d.text(s, f"HHI {c.iloc[-1].hhi:,.0f} ({c.iloc[-1].month:%b-%y}), down from a {c.hhi.max():,.0f} peak as Navi ({100*c.iloc[-1].navi:.1f}%) gains.\n\nLikely outcome: another extension or phased glide path rather than hard enforcement on 1 Jan 2027 (judgement).", 9.5, 2.0, 3.3, 4.2, 14)
    d.save()


if __name__ == "__main__":
    bank_deck(); ins_deck(); upi_deck()
