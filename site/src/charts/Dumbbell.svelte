<script lang="ts">
  // Exhibit 9: for each lever with a peer benchmark, HDFC today -> where the lever takes it -> the named benchmark.
  import { app } from '../lib/store.svelte';
  let w = $state(900);
  const anchors = $derived(app.story!.anchors as any[]);
  const rows = $derived(anchors.map((a) => {
    const borrow = a.lever.startsWith('Retire');
    const fmt = (v: number) => `${(v * 100).toFixed(a.lever.startsWith('Re-mix') ? 2 : 1)}%`;
    const reach = borrow ? a.hdfc - (a.hdfc - a.bench) * a.share : a.hdfc + (a.bench - a.hdfc) * a.share;
    return { name: a.lever.split(' (')[0], metric: a.lever.split('(')[1]?.replace(')', ''), hdfc: a.hdfc, bench: a.bench, reach, share: a.share, src: a.source.split(',')[0].split('(')[0].replace(/ (Q2|FY26|Mar|Sep).*$/, '').trim(), fmt };
  }));
  const sw = $derived(w < 620 ? w : w - 230);
  const sc = (r: any, v: number) => { const lo = Math.min(r.hdfc, r.bench), hi = Math.max(r.hdfc, r.bench), pad = (hi - lo) * 0.22; return 40 + ((v - (lo - pad)) / (hi - lo + 2 * pad)) * (sw - 80); };
</script>
<div bind:clientWidth={w}>
  <div class="legend"><span><i class="d hd"></i>HDFC Bank today</span><span><i class="d rc"></i>Where the move takes it</span><span><i class="d bm"></i>Named benchmark</span></div>
  {#each rows as r}
    <div class="row" class:stack={w < 620}>
      <div class="lab"><b>{r.name}</b><span>{r.metric}</span></div>
      <svg width={sw} height="56" role="img" aria-label={`${r.name}: HDFC ${r.fmt(r.hdfc)}, benchmark ${r.fmt(r.bench)}`}>
        <line x1={sc(r, r.hdfc)} x2={sc(r, r.bench)} y1="26" y2="26" stroke="var(--context-2)" stroke-width="6" stroke-linecap="round" />
        <line x1={sc(r, r.hdfc)} x2={sc(r, r.reach)} y1="26" y2="26" stroke="var(--s1)" stroke-width="6" stroke-linecap="round" />
        <circle cx={sc(r, r.hdfc)} cy="26" r="7" fill="var(--ink)" />
        <circle cx={sc(r, r.reach)} cy="26" r="6" fill="var(--paper)" stroke="var(--s1)" stroke-width="2.5" />
        <circle cx={sc(r, r.bench)} cy="26" r="7" fill="var(--s3)" />
        <text x={sc(r, r.hdfc)} y="50" text-anchor="middle" class="num-t" style="fill: var(--ink); font-size: 11.5px">{r.fmt(r.hdfc)}</text>
        <text x={sc(r, r.bench)} y="50" text-anchor="middle" class="num-t" style="fill: var(--ink); font-size: 11.5px">{r.fmt(r.bench)} · {r.src}</text>
        <text x={(sc(r, r.hdfc) + sc(r, r.reach)) / 2} y="13" text-anchor="middle" style="fill: var(--brand); font-size: 11.5px; font-weight: 600">closes {(r.share * 100).toFixed(0)}% of the gap</text>
      </svg>
    </div>
  {/each}
</div>
<style>
  .legend { display: flex; gap: 18px; flex-wrap: wrap; font-size: 12px; color: var(--ink-2); margin-bottom: 6px; }
  .d { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; vertical-align: -1px; }
  .d.hd { background: var(--ink); } .d.rc { border: 2.5px solid var(--s1); width: 6px; height: 6px; } .d.bm { background: var(--s3); }
  .row { display: grid; grid-template-columns: 230px 1fr; align-items: center; border-top: 1px solid var(--hair-2); }
  .row.stack { grid-template-columns: 1fr; padding-top: 6px; }
  .lab { display: flex; flex-direction: column; font-size: 13.5px; color: var(--ink); } .lab span { font-size: 12px; color: var(--muted); }
  .row svg { overflow: visible; }
</style>
