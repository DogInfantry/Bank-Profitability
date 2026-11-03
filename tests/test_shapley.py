import itertools

import pandas as pd

from shapley import FACTORS_ROA, roa, shapley


def test_contributions_sum_to_gap():
    a = dict(nii=3.1, oi=1.5, opex=1.8, prov=0.6, tax_rate=0.22)
    b = dict(nii=3.8, oi=1.3, opex=2.0, prov=0.3, tax_rate=0.25)
    c = shapley(roa, a, b, FACTORS_ROA)
    assert abs(sum(c.values()) - (roa(b) - roa(a))) < 1e-12


def test_order_independent_and_symmetric():
    a = dict(nii=3.0, oi=1.0, opex=2.0, prov=0.5, tax_rate=0.2)
    b = dict(nii=3.5, oi=1.2, opex=1.8, prov=0.7, tax_rate=0.3)
    c1 = shapley(roa, a, b, FACTORS_ROA)
    c2 = shapley(roa, a, b, list(reversed(FACTORS_ROA)))
    for k in FACTORS_ROA:
        assert abs(c1[k] - c2[k]) < 1e-12
    back = shapley(roa, b, a, FACTORS_ROA)
    for k in FACTORS_ROA:
        assert abs(c1[k] + back[k]) < 1e-12


def test_hdfc_walk_sums(root):
    w = pd.read_csv(root / "data/tidy/hdfc_roa_walk.csv")
    parts = w[["nii_bp", "oi_bp", "opex_bp", "prov_bp", "tax_rate_bp"]].sum(axis=1)
    assert ((parts - w.change_bp).abs() < 1e-9).all()
    two = w.set_index("step")
    chained = two.loc["FY23 to FY24", "change_bp"] + two.loc["FY24 to FY26", "change_bp"] + two.loc["FY26 to Q2 FY27", "change_bp"]
    assert abs(chained - two.loc["FY23 to Q2 FY27", "change_bp"]) < 1e-9


def test_peer_file_consistent(root):
    sh = pd.read_csv(root / "data/tidy/bank_shapley_FY26.csv")
    cols = ["nii", "oi", "opex", "prov", "tax_rate"]
    r = sh[sh.metric == "RoA"]
    assert ((r[cols].sum(axis=1) - r.gap).abs() < 1e-9).all()
    assert len(list(itertools.chain(r.bank))) >= 4
