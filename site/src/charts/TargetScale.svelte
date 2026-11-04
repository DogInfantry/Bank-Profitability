<script lang="ts">
  // Exhibit 18: FY29E RoA on one scale: what the cost of equity needs, the base case, the 2% target, the case with the moves, and what the price needs.
  import { app } from '../lib/store.svelte';
  const s = $derived(app.story!);
  const t = $derived(s.target_test);
  const o = $derived(s.outputs.Base);
  const marks = $derived([
    { v: t.roa_ke, lab: 'Earns the cost of equity', c: 'var(--context)', up: true },
    { v: t.roa_px_cr, lab: 'Meets the price, capital returned', c: 'var(--s2)', up: false },
    { v: o.before_bp / 1e4, lab: 'Base case', c: 'var(--context)', up: true },
    { v: 0.02, lab: 'Target', c: 'var(--target)', up: false },
    { v: o.with_bp / 1e4, lab: 'With the six moves', c: 'var(--s1)', up: true },
    { v: t.roa_px, lab: 'Meets the price as it stands', c: 'var(--s2)', up: false },
  ]);
  let W = $state(700);
  const H = 150, L = 16, R = 16, mid = 76, lo = 0.016, hi = 0.022;
  const narrow = $derived(W < 560);
  const anchor = (px: number) => (px > Math.max(W, 280) - 110 ? 'end' : px < 110 ? 'start' : 'middle');
  const x = $derived((v: number) => L + ((v - lo) / (hi - lo)) * (Math.max(W, 280) - L - R));
</script>
<div bind:clientWidth={W}>
  <svg width={Math.max(W, 280)} height={H} role="img" aria-label={marks.map((m) => `${m.lab} ${(m.v * 100).toFixed(2)}%`).join('; ')}>
    <line x1={L} x2={Math.max(W, 280) - R} y1={mid} y2={mid} stroke="var(--hair)" stroke-width="2" />
    {#each [0.016, 0.017, 0.018, 0.019, 0.02, 0.021, 0.022] as g}
      <line x1={x(g)} x2={x(g)} y1={mid - 4} y2={mid + 4} stroke="var(--muted)" />
      <text x={x(g)} y={H - 4} text-anchor="middle" class="ax">{(g * 100).toFixed(1)}%</text>
    {/each}
    {#each marks as m, i}
      {@const yl = m.up ? (i % 4 === 0 ? 14 : 34) : (i % 4 === 1 ? 118 : 104)}
      <line x1={x(m.v)} x2={x(m.v)} y1={mid} y2={m.up ? yl + 4 : yl - 12} stroke={m.c} stroke-width="1.5" />
      <circle cx={x(m.v)} cy={mid} r="5" fill={m.c} />
      {#if !narrow}<text x={x(m.v)} y={yl} text-anchor={anchor(x(m.v))} class="lab">{m.lab} <tspan class="num">{(m.v * 100).toFixed(2)}%</tspan></text>{/if}
    {/each}
  </svg>
  {#if narrow}<ul class="list">{#each marks as m}<li><i style={`background:${m.c}`}></i>{m.lab} <span class="num">{(m.v * 100).toFixed(2)}%</span></li>{/each}</ul>{/if}
</div>
<style>
  svg { display: block; }
  .ax { font: 500 11px var(--sans); fill: var(--muted); }
  .lab { font: 500 11.5px var(--sans); fill: var(--ink-2); }
  .num { font-family: var(--mono); fill: var(--ink); color: var(--ink); }
  .list { list-style: none; padding: 0; margin: 6px 0 0; font: 400 13px var(--sans); color: var(--ink-2); }
  .list i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 8px; }
</style>
