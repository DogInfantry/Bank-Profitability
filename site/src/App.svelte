<script lang="ts">
  import { onMount } from 'svelte';
  import { app, load } from './lib/store.svelte';
  import Icon from './lib/Icon.svelte';
  import BankGlyph from './lib/BankGlyph.svelte';
  import Palette from './lib/Palette.svelte';
  import AtAGlance from './charts/AtAGlance.svelte';
  import ChAnswer from './chapters/ChAnswer.svelte';
  import ChMerger from './chapters/ChMerger.svelte';
  import ChPeers from './chapters/ChPeers.svelte';
  import ChRunoff from './chapters/ChRunoff.svelte';
  import ChMoves from './chapters/ChMoves.svelte';
  import ChValue from './chapters/ChValue.svelte';
  import ChRisks from './chapters/ChRisks.svelte';
  import ChPlan from './chapters/ChPlan.svelte';
  import Appendix from './chapters/Appendix.svelte';
  import Changelog from './sections/Changelog.svelte';

  const REPO = 'https://github.com/DogInfantry/Bank-Profitability';
  const BR = `${REPO}/blob/claude/wonderful-noether-vgfm7p`;
  const SECTIONS = [
    ['answer', '01', 'The answer'], ['merger', '02', 'The merger broke the margin'], ['peers', '03', 'Against ICICI Bank'], ['runoff', '04', 'The base case'],
    ['moves', '05', 'The six moves'], ['value', '06', 'What it is worth'], ['risks', '07', 'What could break it'], ['plan', '08', 'Next twelve months'],
    ['workbench-a', 'A', 'Test the answer'], ['log', 'B', 'Method and sources'],
  ] as const;
  let paletteOpen = $state(false);
  let progress = $state(0);
  let active = $state('');
  function applyTheme() { const r = document.documentElement; if (app.theme === 'auto') r.removeAttribute('data-theme'); else r.dataset.theme = app.theme; }
  function toggleTheme() {
    const dark = app.theme === 'dark' || (app.theme === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
    app.theme = dark ? 'light' : 'dark'; applyTheme();
    try { localStorage.setItem('theme', app.theme); } catch { /* storage may be blocked */ }
  }
  onMount(() => {
    try { const t = localStorage.getItem('theme'); if (t === 'light' || t === 'dark') { app.theme = t; applyTheme(); } } catch { /* ignore */ }
    load();
    const onScroll = () => { const h = document.documentElement; progress = Math.min(1, h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)); };
    const key = (e: KeyboardEvent) => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); paletteOpen = !paletteOpen; } };
    const onHash = () => { if (location.hash.startsWith('#w=')) app.readHash(); };
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) active = e.target.id; }), { rootMargin: '-40% 0px -55% 0px' });
    const t = setInterval(() => { const els = document.querySelectorAll('section.chapter'); if (els.length) { els.forEach((s) => io.observe(s)); clearInterval(t); } }, 200);
    window.addEventListener('scroll', onScroll, { passive: true }); window.addEventListener('keydown', key); window.addEventListener('hashchange', onHash);
    return () => { window.removeEventListener('scroll', onScroll); window.removeEventListener('keydown', key); window.removeEventListener('hashchange', onHash); io.disconnect(); };
  });
  const s = $derived(app.story);
  const current = $derived(SECTIONS.find((x) => x[0] === active));
</script>

