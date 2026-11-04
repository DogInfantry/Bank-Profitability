<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Row from '../lib/Row.svelte';
  import Stat from '../lib/Stat.svelte';
  import Spot from '../lib/Spot.svelte';
  import RoeBars from '../charts/RoeBars.svelte';
  import ValueBullet from '../charts/ValueBullet.svelte';
  import PbEquation from '../charts/PbEquation.svelte';
  import { pct, ind } from '../lib/format';
  const s = $derived(app.story!);
  const sr = $derived(app.scenarioResults!);
  const v = $derived(sr.Base.valuation);
</script>
<section class="chapter" id="value">
  <ChapterHead n="06" kicker="What it is worth" title="The share price already assumes success" />
  <Row>
    <p class="prose">At a {pct(v.ke, 2)} cost of equity and 8% long-run growth, a bank earning a sustainable return on equity R is worth (R − g) / (Ke − g) times book. Solve that for today's price of ₹{s.price} and the market is paying for <b>{pct(s.roe_implied)}</b> RoE.</p>
    <p class="prose">The base case reaches {pct(sr.Base.years[2].roe)}. The moves are not upside to the price: they are what the price already needs.</p>
    {#snippet rail()}<PbEquation />{/snippet}
  </Row>
  <div class="pair">
    <Exhibit n={11} title={`The price implies ${pct(s.roe_implied)} RoE; the base case delivers ${pct(sr.Base.years[2].roe)}`} units="Return on average equity, FY29E" source={`Driver model (Valuation tab); NSE price 2 Nov 2026; CAPM Ke ${pct(v.ke, 2)}; core bank, latest book`}>
      <RoeBars />
    </Exhibit>
    <Exhibit n={12} title={`The base case is worth ₹${Math.round(v.riPerShare)}-${Math.round(v.sotpPerShare)} a share against ₹${s.price}`} units="₹ per share; bars = base case; whiskers = Downside to Upside"
             source="Driver model: residual income FY27E-FY29E with terminal value; sum of the parts with listed subsidiaries at market value less 20%">
      <ValueBullet />
    </Exhibit>
  </div>
  <Row mid>
    <p class="prose">That is why the stakes are large: every 10 bp of sustainable RoA is worth about <b>₹{ind(s.v10 / 1000)}k cr</b> of equity value. Only the Upside case, with RoA at {pct(sr.Upside.years[2].roa, 2)}, supports today's price on its own.</p>
    {#snippet rail()}
      <div class="v10"><Spot name="coins" size={40} /><Stat label="Value of 10 bp of RoA" value={`₹${ind(s.v10 / 1000)}k cr`} tone="brand" sub="Equity value, at the base-case Ke and growth" /></div>
      <p class="rnote">The answer hinges on the cost of equity. At {pct(v.keBreakEven, 2)} or less, the base case alone supports ₹{s.price}; peer prices imply {pct(s.peer_ke['Axis Bank'], 1)} (Axis) to {pct(s.peer_ke['HDFC Bank'], 1)} (HDFC Bank). Values are rolled forward to the 2 November price date.</p>
    {/snippet}
  </Row>
</section>
<style>
  .v10 { display: grid; grid-template-columns: 48px minmax(0, 1fr); gap: 12px; align-items: start; }
  .v10 :global(.spot) { margin-top: 12px; }
</style>
