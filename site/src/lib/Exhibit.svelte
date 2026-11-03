<script lang="ts">
  // Consulting-style exhibit frame: number, assertion title, units/period, the chart, source line, data toggle.
  import type { Snippet } from 'svelte';
  let { n, title, units, source, wide = false, children, table }: { n: number | string; title: string; units: string; source: string; wide?: boolean; children: Snippet; table?: Snippet } = $props();
  let open = $state(false);
</script>
<figure class="exhibit" class:wide id={`exhibit-${n}`}>
  <figcaption>
    <span class="ex-n">Exhibit {n}</span>
    <span class="ex-t">{title}</span>
    <span class="ex-u">{units}</span>
  </figcaption>
  <div class="ex-body">{@render children()}</div>
  <div class="ex-foot">
    <span class="ex-src">Source: {source}</span>
    {#if table}<button class="ex-btn" aria-expanded={open} onclick={() => (open = !open)}>{open ? 'Hide data' : 'Data'}</button>{/if}
  </div>
  {#if table && open}<div class="ex-table tbl-scroll">{@render table()}</div>{/if}
</figure>
<style>
  .exhibit { margin: 36px 0; padding: 0; max-width: var(--main); }
  .exhibit.wide, :global(.pair) .exhibit, :global(.row) .exhibit { max-width: none; }
  figcaption { display: flex; flex-direction: column; gap: 2px; border-top: 2px solid var(--ink); padding-top: 10px; margin-bottom: 14px; }
  .ex-n { font: 600 11px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--brand); }
  .ex-t { font: 600 19px/1.3 var(--sans); color: var(--ink); letter-spacing: -0.005em; margin-top: 6px; }
  .ex-u { font: 400 13px var(--sans); color: var(--muted); }
  .ex-foot { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; border-top: 1px solid var(--hair); margin-top: 10px; padding-top: 8px; }
  .ex-src { font: 400 11.5px/1.45 var(--sans); color: var(--muted); }
  .ex-btn { flex: none; font: 500 11.5px var(--mono); color: var(--brand); background: none; border: 1px solid var(--hair); border-radius: 3px; padding: 2px 8px; cursor: pointer; }
  .ex-table { margin-top: 10px; }
</style>
