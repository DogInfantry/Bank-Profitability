<script lang="ts">
  import ChapterHead from '../lib/ChapterHead.svelte';
  const lanes = [
    { when: 'Now', span: '0-3 months', items: [
      ['Funding', 'Refinancing plan for the ₹1.93 lakh cr maturing in FY27; deposit-led funding target set', 'Treasurer'],
      ['Cost', 'Branch-vintage review of FY22-FY25 openings; net hiring frozen outside sales', 'COO'],
      ['Fees', 'Open the HDFC Life commission renegotiation on persistency-linked pay', 'Head, Third-party Products'],
      ['Governance', 'Monthly RoA cockpit to the board; one owner per move', 'CFO'] ] },
    { when: 'Next', span: '3-12 months', items: [
      ['Funding', 'Retire ₹75,000 cr above plan; borrowings below 9% of funding', 'Treasurer'],
      ['Assets', 'Pricing floors on new mortgages; SME and secured retail grow within risk appetite', 'CRO, Head Retail Assets'],
      ['Deposits', 'Salary and SME current-account teams live in the top 500 branches', 'Head, Branch Banking'] ] },
    { when: 'Later', span: '12-24 months', items: [
      ['Deposits', 'CASA +1.5 pp on plan; cost of deposits flat while repo rises', 'Head, Branch Banking'],
      ['Payments', 'UPI merchant-acquiring push once MDR economics are proven', 'Head, Payments'],
      ['Target', 'FY29 RoA at or above 2.00%; target reviewed with the FY28 result', 'Board'] ] },
  ];
  const kpis = [['RoA (core)', '1.80%', '2.04%'], ['CASA ratio', '34.1%', '35.0%'], ['Borrowings / funding', '15.1%', '7.2%'], ['Opex / average assets', '1.76%', '1.64%'], ['Credit cost', '0.41%', '≤ 0.68%']];
</script>
<section class="chapter" id="plan">
  <ChapterHead n="08" kicker="Next twelve months" title="Three moves start this quarter; the slow one is funded by the fast ones" />
  <p class="prose">Sequence by time to impact. Retiring borrowings and holding cost pay back inside a year; that buys the patience the CASA rebuild needs.</p>
  <div class="lanes">
    {#each lanes as l}
      <div class="lane">
        <p class="lh"><b>{l.when}</b><span class="mono">{l.span}</span></p>
        {#each l.items as [area, what, who]}<div class="it"><p class="ar">{area}</p><p>{what}</p><p class="who mono">{who}</p></div>{/each}
      </div>
    {/each}
  </div>
  <div class="kpi"><p class="kh">Five numbers the board tracks: FY26 → FY29E with the moves</p>
    <div class="kl">{#each kpis as [k, a, b]}<div><span>{k}</span><span class="num">{a} → <b>{b}</b></span></div>{/each}</div></div>
</section>
<style>
  .lanes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-top: 2px solid var(--ink); margin: 24px calc(-1 * var(--breakout)) 0; }
  .lane { padding: 12px 18px 4px; border-left: 1px solid var(--hair); } .lane:first-child { border-left: 0; padding-left: 0; }
  .lh { display: flex; justify-content: space-between; align-items: baseline; margin: 0 0 6px; } .lh b { font: 600 20px var(--serif); color: var(--brand); } .lh .mono { font-size: 11px; color: var(--muted); }
  .it { padding: 10px 0; border-top: 1px solid var(--hair-2); } .it p { margin: 0; font-size: 14px; color: var(--ink-2); }
  .ar { font: 600 11px var(--sans) !important; letter-spacing: .1em; text-transform: uppercase; color: var(--muted) !important; } .who { font-size: 11px !important; color: var(--muted) !important; margin-top: 4px !important; }
  .kpi { margin-top: 28px; } .kh { font: 600 14px var(--sans); color: var(--ink); }
  .kl { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
  .kl div { display: flex; flex-direction: column; border-left: 2px solid var(--s1); padding: 2px 10px; font-size: 13px; color: var(--muted); } .kl .num { color: var(--ink-2); font-size: 15px; } .kl b { color: var(--brand); }
  @media (max-width: 1100px) { .lanes { margin: 24px 0 0; } }
  @media (max-width: 760px) { .lanes { grid-template-columns: minmax(0, 1fr); } .lane { border-left: 0; padding-left: 0; } }
</style>
