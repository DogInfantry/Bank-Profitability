"""The quarterly panel must be complete, cited, internally consistent and tie to the annual model."""
import pandas as pd
import pytest

from conftest import tl


@pytest.fixture(scope="module")
def panel(root):
    return pd.read_csv(root / "data/tidy/hdfc_quarterly_panel.csv").set_index("period")


def test_every_input_row_is_cited(root):
    for f in ("hdfc_quarterly_kpis.csv", "hdfc_quarterly_chart_reads.csv"):
        d = pd.read_csv(root / "data/inputs" / f)
        assert d.source_file.str.match(r"HDFCBANK_Q[1-4]FY\d{2}_ppt\.pdf").all() and d.page.gt(0).all(), f


def test_panel_covers_post_merger_quarters(panel):
    assert list(panel.index) == ["Q2FY24", "Q3FY24", "Q4FY24", "Q1FY25", "Q2FY25", "Q3FY25", "Q4FY25",
                                 "Q1FY26", "Q2FY26", "Q3FY26", "Q4FY26", "Q1FY27", "Q2FY27"]
    for m in ("deposits", "borrowings", "net_advances", "casa_ratio", "cost_of_funds", "lcr_avg", "credit_cost_bp", "gnpa"):
        assert panel[m].notna().all(), m


def test_gnpa_bridge_ties(panel):
    assert panel.gnpa_bridge_diff.dropna().abs().max() <= 1  # INR bn, rounding on the slide


def test_closing_gnpa_is_next_opening(panel):
    assert (panel.gnpa_close.shift() - panel.gnpa_open).dropna().abs().max() == 0


def test_new_format_advances_mix_sums_to_100(panel):
    s = (panel.mix_retail + panel.mix_smm + panel.mix_wholesale).dropna()
    assert len(s) >= 12 and s.between(99, 101).all()


@pytest.mark.parametrize("q, fy", [("Q4FY24", "FY24A"), ("Q4FY25", "FY25A"), ("Q4FY26", "FY26A")])
def test_year_end_ties_to_annual_model(panel, out, q, fy):
    for metric, line in (("deposits", "Model|Deposits"), ("borrowings", "Model|Borrowings")):
        deck_cr = panel.loc[q, metric] * 100  # INR bn -> INR cr
        assert abs(deck_cr / tl(out, line, fy) - 1) < 0.005, (metric, q)
