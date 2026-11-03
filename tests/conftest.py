import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
YEARS = ["FY20A", "FY21A", "FY22A", "FY23A", "FY24A", "FY25A", "FY26A", "FY27E", "FY28E", "FY29E"]


@pytest.fixture(scope="session")
def root():
    return ROOT


@pytest.fixture(scope="session")
def out():
    """Recalculated model export: {scenario: {"Sheet|Line": [C..N values]}}."""
    return json.loads((ROOT / "data" / "tidy" / "hdfc_model_outputs.json").read_text())


def tl(out, key, year, scn="Base"):
    return out[scn][key][2 + YEARS.index(year)]
