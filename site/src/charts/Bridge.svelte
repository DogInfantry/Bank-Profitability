<script lang="ts">
  // Waterfall: FY26 core RoA -> scenario drift -> six levers -> FY29E. Levers switched off are drawn as outlines.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import { showTip, hideTip } from '../lib/tooltip';
  let w = $state(560);
  const H = 250, m = { t: 18, r: 10, b: 54, l: 40 };
  const SHORT = ['CASA', 'Borrowings', 'Re-mix', 'Productivity', 'Fees', 'UPI'];
  const r = $derived(app.result!);
  const bars = $derived.by(() => {
    const out: { label: string; y0: number; y1: number; kind: 'total' | 'drift' | 'lever' | 'off'; v: number; name: string }[] = [];
    let run = r.bridge.start;
    out.push({ label: 'FY26', y0: 0, y1: run, kind: 'total', v: run, name: 'FY26 core RoA' });
    out.push({ label: 'Drift', y0: run, y1: run + r.bridge.drift, kind: 'drift', v: r.bridge.drift, name: 'Scenario drift before levers' }); run += r.bridge.drift;
    r.levers.forEach((l, i) => { const on = app.leverOn[i]; out.push({ label: SHORT[i], y0: run, y1: run + l.bp, kind: on ? 'lever' : 'off', v: l.bp, name: l.name }); if (on) run += l.bp; });
    out.push({ label: 'FY29E', y0: 0, y1: run, kind: 'total', v: run, name: 'FY29E with levers' });
    return out;
  });
  const lo = $derived(Math.min(140, ...bars.map((b) => Math.min(b.y0 || b.y1, b.y1)) ) - 10);
  const hi = $derived(Math.max(215, ...bars.map((b) => Math.max(b.y0, b.y1))) + 6);
  const x = $derived(d3.scaleBand<string>().domain(bars.map((b) => b.label)).range([m.l, w - m.r]).padding(0.28));
  const y = $derived(d3.scaleLinear().domain([lo, hi]).range([H - m.b, m.t]));
  const top = (b: (typeof bars)[number]) => y(b.kind === 'total' ? b.y1 : Math.max(b.y0, b.y1));
  const ht = (b: (typeof bars)[number]) => Math.max(1.5, b.kind === 'total' ? y(lo) - y(b.y1) : Math.abs(y(b.y0) - y(b.y1)));
  const fill = (b: (typeof bars)[number]) => b.kind === 'total' ? 'var(--ink)' : b.kind === 'drift' ? (b.v >= 0 ? 'var(--context)' : 'var(--target)') : b.kind === 'lever' ? 'var(--s1)' : 'none';
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="RoA bridge from FY26 to FY29E in basis points">
    {#each y.ticks(5) as t}<line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x={m.l - 6} y={y(t) + 4} text-anchor="end" class="num-t">{t}</text>{/each}
    <line x1={m.l} x2={w - m.r} y1={y(200)} y2={y(200)} stroke="var(--target)" stroke-dasharray="4 3" />
    {#each bars as b (b.label)}
      <rect x={x(b.label)} y={top(b)} width={x.bandwidth()} height={ht(b)} rx="2" fill={fill(b)} stroke={b.kind === 'off' ? 'var(--context)' : 'none'} stroke-dasharray={b.kind === 'off' ? '3 2' : null}
            role="presentation" onmousemove={(e) => showTip(e, `<b>${b.name}</b><br>${b.kind === 'total' ? `${b.v.toFixed(1)} bp` : `${b.v >= 0 ? '+' : ''}${b.v.toFixed(1)} bp`}${b.kind === 'off' ? ' (switched off)' : ''}`)} onmouseleave={hideTip} />
      <text x={(x(b.label) ?? 0) + x.bandwidth() / 2} y={top(b) - 5} text-anchor="middle" class="num-t" style="fill: var(--ink-2); font-size: 11px">{b.kind === 'total' ? b.v.toFixed(0) : `${b.v >= 0 ? '+' : ''}${b.v.toFixed(1)}`}</text>
      <text x={(x(b.label) ?? 0) + x.bandwidth() / 2} y={H - m.b + 14} text-anchor="middle" transform={w < 520 ? `rotate(-35 ${(x(b.label) ?? 0) + x.bandwidth() / 2} ${H - m.b + 14})` : null}>{b.label}</text>
    {/each}
    <text x={m.l + 4} y={y(200) - 5} style="fill: var(--target); font-size: 11px; font-weight: 600">target 200 bp</text>
  </svg>
</div>
