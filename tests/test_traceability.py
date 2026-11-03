"""Numbers the reader sees in the memo and the cockpit must come from the recalculated model export."""
import json
import re

from conftest import tl


def memo_text(root):
    from docx import Document
    d = Document(root / "decks/HDFC_CEO_Memo.docx")
    parts = [p.text for p in d.paragraphs] + [c.text for t in d.tables for row in t.rows for c in row.cells]
    return "\n".join(parts)


def test_memo_headline_numbers(root, out):
    txt = memo_text(root)
    b = out["Base"]
    expect = [
        f"{100 * tl(out, 'Model|Return on average assets', 'FY29E'):.2f}%",
        f"{b['Levers|RoA FY29E with levers'][2] / 100:.2f}%",
        f"{100 * b['Valuation|RoE the market is pricing'][2]:.1f}%",
        f"₹{b['Valuation|Residual income per share'][2]:.0f}-{b['Valuation|Sum of the parts per share'][2]:.0f}",
        f"{b['Levers|All levers'][2]:.1f}",
        f"{100 * b['Valuation|Cost of equity'][2]:.1f}%",
    ]
    missing = [e for e in expect if e not in txt]
    assert not missing, f"memo is stale or untraceable: {missing}; rebuild with decks/build_memo.py"


def test_cockpit_payload_matches_export(root, out):
    html = (root / "viz/dashboard.html").read_text()
    data = json.loads(re.search(r"const D = (\{.*?\});\n", html, re.S).group(1))
    hd = data["hd"]
    for s in ("Base", "Upside", "Downside"):
        assert abs(hd["sc"][s]["roa"][-1] - round(100 * tl(out, "Model|Return on average assets", "FY29E", s), 3)) < 1e-9
        assert hd["sc"][s]["sotp"] == round(out[s]["Valuation|Sum of the parts per share"][2])
    assert hd["v10"] == round(out["Base"]["Valuation|Value of +10 bp RoA (equity value)"][2])
