import hashlib
import json

from conftest import YEARS, tl

SC = ["Base", "Upside", "Downside"]


def test_export_matches_current_model(root):
    meta = json.loads((root / "data/tidy/hdfc_model_outputs.meta.json").read_text())
    sha = hashlib.sha256((root / meta["model"]).read_bytes()).hexdigest()
    assert sha == meta["model_sha256"], "model changed since export: run pipeline/export_scenarios.py"


def test_balance_sheet_balances(out):
    for s in SC:
        for y in YEARS[7:]:
            assert abs(tl(out, "Model|Total assets", y, s) - tl(out, "Model|Total liabilities and net worth", y, s)) < 1


def test_lever_bridge_adds_up(out):
    for s in SC:
        L = out[s]
        start, drift = L["Levers|RoA FY26A, core"][2], L["Levers|Scenario drift to FY29E (margin, fees, cost, credit, mix)"][2]
        before, lev, end = L["Levers|RoA FY29E, scenario before levers"][2], L["Levers|Levers"][2], L["Levers|RoA FY29E with levers"][2]
        assert abs(start + drift - before) < 1e-6
        assert abs(before + lev - end) < 1e-6
        assert abs(before - 1e4 * tl(out, "Model|Return on average assets", "FY29E", s)) < 1e-6


def test_scenario_ordering(out):
    roa = {s: tl(out, "Model|Return on average assets", "FY29E", s) for s in SC}
    assert roa["Downside"] < roa["Base"] < roa["Upside"]
    v = {s: out[s]["Valuation|Residual income per share"][2] for s in SC}
    assert v["Downside"] < v["Base"] < v["Upside"]


def test_cost_of_equity_above_growth(out):
    assert out["Base"]["Valuation|Cost of equity"][2] > out["Base"]["Valuation|Long-term growth"][2]


def test_checks_tab_all_pass(out):
    for k, v in out["Base"].items():
        if k.startswith("Checks|"):
            assert "FAIL" not in [x for x in v if isinstance(x, str)], k


def test_tornado_base_matches_model(root, out):
    import pandas as pd
    t = pd.read_csv(root / "data/tidy/hdfc_tornado.csv")
    assert abs(t.roa_base_pct.iloc[0] / 100 - tl(out, "Model|Return on average assets", "FY29E")) < 1e-9
    assert (t.swing_bp >= 0).all() and t.swing_bp.is_monotonic_decreasing
