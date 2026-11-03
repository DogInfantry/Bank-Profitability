<script lang="ts">
  import { app } from '../lib/store.svelte';
  import SecHead from '../lib/SecHead.svelte';
  import Icon from '../lib/Icon.svelte';
  const s = $derived(app.story!);
  const sr = $derived(app.scenarioResults!);
  const torn = $derived(Object.fromEntries(s.tornado.map((t: any) => [t.driver, t.swing_bp])));
  const rows = $derived([
    { risk: 'Credit cost normalises faster', conf: 'Medium', trig: 'Annualised slippages above 1.5% for two quarters', impact: `${((sr.Base.years[2].roa - sr.Downside.years[2].roa) * 1e4).toFixed(0)} bp in the full downside; ${torn['Credit cost'].toFixed(0)} bp on credit alone`, kill: 'Credit cost above 0.80% in FY28 means the 2% target moves to FY30' },
    { risk: 'Deposit costs stay sticky', conf: 'Medium', trig: 'Cost of deposits rises faster than repo for two quarters', impact: `${torn['Cost beta: deposits'].toFixed(0)} bp across beta 0.25 to 0.62`, kill: 'Beta above 0.6 in year one: reprioritise CASA over loan growth' },
    { risk: 'Rate cuts arrive in FY28', conf: 'Low', trig: 'Repo below 5.25% in the RBI forecast survey', impact: `${torn['Policy repo rate, fiscal-year average'].toFixed(0)} bp across the repo range; asset-sensitive`, kill: 'Two cuts: raise the fixed-rate share of new lending' },
    { risk: 'Final IRDAI caps are stricter', conf: 'Low', trig: 'Final rules at or below the September 2026 draft', impact: `${torn['IRDAI cap severity on bank fees'].toFixed(1)} bp; small for the bank, large for HDFC Life`, kill: 'Bancassurance APE falls more than 15%: renegotiate the commission grid' },
    { risk: 'CASA rebuild stalls', conf: 'Medium', trig: 'CASA ratio flat for two quarters', impact: `${torn['CASA ratio, year end'].toFixed(0)} bp across the CASA range`, kill: 'No CASA gain by Q2 FY28: shift weight to borrowing retirement' },
  ]);
</script>
<section class="block" id="risks">
  <SecHead idx="07" kicker="Risks and assumptions" title="What would change our mind">
    <p>Every risk has an early-warning trigger the board can see in a quarterly result, and a kill criterion: the point at which the plan, not just the forecast, should change.</p>
  </SecHead>
  <div class="tbl-scroll"><table class="data reg">
    <thead><tr><th>Risk</th><th>Confidence it is contained</th><th>Early warning</th><th>RoA at stake</th><th>Kill criterion</th></tr></thead>
    <tbody>{#each rows as r}<tr><td><Icon name="alert" /> <b>{r.risk}</b></td><td><span class="conf" data-c={r.conf}>{r.conf}</span></td><td>{r.trig}</td><td class="mono">{r.impact}</td><td>{r.kill}</td></tr>{/each}</tbody>
  </table></div>
  <p class="chart-note">RoA at stake from the tornado and the Downside scenario <a class="src" href="#log">M</a>.</p>
</section>
<style>
  .reg td { font-size: 13.5px; } .reg td b { font-weight: 600; color: var(--ink); } .reg td.mono { font-size: 12px; }
  .reg :global(.icon) { color: var(--s2); }
  .conf { font: 600 11px var(--mono); padding: 1px 6px; border-radius: 3px; border: 1px solid var(--hair); }
  .conf[data-c="Low"] { color: var(--adverse); border-color: currentColor; } .conf[data-c="Medium"] { color: var(--s2); border-color: currentColor; }
</style>
