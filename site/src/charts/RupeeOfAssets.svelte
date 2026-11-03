<script lang="ts">
  // Chapter 2 rail: what every ₹100 of assets earned and where it went, FY23 (last pre-merger year) vs FY26.
  import { app } from '../lib/store.svelte';
  const h = $derived(Object.fromEntries((app.story!.history as any[]).map((r) => [r.fy, r])));
  const YRS = ['FY23', 'FY26'];
  const IN = [['nii', 'Margin', 'var(--s1)'], ['oi', 'Other income', 'var(--seq-2)']] as const;
  const OUT = [['opex', 'Cost', 'var(--context)'], ['prov', 'Provisions', 'var(--context-2)'], ['tax', 'Tax', 'var(--hair)'], ['roa', 'Profit', 'var(--ink)']] as const;
  const W = 320, max = 5.6;
  const sx = (v: number) => (v / max) * W;
  const segs = (r: any, keys: readonly (readonly [string, string, string])[]) => {
    let x = 0;
    return keys.map(([k, lab, c]) => { const v = r[k] * 100; const o = { k, lab, c, v, x: sx(x), w: sx(v) }; x += v; return o; });
  };
</script>
<figure class="roa-rupee">
  <p class="rh">What ₹100 of assets earned, and where it went</p>
  {#each YRS as fy, yi}
    {@const r = h[fy]}
    <p class="yr"><b>{fy}</b>{yi === 0 ? ' · before the merger' : ' · after'}</p>
    <svg viewBox={`0 0 ${W} 50`} width="100%" role="img" aria-label={`${fy}: earned ₹${((r.nii + r.oi) * 100).toFixed(2)} (margin ₹${(r.nii * 100).toFixed(2)}); profit ₹${(r.roa * 100).toFixed(2)}`}>
      {#each segs(r, IN) as g}
        <rect x={g.x} y="0" width={Math.max(0, g.w - 1)} height="20" fill={g.c} />
        {#if g.w > 42}<text x={g.x + 5} y="14" class="in" style={g.k === 'nii' ? 'fill: var(--paper)' : ''}>₹{g.v.toFixed(2)}</text>{/if}
      {/each}
      {#each segs(r, OUT) as g}
        <rect x={g.x} y="25" width={Math.max(0, g.w - 1)} height="20" fill={g.c} />
        {#if g.w > 42}<text x={g.x + 5} y="39" class="in" style={g.k === 'roa' ? 'fill: var(--paper)' : ''}>₹{g.v.toFixed(2)}</text>{/if}
      {/each}
    </svg>
  {/each}
  <div class="key">
    {#each [...IN, ...OUT] as [, lab, c]}<span><i style={`background:${c}`}></i>{lab}</span>{/each}
  </div>
  <p class="cap">Top bar: income. Bottom bar: the same income split into cost, provisions, tax and the profit kept (RoA). Margin shrank by ₹{((h.FY23.nii - h.FY26.nii) * 100).toFixed(2)}; lower cost paid back ₹{((h.FY23.opex - h.FY26.opex) * 100).toFixed(2)}.</p>
</figure>
<style>
  .roa-rupee { margin: 0; border-top: 2px solid var(--ink); padding-top: 10px; }
  .rh { font: 600 14px/1.3 var(--sans); color: var(--ink); margin: 0 0 8px; }
  .yr { font: 400 12px var(--sans); color: var(--muted); margin: 8px 0 4px; } .yr b { color: var(--ink); font-weight: 600; }
  svg { display: block; }
  .in { font: 500 10.5px var(--mono); fill: var(--ink); }
  .key { display: flex; flex-wrap: wrap; gap: 4px 12px; margin-top: 8px; font: 400 11.5px var(--sans); color: var(--muted); }
  .key i { display: inline-block; width: 9px; height: 9px; margin-right: 5px; vertical-align: -1px; border: 1px solid var(--hair); }
  .cap { font: 400 12.5px/1.45 var(--sans); color: var(--ink-2); margin: 8px 0 0; }
</style>
