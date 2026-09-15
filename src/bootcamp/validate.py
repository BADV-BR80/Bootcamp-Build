"""Layer 2 — schema enforcement.

Every adapter's output passes through `validate_table` before it is written.
Beyond the usual required-field and type checks, this is where the governing
rule of `data-architecture.md` §3 is made executable: an adapter that tries to
emit a column carrying *meaning* rather than *format* is rejected by name, with
the reason and the layer the decision actually belongs to.
"""

from __future__ import annotations

import pandas as pd

from .canonical import DATE, DECIMAL, ENUMS, INT, STRING, TABLES, Table


class SchemaError(ValueError):
    """Raised when an adapter's output does not match the canonical contract."""


def _fail(table: str, problems: list[str]) -> None:
    bullets = "\n".join(f"  - {p}" for p in problems)
    raise SchemaError(f"{table}: canonical schema violated\n{bullets}")


def _coerce(series: pd.Series, dtype: str, table: str, field: str) -> pd.Series:
    try:
        if dtype == DATE:
            return pd.to_datetime(series, errors="raise")
        if dtype == DECIMAL:
            return pd.to_numeric(series, errors="raise").astype("float64")
        if dtype == INT:
            return pd.to_numeric(series, errors="raise").astype("Int64")
        return series.astype("string")
    except (ValueError, TypeError) as exc:
        raise SchemaError(
            f"{table}.{field}: values are not coercible to {dtype} — {exc}"
        ) from exc


def validate_table(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize one canonical table.

    Returns a copy with columns ordered and typed to the schema. Raises
    `SchemaError` with every problem found, rather than only the first.
    """
    if table_name not in TABLES:
        raise SchemaError(
            f"unknown canonical table {table_name!r} — "
            f"expected one of {', '.join(sorted(TABLES))}"
        )
    table: Table = TABLES[table_name]
    problems: list[str] = []

    missing = [f for f in table.required_names if f not in df.columns]
    if missing:
        problems.append(f"required field(s) absent: {', '.join(missing)}")

    # The architecture guardrail. Checked before the generic unknown-column
    # check so the error explains *why* rather than just saying "unexpected".
    for col in df.columns:
        reason = table.forbidden_reason(col)
        if reason is not None:
            problems.append(
                f"column {col!r} must not be emitted by an adapter: {reason}"
            )

    unknown = [
        c for c in df.columns
        if c not in table.field_names and table.forbidden_reason(c) is None
    ]
    if unknown:
        problems.append(
            f"unrecognized column(s): {', '.join(unknown)}. Adapters emit the "
            f"canonical fields and nothing else; anything extra belongs in "
            f"client config (layer 3) or is a derived value (layer 4)"
        )

    if problems:
        _fail(table_name, problems)

    out = pd.DataFrame(index=df.index)
    for field in table.fields:
        if field.name in df.columns:
            out[field.name] = _coerce(df[field.name], field.dtype, table_name, field.name)
        else:
            out[field.name] = pd.Series([pd.NA] * len(df), index=df.index, dtype="object")

    for field in table.fields:
        if field.required and out[field.name].isna().any():
            n = int(out[field.name].isna().sum())
            problems.append(f"required field {field.name!r} is null in {n} row(s)")

    for (tname, fname), allowed in ENUMS.items():
        if tname != table_name or fname not in out.columns:
            continue
        seen = set(out[fname].dropna().astype(str).unique())
        bad = sorted(seen - allowed)
        if bad:
            problems.append(
                f"{fname}: value(s) {', '.join(repr(b) for b in bad)} outside "
                f"the allowed set {{{', '.join(sorted(allowed))}}}"
            )

    if problems:
        _fail(table_name, problems)

    return out


def validate_all(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Validate a full adapter output. Reports every table's problems together."""
    validated: dict[str, pd.DataFrame] = {}
    errors: list[str] = []
    for name, df in tables.items():
        try:
            validated[name] = validate_table(name, df)
        except SchemaError as exc:
            errors.append(str(exc))
    if errors:
        raise SchemaError("\n\n".join(errors))
    return validated
