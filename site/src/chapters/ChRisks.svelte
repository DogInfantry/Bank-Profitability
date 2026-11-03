<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Tornado from '../charts/Tornado.svelte';
  import BetaScatter from '../charts/BetaScatter.svelte';
  const s = $derived(app.story!);
  const sr = $derived(app.scenarioResults!);
  const torn = $derived(Object.fromEntries(s.tornado.map((t: any) => [t.driver, t.swing_bp])));
  const rows = $derived([
    ['Credit cost normalises faster', 'Annualised slippages above 1.5% for two quarters', `${torn['Credit cost'].toFixed(0)} bp`, 'Credit cost above 0.80% in FY28: the 2% date moves to FY30'],
    ['Deposit costs stay sticky', 'Cost of deposits rising faster than repo for two quarters', `${torn['Cost beta: deposits'].toFixed(0)} bp`, 'Beta above 0.6 in year one: put CASA ahead of loan growth'],
    ['Rates fall in FY28', 'Repo below 5.25% in the RBI forecaster survey', `${torn['Policy repo rate, fiscal-year average'].toFixed(0)} bp`, 'Two cuts: raise the fixed-rate share of new lending'],
    ['CASA rebuild stalls', 'CASA ratio flat for two quarters', `${torn['CASA ratio, year end'].toFixed(0)} bp`, 'No gain by Q2 FY28: shift weight to borrowing retirement'],
    ['Final IRDAI caps are stricter', 'Final rules at or below the September 2026 draft', `${torn['IRDAI cap severity on bank fees'].toFixed(1)} bp`, 'Bancassurance APE down 15%: renegotiate the commission grid'],
  ]);
</script>
<section class="chapter" id="risks">
  <ChapterHead n="07" kicker="Risks" title="What could break it: the rate path, credit cost and deposit pricing" />
  <p class="prose">The full workbook was recalculated 24 times, moving one assumption at a time across its scenario range. Three assumptions matter far more than the rest. The bank is asset-sensitive, so the repo path leads; credit cost and the pace of loan growth follow.</p>
  <Exhibit n={11} wide title="The repo path, loan growth and credit cost move FY29E RoA most; regulation barely registers"
           units="Change in FY29E RoA vs base, bp, when one driver moves to the low or high end of its range; all else base"
           source="Driver model recalculated in LibreOffice (pipeline/tornado.py); ranges = min/max of the scenario inputs; deposit beta 0.25 to 0.62">
    <Tornado />
  </Exhibit>
  <div class="two">
    <div>
      <Exhibit n={12} title="Funding costs follow repo about a third in year one and two-thirds in two" units="Annual change in cost of funds vs change in average repo, pp, FY17-FY26"
               source={`HDFC Bank funding costs (Screener, tied to IR26); RBI repo via FactIQ; OLS with one-year lag and merger dummy, R² ${s.beta.r2.toFixed(2)}, n = ${s.beta.n}`}>
        <BetaScatter />
      </Exhibit>
    </div>
    <div class="reg">
      <p class="h">Early warnings the board can see each quarter</p>
      {#each rows as r}
        <div class="risk"><p class="rn">{r[0]} <span class="mono">{r[2]}</span></p><p>Watch: {r[1]}.</p><p class="kill">Kill criterion: {r[3]}.</p></div>
      {/each}
    </div>
  </div>
  <p class="note">In the full Downside case every driver goes wrong at once and FY29E RoA falls to {(sr.Downside.years[2].roa * 100).toFixed(2)}%; the six moves still add about {sr.Downside.bridge.levers.toFixed(0)} bp.</p>
</section>
<style>
  .two { display: grid; grid-template-columns: 1.1fr 1fr; gap: 36px; margin: 0 calc(-1 * var(--breakout)); }
  .reg { padding-top: 36px; } .reg .h { font: 600 15px var(--sans); color: var(--ink); border-top: 2px solid var(--ink); padding-top: 10px; margin: 0 0 6px; }
  .risk { border-bottom: 1px solid var(--hair-2); padding: 9px 0; } .risk p { margin: 0; font-size: 13.5px; color: var(--ink-2); }
  .risk .rn { font-weight: 600; color: var(--ink); display: flex; justify-content: space-between; } .risk .rn .mono { color: var(--s2); font-size: 12px; }
  .risk .kill { color: var(--muted); }
  .note { font-size: 13px; color: var(--muted); }
  @media (max-width: 1100px) { .two { grid-template-columns: minmax(0, 1fr); margin: 0; gap: 0; } }
</style>
