"""Layer 1 — the adapter contract.

An adapter turns one source system's export into canonical tables. That is its
entire job.

**Adapters translate format. They never translate meaning.**
(`data-architecture.md` §3)

The test is the `extract` signature below: it takes file paths and nothing else.
There is deliberately no `client_id` parameter and no config argument, because
an adapter that needs to know which client it is running for has stopped being
one adapter and become five. Every per-client judgment the spec describes —
the billable convention (§3.2), account mapping (§4), service line grain (§5) —
is applied downstream, at layer 4, from client config.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, Sequence, runtime_checkable

import pandas as pd

OPS = "ops"
ACCOUNTING = "accounting"


@runtime_checkable
class Adapter(Protocol):
    #: Value written into every row's `source_system` column.
    source_system: str
    #: OPS or ACCOUNTING.
    kind: str
    #: Canonical table names this adapter produces.
    produces: tuple[str, ...]
    #: One line for `bootcamp list-adapters`.
    description: str

    def extract(self, paths: Sequence[Path]) -> dict[str, pd.DataFrame]:
        """Read the given export files and return canonical tables."""
        ...


_REGISTRY: dict[str, Adapter] = {}


def register(adapter: Adapter) -> Adapter:
    if adapter.source_system in _REGISTRY:
        raise ValueError(f"adapter {adapter.source_system!r} is already registered")
    _REGISTRY[adapter.source_system] = adapter
    return adapter


def get(source_system: str) -> Adapter:
    try:
        return _REGISTRY[source_system]
    except KeyError:
        known = ", ".join(sorted(_REGISTRY)) or "(none registered)"
        raise KeyError(
            f"no adapter for {source_system!r}. Registered: {known}"
        ) from None


def registered() -> dict[str, Adapter]:
    return dict(_REGISTRY)


class NotYetMapped(NotImplementedError):
    """Raised by a stub adapter whose column map is not filled in yet.

    Carries the list of canonical fields still needing a source column, so the
    message says exactly what a real export has to answer.
    """

    def __init__(self, source_system: str, table: str, unmapped: Sequence[str]) -> None:
        self.source_system = source_system
        self.table = table
        self.unmapped = tuple(unmapped)
        fields = "\n".join(f"  - {f}" for f in unmapped)
        super().__init__(
            f"{source_system}: the column map for {table!r} is not complete yet.\n"
            f"These canonical fields still need a source column:\n{fields}\n\n"
            f"Fill in COLUMN_MAP in the adapter module against a real export. "
            f"No other code needs to change."
        )


def apply_column_map(
    df: pd.DataFrame,
    column_map: dict[str, str | None],
    *,
    source_system: str,
    table: str,
    constants: dict[str, object] | None = None,
) -> pd.DataFrame:
    """Rename a flat source export into canonical columns.

    `column_map` is {canonical_field: source_column_header}. A value of None
    means "not mapped yet" and raises `NotYetMapped` naming every such field.
    `constants` supplies canonical fields the source does not carry as columns
    (typically `source_system`).
    """
    unmapped = [k for k, v in column_map.items() if v is None]
    if unmapped:
        raise NotYetMapped(source_system, table, unmapped)

    missing = [src for src in column_map.values() if src not in df.columns]
    if missing:
        raise ValueError(
            f"{source_system}: export is missing expected column(s) "
            f"{', '.join(repr(m) for m in missing)}. Present: "
            f"{', '.join(repr(c) for c in df.columns)}"
        )

    out = pd.DataFrame(
        {canon: df[src] for canon, src in column_map.items()}, index=df.index
    )
    for key, value in (constants or {}).items():
        out[key] = value
    return out
