<script lang="ts">
  // Command palette (⌘K / Ctrl+K): jump to a section, switch the scenario, copy a share link, toggle the theme.
  import { app } from './store.svelte';
  import Icon from './Icon.svelte';
  let { open = $bindable(false), sections, toggleTheme }: { open: boolean; sections: readonly (readonly [string, string, string])[]; toggleTheme: () => void } = $props();
  let q = $state('');
  let sel = $state(0);
  let input: HTMLInputElement | undefined = $state();
  type Item = { label: string; hint: string; run: () => void };
  const items: Item[] = $derived([
    ...sections.map(([id, n, name]) => ({ label: name, hint: `Section ${n}`, run: () => { document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' }); history.replaceState(null, '', `#${id}`); } })),
    ...(['Base', 'Upside', 'Downside'] as const).map((s) => ({ label: `Workbench: ${s} scenario`, hint: 'Scenario', run: () => { app.setPreset(s); document.getElementById('workbench')?.scrollIntoView({ behavior: 'smooth' }); } })),
    { label: 'Copy link to this scenario', hint: 'Share', run: () => navigator.clipboard?.writeText(`${location.origin}${location.pathname}#${app.hash()}`) },
    { label: 'Toggle light / dark', hint: 'Theme', run: toggleTheme },
    { label: 'Open the Excel model', hint: 'Download', run: () => window.open('https://github.com/DogInfantry/Bank-Profitability/blob/claude/wonderful-noether-vgfm7p/models/HDFC_RoA_Path_FY29.xlsx') },
  ]);
  const shown = $derived(items.filter((i) => `${i.label} ${i.hint}`.toLowerCase().includes(q.toLowerCase())));
  $effect(() => { if (open) { q = ''; sel = 0; setTimeout(() => input?.focus(), 0); } });
  function key(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false;
    else if (e.key === 'ArrowDown') { sel = Math.min(sel + 1, shown.length - 1); e.preventDefault(); }
    else if (e.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); e.preventDefault(); }
    else if (e.key === 'Enter' && shown[sel]) { shown[sel].run(); open = false; }
  }
</script>

{#if open}
  <div class="scrim" role="presentation" onclick={() => (open = false)}></div>
  <div class="pal" role="dialog" aria-modal="true" aria-label="Command palette">
    <div class="in"><Icon name="search" /><input bind:this={input} bind:value={q} onkeydown={key} placeholder="Jump to a section or action" aria-label="Search commands" /></div>
    <ul role="listbox">
      {#each shown as it, i}
        <li role="option" aria-selected={i === sel}><button onclick={() => { it.run(); open = false; }} onmouseenter={() => (sel = i)}><span>{it.label}</span><span class="hint">{it.hint}</span></button></li>
      {/each}
      {#if !shown.length}<li class="none">No match</li>{/if}
    </ul>
  </div>
{/if}

<style>
  .scrim { position: fixed; inset: 0; background: rgba(10, 22, 38, .28); z-index: 60; }
  .pal { position: fixed; z-index: 61; top: 14vh; left: 50%; transform: translateX(-50%); width: min(560px, calc(100vw - 32px)); background: var(--surface); border: 1px solid var(--hair); border-radius: 6px; box-shadow: 0 12px 40px rgba(10, 22, 38, .18); overflow: hidden; }
  .in { display: flex; align-items: center; gap: 10px; padding: 12px 14px; border-bottom: 1px solid var(--hair); color: var(--muted); }
  input { flex: 1; border: 0; outline: 0; background: none; font: 400 15px var(--sans); color: var(--ink); }
  ul { list-style: none; margin: 0; padding: 6px; max-height: 50vh; overflow: auto; }
  li button { width: 100%; display: flex; justify-content: space-between; gap: 12px; background: none; border: 0; padding: 9px 10px; border-radius: 4px; cursor: pointer; text-align: left; font-size: 14px; color: var(--ink); }
  li[aria-selected="true"] button { background: var(--brand-wash); }
  .hint { color: var(--muted); font: 500 11px var(--mono); }
  .none { padding: 10px; color: var(--muted); font-size: 13px; }
</style>
