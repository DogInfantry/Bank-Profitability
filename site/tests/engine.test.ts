// Parity: the browser engine must reproduce the recalculated Excel workbook (data/tidy/hdfc_model_outputs.json).
import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { run, scenarioDrivers, type ModelData, type Scenario } from '../src/lib/engine';

const model = JSON.parse(readFileSync(resolve(__dirname, '../public/data/model.json'), 'utf8')) as ModelData;
const xl = JSON.parse(readFileSync(resolve(__dirname, '../../data/tidy/hdfc_model_outputs.json'), 'utf8'));
const YEARS = ['FY20A', 'FY21A', 'FY22A', 'FY23A', 'FY24A', 'FY25A', 'FY26A', 'FY27E', 'FY28E', 'FY29E'];
const col = (s: Scenario, k: string, y: string) => xl[s][k][2 + YEARS.indexOf(y)];
const sc = (s: Scenario, k: string) => xl[s][k][2];

describe.each(['Base', 'Upside', 'Downside'] as Scenario[])('%s scenario matches the Excel model', (s) => {
  const r = run(model, scenarioDrivers(model, s));
  it.each([0, 1, 2])('year %i: RoA within 0.1 bp, NIM within 0.1 bp, PAT and net worth within 1 INR cr', (i) => {
    const y = model.years[i];
    expect(Math.abs(r.years[i].roa - col(s, 'Model|Return on average assets', y)) * 1e4).toBeLessThan(0.1);
    expect(Math.abs(r.years[i].nim - col(s, 'Model|Net interest margin on interest-earning assets', y)) * 1e4).toBeLessThan(0.1);
    expect(Math.abs(r.years[i].pat - col(s, 'Model|Profit after tax', y))).toBeLessThan(1);
    expect(Math.abs(r.years[i].eq - col(s, 'Model|Net worth, closing', y))).toBeLessThan(1);
    expect(Math.abs(r.years[i].ta - col(s, 'Model|Total liabilities and net worth', y))).toBeLessThan(1);
  });
  it('lever bridge matches', () => {
    expect(Math.abs(r.bridge.before - xl[s]['Levers|RoA FY29E, scenario before levers'][2])).toBeLessThan(0.1);
    expect(Math.abs(r.bridge.levers - xl[s]['Levers|Levers'][2])).toBeLessThan(0.1);
    expect(Math.abs(r.bridge.withLevers - xl[s]['Levers|RoA FY29E with levers'][2])).toBeLessThan(0.1);
  });
  it('value per share within INR 0.5', () => {
    expect(Math.abs(r.valuation.sotpPerShare - sc(s, 'Valuation|Sum of the parts per share'))).toBeLessThan(0.5);
    expect(Math.abs(r.valuation.riPerShare - sc(s, 'Valuation|Residual income per share'))).toBeLessThan(0.5);
    expect(Math.abs(r.valuation.roeImplied - sc(s, 'Valuation|RoE the market is pricing'))).toBeLessThan(1e-6);
  });
  it('core RoE and break-even Ke within 0.1 bp', () => {
    expect(Math.abs(r.valuation.roe29Core - sc(s, 'Valuation|Sustainable core-bank RoE: FY29E')) * 1e4).toBeLessThan(0.1);
    expect(Math.abs(r.valuation.keBreakEven - sc(s, 'Valuation|Cost of equity at which sum of the parts equals the price')) * 1e4).toBeLessThan(0.1);
  });
});
