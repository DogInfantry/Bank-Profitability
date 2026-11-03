<script lang="ts">
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import { showTip, hideTip } from '../lib/tooltip';
  let w = $state(560);
  const t = $derived(app.story!.tornado as any[]);
  const base = $derived(t[0].roa_base_pct);
  const narrow = $derived(w < 520);
  const m = $derived({ t: 22, r: 16, b: 26, l: narrow ? 120 : 230 });
  const H = $derived(t.length * 24 + 50);
  const ext = $derived(Math.max(...t.flatMap((d) => [Math.abs(d.roa_low_input_pct - base), Math.abs(d.roa_high_input_pct - base)])) * 100 * 1.1);
  const x = $derived(d3.scaleLinear().domain([-ext, ext]).range([m.l, w - m.r]));
  const fmt = (v: number) => (Math.abs(v) < 1 ? v.toFixed(3) : v.toLocaleString());
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="Tornado: change in FY29E RoA when each driver moves across its range">
    {#each x.ticks(6) as v}<line x1={x(v)} x2={x(v)} y1={m.t} y2={H - m.b} stroke="var(--hair-2)" /><text x={x(v)} y={H - 8} text-anchor="middle" class="num-t">{v > 0 ? '+' : ''}{v}</text>{/each}
    <text x={x(-ext)} y={12} style="font-size: 11px">low input</text><text x={x(ext)} y={12} text-anchor="end" style="font-size: 11px">high input</text>
    {#each t as d, i}
      {@const lo = (d.roa_low_input_pct - base) * 100}
      {@const hi = (d.roa_high_input_pct - base) * 100}
      {@const yy = m.t + i * 24}
      <text x={m.l - 8} y={yy + 13} text-anchor="end" style="fill: var(--ink-2); font-size: {narrow ? 10.5 : 12}px">{narrow ? d.driver.split(',')[0].replace('Share of maturing borrowings retired', 'Borrowings retired').replace('Treasury and other non-fee income', 'Treasury income') : d.driver}</text>
      {#each [[lo, 'var(--context)', 'Low', d.low_input_fy29], [hi, 'var(--s1)', 'High', d.high_input_fy29]] as [v, c, tag, inp]}
        <rect x={Math.min(x(0), x(v as number))} y={yy + 3} width={Math.abs(x(v as number) - x(0))} height="14" rx="2" fill={c as string}
              role="presentation" onmousemove={(e) => showTip(e, `<b>${d.driver}</b><br>${tag} input (FY29E): ${fmt(inp as number)}<br>RoA ${(v as number) >= 0 ? '+' : ''}${(v as number).toFixed(1)} bp vs Base`)} onmouseleave={hideTip} />
      {/each}
      <text x={x(Math.max(lo, hi)) + 4} y={yy + 14} class="num-t" style="font-size: 10.5px">{d.swing_bp.toFixed(1)}</text>
    {/each}
    <line x1={x(0)} x2={x(0)} y1={m.t - 4} y2={H - m.b} stroke="var(--ink)" />
  </svg>
</div>
