<script lang="ts">
  // Metric tree: the north-star RoA decomposed into the ratios and drivers that move it. Values are live (Workbench state).
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import SecHead from '../lib/SecHead.svelte';
  import { pct } from '../lib/format';
  import { showTip, hideTip } from '../lib/tooltip';

  type N = { id: string; label: string; v26: number; v29: number; fmt: (x: number) => string; good: 1 | -1; torn?: string; levers?: number[]; children?: N[] };
  const r = $derived(app.result!);
  const f = $derived(app.model!.fy26);
  const s = $derived(app.story!);
  const torn = $derived(Object.fromEntries(s.tornado.map((t: any) => [t.driver, t.swing_bp])));
  const B = $derived(s.series.Base);
  const p2 = (x: number) => pct(x, 2), p1 = (x: number) => pct(x, 1);
  const tree = $derived.by((): N => {
    const y = r.years[2];
    return {
      id: 'roa', label: 'Return on assets', v26: f.roa_core_bp / 1e4, v29: y.roa, fmt: p2, good: 1, children: [
        { id: 'nii', label: 'NII / assets', v26: B.nii_a[6], v29: y.nii / y.a_ta, fmt: p2, good: 1, children: [
          { id: 'yl', label: 'Yield on advances', v26: f.y_loan, v29: y.y_loan, fmt: p2, good: 1, torn: 'Policy repo rate, fiscal-year average', levers: [2] },
          { id: 'cd', label: 'Cost of deposits', v26: f.c_dep, v29: y.c_dep, fmt: p2, good: -1, torn: 'Cost beta: deposits', levers: [0] },
          { id: 'casa', label: 'CASA ratio', v26: f.casa, v29: y.casa, fmt: p1, good: 1, torn: 'CASA ratio, year end', levers: [0] },
          { id: 'bor', label: 'Borrowings / funding', v26: B.bor_share[6], v29: y.bor / (y.bor + y.dep), fmt: p1, good: -1, torn: 'Share of maturing borrowings retired', levers: [1] } ] },
        { id: 'oi', label: 'Other income / assets', v26: B.oi_a[6], v29: y.oi / y.a_ta, fmt: p2, good: 1, children: [
          { id: 'fee', label: 'Core fees / assets', v26: f.fee / f.a_ta, v29: y.fee / y.a_ta, fmt: p2, good: 1, torn: 'Core fee income growth', levers: [4] },
          { id: 'tr', label: 'Treasury / assets', v26: B.oi_a[6] - f.fee / f.a_ta, v29: y.oth / y.a_ta, fmt: p2, good: 1, torn: 'Treasury and other non-fee income' },
          { id: 'ird', label: 'Regulatory fees (IRDAI, MDR)', v26: 0, v29: (y.irdai + y.mdr) / y.a_ta, fmt: p2, good: 1, torn: 'IRDAI cap severity on bank fees', levers: [5] } ] },
        { id: 'opex', label: 'Opex / assets', v26: B.opex_a[6], v29: y.opex / y.a_ta, fmt: p2, good: -1, children: [
          { id: 'ci', label: 'Cost to income', v26: B.ci[6], v29: y.ci, fmt: p1, good: -1, torn: 'Operating expense growth', levers: [3] } ] },
        { id: 'prov', label: 'Provisions / assets', v26: B.prov_a[6], v29: y.prov / y.a_ta, fmt: p2, good: -1, children: [
          { id: 'cc', label: 'Credit cost', v26: B.cc[6], v29: y.prov / y.a_loans, fmt: p2, good: -1, torn: 'Credit cost' } ] },
        { id: 'tax', label: 'Tax / assets', v26: B.tax_a[6], v29: y.tax / y.a_ta, fmt: p2, good: -1 },
      ] };
  });
  let w = $state(900);
  const layout = $derived.by(() => {
    const root = d3.hierarchy(tree);
    const leaves = root.leaves().length;
    const H = leaves * 52 + 20;
    const W = Math.max(760, w);
    d3.tree<N>().size([H - 40, W - 330])(root);
    return { root: root as d3.HierarchyPointNode<N>, H, W };
  });
  const link = d3.linkHorizontal<any, d3.HierarchyPointNode<N>>().x((d) => d.y + 10).y((d) => d.x + 20);
  let hover = $state<string | null>(null);
  const related = $derived.by(() => {
    if (!hover) return new Set<string>();
    const n = layout.root.descendants().find((d) => d.data.id === hover);
    return new Set([...(n?.ancestors() ?? []), ...(n?.descendants() ?? [])].map((d) => d.data.id));
  });
  function tip(e: MouseEvent, n: N) {
    hover = n.id;
    const lev = (n.levers ?? []).map((i) => r.levers[i]?.name).filter(Boolean);
    showTip(e, `<b>${n.label}</b><br>FY26 ${n.fmt(n.v26)} → FY29E ${n.fmt(n.v29)}${n.torn ? `<br>Tornado swing on FY29E RoA: ${torn[n.torn]?.toFixed(1)} bp` : ''}${lev.length ? `<br>Moved by: ${lev.join(', ')}` : ''}`);
  }
  const maxSwing = $derived(Math.max(...s.tornado.map((t: any) => t.swing_bp)));
