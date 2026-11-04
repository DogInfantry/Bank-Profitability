<script lang="ts">
  // Two-way reverse stress: Base FY29E RoA with the moves and the regulatory overlay, recomputed by the engine
  // (a parity-tested port of the Excel model) for each repo and credit-cost shift. Red cells miss the 2% target
  // at the precision shown (whole bp), so a cell never reads 2.00% and red at once.
  import { app } from '../lib/store.svelte';
  import { run, scenarioDrivers, type Triple } from '../lib/engine';
  const REPO = [-50, -25, 0, 25, 50];   // bp shift to the repo path, every year
  const CC = [-10, 0, 10, 20];          // bp shift to credit cost, every year
  const overlay = $derived(app.story!.regulation.net_bp);
  const grid = $derived(REPO.map((r) => CC.map((c) => {
    const m = app.model!;
    const d = scenarioDrivers(m, 'Base');
    d.repo = d.repo.map((v) => v + r / 1e4) as Triple;
    d.cc = d.cc.map((v) => v + c / 1e4) as Triple;
    return run(m, d).bridge.withLevers + overlay;
  })));
  const target = $derived(app.model!.valuation.target_bp);
</script>
<table class="grid num" aria-label="FY29E RoA with the moves, by repo and credit-cost shift">
  <thead><tr><th>Repo shift</th>{#each CC as c}<th>Credit cost {c > 0 ? '+' : ''}{c} bp</th>{/each}</tr></thead>
  <tbody>
    {#each REPO as r, i}
      <tr><th>{r > 0 ? '+' : ''}{r} bp</th>
        {#each grid[i] as v, j}<td class:miss={Math.round(v) < target} class:base={r === 0 && CC[j] === 0}>{(v / 100).toFixed(2)}%</td>{/each}
      </tr>
    {/each}
  </tbody>
</table>
<style>
  .grid { width: 100%; border-collapse: collapse; font: 13px var(--mono); }
  th { font: 600 12px var(--sans); color: var(--muted); text-align: right; padding: 6px 8px; border-bottom: 1px solid var(--hair); }
  tbody th { text-align: left; border-bottom: 0; }
  td { text-align: right; padding: 6px 8px; border-bottom: 1px solid var(--hair); color: var(--ink); }
  td.miss { color: var(--adverse); }
  td.base { font-weight: 700; outline: 1.5px solid var(--brand); outline-offset: -2px; }
</style>
