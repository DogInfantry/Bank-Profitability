<script lang="ts">
  // Neutral bank emblem (pediment, four columns, base). Deliberately not any bank's trademark.
  let { size = 36, title = '' }: { size?: number; title?: string } = $props();
</script>
<svg width={size} height={size} viewBox="0 0 40 40" role={title ? 'img' : undefined} aria-label={title || undefined} aria-hidden={title ? undefined : 'true'} class="glyph">
  <path d="M20 3 L37 12 L3 12 Z" fill="var(--brand)" />
  <rect x="3" y="13.5" width="34" height="2.2" fill="var(--brand)" />
  {#each [6.5, 14.5, 22.5, 30.5] as x}<rect x={x} y="17.5" width="3" height="13" rx="0.6" fill="var(--brand)" />{/each}
  <rect x="4" y="32.2" width="32" height="2" fill="var(--brand)" />
  <rect x="2" y="35.4" width="36" height="2.4" fill="var(--brand)" />
  <circle cx="20" cy="8.6" r="1.6" fill="var(--paper)" />
</svg>
<style>.glyph { display: block; flex: none; }</style>
