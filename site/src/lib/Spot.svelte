<script lang="ts" module>
  // Spot illustrations in the bank-emblem line style: 1.5 px strokes in the brand colour, no fills beyond small accents.
  export type SpotName = 'vault' | 'ladder' | 'steps' | 'scales' | 'gears' | 'receipt' | 'qr' | 'coins' | 'shield' | 'eye' | 'stop' | 'flow';
</script>
<script lang="ts">
  let { name, size = 44 }: { name: SpotName; size?: number } = $props();
  const teeth = Array.from({ length: 8 }, (_, i) => { const a = (i * Math.PI) / 4; return `M${24 + 9 * Math.cos(a)},${24 + 9 * Math.sin(a)} L${24 + 13 * Math.cos(a)},${24 + 13 * Math.sin(a)}`; }).join(' ');
</script>
<svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true" class="spot" fill="none" stroke="var(--brand)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  {#if name === 'vault'}
    <rect x="7" y="9" width="34" height="28" rx="2" /><circle cx="24" cy="23" r="8" /><circle cx="24" cy="23" r="2" fill="var(--brand)" />
    <path d="M24 15v3M24 28v3M16 23h3M29 23h3M11 37v3M37 37v3" />
  {:else if name === 'ladder'}
    <path d="M15 6v36M31 6v36M15 12h16M15 20h16M15 28h16M15 36h16" /><path d="M39 14v18m-4-4 4 4 4-4" />
  {:else if name === 'steps'}
    <path d="M6 40h8v-7h8v-7h8v-7h8v-7h4" /><path d="M6 40h36" stroke="var(--hair)" /><path d="M34 6h8v8" /><path d="M42 6 30 18" />
  {:else if name === 'scales'}
    <path d="M24 8v32M16 40h16M9 14h30M24 10l0 4" /><path d="M9 14 4 26h10zM39 14l-5 12h10z" /><path d="M4 26a5 4 0 0 0 10 0M34 26a5 4 0 0 0 10 0" />
  {:else if name === 'gears'}
    <circle cx="24" cy="24" r="9" /><circle cx="24" cy="24" r="3" /><path d={teeth} />
  {:else if name === 'receipt'}
    <path d="M12 5h24v37l-4-3-4 3-4-3-4 3-4-3-4 3z" /><path d="M17 13h14M17 19h14M17 25h8" /><path d="M27 31h4" stroke-width="2.2" />
  {:else if name === 'qr'}
    <rect x="7" y="7" width="12" height="12" /><rect x="29" y="7" width="12" height="12" /><rect x="7" y="29" width="12" height="12" />
    <rect x="11" y="11" width="4" height="4" fill="var(--brand)" /><rect x="33" y="11" width="4" height="4" fill="var(--brand)" /><rect x="11" y="33" width="4" height="4" fill="var(--brand)" />
    <path d="M29 29h4v4h-4zM37 33h4v8h-4M29 37h4v4" />
  {:else if name === 'coins'}
    <ellipse cx="24" cy="12" rx="13" ry="4.5" /><path d="M11 12v24c0 2.5 5.8 4.5 13 4.5s13-2 13-4.5V12" /><path d="M11 20c0 2.5 5.8 4.5 13 4.5s13-2 13-4.5M11 28c0 2.5 5.8 4.5 13 4.5s13-2 13-4.5" />
  {:else if name === 'shield'}
    <path d="M24 5 39 10v12c0 9.5-6.5 16-15 20C15.5 38 9 31.5 9 22V10z" /><path d="m17 23 5 5 9-10" />
  {:else if name === 'eye'}
    <path d="M4 24s7-12 20-12 20 12 20 12-7 12-20 12S4 24 4 24z" /><circle cx="24" cy="24" r="5" />
  {:else if name === 'stop'}
    <path d="M17 5h14l12 12v14L31 43H17L5 31V17z" /><path d="M17 24h14" stroke-width="2.4" />
  {:else if name === 'flow'}
    <rect x="5" y="6" width="14" height="10" rx="1.5" /><rect x="29" y="19" width="14" height="10" rx="1.5" /><rect x="5" y="32" width="14" height="10" rx="1.5" />
    <path d="M19 11h6v13h4M19 37h6V24" />
  {/if}
</svg>
<style>.spot { display: block; flex: none; }</style>
