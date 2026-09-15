"""Command line entry point for the extract and canonical layers.

    python -m bootcamp list-adapters
    python -m bootcamp schema [table]
    python -m bootcamp extract --client demo --adapter generic_csv --input <file> [...]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import adapters
from .canonical import TABLES
from .emit import write_inputs_workbook
from .validate import SchemaError, validate_all

REPO_ROOT = Path(__file__).resolve().parents[2]
CLIENTS = REPO_ROOT / "clients"


def cmd_list_adapters(_: argparse.Namespace) -> int:
    registry = adapters.registered()
    if not registry:
        print("no adapters registered")
        return 1
    width = max(len(k) for k in registry)
    for kind in (adapters.ACCOUNTING, adapters.OPS):
        matching = {k: v for k, v in sorted(registry.items()) if v.kind == kind}
        if not matching:
            continue
        print(f"\n{kind}:")
        for key, adapter in matching.items():
            print(f"  {key:<{width}}  {adapter.description}")
            print(f"  {'':<{width}}  produces: {', '.join(adapter.produces)}")
    print()
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    names = [args.table] if args.table else list(TABLES)
    for name in names:
        if name not in TABLES:
            print(f"unknown table {name!r}; known: {', '.join(TABLES)}", file=sys.stderr)
            return 1
        table = TABLES[name]
        print(f"\n{table.name}  —  {table.grain}  ({table.spec_ref})")
        width = max(len(f.name) for f in table.fields)
        for field in table.fields:
            flag = "required" if field.required else "optional"
            print(f"  {field.name:<{width}}  {field.dtype:<8} {flag:<8}  {field.notes}")
        if table.forbidden:
            print("  must never be emitted by an adapter:")
            for col, reason in table.forbidden:
                print(f"    {col} — {reason}")
    print()
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.input]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"input not found: {', '.join(str(m) for m in missing)}", file=sys.stderr)
        return 1

    try:
        adapter = adapters.get(args.adapter)
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 1

    try:
        raw_tables = adapter.extract(paths)
    except adapters.NotYetMapped as exc:
        print(exc, file=sys.stderr)
        return 2
    except NotImplementedError as exc:
        print(exc, file=sys.stderr)
        return 2

    try:
        tables = validate_all(raw_tables)
    except SchemaError as exc:
        print(f"\ncanonical validation failed\n\n{exc}\n", file=sys.stderr)
        return 3

    destination = (
        Path(args.out)
        if args.out
        else CLIENTS / args.client / "output" / "inputs.xlsx"
    )
    written = write_inputs_workbook(
        tables,
        destination,
        client=args.client,
        sources={name: paths for name in tables},
    )
    for name, df in tables.items():
        print(f"  {name:<20} {len(df):>7,} rows")
    print(f"\nwrote {written}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bootcamp", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-adapters", help="show registered source systems")
    p_list.set_defaults(func=cmd_list_adapters)

    p_schema = sub.add_parser("schema", help="print a canonical table's fields")
    p_schema.add_argument("table", nargs="?", help="canonical table name; omit for all")
    p_schema.set_defaults(func=cmd_schema)

    p_extract = sub.add_parser("extract", help="run an adapter and write the inputs workbook")
    p_extract.add_argument("--client", required=True, help="client folder name under clients/")
    p_extract.add_argument("--adapter", required=True, help="source system, e.g. lmn or qbo")
    p_extract.add_argument("--input", required=True, nargs="+", help="export file(s) to read")
    p_extract.add_argument("--out", help="override the output workbook path")
    p_extract.set_defaults(func=cmd_extract)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
