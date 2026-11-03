<script lang="ts">
  // Chapter 4 rail: how the liability side changes. 100% columns, FY23A (pre-merger), FY26A, FY29E base case.
  import { app } from '../lib/store.svelte';
  const fm = $derived(app.story!.funding_mix as { fy: string; dep: number; bor: number; eq: number; ol: number }[]);
  const K = [['bor', 'Borrowings', 'var(--s2)'], ['dep', 'Deposits', 'var(--s1)'], ['eq', 'Net worth', 'var(--context)'], ['ol', 'Other', 'var(--context-2)']] as const;
  const W = 320, H = 182, top = 24, base = 162, cw = 64;
  const cx = (i: number) => 18 + i * ((W - 36 - cw) / 2);
  const cols = $derived(fm.map((r) => {
    const tot = r.dep + r.bor + r.eq + r.ol; let y = top;
    return { fy: r.fy, segs: K.map(([k, lab, c]) => { const sh = (r as any)[k] / tot; const h = sh * (base - top); const o = { k, lab, c, sh, y, h }; y += h; return o; }) };
  }));
</script>
<figure class="fmix">
  <p class="rh">Borrowings shrink as a share of the balance sheet</p>
  <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label={`Share of liabilities and equity: ${cols.map((c) => `${c.fy} borrowings ${(c.segs[0].sh * 100).toFixed(1)}%, deposits ${(c.segs[1].sh * 100).toFixed(1)}%`).join('; ')}`}>
    {#each cols as c, i}
      {#each c.segs as g}
        <rect x={cx(i)} y={g.y} width={cw} height={Math.max(0, g.h - 1)} fill={g.c} />
        {#if g.k === 'bor'}<text x={cx(i) + cw / 2} y={top - 7} text-anchor="middle" class="in bor">{(g.sh * 100).toFixed(1)}%</text>{:else if g.k === 'dep'}<text x={cx(i) + cw / 2} y={g.y + 16} text-anchor="middle" class="in light">{(g.sh * 100).toFixed(0)}%</text>{/if}
      {/each}
      <text x={cx(i) + cw / 2} y={base + 16} text-anchor="middle" class="ax">{c.fy}</text>
      {#if i < cols.length - 1}<path d={`M${cx(i) + cw},${c.segs[0].y + c.segs[0].h} L${cx(i + 1)},${cols[i + 1].segs[0].y + cols[i + 1].segs[0].h}`} stroke="var(--s2)" stroke-width="1" stroke-dasharray="2 2" fill="none" />{/if}
    {/each}
  </svg>
  <div class="key">{#each K as [, lab, c]}<span><i style={`background:${c}`}></i>{lab}</span>{/each}</div>
  <p class="cap">Share of total liabilities and net worth, closing balance sheet. FY23A is the last pre-merger year; FY29E is the base case.</p>
</figure>
<style>
  .fmix { margin: 0; border-top: 2px solid var(--ink); padding-top: 10px; }
  .rh { font: 600 14px/1.3 var(--sans); color: var(--ink); margin: 0 0 8px; }
  svg { display: block; }
  .in { font: 600 11px var(--mono); fill: var(--ink); } .in.light { fill: var(--paper); } .in.bor { fill: var(--s2); }
  .ax { font: 500 11px var(--sans); fill: var(--muted); }
  .key { display: flex; flex-wrap: wrap; gap: 4px 12px; margin-top: 6px; font: 400 11.5px var(--sans); color: var(--muted); }
  .key i { display: inline-block; width: 9px; height: 9px; margin-right: 5px; vertical-align: -1px; }
  .cap { font: 400 12.5px/1.45 var(--sans); color: var(--ink-2); margin: 8px 0 0; }
</style>
