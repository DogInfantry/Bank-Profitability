"""Small framework for IB-standard Excel models on xlsxwriter.

Conventions enforced here (and checked by pipeline/xlsx_lint.py):
  * Garamond throughout, never italic. Headers bold; notes regular grey.
  * Font colour: blue = hard-coded input, black = formula, green = link to another sheet, red = check.
  * Light grey fill on input cells and on historical-period columns only. No other fills.
  * Column A spacer, B line item, C unit, D source/note, E onward periods. Gridlines off, panes frozen.
  * Number formats: INR cr #,##0;(#,##0);"–"   ratios 0.0%   yields 0.00%   multiples 0.00"x"
  * No merged cells. One formula pattern per row within the historical block and within the projection block.
"""
from __future__ import annotations

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

FONT = "Garamond"
BLUE, BLACK, GREEN, RED, GREY = "#0000FF", "#000000", "#008000", "#C00000", "#7F7F7F"
FILL = "#F2F2F2"
NUM = {
    "cr": '#,##0;(#,##0);"–"',
    "cr1": '#,##0.0;(#,##0.0);"–"',
    "pct1": '0.0%;(0.0%);"–"',
    "pct2": '0.00%;(0.00%);"–"',
    "x": '0.00"x";(0.00"x");"–"',
    "bp": '0" bp";(0" bp");"–"',
    "rs": '#,##0.0;(#,##0.0);"–"',
    "num": '#,##0.00;(#,##0.00);"–"',
    "int": '0',
    "text": '@',
    "gen": 'General',
}
YEARS = ["FY20A", "FY21A", "FY22A", "FY23A", "FY24A", "FY25A", "FY26A", "FY27E", "FY28E", "FY29E"]
COLS = [xl_col_to_name(4 + i) for i in range(len(YEARS))]  # E..N
HIST = COLS[:7]
PROJ = COLS[7:]


def prev(c: str) -> str:
    return COLS[COLS.index(c) - 1]


class Book:
    def __init__(self, path: str):
        self.wb = xlsxwriter.Workbook(path, {"default_format_properties": {"font_name": FONT, "font_size": 11}})
        self._fmt = {}
        self.sheets = {}

    def f(self, num="gen", color=BLACK, bold=False, fill=False, top=False, bottom=False, align=None, size=11, wrap=False):
        key = (num, color, bold, fill, top, bottom, align, size, wrap)
        if key not in self._fmt:
            p = {"font_name": FONT, "font_size": size, "font_color": color, "bold": bold, "italic": False,
                 "num_format": NUM.get(num, num), "valign": "vcenter"}
            if fill:
                p["bg_color"] = FILL
            if top:
                p["top"] = 1
            if bottom:
                p["bottom"] = 1
            if align:
                p["align"] = align
            if wrap:
                p["text_wrap"] = True
            self._fmt[key] = self.wb.add_format(p)
        return self._fmt[key]

    def sheet(self, name: str, title: str, subtitle: str, timeline: bool = True, widths=(2, 46, 9, 40)):
        s = Sheet(self, name, title, subtitle, timeline, widths)
        self.sheets[name] = s
        return s

    def close(self):
        for sh in self.sheets.values():
            for item in sh.pending:
                sh._flush_line(*item)
        self.wb.close()


