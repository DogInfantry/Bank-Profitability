<script lang="ts">
  import katex from 'katex';
  import Icon from '../lib/Icon.svelte';
  import { app } from '../lib/store.svelte';
  const tex = (s: string) => katex.renderToString(s, { displayMode: true, throwOnError: false, output: 'html' });
  const releases = [
    ['v3.1', '4 Nov 2026', 'Packaging: an evidence-to-decision table for the CEO chapter; clickable sources with a confidence rating; plan and move figures bound to the model export; phone-width label fixes; a share image.'],
    ['v3.0', '4 Nov 2026', 'Primary-source deck data, marginal funding cost, risk-adjusted moves, a regulation overlay, break-evens and pre-registered Q3 FY27 calls; trading comps and merger precedents; a CEO chapter with three decisions, the variant view, the 2% test and a hundred-day KPI tree.'],
    ['v2.1', '3 Nov 2026', 'One page grid with aligned edges; every argument paired with a visual: answer tiles, the rupee-of-assets strip, funding mix, credit cycle, the P/B equation, risk cards and a dated roadmap.'],
    ['v2.0', '3 Nov 2026', 'Rebuilt as an argued long-read: answer first, twelve numbered and annotated exhibits, the recommendation built move by move; the model moved to an appendix.'],
    ['v1.0', '3 Nov 2026', 'Explorable front end: browser engine tested against the Excel to 0.1 bp.'],
    ['Model 3', '3 Nov 2026', 'Tornado on the live workbook; RoA walk; funding-cost beta regression; peer anchors; call-topic tracker; DuckDB SQL layer; CI.'],
    ['Correction', '3 Nov 2026', 'UPI: October 2026 is the record month (25.47 bn transactions). An earlier version read a 29-day partial row as the full month.'],
    ['Correction', '3 Nov 2026', 'Margins: SBI\'s Q2 FY27 NIM rose 13 bp to 2.94%. An earlier version said every reported NIM fell.'],
    ['Model 2', '3 Nov 2026', 'Integrated HDFC Bank driver model, scenarios, levers and valuation; IB-hygiene lint; steering-committee deck and CEO memo.'],
  ];
  // Source register: [key, what, link (from data/raw/manifest.csv or the export), confidence]. High = primary disclosure;
  // Medium = primary data restructured by a third party, a proposal, or a secondary source tied to filings.
  const sources = $derived([
    ['S1', 'HDFC Bank Integrated Annual Report 2025-26: schedules (pp359-366), maturity pattern (p384), ten-year highlights (p234), stakes (p52), segments (pp445-446)', 'https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/pdf/annual-reports/2025-26/reports/HDFC_Bank_IR26.pdf', 'High', 'Audited filing'],
    ['S2', 'HDFC Bank investor presentations Q2 FY24 to Q2 FY27 (twelve decks); Basel III Pillar 3 at 30 Sep 2026', 'https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/pdf/about-us/financial-results/2026-2027/quarter-2/q2fy27-earnings-presentation.pdf', 'High', 'Company disclosure'],
    ['S3', 'Peer Q2 FY27 decks (ICICI, Axis, Kotak, SBI) for the trading comps; SBI Q2 FY27 press release', 'https://www.icici.bank.in/content/dam/icicibank/india/managed-assets/docs/about-us/2027/Q2-2027-investor-presentation.pdf', 'High', 'Company disclosure'],
    ['S4', 'Screener.in standalone financials and valuation for twelve banks and listed subsidiaries', 'https://www.screener.in/company/HDFCBANK/', 'Medium', 'Secondary, tied to filings'],
    ['S5', 'RBI via FactIQ: policy repo, 10-year G-sec, the forecasters survey, system deposits and credit, bank-wise returns for the merger precedents', 'https://www.rbi.org.in/', 'High', 'Official statistics'],
    ['S6', 'NPCI UPI: P2M value by ticket band, payee banks, monthly totals, via FactIQ', 'https://www.npci.org.in/what-we-do/upi/product-statistics', 'High', 'Official statistics'],
    ['S7', 'IRDAI Handbook 2024-25 and the September 2026 exposure draft on commission and expenses of management', 'https://irdai.gov.in/', 'Medium', 'Proposal, not final'],
    ['S8', 'Earnings-call claims via the FactIQ claim graph (paraphrased; the link opens the Q2 FY27 margin claim)', app.story!.mgmt_nim.claim_source_url, 'Medium', 'Paraphrased by FactIQ'],
    ['M', 'models/HDFC_RoA_Path_FY29.xlsx: driver model, reconciliation checks, strict lint; recalculated headlessly and exported per scenario', 'https://github.com/DogInfantry/Bank-Profitability/blob/main/models/HDFC_RoA_Path_FY29.xlsx', 'Model', 'Built from the sources above'],
  ]);
