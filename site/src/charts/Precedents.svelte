<script lang="ts">
  // Exhibit 8: borrowings / (deposits + borrowings) by years since the merger, ICICI 2002, IDFC First 2018, HDFC 2023 (RBI, domestic).
  import { app } from '../lib/store.svelte';
  type P = { bank: string; period: string; t: number; bor_share: number; casa: number; roa: number };
  const rows = $derived(app.story!.comps.precedents as P[]);
  const S = [['ICICI Bank', 'var(--s2)'], ['IDFC First Bank', 'var(--s3)'], ['HDFC Bank', 'var(--s1)']] as const;
  let W = $state(640);
  const H = 260, L = 40, R = 14, T = 14, Bm = 30;
  const x = $derived((t: number) => L + ((t + 1) / 7) * (Math.max(W, 200) - L - R));
  const y = (v: number) => T + (1 - v / 0.7) * (H - T - Bm);
  const lines = $derived(S.map(([bank, col]) => {
    const pts = rows.filter((r) => r.bank === bank).sort((a, b) => a.t - b.t);
    return { bank, col, pts, d: pts.map((p, i) => `${i ? 'L' : 'M'}${x(p.t).toFixed(1)},${y(p.bor_share).toFixed(1)}`).join(' ') };
  }));
</script>
<div bind:clientWidth={W}>
<svg width={Math.max(W, 200)} height={H} role="img"
     aria-label={lines.map((l) => `${l.bank}: ${l.pts.map((p) => `${p.period} ${(p.bor_share * 100).toFixed(0)}%`).join(', ')}`).join('; ')}>
  {#each [0, 0.2, 0.4, 0.6] as g}
    <line x1={L} x2={Math.max(W, 200) - R} y1={y(g)} y2={y(g)} stroke="var(--hair-2)" />
    <text x={L - 6} y={y(g) + 4} text-anchor="end" class="ax">{(g * 100).toFixed(0)}%</text>
  {/each}
  {#each [-1, 0, 1, 2, 3, 4, 5, 6] as t}<text x={x(t)} y={H - 10} text-anchor="middle" class="ax">{t === 0 ? 'Year 0' : t > 0 ? `+${t}` : t}</text>{/each}
  <line x1={x(0)} x2={x(0)} y1={T} y2={H - Bm} stroke="var(--muted)" stroke-dasharray="2 3" />
  {#each lines as l}
    <path d={l.d} fill="none" stroke={l.col} stroke-width={l.bank === 'HDFC Bank' ? 2.5 : 1.75} />
    {#each l.pts as p}<circle cx={x(p.t)} cy={y(p.bor_share)} r="2.6" fill={l.col} />{/each}
  {/each}
</svg>
</div>
<div class="key">{#each S as [bank, col]}<span><i style={`background:${col}`}></i>{bank}</span>{/each}</div>
<style>
  svg { display: block; }
  .ax { font: 500 11px var(--sans); fill: var(--muted); }
  .key { display: flex; flex-wrap: wrap; gap: 4px 14px; margin-top: 6px; font: 400 12px var(--sans); color: var(--muted); }
  .key i { display: inline-block; width: 14px; height: 3px; margin-right: 6px; vertical-align: 3px; }
</style>
