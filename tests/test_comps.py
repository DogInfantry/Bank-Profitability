"""Trading comps and merger precedents (Comps tab) must tie to their inputs and to the Valuation tab."""
import pandas as pd


def test_hdfc_listed_stakes_tie_to_valuation(out):
    b = out["Base"]
    assert abs(b["Comps|HDFC Bank"][5] - b["Valuation|Subsidiaries, after discount"][2]) < 1e-6


def test_cd_ratio_and_growth_recompute_from_inputs(root, out):
    c = pd.read_csv(root / "data/inputs/peer_comps_sep26.csv").set_index(["bank", "metric"])["value"]
    row = out["Base"]["Comps|ICICI Bank: Sep-26"]
    assert abs(row[8] - c[("ICICIBANK", "net_adv_sep26")] / c[("ICICIBANK", "deposits_sep26")]) < 1e-9
    assert abs(row[5] - (c[("ICICIBANK", "net_adv_sep26")] / c[("ICICIBANK", "net_adv_sep25")] - 1)) < 1e-9


def test_precedent_borrowings_share_recomputes(root, out):
    p = pd.read_csv(root / "data/inputs/merger_precedents_rbi.csv")
    r = p[(p.bank == "ICICIBANK") & (p.t == 0)].iloc[0]
    assert abs(out["Base"]["Comps|ICICI Bank: Mar-02"][5] - r.borrowings / (r.borrowings + r.deposits)) < 1e-9
    # every precedent ran off faster than the base case asks HDFC Bank to
    b = out["Base"]
    model = b["Comps|HDFC Bank model: borrowings share cut a year, FY25A to FY29E"][2]
    assert all(b[f"Comps|{nm}: borrowings share cut a year, year 0 to {t}"][2] > model for nm, t in [("ICICI Bank", "3"), ("IDFC First Bank", "3")])
