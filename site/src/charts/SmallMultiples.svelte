<script lang="ts">
  // Exhibit 2: the RoA tree, FY18-FY26, one panel per line, shared merger marker. Margin is the line that broke.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  let w = $state(1000);
  const cols = $derived(w < 640 ? 2 : 4);
  const pw = $derived((w - (cols - 1) * 22) / cols), ph = 150;
  const hist = $derived(app.story!.history as any[]);
  const P = [
    { k: 'nii', t: 'Net interest income', hi: true }, { k: 'oi', t: 'Other income', hi: false },
    { k: 'opex', t: 'Operating expenses', hi: false }, { k: 'prov', t: 'Provisions', hi: false },
  ];
  const x = $derived(d3.scalePoint<string>().domain(hist.map((h) => h.fy)).range([6, pw - 8]));
</script>
<div bind:clientWidth={w} class="sm" style={`grid-template-columns: repeat(${cols}, minmax(0, 1fr))`}>
  {#each P as p}
    {@const vals = hist.map((h) => h[p.k] as number)}
    {@const y = d3.scaleLinear().domain([0, Math.max(0.045, d3.max(vals)! * 1.1)]).range([ph - 22, 10])}
    {@const a = hist.find((h) => h.fy === 'FY23')[p.k]}
    {@const b = hist[hist.length - 1][p.k]}
    <div>
      <p class="pt">{p.t}</p>
      <p class="pv num"><span>FY23 {(a * 100).toFixed(2)}%</span> → <b class:hi={p.hi}>FY26 {(b * 100).toFixed(2)}%</b> <span class="d">{(b - a) * 1e4 >= 0 ? '+' : '−'}{Math.abs((b - a) * 1e4).toFixed(0)} bp</span></p>
      <svg width={pw} height={ph} role="img" aria-label={`${p.t} as a share of average assets, FY18 to FY26`}>
        {#each y.ticks(3) as t}<line x1="0" x2={pw} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x="0" y={y(t) - 3} class="num-t" style="font-size: 10px">{(t * 100).toFixed(0)}%</text>{/each}
        <line x1={(x('FY23')! + x('FY24')!) / 2} x2={(x('FY23')! + x('FY24')!) / 2} y1="6" y2={ph - 22} stroke="var(--muted)" stroke-dasharray="2 3" />
        <path d={d3.line<number>().x((_, i) => x(hist[i].fy)!).y((v) => y(v))(vals)} fill="none" stroke={p.hi ? 'var(--s1)' : 'var(--ink)'} stroke-width={p.hi ? 2.6 : 1.6} />
        {#each vals as v, i}{#if i === 0 || i === vals.length - 1 || hist[i].fy === 'FY23'}<circle cx={x(hist[i].fy)} cy={y(v)} r="2.8" fill={p.hi ? 'var(--s1)' : 'var(--ink)'} />{/if}{/each}
        <text x={x('FY18')} y={ph - 6} style="font-size: 10px">FY18</text><text x={x('FY26')} y={ph - 6} text-anchor="end" style="font-size: 10px">FY26</text>
      </svg>
    </div>
  {/each}
</div>
<style>
  .sm { display: grid; gap: 22px; }
  .pt { font: 600 13px var(--sans); color: var(--ink); margin: 0; }
  .pv { font-size: 12px; color: var(--muted); margin: 2px 0 4px; }
  .pv b { color: var(--ink); font-weight: 600; } .pv b.hi { color: var(--brand); }
  .pv .d { margin-left: 4px; color: var(--ink-2); }
</style>
