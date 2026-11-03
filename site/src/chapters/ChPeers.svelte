<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import PeerGap from '../charts/PeerGap.svelte';
  import Beeswarm from '../charts/Beeswarm.svelte';
  const g = $derived(app.story!.icici_gap);
</script>
<section class="chapter" id="peers">
  <ChapterHead n="03" kicker="Benchmark" title="Against ICICI Bank the gap is funding; HDFC Bank already wins on cost" />
  <p class="prose">ICICI Bank shows a large Indian private bank can earn more than 2% in this rate cycle. HDFC Bank trails it by {(g.gap * 100).toFixed(0)} bp, and the decomposition points one way: {(g.nii * 100).toFixed(0)} bp of the gap is net interest income and {(g.prov * 100).toFixed(0)} bp is FY26's one-off provisions. On operating cost and fee income HDFC Bank is already ahead.</p>
  <div class="pair wide-pair">
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
<style>
  .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin: 0 calc(-1 * var(--breakout)); }
  .pair :global(.exhibit) { margin: 28px 0; }
  @media (max-width: 1100px) { .pair { grid-template-columns: minmax(0, 1fr); margin: 0; gap: 0; } }
</style>
