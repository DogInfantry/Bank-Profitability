"""The SQL layer must agree with the model and the tidy files it was built from."""
import duckdb
import pytest

from conftest import tl


@pytest.fixture(scope="module")
def con(root):
    db = root / "data/fs.duckdb"
    if not db.exists():
        pytest.skip("run pipeline/warehouse.py first")
    return duckdb.connect(str(db), read_only=True)


def run(con, root, name):
    return con.sql((root / "sql" / f"{name}.sql").read_text()).df()


def test_peer_league_hdfc_matches_peers_tab(con, root, out):
    df = run(con, root, "01_peer_league").set_index("symbol")
    assert abs(df.loc["HDFCBANK", "roa_pct"] - round(100 * out["Base"]["Peers|HDFC Bank"][4], 2)) < 0.011
    assert df.roa_rank.min() == 1 and len(df) == 12


def test_credit_cost_matches_model(con, root, out):
    df = run(con, root, "03_credit_cost_cycle").iloc[0]
    assert abs(df.through_cycle_fy21_26_pct - 100 * out["Base"]["Opex_Credit|Through-the-cycle credit cost, FY21-FY26 average"][2]) < 0.006


def test_mdr_pool_matches_model(con, root, out):
    df = run(con, root, "04_upi_mdr_pool").iloc[0]
    assert abs(df.mdr_pool_cr - out["Base"]["Fees|Annual MDR pool at current run-rate"][2]) < 1


def test_scenario_compare(con, root, out):
    df = run(con, root, "06_scenario_compare").set_index("scenario")
    for s in ("Base", "Upside", "Downside"):
        assert abs(df.loc[s, "roa_fy29_pct"] - round(100 * tl(out, "Model|Return on average assets", "FY29E", s), 2)) < 1e-9
