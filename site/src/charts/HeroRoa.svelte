<script lang="ts">
  // Exhibit 1: RoA FY18-FY26 actual, Q2 FY27, FY27E-FY29E base with the Upside-Downside range, and FY29E with the six moves.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import Note from '../lib/Note.svelte';
  import { showTip, hideTip } from '../lib/tooltip';
  let w = $state(1000);
  const narrow = $derived(w < 640);
  const H = $derived(narrow ? 320 : 420);
  const m = $derived({ t: 30, r: narrow ? 14 : 150, b: 30, l: 44 });
  const s = $derived(app.story!);
  const sr = $derived(app.scenarioResults!);
  const hist = $derived(s.history.map((h: any) => ({ fy: h.fy, v: h.roa })));
  const yrs = $derived([...hist.map((h: any) => h.fy), 'FY27', 'FY28', 'FY29']);
  const x = $derived(d3.scalePoint<string>().domain(yrs).range([m.l, w - m.r]).padding(0.2));
  const y = $derived(d3.scaleLinear().domain([0.012, 0.0245]).range([H - m.b, m.t]));
  const proj = (k: 'Base' | 'Upside' | 'Downside') => sr[k].years.map((yy, i) => ({ fy: `FY${27 + i}`, v: yy.roa }));
  const line = $derived(d3.line<{ fy: string; v: number }>().x((d) => x(d.fy)!).y((d) => y(d.v)));
  const band = $derived(d3.area<number>().x((_, i) => x(['FY26', 'FY27', 'FY28', 'FY29'][i])!)
    .y0((_, i) => y(i === 0 ? hist[hist.length - 1].v : sr.Downside.years[i - 1].roa)).y1((_, i) => y(i === 0 ? hist[hist.length - 1].v : sr.Upside.years[i - 1].roa))([0, 1, 2, 3]) ?? '');
  const last = $derived(hist[hist.length - 1]);
  const base = $derived(proj('Base'));
  const withLev = $derived(sr.Base.bridge.withLevers / 1e4);
  const q2x = $derived((x('FY26')! + x('FY27')!) / 2);
  const tip = (e: PointerEvent, html: string) => showTip(e, html);
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="HDFC Bank return on assets, FY18 to FY29E, against the 2 percent target">
    {#each y.ticks(6) as t}<line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x={m.l - 8} y={y(t) + 4} text-anchor="end" class="num-t">{(t * 100).toFixed(1)}%</text>{/each}
    {#each yrs as yr, i}{#if !narrow || i % 2 === 0}<text x={x(yr)} y={H - 8} text-anchor="middle">{yr}</text>{/if}{/each}
    <rect x={x('FY26')} y={m.t} width={x('FY29')! - x('FY26')! + 14} height={H - m.t - m.b} fill="var(--hair-2)" opacity="0.5" />
    <text x={x('FY27')} y={m.t - 10} text-anchor="middle" style="font-size: 11px; letter-spacing: .08em">PROJECTION</text>
    <line x1={(x('FY23')! + x('FY24')!) / 2} x2={(x('FY23')! + x('FY24')!) / 2} y1={m.t} y2={H - m.b} stroke="var(--muted)" stroke-dasharray="2 3" />
    <text x={(x('FY23')! + x('FY24')!) / 2 + 5} y={m.t + 10} style="font-size: 11px">Merger with HDFC Ltd, Jul 2023</text>
    <line x1={m.l} x2={w - m.r} y1={y(0.02)} y2={y(0.02)} stroke="var(--target)" stroke-width="1.4" />
    <text x={m.l + 4} y={y(0.02) - 6} style="fill: var(--target); font-size: 12px; font-weight: 600">2.00% target</text>
    <path d={band} fill="var(--s1)" opacity="0.12" />
    <path d={line(hist)} fill="none" stroke="var(--ink)" stroke-width="2.4" />
    <path d={line([last, ...base])} fill="none" stroke="var(--s1)" stroke-width="2.4" stroke-dasharray="5 3" />
    <line x1={x('FY29')} x2={x('FY29')} y1={y(base[2].v)} y2={y(withLev)} stroke="var(--s1)" stroke-width="2" />
    {#each hist as h}<circle cx={x(h.fy)} cy={y(h.v)} r="3" fill="var(--ink)" role="presentation" onpointermove={(e) => tip(e, `<b>${h.fy}</b> RoA ${(h.v * 100).toFixed(2)}%`)} onpointerleave={hideTip} />{/each}
    <circle cx={q2x} cy={y(s.q2fy27_roa)} r="4" fill="var(--paper)" stroke="var(--ink)" stroke-width="1.6" />
    <circle cx={x('FY29')} cy={y(base[2].v)} r="4.5" fill="var(--s1)" />
    <circle cx={x('FY29')} cy={y(withLev)} r="6" fill="var(--paper)" stroke="var(--s1)" stroke-width="2.4" />
    {#if !narrow}
      <Note x={x('FY24')!} y={y(hist.find((h: any) => h.fy === 'FY24').v)} dx={-40} dy={-34} anchor="end" lines={['2.00% in FY24', 'flattered by a one-off tax benefit']} />
      <Note x={q2x} y={y(s.q2fy27_roa)} dx={-10} dy={56} anchor="end" lines={[`${(s.q2fy27_roa * 100).toFixed(2)}% in Q2 FY27`, 'annualised; the low point']} dot={false} />
      <Note x={x('FY29')!} y={y(base[2].v)} dx={22} dy={18} lines={[`Base case ${(base[2].v * 100).toFixed(2)}%`, 'run-off, net of credit', 'normalisation']} tone="brand" dot={false} />
      <Note x={x('FY29')!} y={y(withLev)} dx={22} dy={-22} lines={[`With six moves ${(withLev * 100).toFixed(2)}%`, `${sr.Base.bridge.levers.toFixed(1)} bp of levers`]} tone="brand" dot={false} />
      <text x={x('FY29')! + 26} y={y(sr.Upside.years[2].roa) + 4} style="font-size: 11px">Upside {(sr.Upside.years[2].roa * 100).toFixed(2)}%</text>
      <text x={x('FY29')! + 26} y={y(sr.Downside.years[2].roa) + 4} style="font-size: 11px">Downside {(sr.Downside.years[2].roa * 100).toFixed(2)}%</text>
    {/if}
  </svg>
</div>
