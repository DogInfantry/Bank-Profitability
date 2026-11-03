<script lang="ts">
  import SecHead from '../lib/SecHead.svelte';
  import Icon from '../lib/Icon.svelte';
  const lanes = [
    { when: 'Now', span: '0-3 months', items: [
      ['Funding', 'Refinancing plan for ₹1.93 lakh cr of borrowings maturing in FY27; deposit-led target set', 'Treasurer'],
      ['Cost', 'Branch-vintage review of FY22-FY25 openings; net hiring frozen outside sales', 'COO'],
      ['Fees', 'Open renegotiation with HDFC Life on persistency-linked pay', 'Head, Third-party Products'],
      ['Governance', 'RoA cockpit to the board monthly; lever owners named', 'CFO'] ] },
    { when: 'Next', span: '3-12 months', items: [
      ['Funding', 'Retire ₹75,000 cr above plan; borrowings under 9% of funding', 'Treasurer'],
      ['Assets', 'New mortgage origination on pricing floors; SME and secured retail grow within risk appetite', 'CRO, Head Retail Assets'],
      ['Deposits', 'Salary and SME current-account squads live in the top 500 branches', 'Head, Branch Banking'] ] },
    { when: 'Later', span: '12-24 months', items: [
      ['Deposits', 'CASA +1.5 pp on plan; cost of deposits flat while repo rises', 'Head, Branch Banking'],
      ['Payments', 'UPI merchant-acquiring push once MDR economics are proven', 'Head, Payments'],
      ['Target', 'FY29 RoA at or above 2.00%; review the target with the FY28 result', 'Board'] ] },
  ];
  const kpis = [['RoA (core)', '1.80%', '2.04%'], ['CASA ratio', '34.1%', '35.0%'], ['Borrowings / funding', '15.1%', '7.2%'], ['Opex / average assets', '1.76%', '1.64%'], ['Credit cost', '0.41%', '≤0.68%']];
</script>
<section class="block" id="roadmap">
  <SecHead idx="08" kicker="Roadmap" title="Now, next, later: three moves start this quarter">
    <p>Sequenced by time to impact: the funding and cost moves pay back inside a year, so they fund patience on the slower CASA rebuild.</p>
  </SecHead>
  <div class="lanes">
    {#each lanes as l}
      <div class="lane">
        <p class="lane-h"><Icon name="milestone" /> <b>{l.when}</b> <span class="mono">{l.span}</span></p>
        {#each l.items as [area, what, who]}
          <div class="item"><p class="label">{area}</p><p>{what}</p><p class="who mono">{who}</p></div>
        {/each}
      </div>
    {/each}
  </div>
  <div class="kpirow">
    <p class="label">KPIs the board tracks: FY26 → FY29E with levers</p>
    <div class="kl">{#each kpis as [k, a, b]}<div><span>{k}</span><span class="num">{a} → <b>{b}</b></span></div>{/each}</div>
  </div>
</section>
<style>
  .lanes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; border-top: 1px solid var(--ink); }
  .lane { padding: 14px 16px 6px; border-left: 1px solid var(--hair); }
  .lane:first-child { border-left: 0; padding-left: 0; }
  .lane-h { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; color: var(--brand); }
  .lane-h b { font: 600 16px var(--serif); color: var(--ink); } .lane-h .mono { font-size: 11px; color: var(--muted); }
  .item { padding: 10px 0; border-top: 1px solid var(--hair-2); }
  .item p { margin: 0; font-size: 14px; color: var(--ink-2); } .item .who { font-size: 11px; color: var(--muted); margin-top: 4px; }
  .kpirow { margin-top: 26px; }
  .kl { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; margin-top: 8px; }
  .kl div { display: flex; flex-direction: column; border-left: 2px solid var(--s1); padding: 4px 10px; font-size: 13px; color: var(--muted); }
  .kl .num { color: var(--ink-2); font-size: 14px; } .kl b { color: var(--brand); font-weight: 600; }
  @media (max-width: 900px) { .lanes { grid-template-columns: 1fr; } .lane { border-left: 0; padding-left: 0; } }
</style>
