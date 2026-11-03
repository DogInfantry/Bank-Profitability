<script lang="ts">
  // Mount an Observable Plot figure; re-render on width or theme change.
  import { onMount } from 'svelte';
  let { make }: { make: (width: number) => Element } = $props();
  let el: HTMLDivElement; let w = $state(500);
  $effect(() => { const fig = make(w); el.replaceChildren(fig); });
  onMount(() => { const mo = new MutationObserver(() => el.replaceChildren(make(w))); mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] }); return () => mo.disconnect(); });
</script>
<div bind:this={el} bind:clientWidth={w} class="plotfig"></div>
<style>.plotfig :global(svg) { max-width: 100%; height: auto; font-family: var(--sans); }</style>