class Sheet:
    def __init__(self, book: Book, name: str, title: str, subtitle: str, timeline: bool, widths):
        self.b, self.name = book, name
        self.ws = book.wb.add_worksheet(name)
        self.rows: dict[str, int] = {}
        self.pending: list = []
        ws = self.ws
        ws.hide_gridlines(2)
        ws.set_column(0, 0, widths[0]); ws.set_column(1, 1, widths[1]); ws.set_column(2, 2, widths[2]); ws.set_column(3, 3, widths[3])
        ws.set_column(4, 4 + len(YEARS), 11)
        ws.write(0, 1, title, book.f(bold=True, size=14))
        ws.write(1, 1, subtitle, book.f(color=GREY))
        ws.set_landscape(); ws.fit_to_pages(1, 0); ws.set_paper(9)
        ws.set_header(f"&L&\"Garamond\"HDFC Bank: path back to 2% RoA&R&\"Garamond\"{name}")
        ws.set_footer("&L&\"Garamond\"Outside-in, public data only. Not affiliated with HDFC Bank or Bain & Company.&R&\"Garamond\"Page &P of &N")
        self.r = 3
        if timeline:
            self.timeline()

    # ---- layout helpers
    def timeline(self):
        b, ws = self.b, self.ws
        ws.write(self.r, 1, "INR crore unless stated; fiscal year ends 31 March", b.f(color=GREY, bottom=True))
        ws.write(self.r, 2, "Unit", b.f(bold=True, bottom=True))
        ws.write(self.r, 3, "Source / note", b.f(bold=True, bottom=True))
        for i, y in enumerate(YEARS):
            ws.write(self.r, 4 + i, y, b.f(bold=True, bottom=True, align="right", fill=i < len(HIST)))
        ws.freeze_panes(self.r + 1, 4)
        self.r += 1

    def section(self, text: str):
        self.r += 1
        self.ws.write(self.r, 1, text, self.b.f(bold=True, bottom=True))
        self.r += 1

    def note(self, text: str, col: int = 1):
        self.ws.write(self.r, col, text, self.b.f(color=GREY))
        self.r += 1

    def skip(self, n: int = 1):
        self.r += n

    # ---- the workhorse: one line across the timeline
    def line(self, key, label, unit="", note="", hist=None, proj=None, num="cr", bold=False, hist_kind="input",
             proj_kind="calc", top=False):
        """hist / proj: None, a list of values (None = blank) or a callable(col) -> formula string."""
        b, ws, r = self.b, self.ws, self.r
        ws.write(r, 1, label, b.f(bold=bold, top=top))
        ws.write(r, 2, unit, b.f(color=GREY, top=top))
        ws.write(r, 3, note, b.f(color=GREY, top=top))
        self.rows[key] = r
        self.r += 1
        # cells are written at Book.close(), once every row on every sheet is registered (forward references)
        self.pending.append((r, hist, proj, num, bold, hist_kind, proj_kind, top))
        return r

    def _flush_line(self, r, hist, proj, num, bold, hist_kind, proj_kind, top):
        b, ws = self.b, self.ws
        for block, cols, kind in ((hist, HIST, hist_kind), (proj, PROJ, proj_kind)):
            for i, c in enumerate(cols):
                ci = COLS.index(c) + 4
                is_hist = c in HIST
                if block is None:
                    ws.write_blank(r, ci, None, b.f(num=num, fill=is_hist, top=top))
                    continue
                v = block(c) if callable(block) else block[i]
                if v is None:
                    ws.write_blank(r, ci, None, b.f(num=num, fill=is_hist, top=top))
                elif isinstance(v, str) and v.startswith("="):
                    color = {"calc": BLACK, "link": GREEN, "check": RED}[kind if kind != "input" else "calc"]
                    ws.write_formula(r, ci, v, b.f(num=num, color=color, bold=bold, fill=is_hist, top=top))
                else:
                    ws.write_number(r, ci, float(v), b.f(num=num, color=BLUE, bold=bold, fill=True, top=top))

    def scalar(self, key, label, value, unit="", note="", num="gen", kind="input", col=4):
        """A single-value row (assumption or result) in column E."""
        b, ws, r = self.b, self.ws, self.r
        ws.write(r, 1, label, b.f())
        ws.write(r, 2, unit, b.f(color=GREY))
        ws.write(r, 3, note, b.f(color=GREY))
        if isinstance(value, str) and value.startswith("="):
            ws.write_formula(r, col, value, b.f(num=num, color={"calc": BLACK, "link": GREEN, "check": RED, "input": BLACK}[kind]))
        elif isinstance(value, str):
            ws.write(r, col, value, b.f(color=BLUE, fill=True))
        else:
            ws.write_number(r, col, float(value), b.f(num=num, color=BLUE, fill=True))
        self.rows[key] = r
        self.r += 1
        return r

    # ---- references
    def a(self, key: str, col: str = "E") -> str:
        return f"{col}{self.rows[key] + 1}"

    def aa(self, key: str, col: str) -> str:
        """Absolute same-sheet reference (for fixed anchors such as the FY26 column)."""
        return f"${col}${self.rows[key] + 1}"

    def x(self, key: str, col: str = "E") -> str:
        return f"'{self.name}'!${col}${self.rows[key] + 1}"

    def xr(self, key: str, col: str) -> str:
        """Cross-sheet reference that keeps the column relative (copy-across friendly)."""
        return f"'{self.name}'!{col}{self.rows[key] + 1}"
