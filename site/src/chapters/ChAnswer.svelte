<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import HeroRoa from '../charts/HeroRoa.svelte';
  import { pct, ind } from '../lib/format';
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
  const levRoe = $derived(b.levers.reduce((t, l) => t + l.roe, 0));
</script>
<section class="chapter" id="answer">
  <ChapterHead n="01" kicker="The answer" title="Four things the board needs to know" />
  <Exhibit n={1} wide title="RoA held 1.8-2.0% for a decade; the merger pushed it to the floor, and only the six moves clear 2% by FY29"
           units="Return on average assets, %, standalone. FY18-FY26 actual; Q2 FY27 annualised; FY27E-FY29E model, shaded band = Downside to Upside"
           source="HDFC Bank Integrated Annual Report 2025-26 p234; Q2 FY27 results; driver model (models/HDFC_RoA_Path_FY29.xlsx)">
    <HeroRoa />
    {#snippet table()}<table class="data"><thead><tr><th>Year</th><th class="n">RoA</th></tr></thead><tbody>
      {#each s.history as h}<tr><td>{h.fy}</td><td class="n">{(h.roa * 100).toFixed(2)}%</td></tr>{/each}
      <tr><td>Q2 FY27 (annualised)</td><td class="n">{(s.q2fy27_roa * 100).toFixed(2)}%</td></tr>
      {#each b.years as y, i}<tr><td>FY{27 + i}E base</td><td class="n">{(y.roa * 100).toFixed(2)}%</td></tr>{/each}
      <tr><td>FY29E with six moves</td><td class="n">{(b.bridge.withLevers / 100).toFixed(2)}%</td></tr></tbody></table>{/snippet}
  </Exhibit>
  <div class="answer">
    <ol>
      <li><b>The problem is funding, not cost.</b> The 2023 merger brought a mortgage book financed by wholesale borrowings. Net interest income fell from 3.83% of assets to 3.11%; costs fell too, and kept RoA from falling further.</li>
      <li><b>Run-off alone gets to {pct(b.years[2].roa, 2)}, not 2%.</b> ₹1.93 lakh cr of legacy borrowings mature within a year, but credit cost returning to its long-run level takes back part of the gain.</li>
      <li><b>Six moves add {b.bridge.levers.toFixed(1)} bp, to {(b.bridge.withLevers / 100).toFixed(2)}%.</b> Rebuild current and savings deposits, retire borrowings faster, re-price new lending, hold cost growth, protect fee income, and grow UPI acquiring. None asks for more than half of what a named peer already achieves.</li>
      <li><b>The share price already assumes it.</b> At ₹{s.price} the market implies a {pct(s.roe_implied)} return on equity. The base case delivers {pct(b.years[2].roe)}; with the moves, {pct(b.years[2].roe + levRoe)}. Every 10 bp of RoA is worth about ₹{ind(s.v10 / 1000)}k cr of equity value.</li>
    </ol>
  </div>
</section>
<style>
  .answer ol { margin: 0; padding: 0; list-style: none; counter-reset: a; }
  .answer li { counter-increment: a; position: relative; padding: 14px 0 14px 44px; border-top: 1px solid var(--hair); font-family: var(--serif); font-size: 19px; line-height: 1.5; color: var(--ink-2); }
  .answer li::before { content: counter(a); position: absolute; left: 0; top: 14px; font: 600 13px var(--mono); color: var(--brand); border: 1.5px solid var(--brand); border-radius: 50%; width: 26px; height: 26px; display: grid; place-items: center; }
  .answer li b { color: var(--ink); font-weight: 600; }
</style>
