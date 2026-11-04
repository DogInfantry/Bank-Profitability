<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Row from '../lib/Row.svelte';
  import Stat from '../lib/Stat.svelte';
  import TargetScale from '../charts/TargetScale.svelte';
  import KpiTree from '../charts/KpiTree.svelte';
  import { pct } from '../lib/format';
  const s = $derived(app.story!);
  const t = $derived(s.target_test);
  const o = $derived(s.outputs.Base);
  const iy = (y: string) => s.years.indexOf(y);
  const be = $derived(Object.fromEntries(s.breakevens.map((b: any) => [b.driver, b])) as Record<string, any>);
  const g = $derived(be['Advances growth']);
  const prem = $derived(be['Premium over the system fresh rate']);
  const ct = $derived(s.casa_test), cr = $derived(s.capital_return), rg = $derived(s.regulation);
  const lakh = (x: number) => `₹${(x / 1e5).toFixed(2)} lakh cr`;
  const kcr = (x: number) => `₹${Math.round(Math.abs(x) / 1e3)}k cr`;
  const decisions = $derived([
    { q: 'How fast to grow loans', a: 'Grow with the market and win share', b: 'Grow only as fast as deposits allow',
      cost: `Each point of loan growth is worth ${(g.slope_bp_per_unit / 100).toFixed(1)} bp of FY29E RoA; below ${pct(g.breakeven_input)} a year (base ${pct(g.base_input, 0)}) the case falls under 2%.`,
      call: 'Grow at the base pace, not faster: the credit-deposit ratio has to keep falling while borrowings run off.' },
    { q: 'Pay up for deposits, or build CASA slowly', a: 'Price term deposits above the market to fund growth now', b: 'Hold the term-deposit price; rebuild current and savings accounts',
      cost: `A term-deposit premium of ${(prem.breakeven_input * 1e4).toFixed(0)} bp over the system rate erases the headroom. If CASA keeps its recent pace, ${(-ct.roa_bp).toFixed(1)} bp of RoA is at risk.`,
      call: 'Cap the premium well under the break-even and put the branch incentive behind salary and SME current accounts.' },
    { q: 'Return capital, or keep it', a: 'Return the excess Tier 1 now', b: 'Hold it until the expected-credit-loss rules land',
      cost: `Returning ${lakh(cr.excess)} lifts FY29E RoE by ${(cr.roe_uplift * 100).toFixed(1)} points but costs ${kcr(cr.value)} of value; day-one ECL takes ${(-rg.ecl_cet1 * 100).toFixed(2)} points of CET1.`,
      call: 'Keep it through the ECL transition, then return it. It is an RoE optic, not value creation, while RoE is above the cost of equity.' },
  ]);
  // Evidence to decision: what each call rests on, where it is shown, and the Q3 FY27 reading that would reopen it.
  const cm = $derived(s.comps), hd = $derived(s.comps.banks[0]), pace = $derived(s.comps.pace);
  const pr = $derived(Object.fromEntries(s.predictions.map((p: any) => [p.metric, p])) as Record<string, any>);
  const band = (p: any, u: string) => `${p.label.split(',')[0]} outside ${(p.prediction_q3fy27 - p.tolerance).toFixed(1)}-${(p.prediction_q3fy27 + p.tolerance).toFixed(1)}${u} (our call ${p.prediction_q3fy27}${u})`;
  const evidence = $derived([
    ['1. Loan growth', `CD ratio ${pct(hd.cd, 0)} vs a peer median of ${pct(cm.med.cd, 0)}; loan growth ex FCNR (B) ${pct(hd.loan_g_ex, 0)} vs ${pct(cm.med.loan_g_ex, 0)}; the case breaks below ${pct(g.breakeven_input)} growth.`, '6, 15', band(pr.cd_ratio, '%')],
    ['2. Deposits', `CASA ${pct(hd.casa, 0)} vs ${pct(cm.med.casa, 0)} for peers; ${pct(ct.observed, 0)} of new deposits came as CASA in the last four quarters, against ${pct(ct.path, 0)} on the path. After its merger ICICI Bank added ${(pace['ICICI Bank'].casa_bp / 100).toFixed(0)} points of CASA in three years; HDFC Bank has lost ${(-pace['HDFC Bank'].casa_bp / 100).toFixed(1)}.`, '6, 8, 15', band(pr.casa_ratio, '%')],
    ['3. Capital', `${lakh(cr.excess)} of Tier 1 above 15% by FY29E; the day-one ECL top-up is ${(-rg.ecl_cet1 * 100).toFixed(2)} points of CET1, against ${kcr(rg.ecl_buffer)} of floating and contingent provisions; at 2% RoA, RoE is ${pct(t.roe2)} against a ${pct(s.ke, 2)} cost of equity.`, '12, 18', band(pr.credit_cost, ' bp')],
  ]);
  const variant = $derived([
    ['Net interest margin', `“${s.mgmt_nim.said}” (${s.mgmt_nim.speaker_role}, ${s.mgmt_nim.call_date})`, 'Not observable', `${pct(s.series.Base.nim[iy('FY29E')], 2)} by FY29E as borrowings run off`],
    ['RoE, FY29E', 'Not guided', `${pct(s.roe_implied)} (core bank, at the price)`, `${pct(s.series.Base.roe[iy('FY29E')])} before the moves`],
    ['RoA, FY29E', 'Not guided', `${pct(t.roa_px, 2)} needed to earn that RoE`, `${pct(o.with_bp / 1e4, 2)} with the six moves`],
    ['Cost of equity', 'Not disclosed', `${pct(s.ke_be.Base, 1)} (where value equals the price)`, `${pct(s.ke, 2)} (CAPM)`],
    ['Value per share', '-', `₹${s.price}`, `₹${Math.round(o.ri_ps)}-${Math.round(o.sotp_ps)}`],
  ]);
  const stake = [
    ['RBI', 'A falling credit-deposit ratio, stable liquidity, an orderly ECL transition', 'Loan growth no faster than deposits; capital held through ECL', 'Supervisory comments on the CD ratio and LCR'],
    ['Depositors', 'Rates and service', 'No rate war; more salary and current accounts', 'Term deposits moving to higher-paying banks'],
    ['Branches and staff', 'Clear targets and incentives', 'Incentives re-cut from volume to current-account balances', 'Attrition in branch sales teams'],
    ['Board and shareholders', 'RoE and dividends', 'Patience on capital return until ECL is settled', 'Pressure to return capital early'],
    ['HDFC Life and group companies', 'Commission flow from the branches', 'Commission linked to persistency, not first-year premium', 'Lower near-term fee income'],
    ['Corporate borrowers', 'Price', 'Pricing floors; slower wholesale growth', 'Share loss to banks still chasing volume'],
  ];
