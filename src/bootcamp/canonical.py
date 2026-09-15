"""Layer 2 — the canonical tables.

This module is the contract between the adapters (layer 1) and everything
downstream. Adding a source system means writing one adapter that emits these
tables; nothing in this file changes.

See `data-architecture.md` §4 for the narrative version of these schemas.
"""

from __future__ import annotations

from dataclasses import dataclass

# Coercion targets understood by validate.py
STRING = "string"
DATE = "date"
DECIMAL = "decimal"
INT = "int"


@dataclass(frozen=True)
class Field:
    name: str
    dtype: str
    required: bool
    notes: str = ""


@dataclass(frozen=True)
class Table:
    name: str
    grain: str
    spec_ref: str
    fields: tuple[Field, ...]
    #: Columns an adapter must never emit, mapped to the reason why.
    #: See `data-architecture.md` §3 — adapters translate format, not meaning.
    forbidden: tuple[tuple[str, str], ...] = ()

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(f.name for f in self.fields)

    @property
    def required_names(self) -> tuple[str, ...]:
        return tuple(f.name for f in self.fields if f.required)

    def field(self, name: str) -> Field | None:
        return next((f for f in self.fields if f.name == name), None)

    def forbidden_reason(self, name: str) -> str | None:
        return dict(self.forbidden).get(name)


_BILLABLE_REASON = (
    "billable vs nonbillable is the client's own convention (spec §3.2 step 2), "
    "so it is applied from config at layer 4 — never decided inside an adapter"
)
_GRAIN_REASON = (
    "financial service line is resolved from the service_line_map in client "
    "config (spec §5), so it is derived at layer 4 — an adapter only reports "
    "the raw name its source system uses"
)
_CATEGORY_REASON = (
    "account mapping to a standard category is layer 4 (spec §4) and depends on "
    "the client- and global-scoped registry — an adapter only reports the raw name"
)


HOURS_ENTRY = Table(
    name="hours_entry",
    grain="one row per time entry",
    spec_ref="dataset 3 (spec §3.2)",
    fields=(
        Field("entry_id", STRING, True, "source system's own ID — traceability back to the export"),
        Field("date", DATE, True, "the seasonal curve (spec §10) depends entirely on this"),
        Field("employee_ref", STRING, False, "null in crew-based systems that do not attribute time to an individual"),
        Field("crew_ref", STRING, False, ""),
        Field("job_ref", STRING, False, "traceability only"),
        Field("ops_service_line", STRING, True, "raw, exactly as the source system names it"),
        Field("ops_code", STRING, True, "raw activity/task code — the input to billable classification"),
        Field("hours", DECIMAL, True, ""),
        Field("source_system", STRING, True, ""),
    ),
    forbidden=(
        ("billable", _BILLABLE_REASON),
        ("billable_flag", _BILLABLE_REASON),
        ("is_billable", _BILLABLE_REASON),
        ("nonbillable", _BILLABLE_REASON),
        ("service_line", _GRAIN_REASON),
        ("service_line_id", _GRAIN_REASON),
        ("financial_service_line", _GRAIN_REASON),
    ),
)


GL_MONTHLY = Table(
    name="gl_monthly",
    grain="one row per account per month",
    spec_ref="dataset 1 (spec §3)",
    fields=(
        Field("account_raw", STRING, True, "account name exactly as exported"),
        Field("account_number", STRING, False, ""),
        Field("section_hint", STRING, True, "REV / COGS / OH / OTH-INC / OTH-EXP, read from the export's own structure"),
        Field("month", DATE, True, "first day of the month"),
        Field("amount", DECIMAL, True, ""),
        Field("source_system", STRING, True, ""),
    ),
    forbidden=(
        ("standard_category", _CATEGORY_REASON),
        ("category", _CATEGORY_REASON),
        ("category_id", _CATEGORY_REASON),
    ),
)


GL_PERIOD_BY_CLASS = Table(
    name="gl_period_by_class",
    grain="one row per account per class, period total",
    spec_ref="dataset 2 (spec §3.1)",
    fields=(
        Field("account_raw", STRING, True, "account name exactly as exported"),
        Field("account_number", STRING, False, ""),
        Field("section_hint", STRING, True, "REV / COGS / OH / OTH-INC / OTH-EXP, read from the export's own structure"),
        Field("class_raw", STRING, False, "null is meaningful — it is the unclassed block spec §3.1 warns about"),
        Field("period_start", DATE, True, ""),
        Field("period_end", DATE, True, ""),
        Field("amount", DECIMAL, True, ""),
        Field("source_system", STRING, True, ""),
    ),
    forbidden=(
        ("standard_category", _CATEGORY_REASON),
        ("category", _CATEGORY_REASON),
        ("service_line", _GRAIN_REASON),
    ),
)


ROSTER = Table(
    name="roster",
    grain="one row per current employee",
    spec_ref="dataset 5 (spec §3.3)",
    fields=(
        Field("employee_ref", STRING, True, ""),
        Field("name", STRING, True, ""),
        Field("service_line_raw", STRING, True, "required — per-service-line wage rates (spec §6.8) are underivable without it"),
        Field("classification", STRING, True, "'field' or 'overhead' — splits plan line C-01 from O-05"),
        Field("pay_type", STRING, True, "'hourly' or 'salary'"),
        Field("pay_rate", DECIMAL, False, "hourly rate; required when pay_type = hourly"),
        Field("annual_salary", DECIMAL, False, "required when pay_type = salary"),
        Field("source_system", STRING, True, ""),
    ),
    forbidden=(
        ("service_line", _GRAIN_REASON),
        ("service_line_id", _GRAIN_REASON),
        ("burdened_rate", "labor burden is derived company-wide from dataset 1 (spec §6.2), not per employee"),
    ),
)


TABLES: dict[str, Table] = {
    t.name: t for t in (HOURS_ENTRY, GL_MONTHLY, GL_PERIOD_BY_CLASS, ROSTER)
}

#: Valid values for the small set of controlled fields.
ENUMS: dict[tuple[str, str], frozenset[str]] = {
    ("gl_monthly", "section_hint"): frozenset({"REV", "COGS", "OH", "OTH-INC", "OTH-EXP"}),
    ("gl_period_by_class", "section_hint"): frozenset({"REV", "COGS", "OH", "OTH-INC", "OTH-EXP"}),
    ("roster", "classification"): frozenset({"field", "overhead"}),
    ("roster", "pay_type"): frozenset({"hourly", "salary"}),
}
