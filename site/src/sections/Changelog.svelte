<script lang="ts">
  import katex from 'katex';
  import SecHead from '../lib/SecHead.svelte';
  import Icon from '../lib/Icon.svelte';
  const tex = (s: string) => katex.renderToString(s, { displayMode: true, throwOnError: false, output: 'html' });
  const releases = [
    ['v1.0', '3 Nov 2026', 'Explorable front end: browser engine tested against the Excel to 0.1 bp; workbench, metric tree, scrollytelling diagnosis.'],
    ['Model 3', '3 Nov 2026', 'Tornado on the live workbook; RoA walk; funding-cost beta regression; peer anchors; call-topic tracker; DuckDB SQL layer; CI.'],
    ['Correction', '3 Nov 2026', 'UPI: October 2026 is the record month (25.47 bn transactions). An earlier version read a 29-day partial row as the full month.'],
    ['Correction', '3 Nov 2026', 'Margins: SBI\'s Q2 FY27 NIM rose 13 bp to 2.94%. An earlier version said every reported NIM fell.'],
    ['Model 2', '3 Nov 2026', 'Integrated HDFC Bank driver model, scenarios, levers and valuation; IB-hygiene lint; steering-committee deck and CEO memo.'],
  ];
  const sources = [
    ['S1', 'HDFC Bank Integrated Annual Report 2025-26: schedules (pp359-366), maturity pattern (p384), ten-year highlights (p234), stakes (p52)'],
    ['S2', 'HDFC Bank, ICICI Bank, Axis Bank, Kotak investor presentations Q4 FY26 and Q2 FY27; SBI Q2 FY27 press release'],
    ['S3', 'Screener.in standalone financials and valuation for twelve banks and three listed HDFC subsidiaries (secondary, tied to filings)'],
    ['S4', 'RBI: policy repo (Bank Rate change dates), 10-year G-sec, Survey of Professional Forecasters round 102, via FactIQ'],
    ['S5', 'NPCI UPI: P2M value by ticket band, payee banks, monthly totals, via FactIQ'],
    ['S6', 'IRDAI Handbook 2024-25 and the September 2026 exposure draft on commission and expenses of management (proposal)'],
    ['S7', 'HDFC Life FY26 and Q2 FY27 disclosures: VNB, APE, embedded value, channel mix'],
    ['S8', 'Earnings-call claims via the FactIQ claim graph (paraphrased; links go to verbatim quotes)'],
    ['M', 'models/HDFC_RoA_Path_FY29.xlsx: driver model, nine checks, strict lint; recalculated headlessly and exported per scenario'],
  ];
</script>
<section class="block" id="log">
  <SecHead idx="09" kicker="Changelog and method" title="How this was built, and what we got wrong on the way" />
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
      <p class="label"><Icon name="book" /> Source register</p>
      <dl class="src-reg">{#each sources as [k, t]}<div><dt class="mono">{k}</dt><dd>{t}</dd></div>{/each}</dl>
      <p class="label" style="margin-top:22px">Caveats</p>
      <ul class="cav">
        <li>The IRDAI caps are a September 2026 proposal, not final.</li>
        <li>Lever sizes, feasibility and timing are judgements; each is an explicit driver change that can be challenged and re-run.</li>
        <li>HDFC Bank does not disclose its floating-rate share of advances; the model assumes 55% (range 45-65%).</li>
        <li>Values are struck at 31 March 2026 and compared with the 2 November 2026 price; rolling forward would add about 4-5% (see the model audit).</li>
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
  .src-reg { margin: 8px 0 0; } .src-reg div { display: grid; grid-template-columns: 34px 1fr; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--hair-2); }
  .src-reg dt { color: var(--brand); font-size: 12px; } .src-reg dd { margin: 0; font-size: 13.5px; color: var(--ink-2); }
  .cav { padding-left: 18px; font-size: 13.5px; color: var(--ink-2); } .cav li { margin-bottom: 4px; }
  @media (max-width: 900px) { .cols { grid-template-columns: minmax(0, 1fr); } }
</style>
