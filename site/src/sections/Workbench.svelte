<script lang="ts">
  // The live model: presets, driver shifts and lever toggles drive the TypeScript port of the Excel engine.
  import { app, DRIVER_META } from '../lib/store.svelte';
  import SecHead from '../lib/SecHead.svelte';
  import Icon from '../lib/Icon.svelte';
  import RoaPath from '../charts/RoaPath.svelte';
  import Bridge from '../charts/Bridge.svelte';
  import ValueBullet from '../charts/ValueBullet.svelte';
  import { pct } from '../lib/format';
  import type { DriverKey } from '../lib/engine';

  const r = $derived(app.result!);
  const d = $derived(app.drivers!);
  const groups = ['Rates', 'Balance sheet', 'Income and cost'];
  const fmtV = (k: DriverKey, v: number) => (DRIVER_META.find((m) => m.key === k)!.unit === 'x' ? v.toFixed(2) : pct(v, k === 'repo' || k === 'cc' || k === 'oi_pct' ? 2 : 1));
  const fmtS = (k: DriverKey, v: number) => { const u = DRIVER_META.find((m) => m.key === k)!.unit; if (!v) return '0'; return u === 'x' ? `${v > 0 ? '+' : '−'}${Math.abs(v).toFixed(2)}` : `${v > 0 ? '+' : '−'}${(Math.abs(v) * 1e4).toFixed(0)} bp`; };
  let copied = $state(false);
  function share() {
    const url = `${location.origin}${location.pathname}#${app.hash()}`;
    history.replaceState(null, '', `#${app.hash()}`);
    navigator.clipboard?.writeText(url).then(() => { copied = true; setTimeout(() => (copied = false), 1600); }).catch(() => {});
  }
  const gap = $derived(r.bridge.gap);
</script>