</script>
<section class="chapter appendix" id="log">
  <p class="ak-b"><span class="mono">B</span> Appendix</p><h2 class="h2b">Method, sources and corrections</h2>
  <div class="cols">
    <div>
      <p class="label"><Icon name="history" /> Release notes</p>
      <ol class="rel">{#each releases as [v, d, t]}<li><span class="mono tag" class:fix={v === 'Correction'}>{v}</span><span class="mono date">{d}</span><p>{t}</p></li>{/each}</ol>
      <p class="label" style="margin-top:22px"><Icon name="beaker" /> Method in four formulas</p>
      <div class="tex">
        <p class="chart-note">Return on assets as a tree (every ratio over average assets)</p>{@html tex(String.raw`\text{RoA} = \tfrac{\text{NII}}{A} + \tfrac{\text{OI}}{A} - \tfrac{\text{Opex}}{A} - \tfrac{\text{Prov}}{A} - \tfrac{\text{Tax}}{A}`)}
        <p class="chart-note">Order-independent attribution of a change (Shapley)</p>{@html tex(String.raw`\phi_i = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!\,(n-|S|-1)!}{n!}\,\big[f(S \cup \{i\}) - f(S)\big]`)}
        <p class="chart-note">What a return is worth (justified P/B, CAPM cost of equity)</p>{@html tex(String.raw`\tfrac{P}{B} = \frac{\text{RoE} - g}{K_e - g}, \qquad K_e = r_f + \beta \cdot \text{ERP}`)}
        <p class="chart-note">Residual income, FY27E-FY29E plus a fading terminal value</p>{@html tex(String.raw`V_0 = B_0 + \sum_{t=1}^{3} \frac{\text{PAT}_t - K_e B_{t-1}}{(1+K_e)^t} + \frac{\text{RI}_3 (1+g_{ri})}{(K_e - g_{ri})(1+K_e)^3}`)}
      </div>
    </div>
    <div>
      <p class="label"><Icon name="book" /> Source register, with confidence</p>
      <dl class="src-reg">{#each sources as [k, t, url, c, why]}<div><dt class="mono">{k}</dt><dd><a href={url} target="_blank" rel="noopener">{t}</a></dd><dd class="conf" class:hi={c === 'High'}><b>{c}</b>{why}</dd></div>{/each}</dl>
      <p class="label" style="margin-top:22px">Caveats</p>
      <ul class="cav">
        <li>The IRDAI caps are a September 2026 proposal, not final.</li>
        <li>Lever sizes, feasibility and timing are judgements; each is an explicit driver change that can be challenged and re-run.</li>
        <li>HDFC Bank does not disclose its floating-rate share of advances; the model assumes 55% (range 45-65%).</li>
        <li>Values are struck at 31 March 2026 and rolled forward to the 2 November 2026 price date (grown at the cost of equity, less the FY26 dividend).</li>
        <li>No Bain engagement with HDFC Bank is known or implied.</li>
      </ul>
    </div>
  </div>
</section>
<style>
  .cols { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 36px; }
  .rel { list-style: none; padding: 0; margin: 10px 0 0; border-left: 1px solid var(--hair); }
  .rel li { position: relative; padding: 0 0 14px 18px; }
  .rel li::before { content: ''; position: absolute; left: -4px; top: 6px; width: 7px; height: 7px; border-radius: 50%; background: var(--s1); }
  .rel .tag { font-size: 11px; color: var(--brand); margin-right: 8px; } .rel .tag.fix { color: var(--adverse); }
  .rel .date { font-size: 11px; color: var(--muted); }
  .rel p { margin: 2px 0 0; font-size: 14px; color: var(--ink-2); }
  .tex { background: var(--surface); border: 1px solid var(--hair); border-radius: 3px; padding: 6px 16px 10px; overflow-x: auto; color: var(--ink); }
  .tex .chart-note { margin: 10px 0 0; }
  .src-reg { margin: 8px 0 0; } .src-reg div { display: grid; grid-template-columns: 34px minmax(0, 1fr) 104px; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--hair-2); }
  .src-reg dt { color: var(--brand); font-size: 12px; } .src-reg dd { margin: 0; font-size: 13.5px; color: var(--ink-2); }
  .src-reg a { color: inherit; text-decoration: underline; text-decoration-color: var(--hair); text-underline-offset: 2px; overflow-wrap: anywhere; } .src-reg a:hover { text-decoration-color: var(--brand); }
  .src-reg .conf { font: 400 11px/1.35 var(--sans); color: var(--muted); } .src-reg .conf b { display: block; font-weight: 600; color: var(--ink-2); } .src-reg .conf.hi b { color: var(--brand); }
  @media (max-width: 640px) { .src-reg div { grid-template-columns: 34px minmax(0, 1fr); } .src-reg .conf { grid-column: 2; } .src-reg .conf b { display: inline; margin-right: 6px; } }
  .cav { padding-left: 18px; font-size: 13.5px; color: var(--ink-2); } .cav li { margin-bottom: 4px; }
  @media (max-width: 900px) { .cols { grid-template-columns: minmax(0, 1fr); } }
.ak-b { font: 600 11.5px var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin: 0 0 10px; display: flex; gap: 12px; } .ak-b .mono { color: var(--brand); }
  .h2b { font-size: clamp(26px, 3vw, 34px); margin-bottom: 20px; }
</style>
