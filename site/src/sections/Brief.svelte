<script lang="ts">
  import { app } from '../lib/store.svelte';
  import SecHead from '../lib/SecHead.svelte';
  import Spark from '../lib/Spark.svelte';
  import { ind, pct } from '../lib/format';
  const s = $derived(app.story!);
  const base = $derived(app.scenarioResults!.Base);
  const roaPath = $derived([...s.series.Base.roa.slice(1, 7), ...base.years.map((y) => y.roa)]);
  const levTotal = $derived(base.levers.reduce((a, l) => a + l.bp, 0));
</script>

<section class="block" id="brief">
  <SecHead idx="01" kicker="The question and the answer" title="Back above 2% by FY29, but only if management pulls six levers. The share price already assumes it.">
    <p>HDFC Bank earned 1.8 to 2.0% on its assets for a decade. Since the 2023 merger it sits at the bottom of that range, and in Q2 FY27 it earned <b>{pct(s.q2fy27_roa, 2)}</b> annualised. The base case recovers to <b>{pct(base.years[2].roa, 2)}</b> as legacy borrowings run off; six levers add <b>{levTotal.toFixed(1)} bp</b>. Meanwhile the market price implies a <b>{pct(s.roe_implied)}</b> return on equity, and the base case reaches <b>{pct(base.years[2].roe)}</b>.</p>
  </SecHead>

  <div class="kpis">
    <div class="kpi">
      <p class="label">Now · Q2 FY27, annualised</p>
      <p class="big num">{pct(s.q2fy27_roa, 2)}</p>
      <p class="sub">Return on average assets. Reported 1.78%.</p>
    </div>
    <div class="kpi">
      <p class="label">FY29E · base case</p>
      <p class="big num">{pct(base.years[2].roa, 2)}</p>
      <Spark values={roaPath} split={5} target={0.02} />
      <p class="sub">Drift from run-off, net of credit normalisation.</p>
    </div>
    <div class="kpi accent">
      <p class="label">FY29E · with six levers</p>
      <p class="big num">{(base.bridge.withLevers / 100).toFixed(2)}%</p>
      <p class="sub">{base.bridge.gap >= 0 ? `${base.bridge.gap.toFixed(1)} bp of headroom over` : `${(-base.bridge.gap).toFixed(1)} bp short of`} the 2.00% target.</p>
    </div>
    <div class="kpi">
      <p class="label">What the price assumes</p>
      <p class="big num">{pct(s.roe_implied)}</p>
      <p class="sub">RoE implied by P/B at Ke {pct(s.ke)}. Each 10 bp of RoA ≈ ₹{ind(s.v10 / 1000)}k cr of value.</p>
    </div>
  </div>

  <div class="decide">
    <p class="label">Three decisions for the steering committee</p>
    <ol>
      <li><b>Make deposits the binding constraint.</b> Hold the credit-deposit ratio near 93% and fund a 1.5 pp CASA rebuild before chasing loan share. <span class="owner">Owner: Head, Branch Banking</span></li>
      <li><b>Retire ₹75,000 cr of legacy borrowings ahead of plan.</b> They cost {pct(app.model!.fy26.c_bor, 2)} against {pct(app.model!.fy26.c_dep, 2)} for deposits. <span class="owner">Owner: Treasurer</span></li>
      <li><b>Re-price the HDFC Life partnership before the IRDAI caps land.</b> Persistency-linked pay keeps the margin the caps create inside the group. <span class="owner">Owner: Head, Third-party Products</span></li>
    </ol>
  </div>
</section>

<style>
  .kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-top: 1px solid var(--ink); border-bottom: 1px solid var(--hair); margin: 8px 0 28px; }
  .kpi { padding: 16px 18px 18px; border-left: 1px solid var(--hair); }
  .kpi:first-child { border-left: 0; padding-left: 0; }
  .kpi.accent .big { color: var(--brand); }
  .big { font-size: clamp(30px, 3.6vw, 44px); font-weight: 500; margin: 6px 0 4px; letter-spacing: -0.02em; color: var(--ink); }
  .sub { font-size: 13px; color: var(--muted); margin: 4px 0 0; }
  .decide ol { margin: 10px 0 0; padding-left: 22px; max-width: 80ch; }
  .decide li { font-family: var(--serif); font-size: 18px; line-height: 1.5; color: var(--ink-2); margin-bottom: 8px; padding-left: 4px; }
  .decide li b { color: var(--ink); font-weight: 600; }
  .owner { display: inline-block; font: 500 11px var(--mono); color: var(--muted); margin-left: 6px; }
  @media (max-width: 900px) { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } .kpi:nth-child(3) { border-left: 0; padding-left: 0; } }
</style>
