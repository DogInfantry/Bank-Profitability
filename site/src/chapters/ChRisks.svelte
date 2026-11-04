<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Tornado from '../charts/Tornado.svelte';
  import BetaScatter from '../charts/BetaScatter.svelte';
  import RiskCards from '../charts/RiskCards.svelte';
  import StressGrid from '../charts/StressGrid.svelte';
  import Row from '../lib/Row.svelte';
  import Stat from '../lib/Stat.svelte';
  import { ind } from '../lib/format';
  const s = $derived(app.story!);
  const sr = $derived(app.scenarioResults!);
  const reg = $derived(s.regulation);
  const pc = (d: number) => (v: number) => `${(v * 100).toFixed(d)}%`;
  const BE: Record<string, [string, (v: number) => string]> = {
    'Policy repo rate, fiscal-year average': ['Repo rate, FY29 average', pc(2)], 'Credit cost': ['Credit cost', pc(2)],
    'CASA ratio, year end': ['CASA ratio, FY29', pc(1)], 'Premium over the system fresh rate': ['Deposit premium over system', pc(2)],
    'Operating expense growth': ['Opex growth', pc(1)], 'Cost of equity': ['Cost of equity (value = ₹700)', pc(2)],
  };
  const beRows = $derived(s.breakevens.filter((b: any) => b.driver in BE).map((b: any) => ({ ...b, label: BE[b.driver][0], fmt: BE[b.driver][1] })));
  const fmtBp = (v: number) => `${v >= 0 ? '+' : '−'}${Math.abs(v).toFixed(1)}`;
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
  <p class="prose">The full workbook was recalculated {s.tornado.length * 2} times, moving one assumption at a time across its scenario range. Three assumptions matter far more than the rest. The bank is asset-sensitive, so the repo path leads; credit cost and the pace of loan growth follow.</p>
  <Exhibit n={11} wide title="The repo path, loan growth and credit cost move FY29E RoA most"
           units="Change in FY29E RoA vs base, bp, when one driver moves to the low or high end of its range; all else base"
           source="Driver model recalculated in LibreOffice (pipeline/tornado.py); ranges = min/max of the scenario inputs; deposit beta 0.25 to 0.62">
    <Tornado />
  </Exhibit>
  <p class="prose">Rule changes outside the scenario path net {fmtBp(reg.net_bp)} bp of FY29E RoA: the CRR cut to 3% adds {Math.abs(reg.crr_bp).toFixed(1)} bp, and expected-credit-loss provisioning from April 2027 costs {Math.abs(reg.ecl_bp).toFixed(1)} bp a year. The larger ECL risk is day one: a top-up of about ₹{ind(reg.ecl_gross / 1000)}k cr, {(-reg.ecl_cet1 * 100).toFixed(1)} points of CET1 before any relief, against ₹{ind(reg.ecl_buffer / 1000)}k cr of floating and contingent provisions already held. LCR headroom is {(reg.lcr_head * 100).toFixed(0)} points; the April 2026 digital-deposit run-off is offset by the rest of the package.</p>
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
  <p class="prose">What would change our answer. With the moves and the rule changes, the base case clears 2% by only {s.breakevens[0].headroom_bp.toFixed(1)} bp. Each line below is the single input at which it stops clearing, read off the recalculated workbook.</p>
  <div class="pair">
    <Exhibit n={13} title="A small move in any one of these inputs takes the base case below 2%" units="Base input vs the level at which FY29E RoA with the moves falls to 2.0%"
             source="Tornado recalculations (pipeline/breakevens.py); Ke break-even from the Valuation tab">
      <table class="data"><thead><tr><th>Input</th><th class="n">Base</th><th class="n">Break-even</th></tr></thead>
        <tbody>{#each beRows as b}<tr><td>{b.label}</td><td class="n">{b.fmt(b.base_input)}</td><td class="n">{b.fmt(b.breakeven_input)}</td></tr>{/each}</tbody></table>
    </Exhibit>
    <Exhibit n={14} title="Repo and credit cost together: where the base case still clears 2%" units="Base FY29E RoA with the moves and rule changes; red = below 2.0%"
             source="Browser engine (parity-tested port of the Excel model), every year shifted by the amount shown">
      <StressGrid />
    </Exhibit>
  </div>
  <p class="h-reg">Calls we will be scored on: Q3 FY27 results, due mid-January 2027</p>
  <table class="data pred"><thead><tr><th>Metric</th><th class="n">Q2 FY27</th><th class="n">Our Q3 FY27 call</th><th class="n">Tolerance</th></tr></thead>
    <tbody>{#each s.predictions as p}<tr><td>{p.label}</td><td class="n">{p.q2fy27_actual}{p.unit === '%' ? '%' : ''}</td><td class="n"><b>{p.prediction_q3fy27}{p.unit === '%' ? '%' : ''}</b></td><td class="n">±{p.tolerance}</td></tr>{/each}</tbody></table>
  <p class="rnote">Registered on {s.predictions[0].registered_on}, before the results. Rule: halfway from the September actual to the model's March 2027 year end.</p>
</section>
<style>
  .h-reg { font: 600 17px var(--sans); color: var(--ink); margin: 28px 0 0; }
  .pred { max-width: var(--main); margin-top: 10px; }
</style>
