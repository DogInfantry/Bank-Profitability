<script lang="ts">
  // Generic horizontal-axis waterfall in bp: totals in ink, gains in blue, losses in red. Optional on-bar notes.
  import * as d3 from 'd3';
  import { showTip, hideTip } from '../lib/tooltip';
  type Step = { label: string; v: number; total?: boolean; note?: string; dim?: boolean };
  let { steps, lo, hi, H = 300, fmt = (v: number) => v.toFixed(1), unit = 'bp' }: { steps: Step[]; lo: number; hi: number; H?: number; fmt?: (v: number) => string; unit?: string } = $props();
  let w = $state(900);
  const m = { t: 34, r: 10, b: 44, l: 44 };
  const bars = $derived.by(() => { let run = 0; return steps.map((s) => { if (s.total) { run = s.v; return { ...s, y0: lo, y1: s.v }; } const o = { ...s, y0: run, y1: run + s.v }; if (!s.dim) run += s.v; return o; }); });
  const x = $derived(d3.scaleBand<string>().domain(steps.map((s) => s.label)).range([m.l, w - m.r]).padding(0.3));
  const y = $derived(d3.scaleLinear().domain([lo, hi]).range([H - m.b, m.t]));
  const col = (b: any) => (b.total ? 'var(--ink)' : b.dim ? 'none' : b.v >= 0 ? 'var(--s1)' : 'var(--target)');
  const narrow = $derived(w < 560);
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="Waterfall in basis points">
    {#each y.ticks(5) as t}<line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x={m.l - 6} y={y(t) + 4} text-anchor="end" class="num-t">{t}</text>{/each}
    {#each bars as b, i (b.label)}
      {@const top = y(Math.max(b.y0, b.y1))}
      {@const h = Math.max(1.5, Math.abs(y(b.y0) - y(b.y1)))}
      <rect x={x(b.label)} y={top} width={x.bandwidth()} height={h} rx="2" fill={col(b)} stroke={b.dim ? 'var(--context)' : 'none'} stroke-dasharray={b.dim ? '3 2' : null}
            role="presentation" onmousemove={(e) => showTip(e, `<b>${b.label}</b><br>${b.total ? '' : b.v >= 0 ? '+' : ''}${fmt(b.v)} ${unit}${b.note ? `<br>${b.note}` : ''}`)} onmouseleave={hideTip} />
      <text x={x(b.label)! + x.bandwidth() / 2} y={top - 6} text-anchor="middle" class="num-t" style={`fill: ${b.total ? 'var(--ink)' : b.v >= 0 ? 'var(--brand)' : 'var(--adverse)'}; font-size: 12px; font-weight: 600`}>{b.total ? fmt(b.v) : `${b.v >= 0 ? '+' : '−'}${fmt(Math.abs(b.v))}`}</text>
      {#if i < bars.length - 1 && !b.dim}<line x1={x(b.label)! + x.bandwidth()} x2={x(bars[i + 1].label)} y1={y(b.total ? b.y1 : b.y1)} y2={y(b.total ? b.y1 : b.y1)} stroke="var(--muted)" stroke-width="0.6" stroke-dasharray="2 2" />{/if}
      <text x={x(b.label)! + x.bandwidth() / 2} y={H - m.b + 16} text-anchor={narrow ? 'end' : 'middle'} transform={narrow ? `rotate(-35 ${x(b.label)! + x.bandwidth() / 2} ${H - m.b + 16})` : null} style="fill: var(--ink-2)">{b.label}</text>
    {/each}
  </svg>
</div>
