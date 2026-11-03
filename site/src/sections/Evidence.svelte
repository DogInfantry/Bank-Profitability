<script lang="ts">
  import * as Plot from '@observablehq/plot';
  import { app } from '../lib/store.svelte';
  import SecHead from '../lib/SecHead.svelte';
  import Tornado from '../charts/Tornado.svelte';
  import BetaScatter from '../charts/BetaScatter.svelte';
  import Beeswarm from '../charts/Beeswarm.svelte';
  import PlotFigure from '../charts/PlotFigure.svelte';
  const s = $derived(app.story!);
  const css = (v: string) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const FACT = [['nii_bp', 'NII'], ['oi_bp', 'Other income'], ['opex_bp', 'Opex'], ['prov_bp', 'Provisions'], ['tax_rate_bp', 'Tax']];
  const walkRows = $derived((s.walk as any[]).filter((w) => w.step !== 'FY23 to Q2 FY27').flatMap((w) => FACT.map(([k, lab]) => ({ step: w.step, factor: lab, bp: w[k] }))));
  const walkTotal = $derived((s.walk as any[]).find((w) => w.step === 'FY23 to Q2 FY27'));
  function walkFig(width: number) {
    return Plot.plot({
      width, height: 240, marginLeft: 92, marginRight: 14, style: { background: 'transparent', color: css('--muted'), fontSize: '11.5px' },
      fx: { label: null, domain: ['FY23 to FY24', 'FY24 to FY26', 'FY26 to Q2 FY27'] }, y: { label: null, domain: FACT.map((f) => f[1]) },
      x: { label: 'bp of RoA', grid: true, nice: true },
      marks: [
        Plot.barX(walkRows.filter((d) => d.bp >= 0), { fx: 'step', y: 'factor', x: 'bp', fill: css('--s1'), rx: 2, inset: 2,
                               title: (d: any) => `${d.step}\n${d.factor}: +${d.bp.toFixed(1)} bp` }),
        Plot.barX(walkRows.filter((d) => d.bp < 0), { fx: 'step', y: 'factor', x: 'bp', fill: css('--target'), rx: 2, inset: 2,
                               title: (d: any) => `${d.step}\n${d.factor}: ${d.bp >= 0 ? '+' : ''}${d.bp.toFixed(1)} bp` }),
        Plot.ruleX([0], { stroke: css('--ink') }),
        Plot.tip(walkRows, Plot.pointerY({ fx: 'step', y: 'factor', x: 'bp', title: (d: any) => `${d.factor}: ${d.bp >= 0 ? '+' : ''}${d.bp.toFixed(1)} bp` })),
      ],
    });
  }
  function topicFig(width: number) {
    const rows = s.topics as any[];
    return Plot.plot({
      width, height: 230, marginLeft: 170, marginBottom: 36, style: { background: 'transparent', color: css('--muted'), fontSize: '11.5px' },
      x: { label: null, domain: [...new Set(rows.map((r) => r.call))] }, y: { label: null },
      color: { type: 'linear', range: [css('--seq-0'), css('--seq-5')], domain: [0, 8] },
      marks: [
        Plot.cell(rows, { x: 'call', y: 'topic', fill: 'claims', inset: 1, rx: 2 }),
        Plot.text(rows.filter((d) => d.claims < 5), { x: 'call', y: 'topic', text: 'claims', fill: css('--ink-2') }),
        Plot.text(rows.filter((d) => d.claims >= 5), { x: 'call', y: 'topic', text: 'claims', fill: css('--paper') }),
        Plot.tip(rows, Plot.pointer({ x: 'call', y: 'topic', title: (d: any) => `${d.topic}, ${d.call}: ${d.claims} claims` })),
      ],
    });
  }
</script>

