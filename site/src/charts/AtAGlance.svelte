<script lang="ts">
  // Masthead panel: the answer in three numbers, each with a micro-chart drawn from the model.
  import { app } from '../lib/store.svelte';
  import { ind } from '../lib/format';
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
  const pts = $derived([
    { k: 'Q2 FY27', v: s.q2fy27_roa * 100 },
    { k: 'FY29E base', v: b.years[2].roa * 100 },
    { k: 'FY29E, six moves', v: b.bridge.withLevers / 100 },
  ]);
  const W = 300, H = 92, L = 8, R = 8, T = 18, B = 22;
  const lo = 1.6, hi = 2.15;
  const x = (i: number) => L + (i * (W - L - R)) / 2;
  const y = (v: number) => T + ((hi - v) / (hi - lo)) * (H - T - B);
  const vmax = 800;
  const vx = (v: number) => (v / vmax) * W;
  const totVal = $derived(b.levers.reduce((t, l) => t + l.value, 0));
  const levTot = $derived(b.levers.reduce((t, l) => t + l.bp, 0));
  const SHADES = ['var(--seq-5)', 'var(--seq-4)', 'var(--seq-3)', 'var(--seq-2)', 'var(--seq-1)', 'var(--seq-1)'];
</script>
<div class="glance" aria-label="The answer at a glance">
  <p class="gh">At a glance</p>
  <div class="g">
    <p class="gl">Return on assets</p>
    <p class="gv num">{pts[0].v.toFixed(2)}% <span class="ar">→</span> <b>{pts[2].v.toFixed(2)}%</b></p>
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={`RoA ${pts.map((p) => `${p.k} ${p.v.toFixed(2)}%`).join(', ')}; target 2%`}>
      <line x1={L} x2={W - R} y1={y(2)} y2={y(2)} stroke="var(--target)" stroke-dasharray="3 3" stroke-width="1" />
      <text x={L} y={y(2) - 5} class="t" style="fill: var(--target)">2% target</text>
      <polyline points={pts.map((p, i) => `${x(i)},${y(p.v)}`).join(' ')} fill="none" stroke="var(--s1)" stroke-width="2" />
      {#each pts as p, i}
        <circle cx={x(i)} cy={y(p.v)} r={i === 2 ? 4.5 : 3.5} fill={i === 2 ? 'var(--brand)' : 'var(--paper)'} stroke="var(--brand)" stroke-width="1.6" />
        <text x={x(i)} y={H - 6} text-anchor={i === 0 ? 'start' : i === 2 ? 'end' : 'middle'} class="t">{p.k}</text>
      {/each}
    </svg>
  </div>
  <div class="g">
    <p class="gl">Value per share, base case</p>
    <p class="gv num">₹{Math.round(b.valuation.riPerShare)}-{Math.round(b.valuation.sotpPerShare)} <span class="vs">vs price ₹{s.price}</span></p>
    <svg viewBox={`0 0 ${W} 34`} width="100%" role="img" aria-label={`Base-case value ₹${Math.round(b.valuation.riPerShare)} to ₹${Math.round(b.valuation.sotpPerShare)} per share against a price of ₹${s.price}`}>
      <rect x="0" y="12" width={W} height="6" fill="var(--hair-2)" />
      <rect x={vx(b.valuation.riPerShare)} y="9" width={vx(b.valuation.sotpPerShare) - vx(b.valuation.riPerShare)} height="12" fill="var(--s1)" />
      <line x1={vx(s.price)} x2={vx(s.price)} y1="3" y2="27" stroke="var(--ink)" stroke-width="2" />
      <text x={vx(s.price) - 4} y="33" text-anchor="end" class="t">price</text>
      <text x="0" y="33" class="t">₹0</text><text x={W} y="33" text-anchor="end" class="t">₹{vmax}</text>
    </svg>
  </div>
  <div class="g">
    <p class="gl">Six moves</p>
    <p class="gv num">+{levTot.toFixed(1)} bp <span class="vs">≈ ₹{ind(totVal / 1e5, 1)} lakh cr of value</span></p>
    <svg viewBox={`0 0 ${W} 16`} width="100%" role="img" aria-label={`Six moves: ${b.levers.map((l) => `${l.name} ${l.bp.toFixed(1)} bp`).join('; ')}`}>
      {#each b.levers as l, i}
        {@const x0 = (b.levers.slice(0, i).reduce((t, q) => t + q.bp, 0) / levTot) * W}
        <rect x={x0} y="2" width={Math.max(1, (l.bp / levTot) * W - 2)} height="12" fill={SHADES[i]} />
      {/each}
    </svg>
  </div>
</div>
<style>
  .glance { border-top: 2px solid var(--ink); padding-top: 10px; }
  .gh { font: 600 11px var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--brand); margin: 0 0 4px; }
  .g { border-bottom: 1px solid var(--hair); padding: 10px 0 12px; }
  .g:last-child { border-bottom: 0; }
  .gl { font: 500 12px var(--sans); color: var(--muted); margin: 0; }
  .gv { font: 500 22px/1.25 var(--mono); color: var(--ink); margin: 2px 0 6px; letter-spacing: -0.01em; }
  .gv b { color: var(--brand); font-weight: 600; } .gv .ar { color: var(--muted); }
  .vs { font: 400 12.5px var(--sans); color: var(--muted); letter-spacing: 0; }
  .t { font: 500 10.5px var(--sans); fill: var(--muted); }
  svg { display: block; overflow: visible; }
</style>
