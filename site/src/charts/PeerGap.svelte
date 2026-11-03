<script lang="ts">
  // Exhibit 4: HDFC Bank's FY26 RoA gap to ICICI Bank by factor (Shapley, bp). Negative = costs HDFC RoA.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  let w = $state(500);
  const g = $derived(app.story!.icici_gap);
  const rows = $derived([
    { k: 'Net interest income', v: -g.nii * 100 }, { k: 'Provisions', v: -g.prov * 100 }, { k: 'Other income', v: -g.oi * 100 },
    { k: 'Operating expenses', v: -g.opex * 100 }, { k: 'Tax', v: -g.tax_rate * 100 }, { k: 'Total gap', v: -g.gap * 100, total: true },
  ]);
  const m = $derived({ t: 10, r: 20, b: 26, l: w < 460 ? 118 : 150 });
  const H = 250;
  const x = $derived(d3.scaleLinear().domain([-85, 35]).range([m.l, w - m.r]));
  const y = $derived(d3.scaleBand<string>().domain(rows.map((r) => r.k)).range([m.t, H - m.b]).padding(0.32));
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="RoA gap to ICICI Bank by factor">
    {#each [-60, -40, -20, 0, 20] as t}<line x1={x(t)} x2={x(t)} y1={m.t} y2={H - m.b} stroke={t === 0 ? 'var(--ink)' : 'var(--hair-2)'} /><text x={x(t)} y={H - 8} text-anchor="middle" class="num-t">{t}</text>{/each}
    {#each rows as r}
      <text x={m.l - 8} y={y(r.k)! + y.bandwidth() / 2 + 4} text-anchor="end" style={`fill: var(--ink-2); font-weight: ${r.total ? 600 : 400}`}>{r.k}</text>
      <rect x={Math.min(x(0), x(r.v))} y={y(r.k)} width={Math.abs(x(r.v) - x(0))} height={y.bandwidth()} rx="2" fill={r.total ? 'var(--ink)' : r.v < 0 ? 'var(--target)' : 'var(--s1)'} />
      <text x={r.v < 0 ? x(r.v) - 5 : x(r.v) + 5} y={y(r.k)! + y.bandwidth() / 2 + 4} text-anchor={r.v < 0 ? 'end' : 'start'} class="num-t" style="fill: var(--ink); font-size: 12px">{r.v >= 0 ? '+' : '−'}{Math.abs(r.v).toFixed(0)}</text>
    {/each}
  </svg>
</div>