<section class="block" id="evidence">
  <SecHead idx="06" kicker="Evidence" title="What the answer rests on, and how sensitive it is">
    <p>Each chart answers one question a sceptical partner would ask. The tornado reruns the full workbook 24 times; the beta comes from a regression on ten years of HDFC's own funding costs; the peer view uses all twelve listed banks.</p>
  </SecHead>

  <div class="panel">
    <p class="chart-title">Which assumption moves FY29E RoA most? The repo path, then loan growth and credit cost</p>
    <p class="chart-note">bp change in FY29E RoA when one driver moves to the low or high end of its scenario range; all else Base. Deposit beta runs 0.25 to the regression long-run 0.62.</p>
    <Tornado />
    <details class="tbl"><summary>Table</summary><div class="tbl-scroll"><table class="data"><thead><tr><th>Driver</th><th class="n">Low input</th><th class="n">High input</th><th class="n">RoA low</th><th class="n">RoA high</th><th class="n">Swing, bp</th></tr></thead>
      <tbody>{#each s.tornado as t}<tr><td>{t.driver}</td><td class="n">{t.low_input_fy29}</td><td class="n">{t.high_input_fy29}</td><td class="n">{t.roa_low_input_pct.toFixed(3)}%</td><td class="n">{t.roa_high_input_pct.toFixed(3)}%</td><td class="n">{t.swing_bp.toFixed(1)}</td></tr>{/each}</tbody></table></div></details>
  </div>

  <div class="grid-2 gap">
    <div class="panel">
      <p class="chart-title">How fast do funding costs follow the repo rate? About a third in year one, two-thirds in two</p>
      <p class="chart-note">Annual changes FY17-FY26. OLS with a one-year lag and a merger dummy: same-year beta {s.beta.same_year.toFixed(2)} (s.e. {s.beta.same_year_se.toFixed(2)}), long run {s.beta.long_run.toFixed(2)}, R² {s.beta.r2.toFixed(2)}, n = {s.beta.n}.</p>
      <BetaScatter />
    </div>
    <div class="panel">
      <p class="chart-title">Is 2% realistic? One large private bank already earns more</p>
      <p class="chart-note">FY26 standalone RoA, twelve listed banks; circle area: average assets; blue: HDFC Bank; light grey: public sector. Hover for RoE and P/B.</p>
      <Beeswarm />
      <details class="tbl"><summary>Table</summary><table class="data"><thead><tr><th>Bank</th><th class="n">RoA</th><th class="n">RoE</th><th class="n">P/B</th></tr></thead>
        <tbody>{#each [...s.peers].sort((a, b) => b.roa - a.roa) as p}<tr><td>{p.bank}</td><td class="n">{(p.roa * 100).toFixed(2)}%</td><td class="n">{(p.roe * 100).toFixed(1)}%</td><td class="n">{p.pb.toFixed(2)}x</td></tr>{/each}</tbody></table></details>
    </div>
  </div>

  <div class="grid-2 gap">
    <div class="panel">
      <p class="chart-title">What the merger changed: margin down {(-walkTotal.nii_bp).toFixed(0)} bp, cost back {walkTotal.opex_bp.toFixed(0)} bp (FY23 to Q2 FY27)</p>
      <p class="chart-note">Shapley attribution of HDFC Bank's own RoA change, bp; each step sums exactly to the change. FY24's tax effect was a one-off.</p>
      <PlotFigure make={walkFig} />
    </div>
    <div class="panel">
      <p class="chart-title">Management is talking about deposits every quarter</p>
      <p class="chart-note">Claims per topic per earnings call (FactIQ claim graph; lexical retrieval capped at 50 per topic, so read as emphasis).</p>
      <PlotFigure make={topicFig} />
      <details class="tbl"><summary>Latest claim per topic (paraphrase, with source)</summary><table class="data"><tbody>
        {#each s.topics_latest as t}<tr><td>{t.topic}<br><span class="mono" style="font-size:11px;color:var(--muted)">{t.call}</span></td><td>{t.paraphrase} {#if t.verbatim_url}<a href={t.verbatim_url} target="_blank" rel="noopener">source</a>{/if}</td></tr>{/each}
      </tbody></table></details>
    </div>
  </div>
  <p class="chart-note">Sources: driver model and its tornado <a class="src" href="#log">M</a>; Screener financials for twelve banks <a class="src" href="#log">S3</a>; RBI repo via FactIQ <a class="src" href="#log">S4</a>; earnings calls via FactIQ <a class="src" href="#log">S8</a>.</p>
</section>

<style>.gap { margin-top: 20px; }</style>
