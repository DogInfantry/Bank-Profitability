<script lang="ts">
  // The recommendation: a scroll-built bridge (one lever per step), then peer anchors, then the decision table.
  import { onMount } from 'svelte';
  import scrollama from 'scrollama';
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Waterfall from '../charts/Waterfall.svelte';
  import Dumbbell from '../charts/Dumbbell.svelte';
  import { ind } from '../lib/format';
  const OWNER = ['Head, Branch Banking', 'Treasurer', 'CRO and Head, Retail Assets', 'COO', 'Head, Third-party Products', 'Head, Payments'];
  const SHORT = ['CASA', 'Borrowing', 'Pricing', 'Cost', 'Fees', 'UPI'];
  const WHY = [
    'Move 1.5 pp of deposits from term to current and savings accounts. Salary and SME current-account acquisition in the top 500 branches; term deposits re-priced by tenor.',
    'Retire ₹75,000 cr of legacy borrowings beyond the base plan and refinance with deposits. Each ₹1 lakh cr saves about ₹3,000 cr a year before tax.',
    'Lift the yield on new lending by 10 bp: pricing floors on new mortgages, more SME and secured retail within risk appetite.',
    'Hold operating cost 3% below plan by FY29: a branch-vintage review of the FY22-FY25 openings and a hiring freeze outside sales.',
    'Grow core fees 3% above plan and protect bancassurance through a persistency-linked commission grid with HDFC Life before the IRDAI caps land.',
    'Lift UPI merchant-acquiring share from 6.6% to 10% of payee volume as the new MDR switches on. Small in RoA; a franchise option.',
  ];
  const b = $derived(app.scenarioResults!.Base);
  const meta = $derived(app.model!.levers);
  let step = $state(0);
  let vw = $state(1200);
  const stacked = $derived(vw < 1100);
  // step 0: FY26 only; 1: + base drift; k >= 2: + the first k-1 moves. Unrevealed bars are drawn as dashed outlines.
  const shown = $derived.by(() => {
    const k = stacked ? 7 : Math.min(step, 7);
    const lev = b.levers.map((l, i) => ({ label: SHORT[i], v: l.bp, dim: i >= k - 1 }));
    const end = b.bridge.start + (k >= 1 ? b.bridge.drift : 0) + b.levers.slice(0, Math.max(0, k - 1)).reduce((t, l) => t + l.bp, 0);
    return [{ label: 'FY26', v: b.bridge.start, total: true }, { label: 'Drift', v: b.bridge.drift, dim: k < 1 }, ...lev, { label: k >= 7 ? 'FY29E' : 'So far', v: end, total: true }];
  });
  const texts = $derived([
    { h: 'Start: FY26 core RoA', t: `${b.bridge.start.toFixed(0)} bp, excluding FY26's one-off treasury gain and provisions.` },
    { h: 'Base-case drift', t: `+${b.bridge.drift.toFixed(1)} bp: borrowing run-off and the October repo hike, net of credit normalisation. This lands at ${(b.bridge.before / 100).toFixed(2)}%.` },
    ...b.levers.map((l, i) => ({ h: `${i + 1}. ${l.name}`, t: `${WHY[i]} Worth +${l.bp.toFixed(1)} bp, ₹${ind(l.pat)} cr of PAT in FY29E; ${meta[i].months} months to impact.` })),
  ]);
  let stepsEl: HTMLDivElement;
  onMount(() => {
    const sc = scrollama();
    sc.setup({ step: stepsEl.querySelectorAll('.st') as unknown as HTMLElement[], offset: 0.55 }).onStepEnter((r) => { step = r.index; });
    const ro = new ResizeObserver(() => sc.resize()); ro.observe(stepsEl);
    return () => { sc.destroy(); ro.disconnect(); };
  });
</script>
<svelte:window bind:innerWidth={vw} />
<section class="chapter" id="moves">
  <ChapterHead n="05" kicker="Recommendation" title="Six moves close the gap, and none asks for more than half of what a peer already does" />
  <p class="prose">The recommendation is funding first, asset mix second, cost third. On a wide screen the bridge builds one move at a time as you scroll; the order is by size.</p>
  <div class="scrolly" class:stacked>
    <div class="sticky">
      <Exhibit n={7} title={`Six moves add ${b.bridge.levers.toFixed(1)} bp and take FY29E RoA to ${(b.bridge.withLevers / 100).toFixed(2)}%`}
               units="Return on average assets, bp, FY26 core to FY29E (base case plus moves); axis starts at 150 bp"
               source="Driver model (Levers tab); each move is an explicit driver change on top of the base case">
        <Waterfall steps={shown} lo={150} hi={210} H={320} />
      </Exhibit>
    </div>
    <div class="steps" bind:this={stepsEl}>
      {#each texts as t, i}
        <div class="st" class:on={i === step}><p class="h">{t.h}</p><p class="prose">{t.t}</p></div>
      {/each}
    </div>
  </div>
  <p class="prose">Is each move credible? For four of them there is a named Indian bank already operating where the move would take HDFC Bank, and the move asks for only part of that distance.</p>
  <Exhibit n={8} wide title="Each move closes 28-49% of the gap to a named peer: an ask, not a stretch"
           units="HDFC Bank FY26 → where the move takes it → benchmark; CASA ratio, borrowings share of funding, interest earned / average assets, UPI payee share"
           source="SBI Q2 FY27 press release; ICICI Bank FY26 (Screener, tied to filings); Axis Bank NPCI payee data Sep 2026; driver model">
    <Dumbbell />
  </Exhibit>
  <div class="tbl-scroll">
    <table class="data moves">
      <thead><tr><th>Move</th><th class="n">RoA, bp</th><th class="n">PAT FY29E, ₹ cr</th><th class="n">Equity value, ₹ cr</th><th class="n">Months</th><th>Owner</th></tr></thead>
      <tbody>{#each b.levers as l, i}<tr><td>{l.name}</td><td class="n">+{l.bp.toFixed(1)}</td><td class="n">{ind(l.pat)}</td><td class="n">{ind(l.value)}</td><td class="n">{meta[i].months}</td><td>{OWNER[i]}</td></tr>{/each}
        <tr class="tot"><td>All six</td><td class="n">+{b.bridge.levers.toFixed(1)}</td><td class="n">{ind(b.levers.reduce((t, l) => t + l.pat, 0))}</td><td class="n">{ind(b.levers.reduce((t, l) => t + l.value, 0))}</td><td></td><td></td></tr></tbody>
    </table>
  </div>
  <p class="note">Move sizes, feasibility and timing are judgements for discussion. Each is an explicit driver change in the model, so it can be challenged in the appendix workbench.</p>
</section>
<style>
  .scrolly { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(0, 1fr); gap: 36px; margin: 0 calc(-1 * var(--breakout)); }
  .sticky { position: sticky; top: 60px; align-self: start; }
  .steps { padding: 18vh 0 32vh; }
  .st { min-height: 52vh; opacity: .45; transition: opacity .3s; }
  .st.on { opacity: 1; }
  .st .h { font: 600 15px var(--sans); color: var(--ink); margin: 0 0 6px; }
  .st .prose { font-size: 18px; }
  .moves .tot td { font-weight: 600; border-top: 1px solid var(--ink); }
  .note { font-size: 13px; color: var(--muted); margin-top: 10px; }
  @media (max-width: 1100px) { .scrolly { margin: 0; grid-template-columns: minmax(0, 1fr); gap: 0; } .sticky { position: static; } .st { min-height: 0; opacity: 1; padding: 10px 0; border-top: 1px solid var(--hair-2); } .steps { padding: 0; } }
</style>
