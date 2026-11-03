<script lang="ts">
  // Chapter 6 rail: the justified price-to-book equation with the model's numbers in it. Switch the RoE to see P/B move.
  import { app } from '../lib/store.svelte';
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
  const V = $derived(app.model!.valuation);
  const levRoe = $derived(b.levers.reduce((t, l) => t + l.roe, 0));
  const cases = $derived([
    { k: 'Base case', roe: b.years[2].roe },
    { k: 'With the moves', roe: b.years[2].roe + levRoe },
    { k: "Today's price", roe: s.roe_implied },
  ]);
  let sel = $state(0);
  const c = $derived(cases[sel]);
  const ke = $derived(b.valuation.ke);
  const pb = $derived((c.roe - V.g) / (ke - V.g));
  const p1 = (x: number) => `${(x * 100).toFixed(1)}%`;
</script>
<figure class="pbe">
  <p class="rh">What a return is worth: justified price to book</p>
  <div class="sw" role="group" aria-label="Choose the return on equity">
    {#each cases as cc, i}<button aria-pressed={sel === i} onclick={() => (sel = i)}>{cc.k}</button>{/each}
  </div>
  <div class="eq" aria-live="polite">
    <div class="frac">
      <div class="numr"><span class="tile hi"><small>RoE</small>{p1(c.roe)}</span><span class="op">−</span><span class="tile"><small>g</small>{p1(V.g)}</span></div>
      <div class="bar"></div>
      <div class="den"><span class="tile"><small>Ke</small>{p1(ke)}</span><span class="op">−</span><span class="tile"><small>g</small>{p1(V.g)}</span></div>
    </div>
    <span class="op">=</span>
    <span class="res"><small>P/B</small>{pb.toFixed(2)}×</span>
  </div>
  <p class="cap">RoE is FY29E return on equity, g is long-run growth and Ke the CAPM cost of equity. {sel === 2 ? `The ₹${s.price} price is ${pb.toFixed(2)}× book: it needs ${p1(c.roe)} RoE for good.` : `At ${pb.toFixed(2)}× book the market price of ${(V.mcap / app.model!.fy26.eq).toFixed(2)}× is not covered.`}</p>
</figure>
<style>
  .pbe { margin: 0; border-top: 2px solid var(--ink); padding-top: 10px; }
  .rh { font: 600 14px/1.3 var(--sans); color: var(--ink); margin: 0 0 8px; }
  .sw { display: flex; gap: 0; border: 1px solid var(--hair); border-radius: 4px; overflow: hidden; margin-bottom: 14px; }
  .sw button { flex: 1; font: 500 11.5px var(--sans); color: var(--ink-2); background: none; border: 0; border-left: 1px solid var(--hair); padding: 5px 4px; cursor: pointer; }
  .sw button:first-child { border-left: 0; }
  .sw button[aria-pressed='true'] { background: var(--brand); color: var(--paper); }
  .eq { display: flex; align-items: center; gap: 10px; }
  .frac { display: flex; flex-direction: column; align-items: center; gap: 6px; }
  .numr, .den { display: flex; align-items: center; gap: 6px; }
  .bar { height: 2px; background: var(--ink); align-self: stretch; }
  .tile, .res { display: flex; flex-direction: column; align-items: center; font: 500 15px var(--mono); color: var(--ink); background: var(--surface); border: 1px solid var(--hair); border-radius: 3px; padding: 3px 8px 4px; min-width: 58px; }
  .tile.hi { border-color: var(--s1); color: var(--brand); }
  small { font: 500 9.5px var(--sans); color: var(--muted); letter-spacing: .06em; text-transform: uppercase; }
  .op { font: 400 18px var(--mono); color: var(--muted); }
  .res { font-size: 22px; color: var(--brand); border: 1.5px solid var(--brand); padding: 6px 10px; }
  .cap { font: 400 12.5px/1.45 var(--sans); color: var(--ink-2); margin: 12px 0 0; }
</style>
