<script lang="ts">
  // Exhibit 6: one-page trading comps. HDFC Bank first, then the four peers, then the peer median (Comps tab).
  import { app } from '../lib/store.svelte';
  type B = { bank: string; pb_ex: number; pe: number; roa: number; roe: number; loan_g_ex: number | null; cd: number; casa: number; cet1: number };
  const c = $derived(app.story!.comps as { banks: B[]; med: Record<string, number> });
  const p1 = (v: number | null) => (v == null ? 'n.d.' : `${(v * 100).toFixed(1)}%`);
  const COLS: [keyof B, string, (v: any) => string][] = [
    ['pb_ex', 'P/B ex stakes', (v) => `${v.toFixed(2)}x`], ['pe', 'P/E', (v) => `${v.toFixed(1)}x`],
    ['roa', 'RoA FY26', (v) => `${(v * 100).toFixed(2)}%`], ['roe', 'RoE FY26', p1],
    ['cd', 'CD ratio', p1], ['casa', 'CASA', p1], ['loan_g_ex', 'Loan growth', p1], ['cet1', 'CET1', p1]];
</script>
<div class="tbl-scroll">
  <table class="data comps">
    <thead><tr><th>Bank</th>{#each COLS as [, lab]}<th class="n">{lab}</th>{/each}</tr></thead>
    <tbody>
      {#each c.banks as b, i}
        <tr class:hd={i === 0}><td>{b.bank}</td>{#each COLS as [k, , f]}<td class="n">{f(b[k])}</td>{/each}</tr>
      {/each}
      <tr class="med"><td>Peer median</td>{#each COLS as [k, , f]}<td class="n">{f(c.med[k as string])}</td>{/each}</tr>
    </tbody>
  </table>
</div>
<style>
  .comps tr.hd td { font-weight: 600; color: var(--brand); background: var(--brand-wash); }
  .comps tr.med td { border-top: 1px solid var(--ink); font-weight: 600; }
  .comps td:first-child { white-space: nowrap; }
</style>
