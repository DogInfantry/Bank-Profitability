<script lang="ts">
  import { onMount } from 'svelte';
  import { app, load } from './lib/store.svelte';
  import Icon from './lib/Icon.svelte';
  import Palette from './lib/Palette.svelte';
  import Brief from './sections/Brief.svelte';
  import Diagnosis from './sections/Diagnosis.svelte';
  import MetricTree from './sections/MetricTree.svelte';
  import Workbench from './sections/Workbench.svelte';
  import Bets from './sections/Bets.svelte';
  import Evidence from './sections/Evidence.svelte';
  import Risks from './sections/Risks.svelte';
  import Roadmap from './sections/Roadmap.svelte';
  import Changelog from './sections/Changelog.svelte';

  const REPO = 'https://github.com/DogInfantry/Bank-Profitability';
  const BR = `${REPO}/blob/claude/wonderful-noether-vgfm7p`;
  const SECTIONS = [
    ['brief', '01', 'The answer'], ['diagnosis', '02', 'Diagnosis'], ['tree', '03', 'Metric tree'], ['workbench', '04', 'Workbench'],
    ['bets', '05', 'Bets'], ['evidence', '06', 'Evidence'], ['risks', '07', 'Risks'], ['roadmap', '08', 'Roadmap'], ['log', '09', 'Changelog and method'],
  ] as const;
  let active = $state('brief');
  let paletteOpen = $state(false);

  function applyTheme() {
    const r = document.documentElement;
    if (app.theme === 'auto') r.removeAttribute('data-theme'); else r.dataset.theme = app.theme;
  }
  function toggleTheme() {
    const dark = app.theme === 'dark' || (app.theme === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
    app.theme = dark ? 'light' : 'dark'; applyTheme();
    try { localStorage.setItem('theme', app.theme); } catch { /* storage may be blocked */ }
  }
  onMount(() => {
    try { const t = localStorage.getItem('theme'); if (t === 'light' || t === 'dark') { app.theme = t; applyTheme(); } } catch { /* ignore */ }
    load();
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) active = e.target.id; }), { rootMargin: '-45% 0px -50% 0px' });
    const t = setInterval(() => { const els = document.querySelectorAll('section.block'); if (els.length) { els.forEach((s) => io.observe(s)); clearInterval(t); } }, 200);
    const key = (e: KeyboardEvent) => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); paletteOpen = !paletteOpen; } };
    window.addEventListener('keydown', key);
    const onHash = () => { if (location.hash.startsWith('#w=')) app.readHash(); };
    window.addEventListener('hashchange', onHash);
    return () => { window.removeEventListener('keydown', key); window.removeEventListener('hashchange', onHash); io.disconnect(); };
  });
  const s = $derived(app.story);
</script>

