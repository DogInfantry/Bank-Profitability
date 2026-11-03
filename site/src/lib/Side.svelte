<script lang="ts">
  // Tufte sidenote: in the right margin on wide screens, inline and indented on narrow ones.
  import type { Snippet } from 'svelte';
  let { children }: { children: Snippet } = $props();
</script>
<aside class="side">{@render children()}</aside>
<style>
  .side { font: 400 13px/1.5 var(--sans); color: var(--muted); border-left: 2px solid var(--hair); padding-left: 10px; margin: 6px 0 14px; }
  @media (min-width: 1200px) { .side { float: right; clear: right; width: 230px; margin-right: -270px; margin-top: 4px; } }
</style>
