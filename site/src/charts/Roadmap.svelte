<script lang="ts" module>
  // Chapter 8: the plan as a Gantt on a month axis from November 2026, coloured by workstream, owners at the bar ends,
  // and the three board checkpoints as milestones.
  export type Action = { area: string; short: string; owner: string; s: number; e: number; cont?: boolean };
</script>
<script lang="ts">
  let { actions, milestones }: { actions: Action[]; milestones: { m: number; label: string }[] } = $props();
  const COL: Record<string, string> = { Funding: 'var(--s1)', Deposits: 'var(--s1)', Assets: 'var(--s2)', Cost: 'var(--s3)', Fees: 'var(--context)', Payments: 'var(--context)', Governance: 'var(--ink)' };
  const KEY = [['Funding and deposits', 'var(--s1)'], ['Assets', 'var(--s2)'], ['Cost', 'var(--s3)'], ['Fees and payments', 'var(--context)'], ['Governance', 'var(--ink)']];
  const PH = [{ s: 0, e: 3, k: 'Now' }, { s: 3, e: 12, k: 'Next' }, { s: 12, e: 24, k: 'Later' }];
  const TICKS = [{ m: 0, k: 'Nov 26' }, { m: 4, k: 'Mar 27' }, { m: 10, k: 'Sep 27' }, { m: 16, k: 'Mar 28' }, { m: 22, k: 'Sep 28' }, { m: 28, k: 'Mar 29' }];
  let w = $state(900);
  const narrow = $derived(w < 640);
  const LW = $derived(narrow ? 0 : 250);
  const rh = $derived(narrow ? 42 : 30);
  const top = 26;
  const H = $derived(top + actions.length * rh + 74);
  const x = (m: number) => LW + (m / 28) * (w - LW - 12);
</script>
<div class="road" bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="Twelve to twenty-four month plan by workstream with owners and board checkpoints">
    {#each PH as p, i}
      <rect x={x(p.s)} y={top - 4} width={x(p.e) - x(p.s)} height={actions.length * rh + 8} fill={i % 2 ? 'var(--surface)' : 'var(--brand-wash)'} opacity=".7" />
      <text x={x(p.s) + 6} y={top - 10} class="ph">{p.k}</text>
    {/each}
    {#each TICKS as t}<line x1={x(t.m)} x2={x(t.m)} y1={top - 4} y2={top + actions.length * rh + 6} stroke="var(--hair)" /><text x={x(t.m)} y={top + actions.length * rh + 20} text-anchor={t.m === 28 ? 'end' : t.m === 0 ? 'start' : 'middle'} class="ax">{t.k}</text>{/each}
    {#each actions as a, i}
      {@const y0 = top + i * rh}
      {@const by = narrow ? y0 + 18 : y0 + 7}
      {@const ox = x(a.e) + 6}
      {@const fits = ox + a.owner.length * 6.6 < w}
      {#if narrow}
        <text x="0" y={y0 + 12} class="lab"><tspan class="ar">{a.area}</tspan> {a.short}</text>
      {:else}
        <text x="0" y={y0 + 13} class="ar">{a.area}</text>
        <text x="0" y={y0 + 26} class="lab">{a.short}</text>
      {/if}
      {#if a.cont}<line x1={x(a.e) + a.owner.length * 6.6 + 12} x2={x(28)} y1={by + 6} y2={by + 6} stroke={COL[a.area]} stroke-width="1.5" stroke-dasharray="3 3" />{/if}
      <rect x={x(a.s)} y={by} width={Math.max(4, x(a.e) - x(a.s))} height="12" rx="2" fill={COL[a.area]} />
      <text x={fits ? ox : x(a.s) - 6} y={by + 10} text-anchor={fits ? 'start' : 'end'} class="own">{a.owner}</text>
    {/each}
    {#each milestones as ms, i}
      {@const my = top + actions.length * rh + 40 + (i % 2) * 20}
      {@const left = x(ms.m) + 10 + ms.label.length * 6.6 > w}
      <path d={`M${x(ms.m)},${my - 7} l7,7 -7,7 -7,-7z`} fill={i === milestones.length - 1 ? 'var(--target)' : 'var(--ink)'} />
      <text x={x(ms.m) + (left ? -10 : 10)} y={my + 4} text-anchor={left ? 'end' : 'start'} class="ms">{ms.label}</text>
    {/each}
  </svg>
  <div class="key">{#each KEY as [k, c]}<span><i style={`background:${c}`}></i>{k}</span>{/each}<span><i class="d"></i>Board checkpoint</span></div>
</div>
<style>
  .road { width: 100%; }
  svg { display: block; overflow: visible; }
  .ph { font: 600 12px var(--serif); fill: var(--brand); }
  .ax { font: 500 10.5px var(--sans); fill: var(--muted); }
  .ar { font: 600 9.5px var(--sans); letter-spacing: .1em; text-transform: uppercase; fill: var(--muted); }
  .lab { font: 500 12.5px var(--sans); fill: var(--ink); }
  .own { font: 400 10.5px var(--mono); fill: var(--ink-2); }
  .ms { font: 600 11.5px var(--sans); fill: var(--ink); }
  .key { display: flex; flex-wrap: wrap; gap: 4px 14px; margin-top: 10px; font: 400 11.5px var(--sans); color: var(--muted); }
  .key i { display: inline-block; width: 10px; height: 10px; margin-right: 5px; vertical-align: -1px; border-radius: 2px; }
  .key i.d { transform: rotate(45deg) scale(.8); background: var(--ink); border-radius: 0; }
</style>
