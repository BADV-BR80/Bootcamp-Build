# Data Architecture — DRAFT v0.1

*Status: **draft for review.** Companion to `baseline-plan-build-spec.md`. The spec says what to compute; this says where each piece of it lives and what crosses between the sections.*

---

## 1. The problem this solves

The build has to run against more than one source system — QBO today, plausibly Xero or QBD later; LMN today, plausibly Aspire, SynkedUp or Include later. If source-specific handling is spread through the build, every new system is a rewrite. If it is confined to one layer, every new system is one new adapter and nothing else changes.

Everything below the canonical layer is **written once and never touched again** when a system is added.

---

## 2. Layers

| # | Layer | Source-aware? | Where judgment lives | Built in |
|---|---|---|---|---|
| 0 | **Raw drop** — exports exactly as received, never edited | n/a | none | filesystem |
| 1 | **Adapters** — one per source system, format translation only | **Yes** | **none** | Python |
| 2 | **Canonical tables** — the contract (§3) | No | none | Python → workbook |
| 3 | **Client config** — every judgment call in the build | No | **all of it** | workbook |
| 4 | **Normalize + tie out** — §3.4, §4, §5 | No | applies layer 3 | Python |
| 5 | **Plan build** — §7, §8, §9 | No | none — pure arithmetic | Excel |
| 6 | **Distribution** — §10 | No | none | Excel (curve computed in Python) |
| 7 | **Emission** — §11 QBO budget + COA instruction set | Target-aware | none | Python |

**The Python/Excel handoff is layer 2→3:** Python emits one clean inputs workbook per client, Excel reads it. That boundary is a file a human can open and inspect, which is the point.

---

## 3. The one rule that makes this work

> **Adapters translate format. They never translate meaning.**

An adapter's entire job is to turn one system's export into the canonical shape. It does not decide whether drive time is billable, which service lines roll together, or what "Equipment Rental" means. Every one of those is a per-client judgment (spec §3.2, §4.4, §5) and every one lives in layer 3.

The test: **if an adapter needs to know which client it is running for, the design has failed.** One rule about a specific client inside an adapter turns one LMN adapter into five LMN adapters.

Concretely, this is why the canonical hours record carries `ops_code` but **not** a billable flag. The code is a fact the source system reports; billable-vs-nonbillable is the client's own convention (§3.2 step 2) and is applied from config after the canonical layer.

---

## 4. Canonical tables

### 4.1 `hours_entry` — from any ops system (dataset 3)

One row per time entry.

| Field | Required | Notes |
|---|---|---|
| `entry_id` | Yes | source system's own ID — traceability back to the export |
| `date` | Yes | §3.2 step 4 — the seasonal curve (§10) depends entirely on this |
| `employee_ref` | No | null in crew-based systems where time is not attributed to an individual |
| `crew_ref` | No | |
| `job_ref` | No | traceability only |
| `ops_service_line` | Yes | raw, exactly as the source names it |
| `ops_code` | Yes | raw activity/task code — the input to billable classification |
| `hours` | Yes | |
| `source_system` | Yes | `lmn`, `aspire`, … |

Note the two fields deliberately absent: **no billable flag** and **no financial service line**. Both are config-derived at layer 4.

`employee_ref` is optional because crew-based time tracking may not decompose to individuals. This costs nothing — wage rates come from the roster (§3.3), never from time records.

### 4.2 `gl_monthly` — from any accounting system (dataset 1)

| Field | Required | Notes |
|---|---|---|
| `account_raw` | Yes | account name exactly as exported |
| `account_number` | No | |
| `section_hint` | Yes | REV / COGS / OH / OTH, read from the export's own section structure |
| `month` | Yes | |
| `amount` | Yes | |
| `source_system` | Yes | |

`section_hint` is not authoritative — §4 mapping decides the category. It exists because the gross profit tie (§3.4) needs to know what sits above the line before mapping has run.

### 4.3 `gl_period_by_class` — from any accounting system (dataset 2)

Same fields as `gl_monthly`, but `period_start` / `period_end` in place of `month`, plus:

| Field | Required | Notes |
|---|---|---|
| `class_raw` | No | null is meaningful — it is the unclassed block §3.1 warns about |

### 4.4 `roster` — current employee list (dataset 5)

| Field | Required | Notes |
|---|---|---|
| `employee_ref` | Yes | |
| `name` | Yes | |
| `service_line_raw` | Yes | **required** — without it, per-service-line wage rates (§6.8) cannot be derived |
| `classification` | Yes | `field` or `overhead` — splits C-01 from O-05 |
| `pay_type` | Yes | `hourly` or `salary` |
| `pay_rate` / `annual_salary` | Yes | one or the other per `pay_type` |
| `source_system` | Yes | |

### 4.5 `headcount` — current count by service line (dataset 4)

Derived from `roster` by counting `classification = field` per `service_line_raw`, wherever the roster carries service line. Accepted as a separate input only where it does not. See §6.2 below.

---

## 5. Client config — layer 3

Everything the spec describes as a judgment call, in one place, per client.

| Config table | Spec ref | What it decides |
|---|---|---|
| `ops_code_map` | §3.2 step 2 | ops_code → billable / nonbillable, using the client's own convention |
| `service_line_map` | §5 | ops_service_line → financial service line; produces both grains (§5.3) |
| `account_map` | §4 | normalized account name → standard_category. The registry, `client`-scoped |
| `assumptions` | §6.4 | the assumption register |
| `materiality_threshold` | §4.5 | the cutoff for manual mapping effort |
| `period` | §12 step 1 | historical window and fiscal year |
| `definitional_choices` | §5.5 | drive time treatment, nonbillable definition — recorded for cross-client comparability, never fed back into this client's plan |

The global account registry (§4.6) sits alongside these, shared across all clients rather than per-client.

---

## 6. Consequences worth noting

### 6.1 Adding a source system

One new adapter at layer 1. Nothing at layers 2–7 changes. The work is: read the export format, emit the canonical tables, confirm the tie-outs still pass.

### 6.2 Dataset 4 may collapse into dataset 5

§3 lists headcount-by-service-line and the employee roster as separate datasets, with a cross-check between them (§3.4). But the roster must carry service line anyway — per-service-line wage rates are underivable without it (§6.8). Where it does, headcount is a count over the roster rather than a separate ask, and the cross-check becomes an internal consistency test rather than a reconciliation between two files.

Keep the separate ask only where a client's roster genuinely cannot carry service line. Five required datasets becomes four for most clients.

### 6.3 A richer ops system is a temptation, not an advantage

Some ops platforms report revenue by service line directly, at full operational grain. Using it would appear to dissolve the §5 grain constraint. It does not — it moves the problem. Actuals for budget-vs-actual come out of the accounting system (R9, §11), so a plan built at ops grain still cannot be compared to anything. The constraint is about where actuals *land*, not where revenue can be *seen*.

Revenue always comes from the accounting system. No exceptions by source.
