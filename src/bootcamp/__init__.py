"""Baseline plan build — extract and canonical layers.

Layer 0  raw exports, untouched          clients/<name>/raw/
Layer 1  adapters, format only           bootcamp.adapters
Layer 2  canonical tables + validation   bootcamp.canonical, bootcamp.validate
         handoff to Excel                bootcamp.emit

See data-architecture.md for the full picture and baseline-plan-build-spec.md
for what the numbers mean.
"""

from .canonical import TABLES  # noqa: F401
from .validate import SchemaError, validate_all, validate_table  # noqa: F401

__all__ = ["TABLES", "SchemaError", "validate_all", "validate_table"]
