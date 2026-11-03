<script lang="ts">
  // Tufte-style sparkline: history solid, projection dashed, last point marked, optional target rule.
  import * as d3 from 'd3';
  let { values, split = 6, target = null, w = 140, h = 34 }: { values: (number | null)[]; split?: number; target?: number | null; w?: number; h?: number } = $props();
  const pts = $derived(values.map((v, i) => [i, v] as [number, number | null]).filter((p) => p[1] != null) as [number, number][]);
  const x = $derived(d3.scaleLinear().domain([0, values.length - 1]).range([2, w - 4]));
  const y = $derived.by(() => { const ex = d3.extent([...pts.map((p) => p[1]), ...(target != null ? [target] : [])]) as [number, number]; return d3.scaleLinear().domain(ex).nice().range([h - 3, 3]); });
  const line = $derived(d3.line<[number, number]>().x((p) => x(p[0])).y((p) => y(p[1])));
  const hist = $derived(line(pts.filter((p) => p[0] <= split)) ?? '');
  const proj = $derived(line(pts.filter((p) => p[0] >= split)) ?? '');
  const last = $derived(pts[pts.length - 1]);
</script>
<svg width={w} height={h} aria-hidden="true">
  {#if target != null}<line x1="0" x2={w} y1={y(target)} y2={y(target)} stroke="var(--target)" stroke-dasharray="2 3" stroke-width="1" />{/if}
  <path d={hist} fill="none" stroke="var(--s1)" stroke-width="1.6" />
  <path d={proj} fill="none" stroke="var(--s1)" stroke-width="1.6" stroke-dasharray="3 2" />
  {#if last}<circle cx={x(last[0])} cy={y(last[1])} r="2.6" fill="var(--s1)" />{/if}
</svg>
