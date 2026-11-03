<script lang="ts">
  // Levers as a product backlog: impact, confidence (peer gap closed), time to impact, owner. Matrix: impact x time.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import SecHead from '../lib/SecHead.svelte';
  import { ind } from '../lib/format';
  import { showTip, hideTip } from '../lib/tooltip';
  const OWNER = ['Head, Branch Banking', 'Treasurer', 'CRO and Head, Retail Assets', 'COO', 'Head, Third-party Products', 'Head, Payments'];
  const ANCHOR = ['Rebuild CASA', 'Retire legacy borrowings', 'Re-mix advances', '', '', 'Win UPI acquiring'];
  const base = $derived(app.scenarioResults!.Base);
  const meta = $derived(app.model!.levers);
  const anchors = $derived(app.story!.anchors as any[]);
  const cards = $derived(base.levers.map((l, i) => {
    const a = ANCHOR[i] ? anchors.find((x) => x.lever.startsWith(ANCHOR[i])) : null;
    return { ...l, i, months: meta[i].months, feas: meta[i].feasibility, mech: meta[i].mechanism, owner: OWNER[i], anchor: a,
             wave: meta[i].months <= 12 ? 'Now' : 'Next' };
  }).sort((a, b) => b.bp - a.bp));
  let w = $state(520);
  const H = 300, m = { t: 16, r: 20, b: 40, l: 44 };
  const x = $derived(d3.scaleLinear().domain([6, 21]).range([m.l, w - m.r]));
  const y = $derived(d3.scaleLinear().domain([0, 6.5]).range([H - m.b, m.t]));
  const rad = $derived(d3.scaleSqrt().domain([0, 50000]).range([0, 26]));
  const SHORT = ['CASA', 'Borrowings', 'Re-mix', 'Productivity', 'Fees', 'UPI'];
</script>

<section class="block" id="bets">
  <SecHead idx="05" kicker="Bets" title="Six levers, ranked like a backlog: impact, confidence, time to impact">
    <p>Confidence is evidence, not opinion: for four levers it is the share of the gap to a named peer that the lever would close. A lever that asks for a third of what SBI or ICICI Bank already deliver is a credible ask. HDFC already leads on cost and fees, so those two are sized on its own operating leverage.</p>
  </SecHead>
  <div class="bets">
    <div class="cards">
      {#each cards as c (c.name)}
        <article class="card">
          <header><span class="wave" class:now={c.wave === 'Now'}>{c.wave}</span><h3>{c.name}</h3></header>
          <p class="mech">{c.mech}</p>
          <dl>
            <div><dt>Impact</dt><dd class="num">+{c.bp.toFixed(1)} bp</dd></div>
            <div><dt>PAT FY29E</dt><dd class="num">₹{ind(c.pat)} cr</dd></div>
            <div><dt>Equity value</dt><dd class="num">₹{ind(c.value / 1000)}k cr</dd></div>
            <div><dt>Time to impact</dt><dd class="num">{c.months} months</dd></div>
          </dl>
          {#if c.anchor}
            <div class="anchor">
              <div class="abar"><span style={`width:${Math.min(100, c.anchor.share * 100)}%`}></span></div>
              <p>Closes <b class="num">{(c.anchor.share * 100).toFixed(0)}%</b> of the gap to {c.anchor.source.split(',')[0].split('(')[0].trim()}</p>
            </div>
          {:else}
            <p class="anchor muted">No peer gap: HDFC already leads; sized on its own operating leverage.</p>
          {/if}
          <p class="owner mono">{c.owner}</p>
        </article>
      {/each}
    </div>
    <div class="panel matrix" bind:clientWidth={w}>
      <p class="chart-title">Impact against time to impact</p>
      <p class="chart-note">Circle area: equity value. Up and to the left is where to start.</p>
      <svg width={w} height={H} role="img" aria-label="Lever impact against months to impact">
        <rect x={m.l} y={m.t} width={x(12) - m.l} height={y(2.5) - m.t} fill="var(--brand-wash)" />
        <text x={m.l + 6} y={m.t + 14} style="fill: var(--brand); font-weight: 600">Start now</text>
        {#each y.ticks(6) as t}<line x1={m.l} x2={w - m.r} y1={y(t)} y2={y(t)} stroke="var(--hair-2)" /><text x={m.l - 6} y={y(t) + 4} text-anchor="end" class="num-t">{t}</text>{/each}
        {#each [6, 9, 12, 15, 18, 21] as t}<text x={x(t)} y={H - m.b + 16} text-anchor="middle" class="num-t">{t}</text>{/each}
        <text x={(m.l + w - m.r) / 2} y={H - 6} text-anchor="middle">Months to impact</text>
        <text x="12" y={m.t + 4} style="font-size: 11px">bp</text>
        {#each cards as c (c.name)}
          <circle cx={x(c.months)} cy={y(c.bp)} r={Math.max(5, rad(c.value))} fill="var(--s1)" fill-opacity="0.25" stroke="var(--s1)" stroke-width="1.5"
                  role="presentation" onmousemove={(e) => showTip(e, `<b>${c.name}</b><br>+${c.bp.toFixed(1)} bp · ₹${ind(c.value)} cr of value<br>${c.months} months · feasibility ${c.feas}/5`)} onmouseleave={hideTip} />
          <text x={x(c.months) + Math.max(5, rad(c.value)) + 4} y={y(c.bp) + 4} style="fill: var(--ink); font-weight: 500">{SHORT[c.i]}</text>
        {/each}
      </svg>
    </div>
  </div>
  <p class="chart-note">Lever sizes, feasibility and timing are judgements for discussion; each is an explicit driver change in the model. Peer values: SBI Q2 FY27 press release; ICICI Bank and Axis Bank FY26 and NPCI payee data <a class="src" href="#log">S3</a><a class="src" href="#log">S5</a>.</p>
</section>

<style>
  .bets { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 20px; align-items: start; }
  .cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 250px), 1fr)); gap: 14px; }
  .card { background: var(--surface); border: 1px solid var(--hair); border-top: 2px solid var(--s1); border-radius: 3px; padding: 14px 16px; display: flex; flex-direction: column; gap: 8px; }
  .card header { display: flex; gap: 8px; align-items: baseline; }
  .card h3 { font-size: 18px; }
  .wave { font: 600 10px var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); border: 1px solid var(--hair); padding: 1px 6px; border-radius: 3px; }
  .wave.now { color: var(--brand); border-color: var(--brand); }
  .mech { font-size: 13px; color: var(--muted); margin: 0; }
  dl { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 12px; margin: 4px 0; }
  dt { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
  dd { margin: 0; font-size: 15px; color: var(--ink); }
  .anchor { font-size: 12.5px; color: var(--ink-2); margin: 0; }
  .anchor p { margin: 4px 0 0; }
  .anchor.muted { color: var(--muted); }
  .abar { height: 6px; background: var(--hair-2); border-radius: 3px; overflow: hidden; }
  .abar span { display: block; height: 100%; background: var(--s3); }
  .owner { font-size: 11px; color: var(--muted); margin: 0; }
  .matrix { position: sticky; top: 56px; }
  @media (max-width: 1000px) { .bets { grid-template-columns: minmax(0, 1fr); } .matrix { position: static; } }
</style>
