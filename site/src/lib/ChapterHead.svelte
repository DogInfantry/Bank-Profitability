<script lang="ts">
  let { n, kicker, title }: { n: string; kicker: string; title: string } = $props();
</script>
<header class="ch-head">
  <p class="ch-k"><span class="ch-n">{n}</span>{kicker}</p>
  <h2>{title}</h2>
</header>
<style>
  .ch-head { margin: 0 0 22px; }
  .ch-k { font: 600 11.5px var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin: 0 0 10px; display: flex; gap: 12px; align-items: baseline; }
  .ch-n { color: var(--brand); font-family: var(--mono); letter-spacing: 0; }
  h2 { font-size: clamp(30px, 3.6vw, 42px); line-height: 1.12; letter-spacing: -0.012em; }
</style>
