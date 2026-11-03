<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Side from '../lib/Side.svelte';
  import RoeBars from '../charts/RoeBars.svelte';
  import ValueBullet from '../charts/ValueBullet.svelte';
  import { pct, ind } from '../lib/format';
  const s = $derived(app.story!);
  const sr = $derived(app.scenarioResults!);
  const v = $derived(sr.Base.valuation);
</script>
<section class="chapter" id="value">
  <ChapterHead n="06" kicker="What it is worth" title="The share price already assumes success" />
  <p class="prose">At a {pct(v.ke, 2)} cost of equity and 8% long-run growth, a bank earning a sustainable return on equity R is worth (R − g) / (Ke − g) times book. Solve that for today's price of ₹{s.price} and the market is paying for <b>{pct(s.roe_implied)}</b> RoE. The base case reaches {pct(sr.Base.years[2].roe)}. The moves are not upside to the price: they are what the price already needs.</p>
  <div class="pair">
    <Exhibit n={9} title={`The price implies ${pct(s.roe_implied)} RoE; the base case delivers ${pct(sr.Base.years[2].roe)}`} units="Return on average equity, FY29E" source="Driver model (Valuation tab); NSE price 2 Nov 2026; CAPM Ke 13.13%">
      <RoeBars />
    </Exhibit>
    <Exhibit n={10} title={`The base case is worth ₹${Math.round(v.riPerShare)}-${Math.round(v.sotpPerShare)} a share against ₹${s.price}`} units="₹ per share; bars = base case; whiskers = Downside to Upside"
             source="Driver model: residual income FY27E-FY29E with terminal value; sum of the parts with listed subsidiaries at market value less 20%">
      <ValueBullet />
    </Exhibit>
  </div>
  <Side>Values are struck at 31 March 2026 and compared with the 2 November price. Rolling forward to the price date would add about 4-5% and does not change the conclusion.</Side>
  <p class="prose">That is why the stakes are large: every 10 bp of sustainable RoA is worth about <b>₹{ind(s.v10 / 1000)}k cr</b> of equity value. Only the Upside case, with RoA at {pct(sr.Upside.years[2].roa, 2)}, supports today's price on its own.</p>
</section>
<style>
  .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin: 0 calc(-1 * var(--breakout)); }
  @media (max-width: 1100px) { .pair { grid-template-columns: minmax(0, 1fr); margin: 0; gap: 0; } }
</style>
