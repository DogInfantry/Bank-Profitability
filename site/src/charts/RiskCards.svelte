<script lang="ts">
  // Chapter 7: the early-warning register as cards. The bar is the tornado swing in FY29E RoA for that driver.
  import Spot from '../lib/Spot.svelte';
  type Risk = { name: string; watch: string; bp: number; kill: string };
  let { rows, downside }: { rows: Risk[]; downside: { roa: number; moves: number } } = $props();
  const max = $derived(Math.max(...rows.map((r) => r.bp)));
</script>
<div class="cards">
  {#each rows as r}
    <article class="card">
      <p class="nm">{r.name}</p>
      <div class="sw"><span class="lab">FY29E RoA at risk</span><span class="num">{r.bp < 10 ? r.bp.toFixed(1) : r.bp.toFixed(0)} bp</span></div>
      <svg viewBox="0 0 200 8" width="100%" preserveAspectRatio="none" aria-hidden="true"><rect width="200" height="8" fill="var(--hair-2)" /><rect width={(r.bp / max) * 200} height="8" fill="var(--s2)" /></svg>
      <p class="ln"><Spot name="eye" size={18} /><span><b>Watch</b> {r.watch}</span></p>
      <p class="ln kill"><Spot name="stop" size={18} /><span><b>Act if</b> {r.kill}</span></p>
    </article>
  {/each}
  <article class="card all">
    <Spot name="shield" size={34} />
    <p class="nm">Everything at once</p>
    <p class="big num">{(downside.roa * 100).toFixed(2)}%</p>
    <p class="ln"><span>FY29E RoA in the full Downside case, with every driver wrong together. The six moves still add about <b>{downside.moves.toFixed(0)} bp</b>, so the plan holds up even when the base case does not.</span></p>
  </article>
</div>
<style>
  .cards { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin: 20px 0 8px; }
  .card { background: var(--surface); border: 1px solid var(--hair); border-top: 2px solid var(--ink); padding: 12px 14px 12px; display: flex; flex-direction: column; gap: 6px; }
  .nm { font: 600 15px/1.3 var(--sans); color: var(--ink); margin: 0; }
  .sw { display: flex; justify-content: space-between; align-items: baseline; }
  .sw .lab { font: 500 11px var(--sans); color: var(--muted); } .sw .num { font: 600 14px var(--mono); color: var(--s2); }
  svg { display: block; height: 6px; }
  .ln { display: flex; gap: 8px; align-items: flex-start; margin: 4px 0 0; font: 400 13px/1.45 var(--sans); color: var(--ink-2); }
  .ln b { color: var(--ink); font-weight: 600; margin-right: 2px; }
  .kill { color: var(--ink-2); }
  .all { background: var(--brand-wash); border-top-color: var(--brand); }
  .all .big { font: 500 28px var(--mono); color: var(--brand); margin: 0; }
  @media (max-width: 1000px) { .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 640px) { .cards { grid-template-columns: minmax(0, 1fr); } }
</style>