<section class="block" id="workbench">
  <SecHead idx="04" kicker="Workbench" title="Change any driver and watch the answer move">
    <p>This is the Excel model, ported line by line to the browser and tested against the workbook to within 0.1 bp for every scenario. Start from a preset, nudge a driver, switch a lever off, then copy the link to share exactly what you see.</p>
  </SecHead>

  <div class="bench">
    <aside class="controls panel" aria-label="Model drivers">
      <div class="presets" role="group" aria-label="Scenario preset">
        {#each ['Base', 'Upside', 'Downside'] as p}
          <button class="btn" aria-pressed={app.preset === p && !app.dirty} onclick={() => app.setPreset(p as any)}>{p}</button>
        {/each}
      </div>
      {#each groups as gname}
        <p class="label grp">{gname}</p>
        {#each DRIVER_META.filter((m) => m.group === gname) as m (m.key)}
          {@const shift = app.shift[m.key] ?? 0}
          <label class="drv" title={m.help}>
            <span class="drv-top"><span>{m.label}</span><span class="num">{fmtV(m.key, d[m.key][2])} <span class:mod={shift}>{fmtS(m.key, shift)}</span></span></span>
            <input type="range" min={m.min} max={m.max} step={m.step} value={shift} aria-label={`${m.label} shift`}
                   oninput={(e) => (app.shift = { ...app.shift, [m.key]: +(e.currentTarget as HTMLInputElement).value })} />
          </label>
        {/each}
      {/each}
      <p class="label grp">Levers (on top of the case)</p>
      {#each r.levers as l, i}
        <label class="lev"><input type="checkbox" checked={app.leverOn[i]} onchange={(e) => { const a = [...app.leverOn]; a[i] = (e.currentTarget as HTMLInputElement).checked; app.leverOn = a; }} />
          <span>{l.name}</span><span class="num">{l.bp >= 0 ? '+' : ''}{l.bp.toFixed(1)}</span></label>
      {/each}
      <div class="actions">
        <button class="btn" onclick={() => app.setPreset(app.preset)}>Reset</button>
        <button class="btn" onclick={share}><Icon name="copy" /> {copied ? 'Link copied' : 'Copy link'}</button>
      </div>
    </aside>

    <div class="outputs">
      <div class="readout">
        <div><p class="label">FY29E RoA, before levers</p><p class="v num">{pct(r.years[2].roa, 2)}</p></div>
        <div><p class="label">With levers switched on</p><p class="v num accent">{(r.bridge.withLevers / 100).toFixed(2)}%</p></div>
        <div><p class="label">Against the 2.00% target</p><p class="v num" class:down={gap < 0} class:up={gap >= 0}>{gap >= 0 ? '+' : '−'}{Math.abs(gap).toFixed(1)} bp</p></div>
        <div><p class="label">FY29E RoE · NIM</p><p class="v num small">{pct(r.years[2].roe)} · {pct(r.years[2].nim, 2)}</p></div>
      </div>
      <div class="panel">
        <p class="chart-title">RoA path: the live case against the three presets</p>
        <p class="chart-note">Return on average assets. Hollow marker: FY29E with the levers that are switched on.</p>
        <RoaPath />
      </div>
      <div class="grid-2">
        <div class="panel">
          <p class="chart-title">FY26 to FY29E bridge, bp</p>
          <p class="chart-note">Grey or red: scenario drift. Blue: levers. Dashed outline: lever switched off.</p>
          <Bridge />
        </div>
        <div class="panel">
          <p class="chart-title">Value per share against ₹{app.story!.price}</p>
          <p class="chart-note">Bars: live case. Whiskers: Downside to Upside. Ke {pct(r.valuation.ke, 2)}; justified P/B {r.valuation.pbJustified.toFixed(2)}x.</p>
          <ValueBullet />
          <details class="tbl"><summary>Valuation detail</summary>
            <table class="data"><tbody>
              <tr><td>FY29E RoE (sustainable)</td><td class="n">{pct(r.valuation.roe29)}</td></tr>
              <tr><td>Justified P/B = (RoE − g) / (Ke − g)</td><td class="n">{r.valuation.pbJustified.toFixed(2)}x</td></tr>
              <tr><td>Listed subsidiaries after 20% discount</td><td class="n">₹{Math.round(r.valuation.subsValue).toLocaleString('en-IN')} cr</td></tr>
              <tr><td>RoE the price implies</td><td class="n">{pct(r.valuation.roeImplied)}</td></tr>
            </tbody></table>
          </details>
        </div>
      </div>
    </div>
  </div>
  <p class="chart-note">Driver shifts apply equally to FY27E-FY29E on top of the chosen preset. Values beside each slider are FY29E. Source: driver model <a class="src" href="#log">M</a>; engine parity test in <code>site/tests/engine.test.ts</code>.</p>
</section>

<style>
  .bench { display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 20px; align-items: start; }
  .controls { position: sticky; top: 56px; max-height: calc(100vh - 72px); overflow: auto; padding: 14px 16px; }
  .presets { display: flex; gap: 6px; margin-bottom: 6px; }
  .presets .btn { flex: 1; }
  .grp { margin: 14px 0 4px; }
  .drv { display: block; padding: 5px 0; font-size: 13px; color: var(--ink-2); }
  .drv-top { display: flex; justify-content: space-between; gap: 8px; }
  .drv .num { font-size: 12px; color: var(--ink); }
  .drv .num span { color: var(--muted); margin-left: 4px; }
  .drv .num span.mod { color: var(--brand); }
  input[type=range] { width: 100%; accent-color: var(--brand); height: 18px; }
  .lev { display: grid; grid-template-columns: 18px 1fr auto; gap: 8px; align-items: center; font-size: 13px; padding: 4px 0; color: var(--ink-2); }
  .lev input { accent-color: var(--brand); }
  .lev .num { font-size: 12px; color: var(--ink); }
  .actions { display: flex; gap: 8px; margin-top: 14px; }
  .outputs { display: flex; flex-direction: column; gap: 20px; min-width: 0; }
  .readout { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-top: 1px solid var(--ink); border-bottom: 1px solid var(--hair); }
  .readout > div { padding: 12px 14px; border-left: 1px solid var(--hair); }
  .readout > div:first-child { border-left: 0; padding-left: 0; }
  .v { font-size: 26px; margin: 4px 0 0; letter-spacing: -0.02em; white-space: nowrap; }
  .v.small { font-size: 20px; padding-top: 8px; }
  .v.accent { color: var(--brand); }
  @media (max-width: 1000px) { .bench { grid-template-columns: 1fr; } .controls { position: static; max-height: none; } .readout { grid-template-columns: repeat(2, minmax(0, 1fr)); } .readout > div:nth-child(3) { border-left: 0; padding-left: 0; } }
</style>
