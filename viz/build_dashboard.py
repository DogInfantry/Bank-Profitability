"""Build viz/dashboard.html: a single-file, client-facing dashboard over data/tidy/* and data/inputs/*.

Plotly (pinned CDN build) renders; data is embedded as JSON so the page works offline-from-repo.
Design rules follow the dataviz method: one y-axis per chart, categorical colours fixed to entities,
validated reference palette, light/dark tokens, hover on every mark, a table view behind every chart.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T, I = ROOT / "data" / "tidy", ROOT / "data" / "inputs"
OUT = ROOT / "viz" / "dashboard.html"
BANK_ORDER = ["ICICIBANK", "HDFCBANK", "KOTAKBANK", "AXISBANK", "SBIN"]
BANK_NAME = {"SBIN": "SBI", "HDFCBANK": "HDFC Bank", "ICICIBANK": "ICICI Bank", "AXISBANK": "Axis Bank", "KOTAKBANK": "Kotak"}


def r(x, n=2):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), n)


def payload() -> dict:
    w = pd.read_csv(T / "bank_model_inputs.csv")
    w["avg_assets"] = (w.assets_open + w.assets_close) / 2
    for c in ["nii", "other_income", "opex", "provisions", "tax", "pat"]:
        w[c + "_pct"] = 100 * w[c] * w.annualise / w.avg_assets
    fy = w[w.period == "FY26"].set_index("bank").loc[BANK_ORDER]
    tree = [dict(bank=BANK_NAME[b], nii=r(x.nii_pct), oi=r(x.other_income_pct), opex=r(-x.opex_pct),
                 prov=r(-x.provisions_pct), tax=r(-x.tax_pct), roa=r(x.pat_pct)) for b, x in fy.iterrows()]
    sh = pd.read_csv(T / "bank_shapley_FY26.csv").query("metric=='RoA' and benchmark=='ICICIBANK'")
    shap = [dict(bank=BANK_NAME[x.bank], gap=r(x.gap), nii=r(x.nii), oi=r(x.oi), opex=r(x.opex), prov=r(x.prov), tax=r(x.tax_rate))
            for x in sh.itertuples()]
    f = pd.read_csv(T / "bank_facts.csv")
    h = f[f.metric == "hist_roa"].copy()
    h["fy"] = h.period.str[2:].astype(int)
    hist = {BANK_NAME[b]: dict(x=[f"FY{y}" for y in g.sort_values("fy").fy], y=[r(v) for v in g.sort_values("fy").value])
            for b, g in h.groupby("entity")}
    nim = pd.read_csv(I / "nim_trajectory.csv").dropna(subset=["q2fy27_nim"])
    nimt = [dict(bank=BANK_NAME[x.bank], q4=x.q4fy26_nim, q2=x.q2fy27_nim, chg=x.change_bp, basis=x.basis) for x in nim.itertuples()]
    say = pd.read_csv(I / "concall_say_do.csv").fillna("")
    sayd = [dict(bank=BANK_NAME[x.bank], call=x.call_quarter, said=x.said, outcome=x.outcome, verdict=x.verdict, url=x.claim_source_url)
            for x in say.itertuples()]
    q2 = w[w.period == "Q2FY27"].set_index("bank")
    kpi_bank = dict(best=r(fy.loc["ICICIBANK"].pat_pct), sbi=r(fy.loc["SBIN"].pat_pct),
                    sbi_gap_bp=round(100 * (fy.loc["ICICIBANK"].pat_pct - fy.loc["SBIN"].pat_pct)),
                    sbi_nii_share=round(100 * sh.set_index("bank").loc["SBIN"].nii))
    # insurance
    ir = pd.read_csv(I / "irdai_inputs.csv")
    g = lambda k, s: float(ir[(ir.key == k) & (ir.segment == s)].value.iloc[0])  # noqa: E731
    growth = dict(seg=["LIC (public)", "Private"],
                  comm=[r(100 * (g("total_commission", s) / g("total_commission_PY", s) - 1), 1) for s in ["Public", "Private"]],
                  prem=[r(100 * (g("total_premium", s) / g("total_premium_PY", s) - 1), 1) for s in ["Public", "Private"]])
    eom = {s: r(100 * (g("total_commission", s) + g("opex", s)) / g("total_premium", s), 1) for s in ["Public", "Private"]}
    ch = pd.read_csv(T / "ins_channel_reset.csv")
    chan = [dict(ch=x.channel.replace("Corporate agents - ", "CA: "), rate=r(x.avg_rate, 1), cap=r(x.cap, 1), gap=r(x.gap_pp, 1), reset=r(x.reset_cr, 0)) for x in ch.itertuples()]
    ex = pd.read_csv(T / "ins_insurer_exposure.csv").head(12)
    expo = [dict(ins=x.insurer.replace(" Insurance Company Ltd", "").replace(" Insurance Ltd", "").replace(" Life", " Life").strip(),
                 pct=r(x.reset_pct_total_premium), cr=r(x.reset_cr, 0), bank=r(100 * x.bank_ca_share, 0) if pd.notna(x.bank_ca_share) else None,
                 pat=r(x.reset_pct_pat, 0) if pd.notna(x.reset_pct_pat) else None) for x in ex.itertuples()]
    mcs = pd.read_csv(T / "ins_mc_summary.csv", index_col=0)["reset_cr"]
    gi = [dict(line=l.title(), comm=r(100 * g(f"commission_{l}", "Total") / g(f"gdpi_{l}", "Total"), 1), icr=g(f"icr_{l}", "Total"), gdpi=g(f"gdpi_{l}", "Total"))
          for l in ["motor", "health", "fire", "marine", "others"]]
    promo = pd.read_csv(T / "ins_promoter_bank_hit.csv")
    prom = [dict(bank=BANK_NAME[x.promoter_bank], cr=r(x.bank_channel_reset_cr, 0), pct=r(x.pct_of_bank_other_income, 2)) for x in promo.itertuples()]
    # upi
    m = pd.read_csv(T / "upi_monthly.csv", parse_dates=["month"])
    upi_m = dict(x=m.month.dt.strftime("%b-%y").tolist(), vol=[r(v / 1e3, 2) for v in m.volume_mn], ticket=[r(v, 0) for v in m.avg_ticket_rs],
                 val=[r(v / 1e5, 2) for v in m.value_cr])
    c = pd.read_csv(T / "upi_concentration.csv", parse_dates=["month"])
    upi_c = dict(x=c.month.dt.strftime("%Y-%m").tolist(), **{k: [r(100 * v, 2) for v in c[k]] for k in ["phonepe", "google_pay", "paytm", "navi", "top2_share", "bank_apps"]},
                 hhi=[r(v, 0) for v in c.hhi])
    cm = pd.read_csv(T / "upi_cap_math.csv").set_index("app")
    grid = pd.read_csv(T / "upi_mdr_grid.csv")
    gz = grid.pivot(index="p2m_value_above_2000", columns="exempt_share", values="pool_cr")
    mdr = dict(x=[f"{int(100*v)}% exempt" for v in gz.columns], y=[f"{int(100*v)}% above Rs2k" for v in gz.index], z=[[r(v, 0) for v in row] for row in gz.values])
    cb = pd.read_csv(T / "crunchbase_fs_landscape.csv").fillna("")
    cbd = [dict(co=x.company, seg=x.segment, usd=(r(x.total_funding_usd / 1e6, 0) if x.total_funding_usd != "" else None), last=x.last_round_type, date=x.last_round_date, url=x.crunchbase_url, why=x.relevance)
           for x in cb.itertuples()]
    return dict(tree=tree, shap=shap, hist=hist, nim=nimt, say=sayd, kpi_bank=kpi_bank,
                growth=growth, eom=eom, chan=chan, expo=expo, mc=dict(p10=r(mcs["10%"], 0), p50=r(mcs["50%"], 0), p90=r(mcs["90%"], 0)),
                gi=gi, prom=prom, upi_m=upi_m, upi_c=upi_c,
                cap=dict(pp=r(cm.loc["phonepe", "share_latest_pct"], 1), gp=r(cm.loc["google_pay", "share_latest_pct"], 1),
                         pp_need=r(cm.loc["phonepe", "required_pp_per_month"], 1), pp_trend=r(cm.loc["phonepe", "trend_pp_per_month"], 2),
                         gp_need=r(cm.loc["google_pay", "required_pp_per_month"], 1), gp_trend=r(cm.loc["google_pay", "trend_pp_per_month"], 2)),
                mdr=mdr, mdr_range=[r(grid.pool_cr.min(), 0), r(grid.pool_cr.max(), 0)], cb=cbd,
                q2_note=f"Q2 FY27 columns: {', '.join(BANK_NAME[b] for b in q2.index)}; SBI pending (results 3 Nov 2026).")


HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>India FS Profit Pools</title>
<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js" integrity="sha384-cCVCZkAjYNxaYKbM8lsArLznDF/SvMFr1jcZrvOpSTCa0W40ZAdLzHCEulnUa5i7" crossorigin="anonymous"></script>
<style>
:root{color-scheme:light;--surface-0:#f6f5f2;--surface-1:#fcfcfb;--border:#e2e0da;--text-primary:#0b0b0b;--text-secondary:#52514e;--text-muted:#6f6e69;--grid:#ebe9e4;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--seq-lo:#cde2fb;--seq-hi:#104281;--good:#0ca30c;--critical:#d03b3b;--accent:#2a78d6}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--surface-0:#111110;--surface-1:#1a1a19;--border:#2e2e2b;--text-primary:#f0efec;--text-secondary:#c3c2b7;--text-muted:#9a998f;--grid:#2a2a27;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--seq-lo:#184f95;--seq-hi:#cde2fb;--accent:#3987e5}}
:root[data-theme="dark"]{color-scheme:dark;--surface-0:#111110;--surface-1:#1a1a19;--border:#2e2e2b;--text-primary:#f0efec;--text-secondary:#c3c2b7;--text-muted:#9a998f;--grid:#2a2a27;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--seq-lo:#184f95;--seq-hi:#cde2fb;--accent:#3987e5}
*{box-sizing:border-box}body{margin:0;background:var(--surface-0);color:var(--text-primary);font:15px/1.5 Inter,system-ui,-apple-system,Segoe UI,sans-serif}
header{padding:28px 16px 8px;max-width:1240px;margin:auto}h1{font-size:26px;margin:0 0 4px;letter-spacing:-.01em}.sub{color:var(--text-secondary);margin:0}
nav{position:sticky;top:0;z-index:5;background:var(--surface-0);border-bottom:1px solid var(--border)}nav .in{max-width:1240px;margin:auto;padding:0 16px;display:flex;gap:4px;overflow-x:auto}
nav button{border:0;background:none;color:var(--text-secondary);font:inherit;font-weight:600;padding:12px 14px;border-bottom:2px solid transparent;cursor:pointer;white-space:nowrap}
nav button[aria-selected=true]{color:var(--text-primary);border-color:var(--accent)}#theme{margin-left:auto}
main{max-width:1240px;margin:auto;padding:16px}section{display:none}section.on{display:block}
.answer{background:var(--surface-1);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:8px;padding:14px 16px;margin:8px 0 16px}
.answer b{display:block;font-size:17px;margin-bottom:4px}.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:16px}
.tile{background:var(--surface-1);border:1px solid var(--border);border-radius:8px;padding:12px 14px}.tile .v{font-size:28px;font-weight:700;letter-spacing:-.02em}.tile .l{color:var(--text-secondary);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,540px),1fr));gap:16px}
.card{background:var(--surface-1);border:1px solid var(--border);border-radius:8px;padding:14px 14px 8px;min-width:0}
.card h3{font-size:15px;margin:0 0 2px}.card .note{color:var(--text-muted);font-size:12px;margin:4px 0 6px}.plot{width:100%;height:340px}
details{margin:4px 0 6px;font-size:13px}summary{cursor:pointer;color:var(--text-secondary)}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--border);vertical-align:top}th{color:var(--text-secondary);font-weight:600}
td.n{text-align:right;font-variant-numeric:tabular-nums}.wrap{overflow-x:auto}a{color:var(--accent)}
.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;border:1px solid var(--border)}
.ok::before{content:"\2713  ";color:var(--good)}.no::before{content:"\2715  ";color:var(--critical)}.mid::before{content:"\25D0  ";color:var(--text-muted)}
footer{max-width:1240px;margin:auto;padding:8px 16px 40px;color:var(--text-muted);font-size:12px}
</style></head><body>
<header><h1>India FS profit pools: banks, insurance distribution, UPI</h1>
<p class="sub">Standalone FY26 and Q2 FY27 benchmarks, IRDAI's proposed commission caps, NPCI's monthly data and the new MDR. Data as of 3 Nov 2026. Every figure traces to <code>data/tidy</code> with a source and page.</p></header>
<nav><div class="in" role="tablist">
<button role="tab" aria-selected="true" data-t="banks">Banks</button><button role="tab" aria-selected="false" data-t="ins">Insurance</button>
<button role="tab" aria-selected="false" data-t="upi">UPI</button><button role="tab" aria-selected="false" data-t="say">Say vs do</button>
<button role="tab" aria-selected="false" data-t="src">Sources &amp; method</button><button id="theme" aria-label="Toggle theme">Theme</button></div></nav>
<main>
<section id="banks" class="on">
 <div class="answer"><b>Indian bank RoA gaps have different root causes, so one playbook does not fit all.</b>
 ICICI earns the peer-best FY26 RoA. SBI trails by <span id="k_gap"></span> bp, and the margin gap alone (<span id="k_nii"></span> bp) is bigger than the whole gap: SBI's lower opex per rupee of assets claws some back. Axis's gap is margin plus credit cost; Kotak's is cost.</div>
 <div class="tiles"><div class="tile"><div class="v" id="t1"></div><div class="l">ICICI Bank FY26 RoA (best)</div></div>
 <div class="tile"><div class="v" id="t2"></div><div class="l">SBI FY26 RoA</div></div><div class="tile"><div class="v" id="t3"></div><div class="l">All four reporting banks: Q2 FY27 NIM below Q4 FY26</div></div></div>
 <div class="grid">
  <div class="card"><h3>RoA tree: margin builds returns, opex and provisions consume them</h3><p class="note">% of average assets, FY26 standalone. Diamond = RoA.</p><div class="plot" id="p_tree"></div><details><summary>Table</summary><div class="wrap" id="tb_tree"></div></details></div>
  <div class="card"><h3>Why each bank trails ICICI: Shapley attribution of the RoA gap</h3><p class="note">pp of RoA. Positive = factor widens the gap; negative = works in the bank's favour. Sums exactly to the gap.</p><div class="plot" id="p_shap"></div><details><summary>Table</summary><div class="wrap" id="tb_shap"></div></details></div>
  <div class="card"><h3>Ten-year RoA: SBI's recovery stalls below private peers</h3><p class="note">PAT / average assets, standalone (Screener history).</p><div class="plot" id="p_hist"></div></div>
  <div class="card"><h3>Every reported Q2 FY27 NIM is below Q4 FY26</h3><p class="note">Reported NIM, %. Bases differ: HDFC on total assets, others on interest-earning assets.</p><div class="plot" id="p_nim"></div><details><summary>Table</summary><div class="wrap" id="tb_nim"></div></details></div>
 </div></section>
<section id="ins">
 <div class="answer"><b>Commission caps would reset ~Rs <span id="k_reset"></span> cr a year of distributor income; relative to profit, bank-promoted private insurers are most exposed.</b>
 Private commission grew <span id="k_cg"></span>% vs premium <span id="k_pg"></span>% in FY25. Private expense of management is <span id="k_eom"></span>% of premium against a proposed 15% then 12.5%. The caps are a September 2026 <i>proposal</i>, not final.</div>
 <div class="grid">
  <div class="card"><h3>Distribution captured the growth</h3><p class="note">FY25 YoY growth, %. IRDAI Annual Report Tables I.9-I.10.</p><div class="plot" id="p_growth"></div></div>
  <div class="card"><h3>Every channel's first-year commission sits above its proposed cap</h3><p class="note">Average first-year commission (IRDAI Part 2, Annexure 3) vs blended cap at the base PPT mix (assumption). Lower bound: maxima reach 62-92%.</p><div class="plot" id="p_chan"></div><details><summary>Table</summary><div class="wrap" id="tb_chan"></div></details></div>
  <div class="card"><h3>The reset bites hardest where brokers and corporate agents dominate the mix</h3><p class="note">Commission above cap as % of FY25 total premium, top 12 insurers by rupee reset. Hover for bank-channel share and % of PAT (bank-promoted SBI Life and HDFC Life: ~70-75% of FY25 PAT).</p><div class="plot" id="p_expo" style="height:420px"></div><details><summary>Table</summary><div class="wrap" id="tb_expo"></div></details></div>
  <div class="card"><h3>Non-life: motor pays the most commission per rupee of premium</h3><p class="note">FY25 commission % of GDPI vs incurred claims ratio, by line. Marker area = GDPI.</p><div class="plot" id="p_gi"></div></div>
 </div>
 <div class="tiles" style="margin-top:16px"><div class="tile"><div class="v" id="t_mc"></div><div class="l">Monte Carlo P10-P90 annual reset (Rs cr), 10,000 draws</div></div>
 <div class="tile"><div class="v" id="t_prom"></div><div class="l">Promoter-bank fee hit, % of FY26 other income</div></div></div>
</section>
<section id="upi">
 <div class="answer"><b>UPI's first fee is a value-driven pool, and the 30% app cap is out of reach by December 2026.</b>
 NPCI's own file puts the record at Aug-26; Oct-26 was <span id="k_oct"></span> bn transactions, not the 25.47 bn widely reported. PhonePe needs to shed <span id="k_ppn"></span> pp a month; its 12-month trend is <span id="k_ppt"></span> pp.</div>
 <div class="grid">
  <div class="card"><h3>Monthly volume plateaued after the August record</h3><p class="note">Transactions, bn (NPCI product statistics).</p><div class="plot" id="p_vol"></div></div>
  <div class="card"><h3>Average ticket has drifted down about Rs 80 since early 2026</h3><p class="note">Rs per transaction = value / volume.</p><div class="plot" id="p_ticket"></div></div>
  <div class="card"><h3>Top-two apps stay far above the 30% cap</h3><p class="note">Share of UPI volume, % (NPCI app-wise). Dashed line = 30% cap.</p><div class="plot" id="p_share"></div></div>
  <div class="card"><h3>MDR pool: Rs <span id="k_mdr"></span> cr a year, depending on two unknowns</h3><p class="note">0.4% on P2M tickets above Rs 2,000 (DFS FAQ, 15 Sep 2026), on trailing-12-month value. Rows and columns are assumptions.</p><div class="plot" id="p_mdr"></div></div>
 </div>
 <div class="card" style="margin-top:16px"><h3>Who is funding the challengers (Crunchbase)</h3><div class="wrap" id="tb_cb"></div></div>
</section>
<section id="say"><div class="answer"><b>Management said vs what the P&amp;L did: guidance on margins held for ICICI and Kotak for a few quarters, then broke in Q2 FY27.</b> Paraphrased management claims, each linked to its verbatim quote (FactIQ earnings-call graph), scored against reported NIM from the banks' own decks.</div>
 <div class="card"><div class="wrap" id="tb_say"></div></div></section>
<section id="src"><div class="card"><h3>Sources and method</h3><div id="srcbody"></div></div></section>
</main>
<footer>Prepared by Anklesh. Inferences are labelled as estimates. Bain themes are referenced for framing only; no Bain charts or data are reproduced. <span id="q2note"></span></footer>
<script>
const D = __DATA__;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const $ = id => document.getElementById(id);
const bankColor = b => ({"ICICI Bank":css('--s1'),"HDFC Bank":css('--s2'),"Kotak":css('--s3'),"Axis Bank":css('--s4'),"SBI":css('--s5')})[b];
function base(extra={}){return Object.assign({paper_bgcolor:css('--surface-1'),plot_bgcolor:css('--surface-1'),font:{color:css('--text-secondary'),size:12,family:'Inter,system-ui,sans-serif'},
 margin:{l:56,r:16,t:8,b:44},xaxis:{gridcolor:css('--grid'),zerolinecolor:css('--border'),linecolor:css('--border')},yaxis:{gridcolor:css('--grid'),zerolinecolor:css('--text-muted'),linecolor:css('--border')},
 legend:{orientation:'h',y:-0.18,font:{color:css('--text-secondary')}},hoverlabel:{bgcolor:css('--surface-1'),bordercolor:css('--border'),font:{color:css('--text-primary')}},bargap:0.35},extra)}
const cfg={displayModeBar:false,responsive:true};
function table(el,cols,rows){$(el).innerHTML='<table><thead><tr>'+cols.map(c=>`<th>${c[0]}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>{const v=c[1](r);return `<td class="${typeof v==='number'?'n':''}">${v??'-'}</td>`}).join('')+'</tr>').join('')+'</tbody></table>'}
function draw(){
 const k=D.kpi_bank; $('k_gap').textContent=Math.round(k.sbi_gap_bp); $('k_nii').textContent=k.sbi_nii_share; $('t1').textContent=k.best.toFixed(2)+'%'; $('t2').textContent=k.sbi.toFixed(2)+'%'; $('t3').textContent=D.nim.length+' of '+D.nim.length;
 const comps=[['nii','NII',css('--s1')],['oi','Other income',css('--s3')],['opex','Opex',css('--s2')],['prov','Provisions',css('--s4')],['tax','Tax',css('--s5')]];
 const banks=D.tree.map(r=>r.bank);
 Plotly.react('p_tree',[...comps.map(([k,n,c])=>({type:'bar',name:n,x:banks,y:D.tree.map(r=>r[k]),marker:{color:c,line:{color:css('--surface-1'),width:2}},hovertemplate:'%{x}<br>'+n+': %{y:.2f}%<extra></extra>'})),
  {type:'scatter',mode:'markers+text',name:'RoA',x:banks,y:D.tree.map(r=>r.roa),text:D.tree.map(r=>r.roa.toFixed(2)),textposition:'top center',textfont:{color:css('--text-primary')},marker:{symbol:'diamond',size:11,color:css('--text-primary'),line:{color:css('--surface-1'),width:2}},hovertemplate:'%{x}<br>RoA: %{y:.2f}%<extra></extra>'}],
  base({barmode:'relative',yaxis:{title:'% of avg assets',gridcolor:css('--grid'),zerolinecolor:css('--text-muted')}}),cfg);
 table('tb_tree',[['Bank',r=>r.bank],['NII',r=>r.nii],['Other inc.',r=>r.oi],['Opex',r=>r.opex],['Prov.',r=>r.prov],['Tax',r=>r.tax],['RoA',r=>r.roa]],D.tree);
 const sf=[['nii','NII',css('--s1')],['oi','Other income',css('--s3')],['opex','Opex',css('--s2')],['prov','Provisions',css('--s4')],['tax','Tax rate',css('--s5')]];
 const sb=D.shap.map(r=>r.bank);
 Plotly.react('p_shap',sf.map(([k,n,c])=>({type:'bar',orientation:'h',name:n,y:sb,x:D.shap.map(r=>r[k]),marker:{color:c,line:{color:css('--surface-1'),width:2}},hovertemplate:'%{y}<br>'+n+': %{x:+.2f} pp<extra></extra>'})),
  base({barmode:'relative',margin:{l:80,r:16,t:8,b:44},legend:{orientation:'h',y:-0.3},xaxis:{title:'pp of RoA (gap to ICICI)',gridcolor:css('--grid'),zerolinecolor:css('--text-muted')}}),cfg);
 table('tb_shap',[['Bank',r=>r.bank],['Gap',r=>r.gap],['NII',r=>r.nii],['Other inc.',r=>r.oi],['Opex',r=>r.opex],['Prov.',r=>r.prov],['Tax',r=>r.tax]],D.shap);
 Plotly.react('p_hist',Object.entries(D.hist).map(([b,s])=>({type:'scatter',mode:'lines+markers',name:b,x:s.x,y:s.y,line:{color:bankColor(b),width:2},marker:{size:8,color:bankColor(b),line:{color:css('--surface-1'),width:2}},hovertemplate:b+' %{x}: %{y:.2f}%<extra></extra>'})),
  base({yaxis:{title:'RoA %',gridcolor:css('--grid'),zerolinecolor:css('--text-muted')}}),cfg);
 Plotly.react('p_nim',D.nim.map(r=>({type:'scatter',mode:'lines+markers+text',name:r.bank,x:[0,1],y:[r.q4,r.q2],text:['',r.bank+' '+r.chg+' bp'],textposition:'middle right',textfont:{color:css('--text-secondary')},line:{color:bankColor(r.bank),width:2},marker:{size:9,color:bankColor(r.bank),line:{color:css('--surface-1'),width:2}},hovertemplate:r.bank+' %{x}: %{y:.2f}%<extra></extra>'})),
  base({showlegend:false,margin:{l:56,r:16,t:8,b:44},xaxis:{tickvals:[0,1],ticktext:['Q4 FY26','Q2 FY27'],range:[-0.15,2.1],gridcolor:css('--grid')},yaxis:{title:'NIM %',gridcolor:css('--grid')}}),cfg);
 table('tb_nim',[['Bank',r=>r.bank],['Q4 FY26',r=>r.q4],['Q2 FY27',r=>r.q2],['Change (bp)',r=>r.chg],['Basis',r=>r.basis]],D.nim);
 // insurance
 $('k_reset').textContent=Math.round(D.chan.reduce((a,r)=>a+r.reset,0)).toLocaleString('en-IN'); $('k_cg').textContent=D.growth.comm[1]; $('k_pg').textContent=D.growth.prem[1]; $('k_eom').textContent=D.eom.Private;
 $('t_mc').textContent=D.mc.p10.toLocaleString('en-IN')+'-'+D.mc.p90.toLocaleString('en-IN'); $('t_prom').textContent=Math.min(...D.prom.map(p=>p.pct)).toFixed(1)+'-'+Math.max(...D.prom.map(p=>p.pct)).toFixed(1)+'%';
 Plotly.react('p_growth',[{type:'bar',name:'Commission growth',x:D.growth.seg,y:D.growth.comm,marker:{color:css('--s2')},text:D.growth.comm.map(v=>v+'%'),textposition:'outside',textfont:{color:css('--text-primary')},hovertemplate:'%{x}: commission %{y}%<extra></extra>'},
  {type:'bar',name:'Premium growth',x:D.growth.seg,y:D.growth.prem,marker:{color:css('--s1')},text:D.growth.prem.map(v=>v+'%'),textposition:'outside',textfont:{color:css('--text-primary')},hovertemplate:'%{x}: premium %{y}%<extra></extra>'}],
  base({barmode:'group',yaxis:{title:'YoY %',range:[-8,46],gridcolor:css('--grid'),zerolinecolor:css('--text-muted')}}),cfg);
 const cy=D.chan.map(r=>r.ch);
 Plotly.react('p_chan',[...D.chan.map(r=>({type:'scatter',mode:'lines',x:[r.cap,r.rate],y:[r.ch,r.ch],line:{color:css('--border'),width:3},hoverinfo:'skip',showlegend:false})),
  {type:'scatter',mode:'markers',name:'Proposed cap',x:D.chan.map(r=>r.cap),y:cy,marker:{size:12,color:css('--s4'),line:{color:css('--surface-1'),width:2}},hovertemplate:'%{y}<br>cap %{x:.1f}%<extra></extra>'},
  {type:'scatter',mode:'markers+text',name:'Average paid',x:D.chan.map(r=>r.rate),y:cy,text:D.chan.map(r=>'+'+r.gap+' pp'),textposition:'middle right',textfont:{color:css('--text-secondary')},marker:{size:12,color:css('--s1'),line:{color:css('--surface-1'),width:2}},hovertemplate:'%{y}<br>avg %{x:.0f}%<extra></extra>'}],
  base({margin:{l:120,r:60,t:8,b:44},legend:{orientation:'h',y:-0.3},xaxis:{title:'First-year commission, % of premium',gridcolor:css('--grid'),range:[0,75]}}),cfg);
 table('tb_chan',[['Channel',r=>r.ch],['Avg %',r=>r.rate],['Cap %',r=>r.cap],['Gap pp',r=>r.gap],['Reset Rs cr',r=>r.reset.toLocaleString('en-IN')]],D.chan);
 const ex=[...D.expo].reverse();
 Plotly.react('p_expo',[{type:'bar',orientation:'h',x:ex.map(r=>r.pct),y:ex.map(r=>r.ins),marker:{color:css('--s1')},customdata:ex.map(r=>[r.cr,r.bank,r.pat]),
  hovertemplate:'%{y}<br>%{x:.2f}% of premium (Rs %{customdata[0]:,} cr)<br>bank channel: %{customdata[1]}% of indiv. NB<br>% of FY25 PAT: %{customdata[2]}<extra></extra>'}],
  base({showlegend:false,margin:{l:210,r:16,t:8,b:44},xaxis:{title:'% of FY25 total premium',gridcolor:css('--grid')}}),cfg);
 table('tb_expo',[['Insurer',r=>r.ins],['Reset Rs cr',r=>r.cr],['% premium',r=>r.pct],['Bank channel %',r=>r.bank],['% FY25 PAT',r=>r.pat]],D.expo);
 Plotly.react('p_gi',[{type:'scatter',mode:'markers+text',x:D.gi.map(r=>r.comm),y:D.gi.map(r=>r.icr),text:D.gi.map(r=>r.line),textposition:'top center',textfont:{color:css('--text-secondary')},
  marker:{size:D.gi.map(r=>8+Math.sqrt(r.gdpi)/12),color:css('--s1'),opacity:.85,line:{color:css('--surface-1'),width:2}},hovertemplate:'%{text}<br>commission %{x:.1f}% of GDPI<br>ICR %{y:.1f}%<extra></extra>'}],
  base({showlegend:false,xaxis:{title:'Commission % of GDPI',gridcolor:css('--grid')},yaxis:{title:'Incurred claims ratio %',gridcolor:css('--grid')}}),cfg);
 // upi
 $('k_oct').textContent=D.upi_m.vol.at(-1); $('k_ppn').textContent=D.cap.pp_need; $('k_ppt').textContent=D.cap.pp_trend; $('k_mdr').textContent=D.mdr_range.map(v=>v.toLocaleString('en-IN')).join('-');
 Plotly.react('p_vol',[{type:'bar',x:D.upi_m.x,y:D.upi_m.vol,marker:{color:css('--s1')},hovertemplate:'%{x}: %{y:.2f} bn<extra></extra>'}],base({showlegend:false,margin:{l:56,r:24,t:8,b:56},yaxis:{title:'bn transactions',gridcolor:css('--grid')}}),cfg);
 Plotly.react('p_ticket',[{type:'scatter',mode:'lines+markers',x:D.upi_m.x,y:D.upi_m.ticket,line:{color:css('--s1'),width:2},marker:{size:8,color:css('--s1'),line:{color:css('--surface-1'),width:2}},hovertemplate:'%{x}: Rs %{y:,}<extra></extra>'}],base({showlegend:false,margin:{l:56,r:24,t:8,b:56},yaxis:{title:'Rs per transaction',gridcolor:css('--grid')}}),cfg);
 const ser=[['phonepe','PhonePe',css('--s5')],['google_pay','Google Pay',css('--s1')],['paytm','Paytm',css('--s3')],['navi','Navi',css('--s4')]];
 Plotly.react('p_share',[...ser.map(([k,n,c])=>({type:'scatter',mode:'lines',name:n,x:D.upi_c.x,y:D.upi_c[k],line:{color:c,width:2},hovertemplate:n+' %{x}: %{y:.1f}%<extra></extra>'})),
  {type:'scatter',mode:'lines',name:'30% cap',x:[D.upi_c.x[0],D.upi_c.x.at(-1)],y:[30,30],line:{color:css('--text-muted'),width:1.5,dash:'dash'},hoverinfo:'skip'}],
  base({yaxis:{title:'% of volume',gridcolor:css('--grid')},hovermode:'x unified'}),cfg);
 Plotly.react('p_mdr',[{type:'heatmap',x:D.mdr.x,y:D.mdr.y,z:D.mdr.z,colorscale:[[0,css('--seq-lo')],[1,css('--seq-hi')]],texttemplate:'%{z:,}',textfont:{size:12},hovertemplate:'%{y}, %{x}<br>Rs %{z:,} cr / yr<extra></extra>',showscale:false}],
  base({margin:{l:110,r:16,t:8,b:44}}),cfg);
 table('tb_cb',[['Company',r=>`<a href="${r.url}" target="_blank" rel="noopener">${r.co}</a>`],['Segment',r=>r.seg],['Total funding (US$ mn)',r=>r.usd],['Last round',r=>r.last+(r.date?' ('+r.date+')':'')],['Why it matters',r=>r.why]],D.cb);
 const vc=v=>v.startsWith('Delivered')?'ok':(v==='Missed'?'no':'mid');
 table('tb_say',[['Bank',r=>r.bank],['Call',r=>r.call],['Management said (paraphrase; verbatim at source)',r=>`${r.said} <a href="${r.url}" target="_blank" rel="noopener">source</a>`],['What happened',r=>r.outcome],['Verdict',r=>`<span class="pill ${vc(r.verdict)}">${r.verdict}</span>`]],D.say);
 $('q2note').textContent=D.q2_note;
}
$('srcbody').innerHTML=`<ul>
<li><b>Banks:</b> standalone P&amp;L and balance sheet from Screener.in, tied out to each bank's Q4 FY26 / Q2 FY27 investor presentation (page-cited in <code>data/inputs/bank_reported.csv</code>); HDFC Q2 FY27 PPOP from NSE XBRL. SBI's 'Total Provisions' includes tax and is excluded here.</li>
<li><b>Attribution:</b> Shapley values over RoA = (NII + OI - opex - provisions) x (1 - tax rate); order-independent, sums to the gap.</li>
<li><b>Insurance:</b> IRDAI Annual Report 2024-25 (Tables I.9-I.14), IRDAI Handbook 2024-25 (T2, T3, T13, T99, T100), IRDAI consultation 'Recalibrating Economics of Insurance Distribution' Part 1 (Box 2, 4A, 4B) and Part 2 (Annexure 3). Caps are <i>proposed</i>. The premium-paying-term mix is an assumption, stress-tested by Monte Carlo.</li>
<li><b>UPI:</b> NPCI product statistics and app-wise statistics (user-downloaded); DFS MDR FAQ (15 Sep 2026); PIB FY26 P2M/P2P split. App names normalised with our own rules; method credited to koushikxy/upi-payments-dashboard (no files copied).</li>
<li><b>Market:</b> Crunchbase (request id logged in <code>data/tidy/crunchbase_fs_landscape.csv</code>); FactIQ earnings-call claim graph for management quotes.</li>
<li><b>Checks:</b> each workbook has a checks tab: PBT tie, RoA vs reported, AR totals vs Handbook, NPCI app sum vs total, HHI vs reference.</li></ul>`;
document.querySelectorAll('nav [role=tab]').forEach(b=>b.onclick=()=>{document.querySelectorAll('nav [role=tab]').forEach(x=>x.setAttribute('aria-selected',x===b));document.querySelectorAll('section').forEach(s=>s.classList.toggle('on',s.id===b.dataset.t));window.dispatchEvent(new Event('resize'))});
$('theme').onclick=()=>{const d=document.documentElement;const dark=d.dataset.theme?d.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;d.dataset.theme=dark?'light':'dark';draw()};
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',draw);
draw();
</script></body></html>"""


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HTML.replace("__DATA__", json.dumps(payload(), ensure_ascii=False)))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size/1e3:.0f} KB)")


if __name__ == "__main__":
    main()
