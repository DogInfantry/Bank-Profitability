<script lang="ts">
  // Value per share vs the price: live bars, scenario ranges as whiskers, the ₹700 price as a rule.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  let w = $state(560);
  const H = 112, m = { t: 8, r: 16, b: 22, l: 128 };
  const r = $derived(app.result!.valuation);
  const sr = $derived(app.scenarioResults!);
  const price = $derived(app.story!.price);
  const rows = $derived([
    { label: 'Residual income', v: r.riPerShare, lo: sr.Downside.valuation.riPerShare, hi: sr.Upside.valuation.riPerShare },
    { label: 'Sum of the parts', v: r.sotpPerShare, lo: sr.Downside.valuation.sotpPerShare, hi: sr.Upside.valuation.sotpPerShare },
  ]);
  const x = $derived(d3.scaleLinear().domain([0, 900]).range([m.l, w - m.r]));
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="Value per share against the share price">
    {#each x.ticks(6) as t}<text x={x(t)} y={H - 4} text-anchor="middle" class="num-t">₹{t}</text>{/each}
    {#each rows as row, i}
      {@const yy = m.t + i * 40}
      <text x={m.l - 10} y={yy + 18} text-anchor="end" style="fill: var(--ink-2)">{row.label}</text>
      <rect x={x(0)} y={yy + 6} width={x(Math.max(0, row.v)) - x(0)} height="18" rx="2" fill="var(--s1)" />
      <line x1={x(row.lo)} x2={x(row.hi)} y1={yy + 15} y2={yy + 15} stroke="var(--ink)" stroke-width="1" />
      <line x1={x(row.lo)} x2={x(row.lo)} y1={yy + 9} y2={yy + 21} stroke="var(--ink)" /><line x1={x(row.hi)} x2={x(row.hi)} y1={yy + 9} y2={yy + 21} stroke="var(--ink)" />
      <text x={x(Math.max(0, row.v)) + 6} y={yy + 4} class="num-t" style="fill: var(--ink); font-size: 12px; font-weight: 600">₹{Math.round(row.v)}</text>
    {/each}
    <line x1={x(price)} x2={x(price)} y1={m.t} y2={H - m.b} stroke="var(--target)" stroke-width="1.6" />
    <text x={x(price) + 4} y={m.t + 8} style="fill: var(--target); font-size: 11px; font-weight: 600">price ₹{price}</text>
  </svg>
</div>
