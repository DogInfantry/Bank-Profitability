<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import PeerGap from '../charts/PeerGap.svelte';
  import Beeswarm from '../charts/Beeswarm.svelte';
  import Row from '../lib/Row.svelte';
  import Stat from '../lib/Stat.svelte';
  import CompsTable from '../charts/CompsTable.svelte';
  import { pct } from '../lib/format';
  const g = $derived(app.story!.icici_gap);
  const s = $derived(app.story!);
  const c = $derived(s.comps);
  const h = $derived(c.banks[0]);
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
  <Row>
    <p class="prose">The market already marks HDFC Bank down for this. Net of its listed stakes it trades at {h.pb_ex.toFixed(2)}x book, {pct(-c.pb_prem, 0)} below the peer median of {c.med.pb_ex.toFixed(2)}x. Its FY26 RoA of {pct(h.roa, 2)} is above the peer median ({pct(c.med.roa, 2)}) and its RoE of {pct(h.roe)} is close to it ({pct(c.med.roe)}), so returns do not explain the discount.</p>
    <p class="prose">Funding does. HDFC Bank lends {pct(h.cd, 0)} of its deposits against a peer median of {pct(c.med.cd, 0)}, carries {pct(h.casa, 0)} of deposits in current and savings accounts against {pct(c.med.casa, 0)}, and grew loans {pct(h.loan_g_ex, 0)} in the year to September against {pct(c.med.loan_g_ex, 0)}. The answer in this case, fixing the funding, is also what would close the multiple.</p>
    {#snippet rail()}
      <Stat label="P/B ex listed stakes" value={`${h.pb_ex.toFixed(2)}x`} sub={`Peer median ${c.med.pb_ex.toFixed(2)}x (ICICI, Axis, Kotak, SBI)`} />
      <Stat label="Price at the peer median multiple" value={`₹${Math.round(c.px_at_med)}`} tone="brand" sub={`Against ₹${s.price} on 2 Nov 2026`} />
    {/snippet}
  </Row>
  <Exhibit n={6} wide title={`HDFC Bank earns peer-level returns but trades ${pct(-c.pb_prem, 0)} below peers: the market prices the funding gap`}
           units="Standalone. P/B and P/E at 2 Nov 2026 (P/B net of listed stakes at market, less the holding-company discount); RoA and RoE FY26; balance sheet 30 Sep 2026; loan growth year on year, excluding FCNR (B) swap loans"
           source="Screener (market data, FY26 financials); Q2 FY27 investor decks; ICICI Bank Form 20-F FY2026 and SBI Q2 FY27 deck (subsidiary stakes); Comps tab">
    <CompsTable />
  </Exhibit>
  <p class="rnote">Kotak's multiples set group market cap against standalone book and earnings, because its subsidiaries are unlisted, which flatters them; the median is less exposed to that than the mean. HDFC Bank's loan growth excludes its FCNR leverage loans; its FCNR deposits are not disclosed.</p>
</section>
