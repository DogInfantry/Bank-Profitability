<script lang="ts">
  // Exhibit 10: the RoE the share price implies, against what the base case and the six moves deliver by FY29E.
  import { app } from '../lib/store.svelte';
  let w = $state(500);
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
  const levRoe = $derived(b.levers.reduce((t, l) => t + l.roe, 0));
  const rows = $derived([
    { k: 'Base case, FY29E', v: b.years[2].roe, c: 'var(--context)' },
    { k: 'With the six moves', v: b.years[2].roe + levRoe, c: 'var(--s1)' },
    { k: 'Implied by the ₹700 price', v: s.roe_implied, c: 'var(--ink)' },
  ]);
  const x = (v: number) => 150 + (v / 0.2) * (w - 210);
</script>
<div bind:clientWidth={w}>
  <svg width={w} height="150" role="img" aria-label="Return on equity: base, with levers, and implied by the price">
    {#each rows as r, i}
      <text x="142" y={30 + i * 42} text-anchor="end" style="fill: var(--ink-2)">{r.k}</text>
      <rect x="150" y={14 + i * 42} width={x(r.v) - 150} height="24" rx="2" fill={r.c} />
      <text x={x(r.v) + 6} y={31 + i * 42} class="num-t" style="fill: var(--ink); font-weight: 600; font-size: 13px">{(r.v * 100).toFixed(1)}%</text>
    {/each}
  </svg>
</div>
