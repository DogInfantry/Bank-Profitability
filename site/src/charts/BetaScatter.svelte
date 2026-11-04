<script lang="ts">
  // Change in cost of funds vs change in average repo, FY17-FY26, with the same-year (0.37) and long-run (0.62) slopes.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import { showTip, hideTip } from '../lib/tooltip';
  let w = $state(480);
  const H = 280, m = { t: 14, r: 92, b: 36, l: 46 };
  const b = $derived(app.story!.beta);
  const pts = $derived(b.points as any[]);
  const x = $derived(d3.scaleLinear().domain([-1.6, 1.8]).range([m.l, w - m.r]));
  const y = $derived(d3.scaleLinear().domain([-1.2, 2.1]).range([H - m.b, m.t]));
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="Funding-cost beta scatter">
    {#each y.ticks(5) as t}<line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x={m.l - 6} y={y(t) + 4} text-anchor="end" class="num-t">{t}</text>{/each}
    {#each x.ticks(6) as t}<text x={x(t)} y={H - m.b + 15} text-anchor="middle" class="num-t">{t}</text>{/each}
    <text x={(m.l + w - m.r) / 2} y={H - 4} text-anchor="middle">Change in average repo, pp</text>
    <text x="4" y={m.t - 2} style="font-size: 11px">Δ cost of funds, pp</text>
    <line x1={x(0)} x2={x(0)} y1={m.t} y2={H - m.b} stroke="var(--hair)" /><line x1={m.l} x2={w - m.r} y1={y(0)} y2={y(0)} stroke="var(--hair)" />
    {#each [[b.same_year, 'var(--s1)', `same year ${b.same_year.toFixed(2)}`], [b.long_run, 'var(--s2)', `long run ${b.long_run.toFixed(2)}`]] as [s, c, lab]}
      <line x1={x(-1.5)} x2={x(1.7)} y1={y(-1.5 * (s as number))} y2={y(1.7 * (s as number))} stroke={c as string} stroke-width="1.8" />
      <text x={x(1.7) + 4} y={y(1.7 * (s as number)) + 4} style={`fill: ${c}; font-size: 11px; font-weight: 600`}>{lab}</text>
    {/each}
    {#each pts as p}
      {@const merger = p.fy_end === 2024}
      <circle cx={x(p.d_repo)} cy={y(p.d_cof)} r="5" fill={merger ? 'var(--surface)' : 'var(--ink)'} stroke="var(--ink)" stroke-width="1.5"
              role="presentation" onmousemove={(e) => showTip(e, `<b>FY${String(p.fy_end).slice(2)}</b><br>Δ repo ${p.d_repo.toFixed(2)} pp · Δ cost of funds ${p.d_cof.toFixed(2)} pp${merger ? '<br>Merger year: absorbed by a dummy' : ''}`)} onmouseleave={hideTip} />
      {#if merger}<text x={x(p.d_repo) + 8} y={y(p.d_cof) + 4} style="font-size: 11px">FY24 merger</text>{/if}
    {/each}
  </svg>
</div>