<div class="status" role="banner">
  <div class="wrap status-in">
    <span class="mono"><Icon name="versions" /> v1.0</span>
    {#if s?.checks?.total}
      <span class="mono ok"><Icon name="check" /> {s.checks.total - s.checks.fail}/{s.checks.total}<span class="hide-s"> model checks pass</span></span>
    {/if}
    {#if s}<a class="mono hide-s" href={`${REPO}/blob/claude/wonderful-noether-vgfm7p/models/HDFC_RoA_Path_FY29.xlsx`}><Icon name="commit" /> model {s.model_sha}</a>{/if}
    <span class="mono hide-s">data as of 3 Nov 2026</span>
    <span class="spacer"></span>
    <button class="kbd" onclick={() => (paletteOpen = true)} aria-label="Open command palette"><Icon name="palette" /> <span class="hide-s">Jump to</span> <kbd>⌘K</kbd></button>
    <button class="kbd" onclick={toggleTheme} aria-label="Toggle light and dark theme"><Icon name="sun" /></button>
  </div>
</div>

<header class="wrap mast">
  <p class="label">An outside-in case · FY27 to FY29 · built as a model you can operate</p>
  <h1>The 2% Question</h1>
  <p class="deck-line">What restores HDFC Bank's return on assets to 2% by FY29, what each move is worth, and what the share price already assumes.</p>
  <p class="disclaimer">Independent outside-in case study using public data only; not commissioned by, or affiliated with, HDFC Bank or Bain &amp; Company. Brand colours are used for orientation only.</p>
</header>

<div class="layout wrap">
  <nav class="rail" aria-label="Sections">
    {#each SECTIONS as [id, n, name]}
      <a href={`#${id}`} class:on={active === id}><span class="mono">{n}</span> {name}</a>
    {/each}
    <div class="rail-foot">
      <a href={`${REPO}`}><Icon name="external" /> Repository</a>
      <a href={`${BR}/models/HDFC_RoA_Path_FY29.xlsx`}><Icon name="download" /> Excel model</a>
      <a href={`${BR}/decks/pdf/HDFC_CEO_Memo.pdf`}><Icon name="download" /> CEO memo</a>
    </div>
  </nav>
  <main>
    {#if app.story && app.model && app.result}
      <Brief />
      <Diagnosis />
      <MetricTree />
      <Workbench />
      <Bets />
      <Evidence />
      <Risks />
      <Roadmap />
      <Changelog />
    {:else}
      <p class="loading mono">Loading the model…</p>
    {/if}
  </main>
</div>

<footer class="wrap foot">
  <p>Prepared by Anklesh. Every number on this page is computed from <a href={REPO}>the repository's</a> recalculated Excel model or its cited inputs; the browser model is tested against the workbook to within 0.1 bp. Icons: GitHub Primer Octicons (MIT).</p>
</footer>

<Palette bind:open={paletteOpen} sections={SECTIONS} {toggleTheme} />

<style>
  .status { position: sticky; top: 0; z-index: 20; background: var(--paper); border-bottom: 1px solid var(--hair); }
  .status-in { display: flex; align-items: center; gap: 18px; height: 40px; font-size: 12px; color: var(--muted); }
  .status a { color: var(--muted); text-decoration: none; }
  .status a:hover { color: var(--brand); }
  .status .ok { color: var(--good); }
  .spacer { flex: 1; }
  .kbd { display: inline-flex; align-items: center; gap: 6px; background: none; border: 1px solid var(--hair); border-radius: 4px; padding: 3px 8px; cursor: pointer; color: var(--ink-2); font-size: 12px; }
  kbd { font: 500 11px var(--mono); color: var(--muted); }
  .mast { padding-top: 56px; padding-bottom: 28px; }
  h1 { font-size: clamp(48px, 8vw, 96px); line-height: .98; font-weight: 500; letter-spacing: -0.02em; margin: 14px 0 18px; }
  .deck-line { font-family: var(--serif); font-size: clamp(20px, 2.2vw, 26px); line-height: 1.35; color: var(--ink-2); max-width: 30em; }
  .disclaimer { font-size: 12.5px; color: var(--muted); border-left: 2px solid var(--hair); padding-left: 10px; max-width: 70ch; margin-top: 18px; }
  .layout { display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: 40px; }
  .rail { position: sticky; top: 64px; align-self: start; display: flex; flex-direction: column; gap: 2px; padding-top: 72px; font-size: 13px; }
  .rail a { color: var(--muted); text-decoration: none; padding: 5px 8px; border-left: 2px solid transparent; }
  .rail a .mono { font-size: 11px; margin-right: 6px; }
  .rail a.on { color: var(--ink); border-left-color: var(--brand); }
  .rail a:hover { color: var(--brand); }
  .rail-foot { margin-top: 22px; padding-top: 14px; border-top: 1px solid var(--hair); display: flex; flex-direction: column; gap: 2px; }
  main { min-width: 0; }
  .loading { padding: 80px 0; color: var(--muted); }
  .foot { padding: 40px 24px 60px; font-size: 12.5px; color: var(--muted); border-top: 1px solid var(--hair); margin-top: 40px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } .rail { display: none; } .hide-s { display: none; } .status-in { gap: 10px; } }
</style>