</script>
<section class="chapter" id="sowhat">
  <ChapterHead n="09" kicker="For the CEO" title="Three decisions decide whether 2% holds; the first hundred days show which way they went" />
  <Row>
    <p class="prose">The analysis comes down to three choices only management can make. Each has a cost that the model can price, and each has a side that keeps the base case above 2%.</p>
    {#snippet rail()}
      <Stat label="Headroom over 2% in the base case" value={`${s.breakevens[0].headroom_bp.toFixed(1)} bp`} tone="adverse" sub="With the six moves and the rule changes" />
    {/snippet}
  </Row>
  <div class="dec">
    {#each decisions as d, i}
      <article>
        <p class="dn">Decision {i + 1}</p>
        <h3>{d.q}</h3>
        <p class="opt"><b>Option A.</b> {d.a}</p>
        <p class="opt"><b>Option B.</b> {d.b}</p>
        <p class="cost">{d.cost}</p>
        <p class="call"><b>Our call.</b> {d.call}</p>
      </article>
    {/each}
  </div>

  <p class="h-reg">From evidence to decision</p>
  <div class="tbl-scroll">
    <table class="data e2d">
      <thead><tr><th>Decision</th><th>What the evidence says</th><th class="n">Exhibits</th><th>Q3 FY27 reading that reopens the call</th></tr></thead>
      <tbody>{#each evidence as r}<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td class="n">{r[2]}</td><td>{r[3]}</td></tr>{/each}</tbody>
    </table>
  </div>

  <Row>
    <p class="prose">Is 2% the right target? RoA is a proxy; the test that matters is RoE against the cost of equity. At FY29E leverage of {t.lev.toFixed(1)}x, 2.0% RoA buys {pct(t.roe2)} RoE. Earning the cost of equity needs only {pct(t.roa_ke, 2)}, so 2% clears it comfortably.</p>
    <p class="prose">The share price asks for more: {pct(t.roa_px, 2)} as the balance sheet stands, or {pct(t.roa_px_cr, 2)} if the excess capital is returned. So 2% is the right operating target, and capital return is what closes the rest of the gap to the price.</p>
    {#snippet rail()}
      <Stat label="RoE at 2.0% RoA, FY29E" value={pct(t.roe2)} tone="brand" sub={`Cost of equity ${pct(s.ke, 2)}`} />
    {/snippet}
  </Row>
  <Exhibit n={18} wide title={`2% clears the cost of equity; meeting the price needs ${pct(t.roa_px, 2)}, or ${pct(t.roa_px_cr, 2)} with capital returned`}
           units="FY29E RoA, Base; each threshold is the RoE it implies divided by FY29E leverage"
           source="Levers tab ('Is 2% the right target?'), Valuation tab (CAPM Ke, price-implied core RoE)">
    <TargetScale />
  </Exhibit>

  <Exhibit n={19} wide title="Where we differ: management guides the margin up, the price assumes more RoE than we find"
           units="Management from the Q2 FY27 earnings call; the middle column is what the share price implies (no sell-side consensus is used); our view is the Base case"
           source="FactIQ earnings-call claims (data/inputs/concall_say_do.csv); Valuation and Levers tabs">
    <div class="tbl-scroll">
      <table class="data">
        <thead><tr><th></th><th>Management says</th><th>The price assumes</th><th>We say</th></tr></thead>
        <tbody>{#each variant as r}<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>{/each}</tbody>
      </table>
    </div>
  </Exhibit>

  <p class="h-reg">Who has to move, and what it costs them</p>
  <div class="tbl-scroll">
    <table class="data">
      <thead><tr><th>Stakeholder</th><th>Wants</th><th>What the plan asks</th><th>Watch for</th></tr></thead>
      <tbody>{#each stake as r}<tr><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>{/each}</tbody>
    </table>
  </div>

  <Exhibit n={20} wide title={`The first hundred days: ${s.predictions.length} numbers in the Q3 FY27 results tell the board whether the plan is on track`}
           units="Q2 FY27 actual → our pre-registered Q3 FY27 call (results due mid-January 2027), with the model's FY27E year end"
           source="data/inputs/hdfc_q3fy27_predictions.csv (registered 4 Nov 2026); Model tab">
    <KpiTree />
  </Exhibit>
</section>
<style>
  .dec { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; margin: 18px 0 8px; }
  .dec article { border-top: 2px solid var(--ink); padding-top: 10px; }
  .dn { font: 600 11px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--brand); margin: 0; }
  .dec h3 { font: 600 18px/1.3 var(--sans); color: var(--ink); margin: 6px 0 8px; }
  .opt, .cost, .call { font: 400 14px/1.5 var(--sans); color: var(--ink-2); margin: 0 0 6px; }
  .cost { color: var(--ink); border-left: 2px solid var(--hair); padding-left: 10px; }
  .call b, .opt b { color: var(--ink); font-weight: 600; }
  .h-reg { font: 600 17px var(--sans); color: var(--ink); margin: 28px 0 8px; }
  .e2d td:nth-child(3) { white-space: nowrap; } .e2d td:nth-child(2) { min-width: 300px; } .e2d td:nth-child(4) { min-width: 180px; }
</style>
