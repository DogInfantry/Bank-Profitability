<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Tornado from '../charts/Tornado.svelte';
  import BetaScatter from '../charts/BetaScatter.svelte';
  import RiskCards from '../charts/RiskCards.svelte';
  import Row from '../lib/Row.svelte';
  import Stat from '../lib/Stat.svelte';
  const s = $derived(app.story!);
  const sr = $derived(app.scenarioResults!);
  const torn = $derived(Object.fromEntries(s.tornado.map((t: any) => [t.driver, t.swing_bp])));
  const rows = $derived([
    { name: 'Credit cost normalises faster', watch: 'annualised slippages above 1.5% for two quarters', bp: torn['Credit cost'], kill: 'credit cost above 0.80% in FY28: the 2% date moves to FY30' },
    { name: 'Deposit costs stay sticky', watch: 'cost of deposits rising faster than repo for two quarters', bp: torn['Cost beta: deposits'], kill: 'beta above 0.6 in year one: put CASA ahead of loan growth' },
    { name: 'Rates fall in FY28', watch: 'repo below 5.25% in the RBI forecaster survey', bp: torn['Policy repo rate, fiscal-year average'], kill: 'two cuts: raise the fixed-rate share of new lending' },
    { name: 'CASA rebuild stalls', watch: 'CASA ratio flat for two quarters', bp: torn['CASA ratio, year end'], kill: 'no gain by Q2 FY28: shift weight to borrowing retirement' },
    { name: 'Final IRDAI caps are stricter', watch: 'final rules at or below the September 2026 draft', bp: torn['IRDAI cap severity on bank fees'], kill: 'bancassurance APE down 15%: renegotiate the commission grid' },
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
  <Row>
    <Exhibit n={12} title="Funding costs follow repo about a third in year one and two-thirds in two" units="Annual change in cost of funds vs change in average repo, pp, FY17-FY26"
             source={`HDFC Bank funding costs (Screener, tied to IR26); RBI repo via FactIQ; OLS with one-year lag and merger dummy, R² ${s.beta.r2.toFixed(2)}, n = ${s.beta.n}`}>
      <BetaScatter />
    </Exhibit>
    {#snippet rail()}
      <Stat label="Deposit-cost beta, same year" value={s.beta.same_year.toFixed(2)} tone="brand" sub="Share of a repo move that reaches funding cost within the year; the model uses 0.35" />
      <Stat label="Long-run beta" value={s.beta.long_run.toFixed(2)} sub="Including the year-two catch-up; the risk case in the tornado" />
      <p class="rnote">A higher beta erodes what an asset-sensitive bank gains from rising rates: deposits reprice faster than the model assumes.</p>
    {/snippet}
  </Row>
  <p class="h-reg">Early warnings the board can see each quarter</p>
  <RiskCards {rows} downside={{ roa: sr.Downside.years[2].roa, moves: sr.Downside.bridge.levers }} />
</section>
<style>
  .h-reg { font: 600 17px var(--sans); color: var(--ink); margin: 28px 0 0; }
</style>
