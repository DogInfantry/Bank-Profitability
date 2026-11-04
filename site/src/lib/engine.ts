// The browser model: a line-by-line port of the FY27E-FY29E projection in models/HDFC_RoA_Path_FY29.xlsx
// (Model, Fees, Levers and Valuation tabs; see pipeline/build_hdfc_model.py). tests/engine.test.ts proves the
// port reproduces the recalculated workbook for Base, Upside and Downside.

export type Triple = [number, number, number];
export type DriverKey =
  | 'repo' | 'b_loan' | 'b_inv' | 'b_dep' | 'b_bor' | 'g_loan' | 'g_dep' | 'casa'
  | 'runoff' | 'g_fee' | 'oi_pct' | 'irdai' | 'g_opex' | 'cc' | 'td_prem';
export type Drivers = Record<DriverKey, Triple>;
export type Scenario = 'Base' | 'Upside' | 'Downside';

export interface ModelData {
  years: string[];
  scenarios: Scenario[];
  fy26: Record<string, number>;
  repo_fy26: number;
  drivers: Record<DriverKey, Record<Scenario, Triple>>;
  fixed: { matur: Triple; spread_td: Triple; tax: Triple; payout: Triple; fresh0: number; repo_ref: number; b_fresh: number };
  fees: { hlife_bank_reset: number; other_ins_mult: number; pool: number; p2m_g: number; hd_share: number; acq_share: number; mdr_frac: Triple };
  levers: { name: string; size: number; unit: string; mechanism: string; feasibility: number; months: number }[];
  valuation: Record<string, number>;
  model_sha256: string;
}

export interface Year {
  loans: number; fixed: number; dep: number; bor: number; ol: number; div: number; eq: number; liq: number; cash_ret: number; ta: number;
  a_loans: number; a_liq: number; a_dep: number; a_bor: number; a_ta: number; a_eq: number; a_ta_x: number;
  y_loan: number; y_liq: number; casa: number; c_dep: number; c_bor: number; inc_casa: number; td_book: number; td_fresh: number;
  ii: number; ie: number; nii: number; fee: number; irdai: number; mdr: number; oth: number; oi: number; rev: number;
  opex: number; ppop: number; prov: number; pbt: number; tax: number; pat: number;
  roa: number; roe: number; nim: number; ci: number; cd: number;
}

export interface LeverResult { name: string; pretax: number; pat: number; bp: number; roe: number; value: number; perShare: number }

export interface Result {
  years: Year[];
  levers: LeverResult[];
  bridge: { start: number; drift: number; before: number; levers: number; withLevers: number; target: number; gap: number };
  valuation: { ke: number; roe29: number; roe29Core: number; pbJustified: number; coreValue: number; subsValue: number; sotpPerShare: number;
               riPv: number; riTv: number; riPerShare: number; pbCore: number; roeImplied: number; keBreakEven: number; v10: number };
}

export function scenarioDrivers(m: ModelData, s: Scenario): Drivers {
  const out = {} as Drivers;
  for (const k of Object.keys(m.drivers) as DriverKey[]) out[k] = [...m.drivers[k][s]] as Triple;
  return out;
}