<nav class="bar" aria-label="Chapters">
  <div class="bar-in">
    <a class="brandmark" href="#top"><BankGlyph size={20} /><span>The 2% Question</span></a>
    <span class="cur">{#if current}<span class="mono">{current[1]}</span> {current[2]}{/if}</span>
    <span class="sp"></span>
    <button class="bb" onclick={() => (paletteOpen = true)} aria-label="Open chapter menu"><Icon name="palette" /><span class="hs">Chapters</span><kbd>⌘K</kbd></button>
    <button class="bb" onclick={toggleTheme} aria-label="Toggle light and dark theme"><Icon name="sun" /></button>
  </div>
  <div class="prog" style={`transform: scaleX(${progress})`}></div>
</nav>

<header class="mast" id="top">
  <div class="mast-l">
    <div class="kick"><BankGlyph size={40} title="Bank" /><div><p class="k1">HDFC Bank · Return on assets · FY23 to FY29</p><p class="k2">An outside-in case study</p></div></div>
    <h1>HDFC Bank can earn 2% again. It has to fix funding, not cost.</h1>
    <p class="stand">The 2023 merger moved HDFC Bank's problem from cost to margin. Legacy borrowings running off will take return on assets to 1.86% by FY29. Six funding-led moves take it to 2.04%, and the share price already assumes they happen.</p>
    <p class="by">By Anklesh · 3 November 2026 · Data to Q2 FY27 · About 12 minutes</p>
  </div>
  <div class="mast-r">{#if app.story && app.result}<AtAGlance />{/if}</div>
  <p class="disc">Independent outside-in case study using public data only; not commissioned by, or affiliated with, HDFC Bank or Bain &amp; Company. Every number traces to <a href={REPO}>the repository</a> and its <a href={`${BR}/models/HDFC_RoA_Path_FY29.xlsx`}>Excel model</a>.</p>
</header>

<main class="col">
  {#if app.story && app.model && app.result}
    <ChAnswer /><ChMerger /><ChPeers /><ChRunoff /><ChMoves /><ChValue /><ChRisks /><ChPlan /><Appendix /><Changelog />
    <section class="repro">
      <p class="kh">Reproducibility</p>
      <p><Icon name="check" /> {s?.checks?.total - s?.checks?.fail}/{s?.checks?.total} model reconciliation checks pass · <Icon name="commit" /> model {s?.model_sha} · browser model matches the workbook within 0.1 bp (15 tests) · <a href={`${BR}/docs/model_audit.md`}>independent model audit</a> · <a href={`${BR}/decks/pdf/HDFC_CEO_Memo.pdf`}>two-page CEO memo</a></p>
    </section>
  {:else}
    <p class="loading mono">Loading the model…</p>
  {/if}
</main>

<footer class="foot"><p>Prepared by Anklesh. Bank emblem is a neutral illustration, not any bank's mark. Icons: GitHub Primer Octicons (MIT). Type: EB Garamond, IBM Plex.</p></footer>

<Palette bind:open={paletteOpen} sections={SECTIONS} {toggleTheme} />

<style>
  /* One page grid: 12 columns across --wide. Prose sits in the first 8; the right 4 hold rail visuals; wide exhibits span all 12. */
  :global(:root) { --wide: 1080px; --main: 700px; }
  .bar { position: sticky; top: 0; z-index: 30; background: color-mix(in srgb, var(--paper) 94%, transparent); backdrop-filter: blur(6px); border-bottom: 1px solid var(--hair); }
  .bar-in { max-width: calc(var(--wide) + 40px); margin: 0 auto; padding: 0 20px; height: 44px; display: flex; align-items: center; gap: 16px; }
  .brandmark { display: flex; align-items: center; gap: 8px; text-decoration: none; color: var(--ink); font: 600 15px var(--serif); }
  .cur { font: 500 12.5px var(--sans); color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; } .cur .mono { color: var(--brand); margin-right: 4px; }
  .sp { flex: 1; }
  .bb { display: inline-flex; align-items: center; gap: 6px; background: none; border: 1px solid var(--hair); border-radius: 4px; padding: 3px 8px; cursor: pointer; color: var(--ink-2); font-size: 12px; }
  kbd { font: 500 11px var(--mono); color: var(--muted); }
  .prog { height: 2px; background: var(--brand); transform-origin: 0 50%; }
  .mast { max-width: calc(var(--wide) + 40px); margin: 0 auto; padding: 64px 20px 36px; display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 4fr); column-gap: 56px; align-items: end; }
  .kick { display: flex; gap: 14px; align-items: center; margin-bottom: 26px; }
  .k1 { font: 600 12px var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--brand); margin: 0; } .k2 { font: 400 13px var(--sans); color: var(--muted); margin: 2px 0 0; }
  h1 { font-size: clamp(38px, 5vw, 62px); line-height: 1.04; letter-spacing: -0.02em; font-weight: 500; margin: 0 0 22px; }
  .stand { font: 400 clamp(19px, 1.9vw, 22px)/1.45 var(--serif); color: var(--ink-2); margin: 0 0 18px; }
  .by { font: 500 13px var(--sans); color: var(--ink-2); border-top: 1px solid var(--hair); padding-top: 12px; margin: 0; }
  .mast-r { padding-bottom: 2px; }
  .disc { grid-column: 1 / -1; font-size: 12.5px; color: var(--muted); max-width: 90ch; margin: 22px 0 0; }
  .col { max-width: calc(var(--wide) + 40px); margin: 0 auto; padding: 0 20px; }
  .col :global(section.chapter) { padding: 56px 0 20px; border-top: 1px solid var(--hair); }
  .col :global(.prose) { font-size: 19px; max-width: var(--main); }
  .repro { border-top: 1px solid var(--hair); padding: 28px 0; font-size: 13px; color: var(--muted); } .repro .kh { font: 600 13px var(--sans); color: var(--ink); margin: 0 0 6px; }
  .loading { padding: 80px 0; color: var(--muted); }
  .foot { max-width: calc(var(--wide) + 40px); margin: 0 auto; padding: 20px 20px 60px; font-size: 12px; color: var(--muted); }
  @media (max-width: 1000px) { .mast { grid-template-columns: minmax(0, 1fr); } .mast-r { margin-top: 28px; max-width: 520px; } }
  @media (max-width: 640px) { .hs, .cur { display: none; } .mast { padding-top: 40px; } }
</style>
