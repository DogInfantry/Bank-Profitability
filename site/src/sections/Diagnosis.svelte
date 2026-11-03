<script lang="ts">
  // Scrollytelling: one sticky alluvial of where each ₹100 of average assets goes, morphing year by year.
  import { onMount } from 'svelte';
  import { Tween } from 'svelte/motion';
  import { cubicInOut } from 'svelte/easing';
  import scrollama from 'scrollama';
  import { app } from '../lib/store.svelte';
  import SecHead from '../lib/SecHead.svelte';
  import { pct } from '../lib/format';
  import type { Year } from '../lib/engine';

  type Flow = { nii: number; oi: number; opex: number; prov: number; tax: number; pat: number };
  const s = $derived(app.story!);
  const base = $derived(app.scenarioResults!.Base);
  const tax29 = $derived(app.model!.fixed.tax[2]);
  const fromSeries = (i: number): Flow => {
    const B = s.series.Base;
    return { nii: B.nii_a[i] * 100, oi: B.oi_a[i] * 100, opex: B.opex_a[i] * 100, prov: B.prov_a[i] * 100, tax: B.tax_a[i] * 100, pat: B.roa[i] * 100 };
  };
  const fromYear = (y: Year): Flow => ({ nii: y.nii / y.a_ta * 100, oi: y.oi / y.a_ta * 100, opex: y.opex / y.a_ta * 100, prov: y.prov / y.a_ta * 100, tax: y.tax / y.a_ta * 100, pat: y.pat / y.a_ta * 100 });
  const withLevers = $derived.by((): Flow => {
    const y = base.years[2]; const f = fromYear(y); const L = base.levers; const k = 100 / y.a_ta;
    const nii = (L[0].pretax + L[1].pretax + L[2].pretax) * k, oi = (L[4].pretax + L[5].pretax) * k, opex = L[3].pretax * k;
    const all = nii + oi + opex;
    return { nii: f.nii + nii, oi: f.oi + oi, opex: f.opex - opex, prov: f.prov, tax: f.tax + all * tax29, pat: f.pat + all * (1 - tax29) };
  });
  const walk = $derived(Object.fromEntries(s.walk.map((w: any) => [w.step, w])));
  const steps = $derived([
    { tag: 'FY23', name: 'Before the merger', flow: fromSeries(3),
      text: `Per ₹100 of average assets, HDFC Bank earned ₹${fromSeries(3).nii.toFixed(2)} of net interest income and ₹${fromSeries(3).oi.toFixed(2)} of other income. After costs, provisions and tax, ₹${fromSeries(3).pat.toFixed(2)} reached shareholders.` },
    { tag: 'FY24', name: 'The merger year', flow: fromSeries(4),
      text: `The merger with HDFC Ltd brought a mortgage book funded by wholesale borrowings. RoA printed ${pct(s.series.Base.roa[4], 2)}, but a one-off tax benefit added ${walk['FY23 to FY24'].tax_rate_bp.toFixed(0)} bp; NII already gave up ${(-walk['FY23 to FY24'].nii_bp).toFixed(0)} bp.` },
    { tag: 'FY26', name: 'The reset', flow: fromSeries(6),
      text: `By FY26 net interest income was down to ₹${fromSeries(6).nii.toFixed(2)}. Cost discipline gave back ${walk['FY23 to Q2 FY27'].opex_bp.toFixed(0)} bp from FY23 to Q2 FY27, but margin took ${(-walk['FY23 to Q2 FY27'].nii_bp).toFixed(0)} bp. The problem moved from cost to margin.` },
    { tag: 'FY29E', name: 'Base case', flow: fromYear(base.years[2]),
      text: `As legacy borrowings mature, NII recovers to ₹${fromYear(base.years[2]).nii.toFixed(2)}. Credit cost normalising towards its ${pct(s.ttc_cc, 2)} through-the-cycle level absorbs part of it. RoA lands at ${pct(base.years[2].roa, 2)}: short of 2%.` },
    { tag: 'FY29E', name: 'With six levers', flow: withLevers,
      text: `Funding mix, asset mix, productivity and fees add ${base.bridge.levers.toFixed(1)} bp. ₹${withLevers.pat.toFixed(2)} of every ₹100 reaches shareholders: ${(base.bridge.withLevers / 100).toFixed(2)}%, just over the line.` },
  ]);

  let step = $state(0);
  const t = new Tween<Flow>({ nii: 3.8, oi: 1.4, opex: 2.1, prov: 0.5, tax: 0.6, pat: 1.95 }, { duration: 700, easing: cubicInOut });
  $effect(() => { t.target = steps[step].flow; });

  let wv = $state(620);
  const H = 440, W = $derived(Math.max(280, wv));
  const g = $derived.by(() => {
    const f = t.current;
    const total = f.nii + f.oi;
    const k = (H - 90) / 6.0;                      // fixed scale: 6.0 per ₹100 fills the plot, so heights compare across steps
    const gap = 14, nodeW = 10;
    const narrow = W < 520; const x0 = narrow ? 66 : 112, x1 = W * 0.5 - nodeW / 2, x2 = W - (narrow ? 64 : 112);
    const left = [{ key: 'nii', label: narrow ? 'NII' : 'Net interest', v: f.nii }, { key: 'oi', label: 'Other income', v: f.oi }];
    const right = [{ key: 'pat', label: narrow ? 'PAT' : 'Profit (RoA)', v: f.pat }, { key: 'tax', label: 'Tax', v: f.tax }, { key: 'prov', label: 'Provisions', v: f.prov }, { key: 'opex', label: 'Opex', v: f.opex }];
    const top = 30;
    let y = top; const L = left.map((n) => { const o = { ...n, y0: y, y1: y + n.v * k }; y = o.y1 + gap; return o; });
    const midH = total * k, midY = top + (L[1].y1 - top - midH) / 2;
    y = top; const R = right.map((n) => { const o = { ...n, y0: y, y1: y + n.v * k }; y = o.y1 + gap; return o; });
    const band = (xa: number, ya0: number, ya1: number, xb: number, yb0: number, yb1: number) => {
      const xm = (xa + xb) / 2;
      return `M${xa},${ya0}C${xm},${ya0} ${xm},${yb0} ${xb},${yb0}L${xb},${yb1}C${xm},${yb1} ${xm},${ya1} ${xa},${ya1}Z`;
    };
    let my = midY; const inL = L.map((n) => { const h = n.v * k; const p = band(x0 + nodeW, n.y0, n.y1, x1, my, my + h); my += h; return { key: n.key, d: p }; });
    my = midY; const outR = R.map((n) => { const h = n.v * k; const p = band(x1 + nodeW, my, my + h, x2, n.y0, n.y1); my += h; return { key: n.key, d: p }; });
    return { L, R, inL, outR, x0, x1, x2, nodeW, midY, midH, total };
  });
  const fill = (k: string) => (k === 'pat' ? 'var(--s1)' : k === 'nii' || k === 'oi' ? 'var(--seq-2)' : 'var(--context-2)');

  let stepsEl: HTMLDivElement;
  onMount(() => {
    const sc = scrollama();
    sc.setup({ step: stepsEl.querySelectorAll('.step') as unknown as HTMLElement[], offset: 0.6 }).onStepEnter((r) => { step = r.index; });
    const ro = new ResizeObserver(() => sc.resize()); ro.observe(stepsEl);
    return () => { sc.destroy(); ro.disconnect(); };
  });
