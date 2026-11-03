<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import PeerGap from '../charts/PeerGap.svelte';
  import Beeswarm from '../charts/Beeswarm.svelte';
  import Row from '../lib/Row.svelte';
  import Stat from '../lib/Stat.svelte';
  const g = $derived(app.story!.icici_gap);
</script>
<section class="chapter" id="peers">
  <ChapterHead n="03" kicker="Benchmark" title="Against ICICI Bank the gap is funding; HDFC Bank already wins on cost" />
  <Row mid>
    <p class="prose">ICICI Bank shows a large Indian private bank can earn more than 2% in this rate cycle. HDFC Bank trails it by {(g.gap * 100).toFixed(0)} bp, and the decomposition points one way: {(g.nii * 100).toFixed(0)} bp of the gap is net interest income and {(g.prov * 100).toFixed(0)} bp is FY26's one-off provisions. On operating cost and fee income HDFC Bank is already ahead.</p>
    {#snippet rail()}
      <Stat label="RoA gap to ICICI Bank, FY26" value={`−${(g.gap * 100).toFixed(0)} bp`} sub="HDFC Bank 1.80% against ICICI Bank's 2.2%" />
      <Stat label="Of which margin" value={`−${(g.nii * 100).toFixed(0)} bp`} tone="adverse" sub="Net interest income per rupee of assets" />
      <Stat label="Where HDFC Bank leads" value={`+${(-g.opex * 100).toFixed(0)} bp`} tone="brand" sub="Lower operating cost per rupee of assets" />
    {/snippet}
  </Row>
  <div class="pair">
    <Exhibit n={4} title={`The ${(g.gap * 100).toFixed(0)} bp gap to ICICI Bank is margin and one-off provisions`} units="Contribution to HDFC Bank's FY26 RoA gap vs ICICI Bank, bp (negative = costs HDFC)"
             source="Screener standalone FY26 financials, tied to annual reports; Shapley attribution (pipeline/shapley.py)">
      <PeerGap />
    </Exhibit>
    <Exhibit n={5} title="2% is reachable: ICICI Bank already earns 2.2%" units="FY26 standalone RoA, twelve listed banks; circle area = average assets; blue = HDFC Bank"
             source="Screener standalone FY26 financials and valuation for twelve banks">
      <Beeswarm />
    </Exhibit>
  </div>
</section>
