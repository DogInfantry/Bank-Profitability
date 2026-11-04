"""What would change the answer: break-even inputs at which Base FY29E RoA with levers falls to the 2.0% target.

Slopes come from the tornado (pipeline/tornado.py: the workbook recalculated at each driver's low and high input),
so every break-even is read off the live model, linear between the two recalculated points. The levers and the
regulatory overlay are held at their Base values (they move little with these drivers).
Also carries the valuation break-even (Ke at which sum of the parts = price) from the export.
Output: data/tidy/hdfc_breakevens.csv
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "data/tidy"


def main() -> None:
    b = json.loads((T / "hdfc_model_outputs.json").read_text())["Base"]
    with_lev = b["Levers|RoA FY29E with levers"][2] + b["Regulation|FY29E RoA effect of the rule changes"][2]   # bp
    target = b["Levers|Target"][2]
    torn = pd.read_csv(T / "hdfc_tornado.csv")
    rows = []
    for t in torn.itertuples():
        slope = (t.roa_high_input_pct - t.roa_low_input_pct) * 100 / (t.high_input_fy29 - t.low_input_fy29)   # bp of RoA per unit of input
        be = t.base_input_fy29 + (target - with_lev) / slope if slope else float("nan")
        lo, hi = sorted((t.low_input_fy29, t.high_input_fy29))
        rows.append(dict(driver=t.driver, base_input=t.base_input_fy29, breakeven_input=be, move_to_breakeven=be - t.base_input_fy29,
                         low_input=t.low_input_fy29, high_input=t.high_input_fy29, inside_scenario_range=lo <= be <= hi,
                         slope_bp_per_unit=slope, test="FY29E RoA with levers and overlay = 2.0%"))
    rows.append(dict(driver="Cost of equity", base_input=b["Valuation|Cost of equity"][2],
                     breakeven_input=b["Valuation|Cost of equity at which sum of the parts equals the price"][2],
                     move_to_breakeven=b["Valuation|Cost of equity at which sum of the parts equals the price"][2] - b["Valuation|Cost of equity"][2],
                     test="Base sum of the parts = share price"))
    df = pd.DataFrame(rows)
    df["headroom_bp"] = with_lev - target
    df["source"] = "pipeline/breakevens.py from data/tidy/hdfc_tornado.csv and hdfc_model_outputs.json (Base)"
    df.to_csv(T / "hdfc_breakevens.csv", index=False)
    print(f"headroom {with_lev - target:.1f} bp")
    print(df[["driver", "base_input", "breakeven_input", "inside_scenario_range"]].round(4).to_string())


if __name__ == "__main__":
    main()
