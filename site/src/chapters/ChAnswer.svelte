<script lang="ts">
  import { app } from '../lib/store.svelte';
  import ChapterHead from '../lib/ChapterHead.svelte';
  import Exhibit from '../lib/Exhibit.svelte';
  import HeroRoa from '../charts/HeroRoa.svelte';
  import AnswerTiles from '../charts/AnswerTiles.svelte';
  const s = $derived(app.story!);
  const b = $derived(app.scenarioResults!.Base);
</script>
<section class="chapter" id="answer">
  <ChapterHead n="01" kicker="The answer" title="Four things the board needs to know" />
  <AnswerTiles />
  <Exhibit n={1} wide title="RoA held 1.8-2.0% for a decade; the merger pushed it to the floor, and only the six moves clear 2% by FY29"
           units="Return on average assets, %, standalone. FY18-FY26 actual; Q2 FY27 annualised; FY27E-FY29E model, shaded band = Downside to Upside"
           source="HDFC Bank Integrated Annual Report 2025-26 p234; Q2 FY27 results; driver model (models/HDFC_RoA_Path_FY29.xlsx)">
    <HeroRoa />
    {#snippet table()}<table class="data"><thead><tr><th>Year</th><th class="n">RoA</th></tr></thead><tbody>
      {#each s.history as h}<tr><td>{h.fy}</td><td class="n">{(h.roa * 100).toFixed(2)}%</td></tr>{/each}
      <tr><td>Q2 FY27 (annualised)</td><td class="n">{(s.q2fy27_roa * 100).toFixed(2)}%</td></tr>
      {#each b.years as y, i}<tr><td>FY{27 + i}E base</td><td class="n">{(y.roa * 100).toFixed(2)}%</td></tr>{/each}
      <tr><td>FY29E with six moves</td><td class="n">{(b.bridge.withLevers / 100).toFixed(2)}%</td></tr></tbody></table>{/snippet}
  </Exhibit>
</section>
