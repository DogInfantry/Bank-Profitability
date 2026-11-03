// Shared state: the loaded data, the workbench scenario (preset + driver shifts + lever toggles) and its live result.
import { run, scenarioDrivers, type DriverKey, type Drivers, type ModelData, type Result, type Scenario } from './engine';

export interface Story { [k: string]: any }

export const DRIVER_META: { key: DriverKey; label: string; unit: 'pct' | 'x' | 'pp'; step: number; min: number; max: number; group: string; help: string }[] = [
  { key: 'repo', label: 'Policy repo rate', unit: 'pct', step: 0.0025, min: -0.015, max: 0.015, group: 'Rates', help: 'Shift to the fiscal-year average repo path' },
  { key: 'b_loan', label: 'Loan yield beta', unit: 'x', step: 0.05, min: -0.3, max: 0.3, group: 'Rates', help: 'Pass-through of repo into the yield on advances' },
  { key: 'b_dep', label: 'Deposit cost beta', unit: 'x', step: 0.05, min: -0.2, max: 0.3, group: 'Rates', help: 'Same-year regression estimate 0.37; long run 0.62' },
  { key: 'g_loan', label: 'Advances growth', unit: 'pct', step: 0.01, min: -0.06, max: 0.06, group: 'Balance sheet', help: 'Annual growth in advances' },
  { key: 'g_dep', label: 'Deposit growth', unit: 'pct', step: 0.01, min: -0.06, max: 0.06, group: 'Balance sheet', help: 'Annual growth in deposits; with advances it sets the CD ratio' },
  { key: 'casa', label: 'CASA ratio', unit: 'pct', step: 0.005, min: -0.03, max: 0.04, group: 'Balance sheet', help: 'Year-end share of current and savings accounts' },
  { key: 'runoff', label: 'Borrowings retired', unit: 'pct', step: 0.05, min: -0.4, max: 0.4, group: 'Balance sheet', help: 'Share of maturing legacy borrowings replaced by deposits' },
  { key: 'g_fee', label: 'Core fee growth', unit: 'pct', step: 0.01, min: -0.05, max: 0.05, group: 'Income and cost', help: 'Commission, exchange and brokerage' },
  { key: 'oi_pct', label: 'Treasury income', unit: 'pct', step: 0.0005, min: -0.001, max: 0.001, group: 'Income and cost', help: 'Treasury and other non-fee income, % of average assets' },
  { key: 'g_opex', label: 'Opex growth', unit: 'pct', step: 0.01, min: -0.04, max: 0.04, group: 'Income and cost', help: 'Annual growth in operating expenses' },
  { key: 'cc', label: 'Credit cost', unit: 'pct', step: 0.0005, min: -0.003, max: 0.004, group: 'Income and cost', help: 'Loan-loss provisions / average advances' },
  { key: 'irdai', label: 'IRDAI cap severity', unit: 'x', step: 0.25, min: -1, max: 1, group: 'Income and cost', help: 'Share of the proposed cap effect that reaches bank fees' },
];

class AppState {
  model = $state<ModelData | null>(null);
  story = $state<Story | null>(null);
  preset = $state<Scenario>('Base');
  shift = $state<Record<string, number>>({});
  leverOn = $state<boolean[]>([true, true, true, true, true, true]);
  theme = $state<'light' | 'dark' | 'auto'>('auto');

  drivers: Drivers | null = $derived.by(() => {
    if (!this.model) return null;
    const d = scenarioDrivers(this.model, this.preset);
    for (const m of DRIVER_META) {
      const s = this.shift[m.key] ?? 0;
      if (s) d[m.key] = d[m.key].map((v) => Math.max(0, v + s)) as Drivers[DriverKey];
    }
    return d;
  });
  result: Result | null = $derived(this.model && this.drivers ? run(this.model, this.drivers, this.leverOn) : null);
  scenarioResults: Record<Scenario, Result> | null = $derived.by(() => {
    const m = this.model;
    if (!m) return null;
    return { Base: run(m, scenarioDrivers(m, 'Base')), Upside: run(m, scenarioDrivers(m, 'Upside')), Downside: run(m, scenarioDrivers(m, 'Downside')) };
  });
  dirty = $derived(Object.values(this.shift).some((v) => v) || this.leverOn.some((v) => !v));

  setPreset(s: Scenario) { this.preset = s; this.shift = {}; this.leverOn = [true, true, true, true, true, true]; }
  hash(): string {
    const parts = Object.entries(this.shift).filter(([, v]) => v).map(([k, v]) => `${k}:${+v.toFixed(5)}`);
    return `w=${this.preset};${parts.join(',')};${this.leverOn.map((b) => (b ? 1 : 0)).join('')}`;
  }
  readHash() {
    const m = /w=([A-Za-z]+);([^;]*);([01]{6})/.exec(decodeURIComponent(location.hash));
    if (!m) return;
    if (['Base', 'Upside', 'Downside'].includes(m[1])) this.preset = m[1] as Scenario;
    const sh: Record<string, number> = {};
    for (const kv of m[2].split(',').filter(Boolean)) { const [k, v] = kv.split(':'); if (DRIVER_META.some((d) => d.key === k)) sh[k] = +v; }
    this.shift = sh;
    this.leverOn = m[3].split('').map((c) => c === '1');
  }
}

export const app = new AppState();

export async function load() {
  const [m, s] = await Promise.all([fetch('./data/model.json').then((r) => r.json()), fetch('./data/story.json').then((r) => r.json())]);
  app.model = m; app.story = s;
  app.readHash();
}
