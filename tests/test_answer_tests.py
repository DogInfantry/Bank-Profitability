"""Break-evens must agree with the model, and the Q3 FY27 calls must stay registered before the results."""
import pandas as pd


def test_breakeven_headroom_matches_the_bridge(root, out):
    be = pd.read_csv(root / "data/tidy/hdfc_breakevens.csv")
    b = out["Base"]
    headroom = b["Levers|RoA FY29E with levers"][2] + b["Regulation|FY29E RoA effect of the rule changes"][2] - b["Levers|Target"][2]
    assert abs(be.headroom_bp.iloc[0] - headroom) < 1e-9


def test_breakevens_sit_on_the_right_side_of_base(root):
    be = pd.read_csv(root / "data/tidy/hdfc_breakevens.csv").set_index("driver")
    assert be.loc["Credit cost", "breakeven_input"] > be.loc["Credit cost", "base_input"]          # more credit cost hurts
    assert be.loc["CASA ratio, year end", "breakeven_input"] < be.loc["CASA ratio, year end", "base_input"]  # less CASA hurts


def test_predictions_registered_before_results(root):
    p = pd.read_csv(root / "data/inputs/hdfc_q3fy27_predictions.csv")
    assert (pd.to_datetime(p.registered_on) < "2027-01-01").all() and p.prediction_q3fy27.notna().all()


def test_two_percent_target_brackets(out):
    # 2% RoA must clear Ke at FY29E leverage; the price-implied RoA must fall once capital is returned
    b = out["Base"]
    s = lambda k: b[f"Levers|{k}"][2]  # noqa: E731
    assert s("RoA that just earns the cost of equity") < 0.02 < s("RoA that earns the RoE the price implies")
    assert s("RoA that earns the price-implied RoE after capital return") < s("RoA that earns the RoE the price implies")
    assert abs(s("RoE at the 2.0% target") - 0.02 * s("Average assets / average net worth, FY29E")) < 1e-9