</script>

<section class="block" id="tree">
  <SecHead idx="03" kicker="Metric tree" title="One north star, five ratios, eleven drivers">
    <p>RoA decomposes exactly into margin, other income, cost, provisions and tax. Each leaf shows FY26 and FY29E under the <b>current Workbench settings</b>, and the bar beside it is that driver's tornado swing: how much FY29E RoA moves across its plausible range.</p>
  </SecHead>
  <div class="panel tbl-scroll"><div bind:clientWidth={w}></div>
    <svg width={layout.W} height={layout.H} role="img" aria-label="Metric tree from RoA to its drivers">
      {#each layout.root.links() as l}
        <path d={link(l)} fill="none" stroke={hover && related.has(l.target.data.id) && related.has(l.source.data.id) ? 'var(--brand)' : 'var(--hair)'} stroke-width="1.2" />
      {/each}
      {#each layout.root.descendants() as n (n.data.id)}
        {@const d = n.data}
        {@const delta = (d.v29 - d.v26) * d.good}
        <g transform={`translate(${n.y + 10},${n.x + 20})`} class="node" class:dim={hover && !related.has(d.id)}
           role="button" tabindex="0" aria-label={`${d.label}: FY26 ${d.fmt(d.v26)}, FY29E ${d.fmt(d.v29)}`}
           onmousemove={(e) => tip(e, d)} onmouseleave={() => { hover = null; hideTip(); }} onfocus={() => (hover = d.id)} onblur={() => (hover = null)}>
          <circle r={n.depth === 0 ? 6 : 4} fill={n.depth === 0 ? 'var(--brand)' : 'var(--surface)'} stroke="var(--brand)" stroke-width="1.5" />
          <text x="10" y="-4" style={`fill: var(--ink); font-weight: ${n.depth === 0 ? 600 : 500}; font-size: ${n.depth === 0 ? 14 : 12.5}px`}>{d.label}</text>
          <text x="10" y="12" class="num-t">{d.fmt(d.v26)} → <tspan style={`fill: ${Math.abs(delta) < 1e-5 ? 'var(--muted)' : delta > 0 ? 'var(--good)' : 'var(--adverse)'}`}>{d.fmt(d.v29)}</tspan></text>
          {#if d.torn && torn[d.torn] != null}
            <rect x="150" y="2" width={(torn[d.torn] / maxSwing) * 70} height="6" rx="2" fill="var(--s2)" opacity="0.85" />
            <text x={156 + (torn[d.torn] / maxSwing) * 70} y="9" class="num-t" style="font-size: 10.5px">{torn[d.torn].toFixed(0)} bp</text>
          {/if}
        </g>
      {/each}
    </svg>
  </div>
  <p class="chart-note">Green: moving in RoA's favour; red: against it. Amber bar: tornado swing on FY29E RoA (Evidence, section 06). Source: driver model <a class="src" href="#log">M</a>.</p>
</section>

<style>
  .node { cursor: default; transition: opacity .2s; outline: none; }
  .node.dim { opacity: .3; }
  svg { display: block; }
</style>
