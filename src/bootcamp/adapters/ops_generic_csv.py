"""Layer 1 — generic flat CSV hours adapter.

The fallback path, and the one that works today. It expects a CSV whose headers
already are the canonical `hours_entry` field names, which is what you get from
a client who can produce a simple flat time export, or from a hand-built file
while a real system adapter is still being written.

It is also what the test fixtures and the `_demo` client run against, so the
whole pipeline below layer 1 is exercisable before any real export arrives.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from ..canonical import HOURS_ENTRY
from .base import OPS, register


class GenericCsvHours:
    source_system = "generic_csv"
    kind = OPS
    produces = ("hours_entry",)
    description = "Flat CSV whose headers are already the canonical hours_entry fields"

    def extract(self, paths: Sequence[Path]) -> dict[str, pd.DataFrame]:
        if not paths:
            raise ValueError("generic_csv: no input files given")
        frames = [pd.read_csv(p) for p in paths]
        df = pd.concat(frames, ignore_index=True)
        for field in HOURS_ENTRY.fields:
            if field.name not in df.columns and not field.required:
                df[field.name] = pd.NA
        df["source_system"] = self.source_system
        return {"hours_entry": df}


register(GenericCsvHours())
