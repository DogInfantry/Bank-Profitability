<script lang="ts">
  // Appendix A rail: how the driver model is wired, from inputs to value. Static schematic in the emblem's line style.
  import { app } from '../lib/store.svelte';
  const nDrv = $derived(Object.keys(app.model!.drivers).length);
  const steps = $derived([
    ['Inputs', `${nDrv} drivers × 3 scenarios, FY27E-FY29E`],
    ['Balance sheet', 'Advances, deposits, legacy borrowings running off; average balances'],
    ['Profit and loss', 'Margin by rate and volume, fees, cost, credit cost, tax'],
    ['Returns', 'RoA and RoE, with the six moves as driver changes'],
    ['Value', 'Residual income, sum of the parts, justified P/B'],
  ]);
</script>
<figure class="flow" aria-label="How the model works">
  <p class="rh">How the model works</p>
  <ol>
    {#each steps as [h, t], i}<li><span class="n mono">{i + 1}</span><div><b>{h}</b><span>{t}</span></div></li>{/each}
  </ol>
  <p class="cap">Every step is a formula in the Excel workbook; the page re-runs the same arithmetic and is tested against it to 0.1 bp.</p>
</figure>
<style>
  .flow { margin: 0; border-top: 2px solid var(--ink); padding-top: 10px; }
  .rh { font: 600 14px var(--sans); color: var(--ink); margin: 0 0 10px; }
  ol { list-style: none; margin: 0; padding: 0; position: relative; }
  ol::before { content: ''; position: absolute; left: 12px; top: 14px; bottom: 14px; border-left: 1.5px solid var(--brand); }
  li { position: relative; display: flex; gap: 12px; align-items: flex-start; padding: 0 0 12px; }
  .n { flex: none; width: 25px; height: 25px; border-radius: 50%; display: grid; place-items: center; background: var(--paper); border: 1.5px solid var(--brand); color: var(--brand); font-size: 11.5px; position: relative; }
  li div { display: flex; flex-direction: column; font: 400 12.5px/1.4 var(--sans); color: var(--ink-2); padding-top: 3px; }
  li b { font: 600 13px var(--sans); color: var(--ink); }
  .cap { font: 400 12px/1.45 var(--sans); color: var(--muted); margin: 2px 0 0; }
</style>
