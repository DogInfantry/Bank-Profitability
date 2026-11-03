<script lang="ts">
  // RoA path: history solid; Base/Upside/Downside thin; the live Workbench case bold; red 2% rule. Crosshair tooltip.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import { showTip, hideTip } from '../lib/tooltip';
  let w = $state(560);
  const H = 260, m = { t: 14, r: 64, b: 26, l: 40 };
  const yrs = ['FY21', 'FY22', 'FY23', 'FY24', 'FY25', 'FY26', 'FY27', 'FY28', 'FY29'];
  const s = $derived(app.story!);
  const hist = $derived(s.series.Base.roa.slice(1, 7) as number[]);
  const proj = $derived(Object.fromEntries((['Base', 'Upside', 'Downside'] as const).map((k) => [k, app.scenarioResults![k].years.map((y) => y.roa)])));
  const live = $derived(app.result!.years.map((y) => y.roa));
  const withLev = $derived(app.result!.bridge.withLevers / 1e4);
  const x = $derived(d3.scalePoint<string>().domain(yrs).range([m.l, w - m.r]));
  const y = $derived(d3.scaleLinear().domain([0.012, 0.025]).range([H - m.b, m.t]));
  const line = (vals: number[], start: number) => d3.line<number>().x((_, i) => x(yrs[start + i])!).y((v) => y(v))(vals) ?? '';
  let hx = $state<number | null>(null);
  function move(e: PointerEvent) {
    const r = (e.currentTarget as SVGElement).getBoundingClientRect();
    const px = e.clientX - r.left; const i = Math.round(((px - m.l) / (w - m.l - m.r)) * (yrs.length - 1));
    if (i < 0 || i >= yrs.length) return hideTip();
    hx = i;
    const rows = i < 6 ? `Actual <b>${(hist[i] * 100).toFixed(2)}%</b>` : `Workbench <b>${(live[i - 6] * 100).toFixed(2)}%</b><br>Base ${(proj.Base[i - 6] * 100).toFixed(2)}% · Upside ${(proj.Upside[i - 6] * 100).toFixed(2)}% · Downside ${(proj.Downside[i - 6] * 100).toFixed(2)}%`;
    showTip(e, `<b>${yrs[i]}</b><br>${rows}`);
  }
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="Return on assets, FY21 to FY29E" onpointermove={move} onpointerleave={() => { hx = null; hideTip(); }}>
    {#each y.ticks(5) as t}<line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x={m.l - 6} y={y(t) + 4} text-anchor="end" class="num-t">{(t * 100).toFixed(1)}%</text>{/each}
    {#each yrs as yr, i}{#if w > 480 || i % 2 === 0}<text x={x(yr)} y={H - 6} text-anchor="middle">{yr}</text>{/if}{/each}
    <rect x={x('FY26')} y={m.t} width={(x('FY29') ?? 0) - (x('FY26') ?? 0)} height={H - m.t - m.b} fill="var(--hair-2)" opacity="0.45" />
    <line x1={m.l} x2={w - m.r} y1={y(0.02)} y2={y(0.02)} stroke="var(--target)" stroke-dasharray="4 3" stroke-width="1.2" />
    <text x={m.l + 4} y={y(0.02) - 5} style="fill: var(--target); font-weight: 600; font-size: 11px">2.00% target</text>
    {#each ['Upside', 'Downside', 'Base'] as k}
      <path d={line([hist[5], ...proj[k]], 5)} fill="none" stroke="var(--context)" stroke-width="1.2" stroke-dasharray="3 3" />
      <text x={w - m.r + 4} y={y(proj[k][2]) + 4} style="font-size: 11px">{k}</text>
    {/each}
    <path d={line(hist, 0)} fill="none" stroke="var(--ink)" stroke-width="2" />
    <path d={line([hist[5], ...live], 5)} fill="none" stroke="var(--s1)" stroke-width="2.6" />
    <line x1={x('FY29')} x2={x('FY29')} y1={y(live[2])} y2={y(withLev)} stroke="var(--s1)" stroke-width="1" />
    <circle cx={x('FY29')} cy={y(withLev)} r="5" fill="var(--surface)" stroke="var(--s1)" stroke-width="2" />
    <circle cx={x('FY29')} cy={y(live[2])} r="4" fill="var(--s1)" stroke="var(--surface)" stroke-width="2" />
    {#if hx != null}<line x1={x(yrs[hx])} x2={x(yrs[hx])} y1={m.t} y2={H - m.b} stroke="var(--muted)" stroke-width="0.8" />{/if}
  </svg>
</div>
