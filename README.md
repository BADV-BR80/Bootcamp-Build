# Bootcamp-Build

Build for the 5-5-5 Budget Bootcamp Cohort: collect a client's historical data,
build a baseline annual plan, produce chart-of-accounts restructure instructions,
and emit a monthly budget for import into their accounting system.

## Documents

| File | What it is |
|---|---|
| `baseline-plan-build-spec.md` | The methodology spec (v1.0) — rules, entities, derivations, workflow |
| `data-architecture.md` | **Draft** — the seven layers, the canonical schemas, and where judgment lives |
| `plan-line-definitions.md` | **Draft** — the category and plan-line configuration (`.xlsx` mirror alongside) |
| `reference/PL_Summary_Accounts.xlsx` | Client-supplied summary account list — source of the 18 categories |

## What is built

Layers 0–2 of `data-architecture.md`: raw drop, adapters, canonical tables, and
the handoff workbook that the Excel model will read.

| Layer | Status |
|---|---|
| 0 — raw drop | folder structure in `clients/_template/` |
| 1 — adapters | registry and contract done. `generic_csv` works; `lmn` and `qbo` are wired stubs |
| 2 — canonical + validation | done |
| 2→3 — inputs workbook | done |
| 3 — client config | template workbook only; loader not built |
| 4–7 — normalize, plan, distribute, emit | not started |

The two stubs are stubs for one reason: neither has been seen against a real
export yet. `lmn` needs its `COLUMN_MAP` filled in — nothing else. `qbo` needs
`_parse_pl` written, and the four ragged cases it has to handle are documented
in the module.

## Running it

```bash
pip install -r requirements.txt
export PYTHONPATH=src

python -m bootcamp list-adapters
python -m bootcamp schema hours_entry
python -m bootcamp extract --client _demo --adapter generic_csv \
    --input clients/_demo/raw/ops/hours.csv

python -m pytest
```

`clients/_demo/` holds synthetic data so the pipeline runs on a fresh clone.

## Adding a client

```bash
cp -r clients/_template clients/<client-name>
```

Raw exports and generated outputs are gitignored — client financial data does
not belong in this repository.

## The rule worth knowing

**Adapters translate format. They never translate meaning.**

An adapter turns one system's export into the canonical shape and does nothing
else. It does not decide whether drive time is billable, which service lines
roll together, or what an account means — those are per-client judgments and
they live in client config. The canonical schema enforces this rather than
merely documenting it: `hours_entry` has no `billable` column, so an adapter
that tries to emit one is rejected by name, with the reason and the layer the
decision belongs to.

The test for a new adapter: if it needs to know *which client* it is running
for, the design has failed.
