<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Row from '../lib/Row.svelte';
  import Ladder from '../charts/Ladder.svelte';
  import FundingMix from '../charts/FundingMix.svelte';
  import CreditCycle from '../charts/CreditCycle.svelte';
  import Precedents from '../charts/Precedents.svelte';
  import Stat from '../lib/Stat.svelte';
  import { pct } from '../lib/format';
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
  const f = $derived(app.model!.fy26);
  const c = $derived(s.comps);
  const pi = $derived(c.pace['ICICI Bank']), pf = $derived(c.pace['IDFC First Bank']), ph = $derived(c.pace['HDFC Bank']);
  const pp = (x: number) => (x * 100).toFixed(1);
</script>
<section class="chapter" id="runoff">
  <ChapterHead n="04" kicker="Base case" title={`Run-off does half the work; the base case still stops at ${pct(b.bridge.before / 1e4, 2)}`} />
  <Row>
    <p class="prose">The merger's legacy borrowings cost {pct(f.c_bor, 2)} against {pct(f.c_dep, 2)} for deposits. Most of them mature soon: ₹1.93 lakh cr within a year. Replacing 60% of maturing borrowings with deposits, the base case, takes borrowings from 19% of funding in FY25 to 7% by FY29 and lifts the margin to {pct(b.years[2].nim, 2)}.</p>
    <p class="prose">That repair is mechanical: it happens as bonds fall due, whatever management does. Borrowings end FY29 a smaller share of the balance sheet than before the merger, and deposits carry almost all of the growth.</p>
    {#snippet rail()}<FundingMix />{/snippet}
  </Row>
  <Exhibit n={7} wide title="Most legacy borrowings mature within a year, so funding mix normalises mechanically"
           units="Left: borrowings by residual maturity at 31 March 2026, ₹ cr. Right: average borrowings / (deposits + borrowings), FY21-FY29E (base case)"
           source="HDFC Bank IR26 p384 (maturity pattern) and Schedule 4; driver model, Margin tab">
    <Ladder />
  </Exhibit>
  <Row>
    <p class="prose">Two Indian mergers show the run-off is the easier half. ICICI Bank absorbed ICICI Ltd in 2002 with borrowings at {pct(pi.b0, 0)} of funding and cut that share by {pp(pi.pace)} points a year. IDFC First started from {pct(pf.b0, 0)} and cut {pp(pf.pace)} points a year. HDFC Bank started from {pct(ph.b0, 0)} and has cut {pp(ph.pace)} points a year so far. The base case asks for {pp(c.model_pace)} points a year to FY29, slower than all three.</p>
    <p class="prose">The harder half is what replaces the borrowings. Both precedents raised the share of current and savings deposits as they shrank borrowings: ICICI Bank by {(pi.casa_bp / 100).toFixed(0)} points in three years, IDFC First by {(pf.casa_bp / 100).toFixed(0)}. HDFC Bank's share has fallen {(-ph.casa_bp / 100).toFixed(0)} points in eighteen months. The risk in the funding plan is the CASA path, not the pace of run-off; chapter 7 tests it.</p>
    {#snippet rail()}
      <Stat label="Borrowings share cut a year" value={`${pp(c.model_pace)} pts`} sub={`Base case to FY29; ICICI Bank ${pp(pi.pace)}, IDFC First ${pp(pf.pace)}, HDFC Bank so far ${pp(ph.pace)}`} />
      <Stat label="CASA ratio since the merger" value={`−${(-ph.casa_bp / 100).toFixed(1)} pts`} tone="adverse" sub={`HDFC Bank, Mar-24 to Sep-25; ICICI Bank +${(pi.casa_bp / 100).toFixed(1)} in its first three years`} />
    {/snippet}
  </Row>
  <Exhibit n={8} wide title={`HDFC Bank needs to cut borrowings ${pp(c.model_pace)} points a year; ICICI Bank managed ${pp(pi.pace)} after 2002`}
           units="Borrowings / (deposits + borrowings), domestic operations, end-March; year 0 = first March after the merger took effect (HDFC Bank to Sep-25)"
           source="RBI bank-wise performance indicators (OSMOS returns), via FactIQ; Comps tab">
    <Precedents />
    {#snippet table()}
      <table class="data"><thead><tr><th>Bank</th><th>Period</th><th class="n">Year</th><th class="n">Borrowings share</th><th class="n">CASA</th><th class="n">RoA</th></tr></thead>
        <tbody>{#each c.precedents as p}<tr><td>{p.bank}</td><td>{p.period}</td><td class="n">{p.t}</td><td class="n">{pct(p.bor_share)}</td><td class="n">{pct(p.casa)}</td><td class="n">{pct(p.roa, 2)}</td></tr>{/each}</tbody></table>
    {/snippet}
  </Exhibit>
  <Row>
    <p class="prose">Run-off is not the whole story. Credit cost has been running at {pct(s.recent_cc, 2)} of advances against a through-the-cycle {pct(s.ttc_cc, 2)}; as it normalises it takes about {s.norm_roa_bp.toFixed(0)} bp of RoA back.</p>
    <p class="prose">Net of both, the base case recovers to <b>{pct(b.years[2].roa, 2)}</b> by FY29: better, but not 2%. The remaining distance is the job of management, and chapter 5 sets out how to cover it.</p>
    {#snippet rail()}<CreditCycle />{/snippet}
  </Row>
</section>
