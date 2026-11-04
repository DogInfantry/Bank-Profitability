<script lang="ts">
  // Exhibit 7: legacy borrowings by maturity (31 Mar 2026), and borrowings as a share of funding, FY21-FY29E.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  let w = $state(900);
  const s = $derived(app.story!);
  const mat = $derived.by(() => {
    const m = s.maturity as any[]; const sum = (a: any[]) => a.reduce((t, r) => t + r.amount_cr, 0);
    return [{ k: 'Within 1 year', v: sum(m.slice(0, 8)) }, { k: '1-3 years', v: m[8].amount_cr }, { k: '3-5 years', v: m[9].amount_cr }, { k: 'Over 5 years', v: m[10].amount_cr }];
  });
  const total = $derived(mat.reduce((t, r) => t + r.v, 0));
  const narrow = $derived(w < 700);
  const lw = $derived(narrow ? w : w * 0.48), rw = $derived(narrow ? w : w * 0.48);
  const x = $derived(d3.scaleLinear().domain([0, 200000]).range([110, lw - 70]));
  const share = $derived((s.series.Base.bor_share as number[]).slice(1));
  const yrs = ['FY21', 'FY22', 'FY23', 'FY24', 'FY25', 'FY26', 'FY27', 'FY28', 'FY29'];
  const sx = $derived(d3.scalePoint<string>().domain(yrs).range([34, rw - 14]));
  const sy = d3.scaleLinear().domain([0, 0.22]).range([190, 16]);
</script>
<div bind:clientWidth={w} class="lad" class:narrow>
  <div>
    <p class="pt">Borrowings by residual maturity, ₹ cr (total ₹{Math.round(total).toLocaleString('en-IN')} cr)</p>
    <svg width={lw} height="190" role="img" aria-label="Borrowings by maturity bucket">
      {#each mat as r, i}
        <text x="104" y={28 + i * 40} text-anchor="end" style="fill: var(--ink-2)">{r.k}</text>
        <rect x="110" y={14 + i * 40} width={x(r.v) - 110} height="22" rx="2" fill={i === 0 ? 'var(--s1)' : 'var(--context)'} />
        <text x={x(r.v) + 6} y={30 + i * 40} class="num-t" style={`fill: var(--ink); font-size: 12px; font-weight: ${i === 0 ? 600 : 400}`}>₹{(r.v / 1e5).toFixed(2)} lakh cr</text>
      {/each}
    </svg>
  </div>
  <div>
    <p class="pt">Borrowings / (deposits + borrowings), average</p>
    <svg width={rw} height="210" role="img" aria-label="Borrowings share of funding FY21 to FY29E">
      {#each [0, 0.1, 0.2] as t}<line x1="30" x2={rw} y1={sy(t)} y2={sy(t)} stroke="var(--hair-2)" /><text x="26" y={sy(t) + 4} text-anchor="end" class="num-t">{t * 100}%</text>{/each}
      {#each yrs as yr, i}
        <rect x={sx(yr)! - 9} y={sy(share[i])} width="18" height={sy(0) - sy(share[i])} rx="2" fill={i >= 6 ? 'var(--s1)' : i >= 3 && i <= 4 ? 'var(--ink)' : 'var(--context)'} />
        {#if i % 2 === 0 || !narrow}<text x={sx(yr)} y="206" text-anchor="middle" style="font-size: 10.5px">{yr}</text>{/if}
        {#if i === 4 || i === 8}<text x={sx(yr)} y={sy(share[i]) - 5} text-anchor="middle" class="num-t" style="fill: var(--ink); font-size: 11.5px; font-weight: 600">{(share[i] * 100).toFixed(1)}%</text>{/if}
      {/each}
    </svg>
  </div>
</div>
<style>
  .lad { display: grid; grid-template-columns: 1fr 1fr; gap: 4%; }
  .lad.narrow { grid-template-columns: 1fr; }
  .pt { font: 600 13px var(--sans); color: var(--ink); margin: 0 0 4px; }
</style>
