<script lang="ts">
  // The recommendation: a scroll-built bridge (one lever per step), then peer anchors, then the decision table.
  import { onMount } from 'svelte';
  import scrollama from 'scrollama';
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Waterfall from '../charts/Waterfall.svelte';
  import Dumbbell from '../charts/Dumbbell.svelte';
  import Spot, { type SpotName } from '../lib/Spot.svelte';
  import { ind } from '../lib/format';
  const OWNER = ['Head, Branch Banking', 'Treasurer', 'CRO and Head, Retail Assets', 'COO', 'Head, Third-party Products', 'Head, Payments'];
  const SHORT = ['CASA', 'Borrowing', 'Pricing', 'Cost', 'Fees', 'UPI'];
  const SPOT: SpotName[] = ['vault', 'ladder', 'scales', 'gears', 'receipt', 'qr'];
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
  const maxBp = $derived(Math.max(...b.levers.map((l) => l.bp)));
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
    { h: 'Start: FY26 core RoA', spot: 'steps' as SpotName, chip: `${b.bridge.start.toFixed(0)} bp`, t: "Excludes FY26's one-off treasury gain and provisions.", facts: [] as string[][] },
    { h: 'Base-case drift', spot: 'flow' as SpotName, chip: `+${b.bridge.drift.toFixed(1)} bp`, t: `Borrowing run-off and the October repo hike, net of credit normalisation. This lands at ${(b.bridge.before / 100).toFixed(2)}%.`, facts: [] as string[][] },
    ...b.levers.map((l, i) => ({ h: `${i + 1}. ${l.name}`, spot: SPOT[i], chip: `+${l.bp.toFixed(1)} bp`, t: WHY[i],
      facts: [['PAT FY29E', `₹${ind(l.pat)} cr`], ['Impact in', `${meta[i].months} months`], ['Owner', OWNER[i]]] })),
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
        <div class="st" class:on={i === step}>
          <div class="card">
            <div class="ch"><Spot name={t.spot} size={36} /><p class="h">{t.h}</p><span class="chip num">{t.chip}</span></div>
            <p class="tx">{t.t}</p>
            {#if t.facts.length}<dl>{#each t.facts as [k, v]}<div><dt>{k}</dt><dd>{v}</dd></div>{/each}</dl>{/if}
          </div>
        </div>
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
      <thead><tr><th>Move</th><th class="n">RoA, bp</th><th class="barc" aria-hidden="true"></th><th class="n">PAT FY29E, ₹ cr</th><th class="n">Equity value, ₹ cr</th><th>Feasibility</th><th class="n">Months</th><th>Owner</th></tr></thead>
      <tbody>{#each b.levers as l, i}<tr><td><span class="mv"><Spot name={SPOT[i]} size={22} />{l.name}</span></td><td class="n">+{l.bp.toFixed(1)}</td>
          <td class="barc"><svg viewBox="0 0 100 10" width="100" height="10" aria-hidden="true"><rect width={(l.bp / maxBp) * 100} height="10" fill="var(--s1)" /></svg></td>
          <td class="n">{ind(l.pat)}</td><td class="n">{ind(l.value)}</td>
          <td><span class="dots" role="img" aria-label={`${meta[i].feasibility} of 5`}>{#each [1, 2, 3, 4, 5] as d}<i class:on={d <= meta[i].feasibility}></i>{/each}</span></td>
          <td class="n">{meta[i].months}</td><td>{OWNER[i]}</td></tr>{/each}
        <tr class="tot"><td>All six</td><td class="n">+{b.bridge.levers.toFixed(1)}</td><td></td><td class="n">{ind(b.levers.reduce((t, l) => t + l.pat, 0))}</td><td class="n">{ind(b.levers.reduce((t, l) => t + l.value, 0))}</td><td></td><td></td><td></td></tr></tbody>
    </table>
  </div>
  <p class="note">Feasibility is scored 1-5 on the Levers tab of the model. Move sizes, feasibility and timing are judgements for discussion. Each is an explicit driver change in the model, so it can be challenged in the appendix workbench.</p>
</section>
<style>
  .scrolly { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 48px; }
  .sticky { position: sticky; top: max(56px, calc(50vh - 270px)); align-self: start; }
  .sticky :global(.exhibit) { max-width: none; }
  .steps { padding: 14vh 0 36vh; }
  .st { min-height: 38vh; opacity: .4; transition: opacity .3s; }
  .st:last-child { min-height: 0; }
  .st.on { opacity: 1; }
  .card { border-top: 2px solid var(--ink); background: var(--surface); border-left: 1px solid var(--hair); border-right: 1px solid var(--hair); border-bottom: 1px solid var(--hair); padding: 12px 16px 14px; }
  .st.on .card { border-top-color: var(--brand); }
  .ch { display: flex; align-items: center; gap: 12px; }
  .ch .h { font: 600 15.5px/1.3 var(--sans); color: var(--ink); margin: 0; flex: 1; }
  .chip { font: 600 14px var(--mono); color: var(--brand); background: var(--brand-wash); border-radius: 3px; padding: 2px 8px; white-space: nowrap; }
  .tx { font: 400 17px/1.5 var(--serif); color: var(--ink-2); margin: 10px 0 0; }
  dl { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin: 12px 0 0; border-top: 1px solid var(--hair-2); padding-top: 8px; }
  dt { font: 600 10px var(--sans); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); } dd { margin: 2px 0 0; font: 500 12.5px var(--sans); color: var(--ink); }
  .mv { display: inline-flex; align-items: center; gap: 8px; }
  .barc { width: 108px; } .barc svg { display: block; }
  .dots { display: inline-flex; gap: 3px; } .dots i { width: 8px; height: 8px; border-radius: 50%; border: 1px solid var(--s1); } .dots i.on { background: var(--s1); }
  .moves .tot td { font-weight: 600; border-top: 1px solid var(--ink); }
  .note { font-size: 13px; color: var(--muted); margin-top: 10px; }
  @media (max-width: 1100px) { .scrolly { grid-template-columns: minmax(0, 1fr); gap: 0; } .sticky { position: static; } .st { min-height: 0; opacity: 1; padding: 6px 0; } .steps { padding: 0; } }
  @media (max-width: 640px) { dl { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); } }
</style>
