<script lang="ts">
  import Workbench from '../sections/Workbench.svelte';
  import Icon from '../lib/Icon.svelte';
  let open = $state(false);
  $effect(() => { if (location.hash.startsWith('#w=')) open = true; });
</script>
<section class="chapter appendix" id="workbench-a">
  <p class="ak"><span class="mono">A</span> Appendix</p>
  <h2>Test the answer yourself</h2>
  <p class="prose">The recommendation rests on a driver model of HDFC Bank's balance sheet, P&amp;L and valuation. The same model runs in this page, tested against the Excel workbook to within 0.1 bp. Change the rate path, deposit costs, credit cost or any move, and see whether 2% still holds.</p>
  <button class="open" aria-expanded={open} onclick={() => (open = !open)}><Icon name="beaker" /> {open ? 'Close the model' : 'Open the model'}</button>
  {#if open}<div class="wb"><Workbench /></div>{/if}
</section>
<style>
  .ak { font: 600 11.5px var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin: 0 0 10px; display: flex; gap: 12px; } .ak .mono { color: var(--brand); }
  h2 { font-size: clamp(26px, 3vw, 34px); margin-bottom: 14px; }
  .open { display: inline-flex; gap: 8px; align-items: center; font: 600 14px var(--sans); color: var(--paper); background: var(--brand); border: 0; border-radius: 4px; padding: 10px 16px; cursor: pointer; margin-top: 6px; }
  .wb { margin: 10px calc(-1 * var(--breakout)) 0; }
  .wb :global(section.block) { border-top: 0; padding-top: 20px; }
  .wb :global(.sec-head) { display: none; }
  @media (max-width: 1100px) { .wb { margin: 10px 0 0; } }
</style>
