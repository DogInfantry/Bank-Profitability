<script lang="ts">
  // Two-slot row on the page grid: main (8 of 12 columns) and a right rail (4 of 12) for the visual that supports it.
  // Below 1100 px the rail drops under the main slot.
  import type { Snippet } from 'svelte';
  let { children, rail, mid = false }: { children: Snippet; rail: Snippet; mid?: boolean } = $props();
</script>
<div class="row" class:mid>
  <div class="main">{@render children()}</div>
  <aside class="rail">{@render rail()}</aside>
</div>
<style>
  .row { display: grid; grid-template-columns: minmax(0, 8fr) minmax(0, 4fr); gap: 48px; align-items: start; margin: 4px 0; }
  .row.mid { align-items: center; }
  .rail { padding-top: 6px; }
  .main :global(.exhibit:first-child) { margin-top: 12px; }
  @media (max-width: 1100px) { .row { grid-template-columns: minmax(0, 1fr); gap: 4px; } .rail { padding: 0 0 16px; max-width: 520px; } }
</style>
