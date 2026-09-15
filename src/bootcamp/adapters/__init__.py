"""Layer 1 — source system adapters.

Importing this package registers every adapter. Adding a source system means
adding one module here and one import line below; nothing downstream changes.
"""

from .base import (  # noqa: F401
    ACCOUNTING,
    OPS,
    Adapter,
    NotYetMapped,
    apply_column_map,
    get,
    register,
    registered,
)

from . import acct_qbo, ops_generic_csv, ops_lmn  # noqa: F401,E402

__all__ = [
    "ACCOUNTING",
    "OPS",
    "Adapter",
    "NotYetMapped",
    "apply_column_map",
    "get",
    "register",
    "registered",
]
