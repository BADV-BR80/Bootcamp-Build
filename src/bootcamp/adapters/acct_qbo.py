"""Layer 1 — QuickBooks Online P&L adapter.

STATUS: stub. Unlike the ops adapters this one cannot be reduced to a column
map, because a QBO P&L export is not a flat table. The parse strategy is
documented below and the structure is in place; `_parse_pl` is the part that
needs a real export to finish.

A QBO P&L export is ragged in four specific ways, and each one has a decision
attached:

1. **Preamble rows.** Company name, report title and date range sit above the
   header row. Find the header row rather than assuming a fixed offset — the
   number of preamble rows varies with report settings.
2. **Indented account hierarchy.** Sub-accounts are indented under parents in
   the first column, sometimes by leading spaces and sometimes by occupying a
   further column. Depth has to be read before names are stripped, because
   `normalized_name` (spec §4.1) removes exactly the leading whitespace that
   carries it.
3. **Interleaved subtotal rows.** "Total Payroll Expenses" sits among the
   detail rows. These must be dropped, not mapped — summing a column that
   contains both detail and subtotals double-counts silently, and the §3.4
   ties are what would catch it much later.
4. **Section headers.** "Income", "Cost of Goods Sold", "Expenses", "Other
   Income", "Other Expenses" appear as label-only rows. These produce
   `section_hint`, which the gross profit tie needs before mapping has run.

The class column in the by-class export carries a null/blank column for
unclassed transactions. That column is kept, not dropped — it is the unclassed
block spec §3.1 warns about, and the §3.4 revenue tie is what surfaces it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from .base import ACCOUNTING, register

#: QBO section labels → canonical `section_hint`. Confirm against a real export;
#: these are the default English labels and clients do rename them.
SECTION_LABELS: dict[str, str] = {
    "income": "REV",
    "revenue": "REV",
    "cost of goods sold": "COGS",
    "expenses": "OH",
    "operating expenses": "OH",
    "other income": "OTH-INC",
    "other expenses": "OTH-EXP",
    "other expense": "OTH-EXP",
}

#: Row labels that are subtotals rather than accounts. Matched case-insensitively
#: on a `startswith` basis after stripping.
SUBTOTAL_PREFIXES: tuple[str, ...] = (
    "total",
    "gross profit",
    "net income",
    "net operating income",
    "net other income",
)


def _parse_pl(path: Path) -> pd.DataFrame:
    """Parse a QBO P&L export into long form.

    Returns one row per (account, column) with section_hint and depth attached.
    Not yet implemented — see the module docstring for the four cases it has to
    handle and the reason each one matters.
    """
    raise NotImplementedError(
        "qbo: _parse_pl needs a real QBO P&L export to finish.\n"
        "The four ragged cases it has to handle are documented in the module "
        "docstring; the section and subtotal tables above are already in place. "
        "Nothing downstream of this function changes."
    )


class QboProfitAndLoss:
    source_system = "qbo"
    kind = ACCOUNTING
    produces = ("gl_monthly", "gl_period_by_class")
    description = "QuickBooks Online P&L export, monthly and by class (stub — _parse_pl unfinished)"

    def extract(self, paths: Sequence[Path]) -> dict[str, pd.DataFrame]:
        if not paths:
            raise ValueError("qbo: no input files given")
        for path in paths:
            _parse_pl(path)
        raise AssertionError("unreachable until _parse_pl is implemented")


register(QboProfitAndLoss())
