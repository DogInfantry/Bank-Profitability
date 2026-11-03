<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Row from '../lib/Row.svelte';
  import Stat from '../lib/Stat.svelte';
  import SmallMultiples from '../charts/SmallMultiples.svelte';
  import RupeeOfAssets from '../charts/RupeeOfAssets.svelte';
  import Waterfall from '../charts/Waterfall.svelte';
  const s = $derived(app.story!);
  const w = $derived((s.walk as any[]).find((r) => r.step === 'FY23 to Q2 FY27'));
  const steps = $derived([
    { label: 'FY23 RoA', v: w.roa_from_pct * 100, total: true }, { label: 'Net interest', v: w.nii_bp }, { label: 'Other income', v: w.oi_bp },
    { label: 'Opex', v: w.opex_bp }, { label: 'Provisions', v: w.prov_bp }, { label: 'Tax', v: w.tax_rate_bp }, { label: 'Q2 FY27 RoA', v: w.roa_to_pct * 100, total: true },
  ]);
</script>
<section class="chapter" id="merger">
  <ChapterHead n="02" kicker="Diagnosis" title="The merger broke the margin, not the cost base" />
  <Row>
    <p class="prose">Read across the four lines that make up return on assets and only one of them breaks at the merger. Net interest income per rupee of assets, flat at about 3.8-4.0% before July 2023, has fallen every year since. Operating cost per rupee of assets moved the other way: it is at its lowest in a decade.</p>
    <p class="prose">HDFC Ltd brought a large mortgage book, and it came financed by bonds and bank borrowings that cost more than deposits. The bank earns less on every rupee of assets; it holds RoA near 1.8% only because it spends less running them.</p>
    {#snippet rail()}<RupeeOfAssets />{/snippet}
  </Row>
  <Exhibit n={2} wide title="Only the margin line breaks at the merger; cost per rupee of assets is at a ten-year low"
           units="% of simple-average total assets, FY18-FY26, standalone. Dashed line: merger with HDFC Ltd (1 July 2023)"
           source="HDFC Bank Integrated Annual Report 2025-26, ten-year highlights (p234)">
    <SmallMultiples />
    {#snippet table()}<table class="data"><thead><tr><th>Year</th><th class="n">NII</th><th class="n">Other income</th><th class="n">Opex</th><th class="n">Provisions</th><th class="n">RoA</th></tr></thead>
      <tbody>{#each s.history as h}<tr><td>{h.fy}</td>{#each ['nii', 'oi', 'opex', 'prov', 'roa'] as k}<td class="n">{(h[k] * 100).toFixed(2)}%</td>{/each}</tr>{/each}</tbody></table>{/snippet}
  </Exhibit>
  <Row>
    <p class="prose">Put a number on it. From the last pre-merger year to Q2 FY27, RoA fell {(-w.change_bp).toFixed(0)} bp. Margin alone took {(-w.nii_bp).toFixed(0)} bp; lower costs gave back {w.opex_bp.toFixed(0)} bp and lower provisions another {w.prov_bp.toFixed(0)} bp. A cost programme cannot close a gap that was opened by funding.</p>
    <Exhibit n={3} title={`RoA fell ${(-w.change_bp).toFixed(0)} bp since FY23: margin took ${(-w.nii_bp).toFixed(0)} bp, cost gave back ${w.opex_bp.toFixed(0)} bp`}
             units="Contribution to the change in RoA, bp, FY23 to Q2 FY27 (annualised)"
             source="IR26 p234 (FY23); Q2 FY27 standalone results via Screener, tied to the Q2 FY27 presentation; Shapley attribution (pipeline/hdfc_walk.py)">
      <Waterfall {steps} lo={125} hi={205} fmt={(v) => v.toFixed(0)} />
    </Exhibit>
    {#snippet rail()}
      <Stat label="Margin effect" value={`${w.nii_bp.toFixed(0)} bp`} tone="adverse" sub="Net interest income, FY23 to Q2 FY27" />
      <Stat label="Cost effect" value={`+${w.opex_bp.toFixed(0)} bp`} tone="brand" sub="Lower operating cost per rupee of assets" />
      <Stat label="Net change in RoA" value={`${w.change_bp.toFixed(0)} bp`} sub={`${(w.roa_from_pct).toFixed(2)}% to ${(w.roa_to_pct).toFixed(2)}%`} />
      <p class="rnote">Shapley attribution averages each factor's effect over every order of change, so the bars add exactly to the total and do not depend on which factor moves first.</p>
    {/snippet}
  </Row>
</section>
