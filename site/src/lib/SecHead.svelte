<script lang="ts">
  import type { Snippet } from 'svelte';
  let { idx, kicker, title, children }: { idx: string; kicker: string; title: string; children?: Snippet } = $props();
</script>
<div class="sec-head">
  <span class="idx">{idx}</span>
  <div>
    <p class="label">{kicker}</p>
    <h2>{title}</h2>
  </div>
  {#if children}<div class="lede prose">{@render children()}</div>{/if}
</div>