</script>

<section class="block" id="diagnosis">
  <SecHead idx="02" kicker="Diagnosis" title="Follow ₹100 of assets: the merger moved the problem from cost to margin">
    <p>Each band is a share of every ₹100 of average assets. Scroll to move from the last pre-merger year to FY29. Heights use one fixed scale, so a thinner band is a real loss.</p>
  </SecHead>
  <div class="scrolly">
    <div class="sticky panel">
      <p class="label">{steps[step].tag} · {steps[step].name}</p>
      <div bind:clientWidth={wv}>
      <svg width={W} height={H} role="img" aria-label={`Allocation of each ₹100 of average assets, ${steps[step].tag} ${steps[step].name}`}>
        {#each g.inL as l (l.key)}<path d={l.d} fill={fill(l.key)} opacity="0.55" />{/each}
        {#each g.outR as l (l.key)}<path d={l.d} fill={fill(l.key)} opacity={l.key === 'pat' ? 0.85 : 0.5} />{/each}
        {#each g.L as n (n.key)}
          <rect x={g.x0} y={n.y0} width={g.nodeW} height={Math.max(1, n.y1 - n.y0)} rx="2" fill="var(--s1)" opacity="0.9" />
          <text x={g.x0 - 8} y={(n.y0 + n.y1) / 2 - 5} text-anchor="end" style="fill: var(--ink-2)">{n.label}</text>
          <text x={g.x0 - 8} y={(n.y0 + n.y1) / 2 + 11} text-anchor="end" class="num-t" style="fill: var(--ink); font-size: 13px">₹{n.v.toFixed(2)}</text>
        {/each}
        <rect x={g.x1} y={g.midY} width={g.nodeW} height={g.midH} rx="2" fill="var(--ink)" opacity="0.75" />
        <text x={g.x1 + g.nodeW / 2} y={g.midY - 8} text-anchor="middle" class="num-t" style="fill: var(--ink)">Net revenue ₹{g.total.toFixed(2)}</text>
        {#each g.R as n (n.key)}
          <rect x={g.x2} y={n.y0} width={g.nodeW} height={Math.max(1, n.y1 - n.y0)} rx="2" fill={n.key === 'pat' ? 'var(--s1)' : 'var(--context)'} />
          <text x={g.x2 + g.nodeW + 8} y={(n.y0 + n.y1) / 2 - 5} style="fill: var(--ink-2)">{n.label}</text>
          <text x={g.x2 + g.nodeW + 8} y={(n.y0 + n.y1) / 2 + 11} class="num-t" style={`fill: ${n.key === 'pat' ? 'var(--brand)' : 'var(--ink)'}; font-size: 13px; font-weight: ${n.key === 'pat' ? 600 : 400}`}>₹{n.v.toFixed(2)}</text>
        {/each}
      </svg>
      </div>
      <div class="meter">
        <span class="label">RoA vs the 2.00% line</span>
        <div class="bar"><span class="fill" style={`width: ${Math.min(100, (t.current.pat / 2.4) * 100)}%`}></span><span class="tgt" style={`left: ${(2 / 2.4) * 100}%`}></span></div>
        <span class="num">{t.current.pat.toFixed(2)}%</span>
      </div>
    </div>
    <div class="steps" bind:this={stepsEl}>
      {#each steps as st, i}
        <div class="step" class:on={i === step}>
          <p class="label">{st.tag} · {st.name}</p>
          <p class="prose">{st.text}</p>
        </div>
      {/each}
    </div>
  </div>
  <details class="tbl"><summary>Table: per ₹100 of average assets</summary>
    <div class="tbl-scroll"><table class="data"><thead><tr><th>Step</th><th class="n">NII</th><th class="n">Other income</th><th class="n">Opex</th><th class="n">Provisions</th><th class="n">Tax</th><th class="n">PAT (RoA)</th></tr></thead>
      <tbody>{#each steps as st}<tr><td>{st.tag} {st.name}</td>{#each ['nii', 'oi', 'opex', 'prov', 'tax', 'pat'] as k}<td class="n">{(st.flow as any)[k].toFixed(2)}</td>{/each}</tr>{/each}</tbody></table></div>
  </details>
  <p class="chart-note">Source: HDFC Bank IR26 p234 (FY23-FY26) <a class="src" href="#log">S1</a>; FY29E from the driver model <a class="src" href="#log">M</a>. FY26 includes one-off treasury gains and provisions.</p>
</section>

<style>
  .scrolly { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 28px; align-items: start; }
  .sticky { position: sticky; top: 64px; }
  .steps { padding: 10vh 0 30vh; }
  .step { min-height: 62vh; opacity: .35; transition: opacity .3s; }
  .step.on { opacity: 1; }
  .step .prose { font-size: 18px; }
  .meter { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 12px; margin-top: 4px; }
  .bar { position: relative; height: 8px; background: var(--hair-2); border-radius: 4px; }
  .fill { position: absolute; left: 0; top: 0; bottom: 0; background: var(--s1); border-radius: 4px; }
  .tgt { position: absolute; top: -5px; bottom: -5px; width: 2px; background: var(--target); }
  svg { display: block; max-width: 100%; }
  @media (max-width: 900px) { .scrolly { grid-template-columns: 1fr; } .sticky { top: 44px; z-index: 2; } .step { min-height: 50vh; } .steps { padding-top: 0; } }
</style>
