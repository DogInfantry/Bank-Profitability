<script lang="ts">
  // Twelve listed banks on FY26 RoA, collision-resolved with d3-force; circle area = average assets.
  import * as d3 from 'd3';
  import { app } from '../lib/store.svelte';
  import { showTip, hideTip } from '../lib/tooltip';
  let w = $state(560);
  const H = 210, m = { l: 20, r: 20 };
  const PSU = ['State Bank of India', 'Bank of Baroda', 'Punjab National Bank', 'Canara Bank'];
  const peers = $derived(app.story!.peers as any[]);
  const x = $derived(d3.scaleLinear().domain([0, 0.024]).range([m.l, w - m.r]));
  const r = $derived(d3.scaleSqrt().domain([0, d3.max(peers, (p) => p.avg_assets) as number]).range([4, 26]));
  const nodes = $derived.by(() => {
    const ns = peers.map((p) => ({ ...p, x: x(p.roa), y: H / 2 - 10, rr: r(p.avg_assets) }));
    const sim = d3.forceSimulation(ns as any).force('x', d3.forceX((d: any) => x(d.roa)).strength(1)).force('y', d3.forceY(H / 2 - 10).strength(0.08))
      .force('c', d3.forceCollide((d: any) => d.rr + 1.5)).stop();
    for (let i = 0; i < 200; i++) sim.tick();
    return ns;
  });
  const fill = (p: any) => (p.bank === 'HDFC Bank' ? 'var(--s1)' : PSU.includes(p.bank) ? 'var(--context-2)' : 'var(--context)');
</script>
<div bind:clientWidth={w}>
  <svg width={w} height={H} role="img" aria-label="Peer banks by FY26 RoA">
    <line x1={x(0.02)} x2={x(0.02)} y1="6" y2={H - 28} stroke="var(--target)" stroke-dasharray="3 3" />
    <text x={x(0.02) + 4} y="14" style="fill: var(--target); font-size: 11px; font-weight: 600">2.00%</text>
    {#each [0, 0.005, 0.01, 0.015, 0.02] as t}<text x={x(t)} y={H - 8} text-anchor="middle" class="num-t">{(t * 100).toFixed(1)}%</text>{/each}
    {#each nodes as n (n.bank)}
      <circle cx={n.x} cy={n.y} r={n.rr} fill={fill(n)} stroke="var(--surface)" stroke-width="2"
              role="presentation" onmousemove={(e) => showTip(e, `<b>${n.bank}</b><br>RoA ${(n.roa * 100).toFixed(2)}% · RoE ${(n.roe * 100).toFixed(1)}%<br>P/B ${n.pb.toFixed(2)}x · ${PSU.includes(n.bank) ? 'public sector' : 'private'}`)} onmouseleave={hideTip} />
      {#if n.bank === 'HDFC Bank' || n.bank === 'ICICI Bank' || n.bank === 'Kotak Mahindra Bank'}
        <text x={n.x} y={n.y - n.rr - 5} text-anchor="middle" style="fill: var(--ink); font-size: 11px; font-weight: 500">{n.bank.replace(' Mahindra Bank', '').replace('State Bank of India', 'SBI')}</text>
      {/if}
    {/each}
  </svg>
</div>
