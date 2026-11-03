<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import Side from '../lib/Side.svelte';
  import Ladder from '../charts/Ladder.svelte';
  import { pct } from '../lib/format';
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
  const f = $derived(app.model!.fy26);
</script>
<section class="chapter" id="runoff">
  <ChapterHead n="04" kicker="Base case" title="Run-off does half the work; the base case still stops at 1.86%" />
  <p class="prose">The merger's legacy borrowings cost {pct(f.c_bor, 2)} against {pct(f.c_dep, 2)} for deposits. Most of them mature soon: ₹1.93 lakh cr within a year. Replacing 60% of maturing borrowings with deposits, the base case, takes borrowings from 19% of funding in FY25 to 7% by FY29 and lifts the margin to {pct(b.years[2].nim, 2)}.</p>
  <Exhibit n={6} wide title="Most legacy borrowings mature within a year, so funding mix normalises mechanically"
           units="Left: borrowings by residual maturity at 31 March 2026, ₹ cr. Right: average borrowings / (deposits + borrowings), FY21-FY29E (base case)"
           source="HDFC Bank IR26 p384 (maturity pattern) and Schedule 4; driver model, Margin tab">
    <Ladder />
  </Exhibit>
  <Side>Through the cycle means the FY21-FY26 average of loan-loss provisions over average advances; recent means FY24-FY26.</Side>
  <p class="prose">Run-off is not the whole story. Credit cost has been running at {pct(s.recent_cc, 2)} of advances against a through-the-cycle {pct(s.ttc_cc, 2)}; as it normalises it takes about {s.norm_roa_bp.toFixed(0)} bp of RoA back. Net of both, the base case recovers to <b>{pct(b.years[2].roa, 2)}</b> by FY29: better, but not 2%. The remaining distance is the job of management.</p>
</section>
