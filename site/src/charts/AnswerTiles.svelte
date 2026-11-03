<script lang="ts">
  // Chapter 1: the four-part answer as illustrated tiles. Each tile carries one number and a micro-chart from the data.
  import { app } from '../lib/store.svelte';
  import Spot from '../lib/Spot.svelte';
  import { pct, ind } from '../lib/format';
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
  const h = $derived(Object.fromEntries((s.history as any[]).map((r) => [r.fy, r])));
  const levRoe = $derived(b.levers.reduce((t, l) => t + l.roe, 0));
  const near = $derived((s.maturity as any[]).slice(0, 8).reduce((t, r) => t + r.amount_cr, 0));
  const bor = $derived((s.series.Base.bor_share as number[]).slice(4).map((v, i) => ({ fy: s.years[4 + i], v })));
  const SHORT = ['CASA', 'Borrow', 'Pricing', 'Cost', 'Fees', 'UPI'];
  const W = 260;
  const bx = (v: number, max: number) => (v / max) * (W - 92);
</script>
<div class="tiles">
  <article class="tile">
    <header><Spot name="vault" /><span class="n mono">1</span></header>
    <h3>The problem is funding, not cost</h3>
    <p class="big num">{((h.FY26.nii - h.FY23.nii) * 1e4).toFixed(0)} bp <span>margin on assets, FY23 to FY26</span></p>
    <svg viewBox={`0 0 ${W} 58`} width="100%" role="img" aria-label="Net interest income and operating cost per rupee of assets, FY23 and FY26">
      {#each [['Margin', 'nii'], ['Opex', 'opex']] as [lab, k], r}
        {#each ['FY23', 'FY26'] as fy, j}
          {@const v = h[fy][k] * 100}
          <rect x="52" y={r * 30 + j * 12} width={bx(v, 5)} height="10" fill={j ? (k === 'nii' ? 'var(--s1)' : 'var(--context)') : 'var(--context-2)'} />
          <text x={56 + bx(v, 5)} y={r * 30 + j * 12 + 9} class="v">{fy} {v.toFixed(2)}%</text>
        {/each}
        <text x="0" y={r * 30 + 15} class="l">{lab}</text>
      {/each}
    </svg>
    <p class="tx">The 2023 merger brought a mortgage book financed by wholesale borrowings. Net interest income fell from {pct(h.FY23.nii, 2)} of assets to {pct(h.FY26.nii, 2)}; cost fell too and kept RoA from falling further.</p>
  </article>
  <article class="tile">
    <header><Spot name="ladder" /><span class="n mono">2</span></header>
    <h3>Run-off alone gets to {pct(b.years[2].roa, 2)}, not 2%</h3>
    <p class="big num">₹{ind(near / 1e5, 2)} lakh cr <span>of borrowings mature within a year</span></p>
    <svg viewBox={`0 0 ${W} 58`} width="100%" role="img" aria-label={`Borrowings share of funding: ${bor.map((p) => `${p.fy} ${pct(p.v)}`).join(', ')}`}>
      {#each bor as p, i}
        {@const px = 14 + i * ((W - 40) / (bor.length - 1))}
        {@const py = 6 + (0.21 - p.v) / 0.16 * 34}
        {#if i}<line x1={14 + (i - 1) * ((W - 40) / (bor.length - 1))} y1={6 + (0.21 - bor[i - 1].v) / 0.16 * 34} x2={px} y2={py} stroke={i > 2 ? 'var(--s1)' : 'var(--context)'} stroke-width="2" stroke-dasharray={i > 2 ? '4 2' : ''} />{/if}
        <circle cx={px} cy={py} r="3" fill={i === 1 || i === bor.length - 1 ? 'var(--brand)' : 'var(--paper)'} stroke="var(--brand)" stroke-width="1.4" />
        {#if i === 1 || i === bor.length - 1}<text x={px + (i === 1 ? 6 : -6)} y={py - 5} text-anchor={i === 1 ? 'start' : 'end'} class="v">{pct(p.v, 0)}</text>{/if}
        <text x={px} y="56" text-anchor="middle" class="l">{p.fy.slice(2, 4)}</text>
      {/each}
    </svg>
    <p class="tx">Borrowings fall from {pct(bor[1].v, 0)} of funding to {pct(bor[5].v, 0)} as they are replaced by deposits. Credit cost returning to its long-run level takes back about {s.norm_roa_bp.toFixed(0)} bp of the gain.</p>
  </article>
  <article class="tile">
    <header><Spot name="steps" /><span class="n mono">3</span></header>
    <h3>Six moves add {b.bridge.levers.toFixed(1)} bp, to {(b.bridge.withLevers / 100).toFixed(2)}%</h3>
    <p class="big num">+{b.bridge.levers.toFixed(1)} bp <span>each asks under half of a peer's lead</span></p>
    <svg viewBox={`0 0 ${W} 58`} width="100%" role="img" aria-label={`Six moves: ${b.levers.map((l) => `${l.name} ${l.bp.toFixed(1)} bp`).join('; ')}`}>
      {#each b.levers as l, i}
        {@const cw = (W - 10) / 6}
        <rect x={i * cw + 4} y={40 - l.bp * 6} width={cw - 10} height={l.bp * 6} fill="var(--s1)" />
        <text x={i * cw + cw / 2 - 1} y={36 - l.bp * 6} text-anchor="middle" class="v">{l.bp.toFixed(1)}</text>
        <text x={i * cw + cw / 2 - 1} y="54" text-anchor="middle" class="l">{SHORT[i]}</text>
      {/each}
    </svg>
    <p class="tx">Rebuild current and savings deposits, retire borrowings faster, re-price new lending, hold cost growth, protect fees and grow UPI acquiring.</p>
  </article>
  <article class="tile">
    <header><Spot name="coins" /><span class="n mono">4</span></header>
    <h3>The share price already assumes it</h3>
    <p class="big num">{pct(s.roe_implied)} <span>RoE implied by ₹{s.price}</span></p>
    <svg viewBox={`0 0 ${W} 58`} width="100%" role="img" aria-label="Return on equity: base case, with the moves, implied by the price">
      {#each [['Base', b.years[2].roe, 'var(--context)'], ['Moves', b.years[2].roe + levRoe, 'var(--s1)'], ['Price', s.roe_implied, 'var(--ink)']] as [lab, v, c], r}
        <text x="0" y={r * 19 + 11} class="l">{lab}</text>
        <rect x="52" y={r * 19 + 2} width={bx(+v * 100, 20)} height="12" fill={String(c)} />
        <text x={56 + bx(+v * 100, 20)} y={r * 19 + 12} class="v">{pct(+v)}</text>
      {/each}
    </svg>
    <p class="tx">The base case delivers {pct(b.years[2].roe)} RoE; with the moves, {pct(b.years[2].roe + levRoe)}. Every 10 bp of RoA is worth about ₹{ind(s.v10 / 1000)}k cr of equity value.</p>
  </article>
</div>
<style>
  .tiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; border-top: 2px solid var(--ink); margin: 8px 0 12px; }
  .tile { padding: 16px 20px 18px; border-left: 1px solid var(--hair); display: flex; flex-direction: column; }
  .tile:first-child { border-left: 0; padding-left: 0; }
  .tile:last-child { padding-right: 0; }
  header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
  .n { font-size: 12px; color: var(--brand); border: 1.5px solid var(--brand); border-radius: 50%; width: 24px; height: 24px; display: grid; place-items: center; }
  h3 { font: 600 17px/1.3 var(--sans); color: var(--ink); margin: 0 0 8px; min-height: 2.6em; }
  .big { font: 500 24px/1.2 var(--mono); color: var(--brand); margin: 0 0 10px; letter-spacing: -0.01em; }
  .big span { display: block; font: 400 12px/1.35 var(--sans); color: var(--muted); letter-spacing: 0; margin-top: 2px; }
  svg { display: block; overflow: visible; margin-bottom: 10px; }
  .l { font: 500 10.5px var(--sans); fill: var(--muted); }
  .v { font: 500 10.5px var(--mono); fill: var(--ink-2); }
  .tx { font: 400 15.5px/1.45 var(--serif); color: var(--ink-2); margin: 0; }
  @media (max-width: 1100px) { .tiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } .tile:nth-child(3) { border-left: 0; padding-left: 0; } .tile:nth-child(2) { padding-right: 0; } .tile:nth-child(n+3) { border-top: 1px solid var(--hair); } }
  @media (max-width: 640px) { .tiles { grid-template-columns: minmax(0, 1fr); } .tile { border-left: 0; padding-left: 0; padding-right: 0; } .tile + .tile { border-top: 1px solid var(--hair); } h3 { min-height: 0; } }
</style>
