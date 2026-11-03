<script lang="ts">
  // On-chart annotation: a dot at the data point, a leader line, and up to three short lines of text.
  let { x, y, dx = 30, dy = -30, lines, anchor = 'start', tone = 'ink', dot = true }:
    { x: number; y: number; dx?: number; dy?: number; lines: string[]; anchor?: 'start' | 'end' | 'middle'; tone?: 'ink' | 'brand' | 'target'; dot?: boolean } = $props();
  const col = $derived(tone === 'brand' ? 'var(--brand)' : tone === 'target' ? 'var(--target)' : 'var(--ink)');
</script>
<g class="note" aria-hidden="true">
  {#if dot}<circle cx={x} cy={y} r="3" fill="var(--paper)" stroke={col} stroke-width="1.5" />{/if}
  <path d={`M${x},${y} L${x + dx},${y + dy}`} stroke={col} stroke-width="0.9" fill="none" />
  {#each lines as l, i}
    <text x={x + dx + (anchor === 'start' ? 4 : anchor === 'end' ? -4 : 0)} y={y + dy + (dy < 0 ? -4 - (lines.length - 1 - i) * 14 : 12 + i * 14)} text-anchor={anchor}
          style={`fill: ${i === 0 ? col : 'var(--ink-2)'}; font-size: 12px; font-weight: ${i === 0 ? 600 : 400}`}>{l}</text>
  {/each}
</g>
