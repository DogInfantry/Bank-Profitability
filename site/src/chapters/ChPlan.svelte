<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Roadmap, { type Action } from '../charts/Roadmap.svelte';
  // Months from November 2026. Now = 0-3, Next = 3-12, Later = 12-24; the RoA cockpit runs throughout.
  const actions: (Action & { what: string; when: string })[] = [
    { when: 'Now', area: 'Funding', short: 'Refinancing plan, ₹1.93 lakh cr', what: 'Refinancing plan for the ₹1.93 lakh cr maturing in FY27; deposit-led funding target set', owner: 'Treasurer', s: 0, e: 3 },
    { when: 'Now', area: 'Cost', short: 'Branch-vintage review; hiring freeze', what: 'Branch-vintage review of FY22-FY25 openings; net hiring frozen outside sales', owner: 'COO', s: 0, e: 3 },
    { when: 'Now', area: 'Fees', short: 'HDFC Life commission renegotiation', what: 'Open the HDFC Life commission renegotiation on persistency-linked pay', owner: 'Head, Third-party Products', s: 0, e: 3 },
    { when: 'Now', area: 'Governance', short: 'Monthly RoA cockpit to the board', what: 'Monthly RoA cockpit to the board; one owner per move', owner: 'CFO', s: 0, e: 3, cont: true },
    { when: 'Next', area: 'Funding', short: 'Retire ₹75,000 cr above plan', what: 'Retire ₹75,000 cr above plan; borrowings below 9% of funding', owner: 'Treasurer', s: 3, e: 12 },
    { when: 'Next', area: 'Assets', short: 'Pricing floors; SME and secured retail', what: 'Pricing floors on new mortgages; SME and secured retail grow within risk appetite', owner: 'CRO, Head Retail Assets', s: 3, e: 12 },
    { when: 'Next', area: 'Deposits', short: 'Salary and SME current-account teams', what: 'Salary and SME current-account teams live in the top 500 branches', owner: 'Head, Branch Banking', s: 3, e: 12 },
    { when: 'Later', area: 'Deposits', short: 'CASA +1.5 pp on plan', what: 'CASA +1.5 pp on plan; cost of deposits flat while repo rises', owner: 'Head, Branch Banking', s: 12, e: 24 },
    { when: 'Later', area: 'Payments', short: 'UPI merchant-acquiring push', what: 'UPI merchant-acquiring push once MDR economics are proven', owner: 'Head, Payments', s: 12, e: 24 },
  ];
  const milestones = [{ m: 10, label: 'Q2 FY28: CASA checkpoint' }, { m: 17, label: 'FY28 result: target review' }, { m: 28, label: 'FY29: RoA at or above 2.00%' }];
  const roaTarget = $derived(app.scenarioResults!.Base.bridge.withLevers / 100);
  const kpis = $derived([['RoA (core)', 1.80, roaTarget, 2, ''], ['CASA ratio', 34.1, 35.0, 1, ''], ['Borrowings / funding', 15.1, 7.2, 1, ''], ['Opex / average assets', 1.76, 1.64, 2, ''], ['Credit cost', 0.41, 0.68, 2, '≤ ']] as [string, number, number, number, string][]);
</script>
<section class="chapter" id="plan">
  <ChapterHead n="08" kicker="Next twelve months" title="Three moves start this quarter; the slow one is funded by the fast ones" />
  <p class="prose">Sequence by time to impact. Retiring borrowings and holding cost pay back inside a year; that buys the patience the CASA rebuild needs.</p>
  <Exhibit n={13} wide title="Funding and cost move first; deposits and payments compound in year two"
           units="Actions by workstream, months from November 2026, with owners and board checkpoints"
           source="Recommendation; timings from the Levers tab (months to impact) and the risk register kill criteria">
    <Roadmap {actions} {milestones} />
    {#snippet table()}<table class="data"><thead><tr><th>When</th><th>Area</th><th>Action</th><th>Owner</th></tr></thead>
      <tbody>{#each actions as a}<tr><td>{a.when}</td><td>{a.area}</td><td>{a.what}</td><td>{a.owner}</td></tr>{/each}</tbody></table>{/snippet}
  </Exhibit>
  <p class="kh">Five numbers the board tracks: FY26 → FY29E with the moves</p>
  <div class="kl">
    {#each kpis as [k, a, b, dp, pre]}
      {@const up = b > a}
      <div class="kp">
        <span class="kk">{k}</span>
        <span class="kv num">{a.toFixed(dp)}% → <b>{pre}{b.toFixed(dp)}%</b></span>
        <svg viewBox="0 0 120 22" width="100%" height="22" aria-hidden="true">
          <line x1="6" x2="114" y1={up ? 17 : 5} y2={up ? 5 : 17} stroke="var(--s1)" stroke-width="2" />
          <circle cx="6" cy={up ? 17 : 5} r="3" fill="var(--paper)" stroke="var(--s1)" stroke-width="1.5" /><circle cx="114" cy={up ? 5 : 17} r="3.5" fill="var(--brand)" />
        </svg>
        {#if pre}<span class="kn">a ceiling, not a target</span>{/if}
      </div>
    {/each}
  </div>
</section>
<style>
  .kh { font: 600 15px var(--sans); color: var(--ink); margin: 28px 0 10px; }
  .kl { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0; border-top: 2px solid var(--ink); }
  .kp { display: flex; flex-direction: column; gap: 4px; padding: 10px 14px 6px; border-left: 1px solid var(--hair); }
  .kp:first-child { border-left: 0; padding-left: 0; }
  .kk { font: 600 11px var(--sans); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
  .kv { font: 500 16px var(--mono); color: var(--ink-2); } .kv b { color: var(--brand); font-weight: 600; }
  .kn { font: 400 11px var(--sans); color: var(--muted); }
  @media (max-width: 900px) { .kl { grid-template-columns: repeat(2, minmax(0, 1fr)); } .kp { border-left: 0; padding-left: 0; border-top: 1px solid var(--hair-2); } }
</style>
