<script lang="ts">
  // Chapter 4 rail: credit cost FY18-FY26 actual and FY27E-FY29E base case, against the through-the-cycle average.
  import { app } from '../lib/store.svelte';
  const s = $derived(app.story!);
  const pts = $derived([
    ...(s.history as any[]).map((r) => ({ fy: r.fy, v: r.cc * 100, est: false })),
    ...(s.years as string[]).slice(7).map((y, i) => ({ fy: y.slice(0, 4), v: s.series.Base.cc[7 + i] * 100, est: true })),
  ]);
  const W = 320, H = 140, L = 30, R = 10, T = 12, B = 22, hi = 1.2;
  const x = (i: number) => L + (i * (W - L - R)) / (pts.length - 1);
  const y = (v: number) => T + ((hi - v) / hi) * (H - T - B);
  const ttc = $derived(s.ttc_cc * 100);
  const nAct = $derived((s.history as any[]).length);
</script>
<figure class="cc">
  <p class="rh">Credit cost is below its long-run level, and the base case lets it return</p>
  <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={`Credit cost, % of average advances: ${pts.map((p) => `${p.fy}${p.est ? ' estimate' : ''} ${p.v.toFixed(2)}%`).join(', ')}; through-the-cycle ${ttc.toFixed(2)}%`}>
    {#each [0, 0.4, 0.8, 1.2] as t}<line x1={L} x2={W - R} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x={L - 5} y={y(t) + 3.5} text-anchor="end" class="ax">{t.toFixed(1)}</text>{/each}
    <rect x={x(nAct - 0.5)} y={T} width={W - R - x(nAct - 0.5)} height={H - T - B} fill="var(--brand-wash)" />
    <line x1={L} x2={W - R} y1={y(ttc)} y2={y(ttc)} stroke="var(--ink)" stroke-dasharray="4 3" stroke-width="1" />
    <text x={L + 4} y={y(ttc) + 14} class="lab">Through the cycle {ttc.toFixed(2)}%</text>
    <polyline points={pts.slice(0, nAct).map((p, i) => `${x(i)},${y(p.v)}`).join(' ')} fill="none" stroke="var(--s1)" stroke-width="2" />
    <polyline points={pts.slice(nAct - 1).map((p, i) => `${x(nAct - 1 + i)},${y(p.v)}`).join(' ')} fill="none" stroke="var(--s1)" stroke-width="2" stroke-dasharray="4 3" />
    {#each pts as p, i}
      {#if i === nAct - 1 || i === pts.length - 1}<circle cx={x(i)} cy={y(p.v)} r="3.5" fill="var(--brand)" /><text x={x(i)} y={y(p.v) + 15} text-anchor={i === pts.length - 1 ? 'end' : 'middle'} class="lab">{p.v.toFixed(2)}%</text>{/if}
      {#if i % 2 === 0 || i === pts.length - 1}<text x={x(i)} y={H - 6} text-anchor="middle" class="ax">{p.fy.slice(2)}</text>{/if}
    {/each}
    <text x={W - R - 4} y={T + 12} text-anchor="end" class="ax">base case</text>
  </svg>
  <p class="cap">Loan-loss provisions / average advances, %. Normalising takes about {s.norm_roa_bp.toFixed(0)} bp off FY29E RoA. Through the cycle = FY21-FY26 average; recent = FY24-FY26 ({(s.recent_cc * 100).toFixed(2)}%).</p>
</figure>
<style>
  .cc { margin: 0; border-top: 2px solid var(--ink); padding-top: 10px; }
  .rh { font: 600 14px/1.3 var(--sans); color: var(--ink); margin: 0 0 8px; }
  svg { display: block; overflow: visible; }
  .ax { font: 500 10.5px var(--sans); fill: var(--muted); }
  .lab { font: 600 10.5px var(--sans); fill: var(--ink); }
  .cap { font: 400 12.5px/1.45 var(--sans); color: var(--ink-2); margin: 8px 0 0; }
</style>