/** leverOn: which levers count toward "with levers" (default all). leverScale multiplies lever sizes (default 1). */
export function run(m: ModelData, d: Drivers, leverOn: boolean[] = m.levers.map(() => true), leverScale = 1): Result {
  const f26 = m.fy26;
  const olRatio = f26.ol / f26.dep;
  const F = m.fees, V = m.valuation, X = m.fixed;
  let p = { ...f26, cash_ret: 0, repo: m.repo_fy26 } as Record<string, number>;
  const years: Year[] = [];
  for (let i = 0; i < 3; i++) {
    const g = (k: DriverKey) => d[k][i];
    const dRepo = g('repo') - p.repo;
    const loans = p.loans * (1 + g('g_loan'));
    const fixed = p.fixed * (1 + g('g_opex'));
    const dep = p.dep * (1 + g('g_dep'));
    const bor = p.bor - X.matur[i] * g('runoff');
    const ol = dep * olRatio;
    const div = X.payout[i] * p.pat;
    const liq = dep + bor + ol + p.eq - div - loans - fixed;
    const a_loans = (p.loans + loans) / 2;
    const a_liq = (p.liq + p.cash_ret + liq) / 2;
    const a_dep = (p.dep + dep) / 2;
    const a_bor = (p.bor + bor) / 2;
    const a_ta_x = (p.ta + loans + fixed + liq) / 2;
    const y_loan = p.y_loan + g('b_loan') * dRepo;
    const y_liq = p.y_liq + g('b_inv') * dRepo;
    const casa = g('casa');
    // New term deposits at the fresh rate, not the book rate (Model tab: inc_casa, td_book, td_fresh)
    const inc_casa = (casa * dep - p.casa * p.dep) / (dep - p.dep);
    const td_book = p.c_dep + p.casa * X.spread_td[i] + g('b_dep') * dRepo;
    const td_fresh = X.fresh0 + X.b_fresh * (g('repo') - X.repo_ref) + g('td_prem');
    const c_dep = p.c_dep + g('b_dep') * dRepo + (p.casa - casa) * X.spread_td[i] + (dep - p.dep) / dep * (1 - inc_casa) * (td_fresh - td_book);
    const c_bor = p.c_bor + g('b_bor') * dRepo;
    const ii = y_loan * a_loans + y_liq * a_liq;
    const ie = c_dep * a_dep + c_bor * a_bor;
    const nii = ii - ie;
    const fee = p.fee * (1 + g('g_fee'));
    const irdai = -F.hlife_bank_reset * F.other_ins_mult * g('irdai');
    const mdr = F.pool * Math.pow(1 + F.p2m_g, i) * F.hd_share * F.acq_share * F.mdr_frac[i];
    const oth = g('oi_pct') * a_ta_x;
    const oi = fee + irdai + mdr + oth;
    const rev = nii + oi;
    const opex = p.opex * (1 + g('g_opex'));
    const ppop = rev - opex;
    const prov = g('cc') * a_loans;
    const pbt = ppop - prov;
    const tax = X.tax[i] * pbt;
    const pat = pbt - tax;
    const eq = p.eq + pat - div;
    const cash_ret = pat;
    const ta = loans + fixed + liq + cash_ret;
    const a_ta = (p.ta + ta) / 2;
    const a_eq = (p.eq + eq) / 2;
    const y: Year = {
      loans, fixed, dep, bor, ol, div, eq, liq, cash_ret, ta, a_loans, a_liq, a_dep, a_bor, a_ta, a_eq, a_ta_x,
      y_loan, y_liq, casa, c_dep, c_bor, inc_casa, td_book, td_fresh, ii, ie, nii, fee, irdai, mdr, oth, oi, rev, opex, ppop, prov, pbt, tax, pat,
      roa: pat / a_ta, roe: pat / a_eq, nim: nii / (a_loans + a_liq), ci: opex / rev, cd: loans / dep,
    };
    years.push(y);
    p = { ...y, repo: g('repo') } as unknown as Record<string, number>;
  }
  const N = years[2];
  const ke = V.rf + V.beta * V.erp;
  const bvCore = f26.eq - V.subs_cost;
  const tax29 = X.tax[2];
  // Levers: driver deltas on top of the scenario in FY29E (Levers tab)
  const pre = m.levers.map((l, j) => {
    const s = l.size * leverScale;
    switch (j) {
      case 0: return s * X.spread_td[2] * N.a_dep;                       // CASA
      case 1: return s * (N.c_bor - N.td_fresh);                         // borrowings retired, replaced at the fresh TD rate
      case 2: return s * N.a_loans;                                      // asset re-mix (yield)
      case 3: return s * N.opex;                                         // productivity
      case 4: return s * N.fee;                                          // fees
      default: return Math.max(0, s - F.hd_share) * F.pool * Math.pow(1 + F.p2m_g, 2) * F.acq_share; // UPI share target
    }
  });
  const levers: LeverResult[] = m.levers.map((l, j) => {
    const pat = pre[j] * (1 - tax29);
    const roe = pat / N.a_eq;
    const value = roe / (ke - V.g) * bvCore;
    return { name: l.name, pretax: pre[j], pat, bp: pat / N.a_ta * 1e4, roe, value, perShare: value / V.shares };
  });
  const start = f26.roa_core_bp;
  const before = N.roa * 1e4;
  const levSum = levers.reduce((a, l, j) => a + (leverOn[j] ? l.bp : 0), 0);
  // Valuation (Valuation tab): core bank ex subsidiary dividends and investment; values rolled to the price date
  const roe29 = N.roe;
  const roe29Core = (N.pat - V.sdiv_sh * N.oth * (1 - tax29)) / (N.a_eq - V.subs_cost);
  const pbJustified = (roe29Core - V.g) / (ke - V.g);
  const coreValue = pbJustified * bvCore;
  const subsValue = (V.life_m * V.life_s + V.hdb_m * V.hdb_s + V.amc_m * V.amc_s) * (1 - V.hold_disc);
  const eqOpen = [f26.eq, years[0].eq, years[1].eq];
  const ri = years.map((y, i) => y.pat - ke * eqOpen[i]);
  const riPv = ri.reduce((a, r, i) => a + r / Math.pow(1 + ke, i + 1), 0);
  const riTv = ri[2] * (1 + V.ri_g) / (ke - V.ri_g) / Math.pow(1 + ke, 3);
  const divWin = years[0].div;
  const roll = (v: number) => (v * Math.pow(1 + ke, V.t_roll) - divWin) / V.shares;
  const pbCore = (V.mcap - subsValue) / (V.bvps_now * V.shares - V.subs_cost);
  const priceAt = (k: number) => (V.price * V.shares + divWin) / Math.pow(1 + k, V.t_roll);
  const keAt = (k: number) => V.g + (roe29Core - V.g) * bvCore / (priceAt(k) - subsValue);
  return {
    years, levers,
    bridge: { start, drift: before - start, before, levers: levSum, withLevers: before + levSum, target: V.target_bp, gap: before + levSum - V.target_bp },
    valuation: {
      ke, roe29, roe29Core, pbJustified, coreValue, subsValue, sotpPerShare: roll(coreValue + subsValue),
      riPv, riTv, riPerShare: roll(f26.eq + riPv + riTv),
      pbCore, roeImplied: V.g + pbCore * (ke - V.g), keBreakEven: keAt(keAt(ke)),
      v10: 10 / 1e4 * N.a_ta / N.a_eq / (ke - V.g) * bvCore,
    },
  };
}
