<script lang="ts">
  // Stat tile: label, one large tabular number, a short qualifier, and an optional micro-chart.
  import type { Snippet } from 'svelte';
  let { label, value, sub = '', tone = 'ink', children }: { label: string; value: string; sub?: string; tone?: 'ink' | 'brand' | 'adverse'; children?: Snippet } = $props();
</script>
<div class="stat">
  <p class="sl">{label}</p>
  <p class="sv num" class:brand={tone === 'brand'} class:adverse={tone === 'adverse'}>{value}</p>
  {#if sub}<p class="ss">{sub}</p>{/if}
  {#if children}<div class="sm">{@render children()}</div>{/if}
</div>
<style>
  .stat { border-top: 1px solid var(--ink); padding: 8px 0 10px; }
  .sl { font: 600 11px var(--sans); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 0; }
  .sv { font: 500 30px/1.15 var(--mono); color: var(--ink); margin: 4px 0 0; letter-spacing: -0.02em; }
  .sv.brand { color: var(--brand); } .sv.adverse { color: var(--adverse); }
  .ss { font: 400 13px/1.4 var(--sans); color: var(--ink-2); margin: 2px 0 0; }
  .sm { margin-top: 8px; }
</style>
