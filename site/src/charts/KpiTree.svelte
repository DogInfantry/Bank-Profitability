<script lang="ts">
  // Exhibit 20: the first-100-days KPI tree. Root = RoA; branches = the drivers the plan moves; leaves = the frozen Q3 FY27 calls (Q2 actual -> call -> FY27E model).
  import { app } from '../lib/store.svelte';
  const s = $derived(app.story!);
  const base = $derived(s.series.Base);
  const iy = (y: string) => s.years.indexOf(y);
  type P = { metric: string; label: string; unit: string; q2fy27_actual: number; prediction_q3fy27: number; fy27e_model: number | ''; tolerance: number };
  const pr = $derived(Object.fromEntries((s.predictions as P[]).map((p) => [p.metric, p])) as Record<string, P>);
  const branches = [
    { name: 'Funding mix', owner: 'Treasurer', leaves: ['borrowings_share_funding', 'casa_ratio', 'deposits'] },
    { name: 'Balance-sheet discipline', owner: 'CFO', leaves: ['cd_ratio'] },
    { name: 'Margin', owner: 'CFO', leaves: ['nim_total_assets'] },
    { name: 'Credit', owner: 'CRO', leaves: ['credit_cost'] },
  ];
  const f = (p: P, v: number) => (p.unit === '%' ? `${v.toFixed(p.tolerance < 0.1 ? 2 : 1)}%` : p.unit === 'bp' ? `${v.toFixed(0)} bp` : v.toLocaleString('en-IN'));
</script>
<div class="tree">
  <div class="root">
    <span class="k">RoA, core</span>
    <span class="v num">{(base.roa[iy('FY26A')] * 100).toFixed(2)}% → <b>{(s.outputs.Base.with_bp / 100).toFixed(2)}%</b></span>
    <span class="s">FY26A → FY29E with the moves</span>
  </div>
  <div class="branches">
    {#each branches as b}
      <div class="br">
        <p class="bn">{b.name} <span class="ow">{b.owner}</span></p>
        {#each b.leaves as m}
          {@const p = pr[m]}
          <div class="leaf">
            <span class="lk">{p.label}</span>
            <span class="lv num">{f(p, p.q2fy27_actual)} → <b>{f(p, p.prediction_q3fy27)}</b> {#if typeof p.fy27e_model === 'number'}<span class="lt">FY27E {f(p, p.fy27e_model)}</span>{/if}</span>
          </div>
        {/each}
      </div>
    {/each}
  </div>
</div>
<style>
  .tree { display: grid; grid-template-columns: minmax(150px, 210px) 1fr; gap: 0 28px; align-items: center; }
  .root { border: 1px solid var(--ink); padding: 12px 14px; display: flex; flex-direction: column; gap: 4px; position: relative; }
  .root::after { content: ''; position: absolute; right: -28px; top: 50%; width: 28px; border-top: 1px solid var(--hair); }
  .k, .bn { font: 600 13px var(--sans); color: var(--ink); margin: 0; }
  .v { font: 500 16px var(--mono); color: var(--ink-2); } .v b { color: var(--brand); }
  .s, .lt, .ow { font: 400 11.5px var(--sans); color: var(--muted); }
  .branches { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 14px; border-left: 1px solid var(--hair); padding-left: 16px; }
  .br { border-top: 2px solid var(--s1); padding-top: 6px; }
  .leaf { display: flex; flex-direction: column; padding: 6px 0; border-bottom: 1px solid var(--hair-2); }
  .lk { font: 400 12.5px var(--sans); color: var(--ink-2); }
  .lv { font: 500 13px var(--mono); color: var(--ink-2); } .lv b { color: var(--ink); }
  @media (max-width: 640px) { .tree { grid-template-columns: 1fr; gap: 14px; } .root::after { display: none; } .branches { border-left: 0; padding-left: 0; } }
</style>
