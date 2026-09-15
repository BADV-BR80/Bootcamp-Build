"""Layer 1 — LMN (Landscape Management Network) hours adapter.

STATUS: stub. The extraction machinery is in place; the column map below is not
filled in, because it has not been confirmed against a real LMN time export.

When that export arrives, the change is filling in COLUMN_MAP — mapping each
canonical field to the header LMN actually uses. No other code in this module,
and nothing downstream of layer 1, needs to change.

Two LMN-specific things to check against the real file, both anticipated by the
canonical schema rather than worked around here:

1. LMN time tracking can be crew-based rather than per-employee, so
   `employee_ref` may have no source column. It is optional in the canonical
   schema for exactly this reason; map `crew_ref` instead and leave
   `employee_ref` as "" to mark it deliberately absent.
2. LMN's own billable/nonbillable treatment of drive time and shop time must
   NOT be read here, however it is expressed in the export. The activity code
   goes into `ops_code` raw, and the client's convention is applied from the
   `ops_code_map` in client config (spec §3.2 step 2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from .base import OPS, apply_column_map, register

#: {canonical field: LMN export column header}
#: None  = not yet confirmed against a real export
#: ""    = confirmed absent from LMN's export; left null in the canonical table
COLUMN_MAP: dict[str, str | None] = {
    "entry_id": None,
    "date": None,
    "employee_ref": None,
    "crew_ref": None,
    "job_ref": None,
    "ops_service_line": None,
    "ops_code": None,
    "hours": None,
}


class LmnHours:
    source_system = "lmn"
    kind = OPS
    produces = ("hours_entry",)
    description = "LMN time tracking export (stub — COLUMN_MAP not yet filled in)"

    def extract(self, paths: Sequence[Path]) -> dict[str, pd.DataFrame]:
        if not paths:
            raise ValueError("lmn: no input files given")
        frames = [
            pd.read_excel(p) if p.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(p)
            for p in paths
        ]
        df = pd.concat(frames, ignore_index=True)

        mapped = {k: v for k, v in COLUMN_MAP.items() if v != ""}
        out = apply_column_map(
            df,
            mapped,
            source_system=self.source_system,
            table="hours_entry",
            constants={"source_system": self.source_system},
        )
        for canon, src in COLUMN_MAP.items():
            if src == "":
                out[canon] = pd.NA
        return {"hours_entry": out}


register(LmnHours())
