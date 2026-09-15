# Baseline Plan Build Specification
### v1.0

*Self-contained. Everything required to collect a client's historical data, build a baseline annual plan, produce chart-of-accounts restructure instructions, and deliver a monthly budget for import into the accounting system.*

*Scope: this covers **Layer 1** — the baseline plan. Initiatives (Layer 2) are summarised in §15 for context but are not required to complete the four steps below.*

---

## 0. The four steps

1. **Collect** historical and current-state data — §3
2. **Normalize and build** the baseline plan — §4 through §10
3. **Produce COA restructure instructions** — §11.3
4. **Emit a monthly budget** for import — §11.1

§12 is the operating sequence across all four.

---

## 1. What this produces

A driver-based annual budget for a service business, anchored to current operating reality.

The build has two layers, and **the first one is a complete plan on its own.**

**Layer 1 — the Baseline Plan.** Documented current state, annualized: **today's cost structure paired with historical productivity rates.** What the machine the company already has produces over a full year, given a small set of stated assumptions. This is not a draft or a starting point for negotiation. It is a finished, defensible plan, and a company that adds nothing to it has a real budget for the year.

That formulation is the whole design. Current wages, current headcount, current vehicle count — the cost side is what they are paying today. Revenue per man hour, nonbillable rate, and material consumption — the productivity side is what they actually achieved. Neither half is borrowed from anywhere else.

**Layer 2 — Initiatives.** Everything the company wants *above* current output — more revenue, better margin, higher efficiency. Each one closes a specific piece of the gap between current state and desired state, and each is substantiated: a logic, an owner, a completion requirement, and a date, linked to the *how*.

Principles that hold across both:

- **Revenue is calculated, never entered**
- **Baseline comes from history and current state, never from judgment**
- **Every departure from baseline is an owned initiative**, structurally, not by convention

Inputs are historical facts and current counts, plus a short assumption register. Everything else is derived.

### 1.1 Why this is built per company, not to a standard

**No industry standards enter the baseline.** A benchmark that says this service line "should" run at $160 per man hour produces a plan the company was never going to hit, and a set of KPIs it misses from month one. The number that belongs in the baseline is the one their own operation produced.

This holds all the way down to definitional choices. Whether drive time is billable, which ops codes count as nonbillable, how service lines are bounded — these will differ between companies, and **that difference is the product, not an error to normalize away.** Each company gets a plan specific to their operation, their machine.

The consequence is what makes the plan usable: anything the company wants above current output has nowhere to hide. It cannot be absorbed into an optimistic assumption, because every assumption traces to their own actuals. It has to become an initiative with an owner, a logic, a completion requirement, and a date. **Ambition with teeth instead of wishes in a spreadsheet.**

---

## 2. Governing rules

These constrain the whole build. Violating any of them breaks the model's usefulness rather than just its tidiness.

**R1 — Revenue is an output.** `headcount × hrs/head × (1 − nonbillable %) × RPMH`. There is no revenue input cell anywhere.

**R2 — Baseline comes from history and current state, never from judgment.** Today's cost structure paired with historical productivity rates. RPMH, nonbillable %, and COGS rates are calculated from that company's own actuals. Headcount, wages, and vehicle count are current. Hours per head is a stated assumption. **No industry benchmark enters the baseline** — a borrowed number produces a plan the company was never going to hit (§1.1).

**R3 — Baseline ≠ historical revenue.** The difference is the annualization effect (mid-year hires, partial season, understaffed months). It is information and gets reported, not reconciled away.

**R4 — Plan = baseline + initiatives.** Plan values are *derived*, not typed. The only way to move a plan number is to add an initiative that moves it. See §7.

**R4a — The baseline alone is a complete plan.** Layer 1 ships with an empty initiative register and is finished work, not a draft.

**R5 — Historical headcount is never collected.** Unreliable, painful to derive, unnecessary.

**R6 — Two grains, both annual at input.** The plan is built annually from current state. Distribution across periods is a separate, later step (§10). Nothing is collected weekly or monthly.

**R7 — Above the line is per service line; below the line is company-wide.** Revenue and COGS carry a service-line dimension. Overhead, other income, and other expense do not.

**R8 — Nonbillable rate is an hours lever, not an RPMH lever.** RPMH is revenue ÷ *billable* hours. Cutting nonbillable buys more billable hours at the same RPMH. Separate dial, separate owner.

**R9 — The output structure is set by what the company can pull.** The finished budget lands in the same shape their actuals arrive in — account × month, importable to the accounting system — so they can run budget vs. actual themselves without manipulation. The COA restructure that enables this is *downstream* of the mapping, not a prerequisite. See §11.

**R10 — A driver earns a bucket only if it is worth watching.** An account gets its own driver if the resulting metric is something a function would put on a scorecard and act on. If nobody would watch it, it belongs in the inflation bin. This test is self-limiting — nobody wants a thirty-metric dashboard — and it disciplines both the model and the manual mapping effort (§4.5).

---

## 3. Source datasets and transformation

Everything in §6 onward describes **normalized** inputs. Those are not what a client hands over. Five raw datasets come in and are transformed into the configured buckets first.

This is the **one-time historical pull** used to build the plan. It is a different and much larger set than the ongoing in-flight feed that measures against the plan once the year is running — that is two datasets, revenue and hours. Do not conflate them: this list is heavy because it runs once.

| # | Raw dataset | Grain | Produces |
|---|---|---|---|
| 1 | **P&L by month** | Company-wide, monthly | Overhead actuals, labor burden rate, company totals, monthly shape |
| 2 | **P&L by service line, full** | Service line, **period total** | Revenue and COGS by service line → service-line COGS rates. Below-the-line rows are collected but unused |
| 3 | **Hours export** | Transaction-level, dated, ops service line | Billable hours by financial service line, company nonbillable pool, seasonal curve |
| 4 | **Current headcount by service line** | Service line, point-in-time | `field_headcount` |
| 5 | **Current employee list with wage details** | Employee, point-in-time | Current field wage rate |

Datasets 1–3 are historical. Datasets 4–5 are **current state**, which is why the baseline reflects today's cost structure rather than the historical period's.

**This is the required minimum, and nothing else is collected by default.** Company driver counts — vehicles, facilities, equipment units — are deliberately absent. Those costs already sit in the P&L and roll forward through the inflation bin, so the baseline is complete without them. A count is requested only when that bucket earns its own driver, which is a materiality decision made during the build (R10), not a precondition for starting one.

### 3.1 Dataset 2 — full P&L, period total

**Pull the full P&L by service line, not an above-the-line extract.** Restricting the report to above-the-line is awkward in most accounting-system interfaces and does not scale across a set of clients. A full P&L filtered only by date is a one-step pull, and everything above the line is in it. Below-the-line rows come along and are ignored — overhead is taken from dataset 1 at company grain (R7).

**Watch for unclassed transactions.** Transactions with no service line assigned surface as their own column or section. Above the line, that is precisely what the revenue and gross profit ties in §3.4 are for — an unclassed block means service-line revenue and COGS will not sum to the company totals, and the gap has to be resolved with the client rather than absorbed. Expect this at companies that tag inconsistently.

**Use the period as a whole, not an average of monthly ratios.** COGS rates are computed from the period total. Monthly COGS-to-revenue is noisy in a service business: material purchases, subcontractor invoices, and revenue recognition rarely land in the same month. The period total gives a materially more accurate picture of what each service line actually consumes per revenue dollar.

Monthly grain is still needed — from dataset 1, for company-level seasonality and the overhead distribution — but not for rate derivation.

### 3.2 Dataset 3 — the hours transformation

The heaviest transformation in the build.

1. **Map ops service lines to financial service lines.** These will usually not match. Ops systems carry more granularity than the chart of accounts, so the mapping is many-to-one and rolls up (see §5).
2. **Classify billable vs nonbillable** by ops code, **using the company's own convention.** Whether drive time is billable is the common divergence, and there is no right answer to impose — their classification is what produced their historical rates.

   Record the choice, for two reasons. First and non-negotiably: **internal consistency.** The definition used to derive the baseline must be the same one used to measure against it. If drive time is billable in the history, it is billable in the weekly scorecard, or every variance is partly an artifact of the definition changing underneath the number.

   Second, and strictly secondary: it tells you later whether two companies' figures are comparable, which matters only for building normative bands across engagements. **That never reaches back into a client's plan.** Adjusting a company's numbers toward a shared convention is the same failure as quoting them an industry benchmark — a borrowed reality replacing their own.
3. **Aggregate** to billable hours by financial service line, and nonbillable hours as a single company pool (§6.2).
4. **Retain the date dimension.** The same file produces the weekly seasonal curve by service line — no separate ask, and no need to construct a year-one curve from monthly totals.

### 3.3 Dataset 5 — wage rates from current roster

The field wage rate baseline comes from the **current employee list**, not from historical payroll. Raises and market movement since the historical period are therefore already reflected, consistent with the rule that the baseline is what the machine produces *today*.

Labor burden rate is derived separately from dataset 1 — payroll taxes, benefits, and workers' comp over total wages, company-wide.

### 3.4 Tie-out validation

Run before anything downstream. These catch the omissions that quietly corrupt every rate derived from them.

| Check | Rule |
|---|---|
| **Revenue tie** | Σ service-line revenue (dataset 2) = company period revenue (dataset 1) |
| **Gross profit tie** | Σ service-line gross profit (dataset 2) = company period gross profit (dataset 1) |
| **COGS** | Reconciles by arithmetic once both above pass |
| **Headcount cross-check** | Σ headcount (dataset 4) is consistent with the field employee count in dataset 5 |
| **Hours coverage** | Hours export period matches the P&L period exactly |

Both the revenue and gross profit ties are required. Revenue alone leaves COGS omissions invisible; gross profit alone hides offsetting misstatements where revenue and COGS are both wrong by the same amount. Together they close both gaps.

A failed tie is a **data problem to resolve with the client**, not a variance to allocate away.

### 3.5 A note on the chart of accounts

The client's QBO chart of accounts is restructured so their accounts roll into the standard categories inside QBO. That is what makes the round trip work (§11).

**It happens after this stage, not before.** The mapping produced here is what defines the target structure — restructuring first would mean guessing at it. See §11.3 for the sequence and the instruction set.

---

## 4. Normalization — account mapping

### 4.1 Structure

One row per known mapping.

| Field | Description |
|---|---|
| `raw_name` | Account name exactly as it appears in the source |
| `normalized_name` | Lowercased, punctuation stripped, whitespace collapsed, leading account numbers removed |
| `standard_category` | Target category from the canonical list |
| `scope` | `global` or `client` |
| `client_id` | Populated only when scope = `client` |
| `driver` | Inherited from category default; overridable |
| `driver_override_reason` | Required if driver differs from the category default |
| `resolution_method` | How it was resolved (§4.3) |
| `resolved_by` | Person, for manual resolutions |
| `resolved_date` | |
| `generalizable` | Boolean — set at resolution time (§4.4) |
| `promotion_count` | Number of distinct clients where this mapping resolved identically |

### 4.2 Scope is the load-bearing field

Two exception types look identical at resolution time and must not be treated the same.

**Type 1 — novel name, known concept.** "Promo & Trade Shows" → Advertising and Marketing. Universally true. Adding it to the registry as `global` fixes it for every future client permanently. High generalization, no risk.

**Type 2 — genuinely ambiguous concept.** "Equipment Rental" is job-cost at a company that rents per-job and overhead at a company holding a standing lease. "Vehicle Repairs" splits the same way. **The correct answer differs by company.** Learning it from client one and auto-applying it to client two produces a confident wrong mapping — worse than no mapping, because an unmapped account gets reviewed and a wrongly-mapped one never does.

**Default scope for any manual resolution is `client`.** Global is an explicit promotion, never an inference.

### 4.3 Resolution order

Applied in sequence; first match wins.

| Order | Method | Confidence |
|---|---|---|
| 1 | Client-scoped exact match on `normalized_name` | Highest |
| 2 | Global exact match on `normalized_name` | High |
| 3 | Global keyword / pattern rule | Medium — flag for review |
| 4 | Below materiality threshold → inflation bin | Auto, no review |
| 5 | Unresolved → manual queue | — |

Every mapped account carries its `resolution_method` into the output. This makes operator review a scan of medium-and-below rows rather than a re-read of everything, and it shows which keyword rules are actually earning their place across clients.

### 4.4 Manual resolution: ask the driver question

For genuinely ambiguous accounts, do not ask *which category does this belong to.* Ask **what makes this number move.**

> Equipment Rental — does it scale with jobs and hours, or is it fixed regardless of volume?
> - Scales → job cost, hours driver
> - Fixed → overhead, inflation bin

The driver answer determines the category answer. It is an easier question because it is operational rather than taxonomic, and the person who knows it is the client rather than the analyst.

**Safe fallback:** when the driver genuinely cannot be identified, the inflation bin is correct by definition — "no identifiable driver" is exactly what that bin means (§9). An unresolvable account is not a blocker.

**At every manual resolution, capture `generalizable`.** Would this mapping be correct at any client, or only this one? Cheap to answer in the moment; impossible to reconstruct later. This single field is what keeps the registry from degrading as it grows.

### 4.5 Materiality cutoff

Sort unmapped accounts descending by annual dollar value. Resolve down to the threshold; sweep everything below it into the inflation bin without review.

This is R10 applied to mapping effort rather than to bucket count. An account too small to earn a KPI is too small to earn a judgment call — it cannot move net profit enough to matter.

The long tail of oddly-named small accounts is where manual review time disappears, and it is precisely the part that does not affect the plan.

**[OPEN — client-specific]** Threshold value. Candidates: fixed dollar amount, percent of total opex, or "accounts covering the top 80% of spend." Set per engagement; record the value used.

### 4.6 Promotion to global

A `client`-scoped mapping becomes a promotion candidate when:

- `generalizable` = true, **and**
- the same `normalized_name` → `standard_category` has resolved identically at **3 or more distinct clients**

Promotion requires human approval. **Never auto-promote on frequency alone** — three companies in one vertical making the same choice is a plausible coincidence, and a wrong global entry is invisible once written.

---

## 5. Normalization — service line grain

### 5.1 The constraint

The operations system and the accounting system may distinguish service lines at different granularity. Five ops service lines feeding two accounting-system classes is the common case.

**Any metric requiring both systems is capped at the coarsest common grain.** Building the financial plan at five when actuals only arrive at two would require manual allocation to compare plan against actual — reintroducing exactly the subjectivity this structure exists to eliminate. Build at the grain you report at; everything coarser is a roll-up, and nothing is ever allocated downward.

### 5.2 The constraint is per-metric, not global

This is the refinement that preserves the useful granularity.

| Metric | Source | Grain |
|---|---|---|
| Total hours | Ops only | **Operational grain** (full ops detail) |
| Billable / nonbillable split | Ops only | Operational grain |
| Field headcount | Ops only | Operational grain |
| Seasonal curve | Ops only | Operational grain |
| Revenue by service line | Both | **Financial grain** (common) |
| RPMH | Both | Financial grain |
| Gross margin by line | Both | Financial grain |

Hours are planned and scorecarded at full operational detail; anything touching revenue rolls up to the common grain. The Ops scorecard runs at five service lines while the financial view runs at two.

**The threshold test outputs two values, not one:** operational grain and financial grain.

### 5.3 Determining the common grain

Not always a simple count comparison. The common grain is **the coarsest partition both systems can resolve to**: group ops service lines into the smallest set of buckets where each bucket maps wholly into one accounting class, and each class maps wholly into one bucket.

- Clean many-to-one (5 ops → 2 classes) → financial grain is the 2 classes
- Partial overlap (an ops line splitting across two classes) → those lines merge into one bucket, coarsening the result further
- 1:1 alignment → operational and financial grain are identical, no constraint

### 5.4 The gap is a finding, not just a constraint

A client whose ops system distinguishes five service lines while their books distinguish two **cannot see profitability by service line.** That is a concrete, material gap and it should be delivered as such.

The remedy is a class restructure in the accounting system, not a process overhaul — cheap to fix, and it upgrades every subsequent plan. Deliver it with the baseline plan rather than burying it in a mapping note.

### 5.5 Configuration variance

Constraining source systems removes mapping variance. It does not remove **configuration** variance.

Two companies on the same ops system can define service lines differently or code drive time differently. Two accounting files on the same platform can have charts of accounts customized past recognition. The endpoints are identical; what flows through them is not.

This does not threaten a single build — the mapping still resolves. It threatens **comparability across clients**, which matters only if cross-client benchmarks are ever built. It never reaches back into a client's plan.

**Requirement:** during build, record the definitional choices that affect comparability — at minimum how nonbillable is defined and whether drive time is billable. Store alongside the client's registry entries. Without it, cross-client dispersion figures are not comparable and normative bands cannot be built.

---

### 5.6 Service line name registry

Service line names use the same registry structure as §4.1, with the same scope discipline. Service line naming is **more client-idiosyncratic** than account naming, so expect the `global` set to stay small and the `client` set to carry most entries. That is the correct outcome, not a failure of the registry.

---

## 6. Entities

### 6.1 `service_line`
The client's service lines at **financial grain** — the coarsest partition both the ops system and the accounting system can resolve to (see §5).

| Field | Notes |
|---|---|
| `service_line_id` | |
| `name` | |
| `ops_lines_mapped` | Which ops-system lines roll into this |

### 6.2 `historicals`
For a stated period (TTM or the most recent clean window). Sourced from invoicing and payroll — the two most reliable datasets in a service business.

**Per service line:**

| Field | Source |
|---|---|
| `revenue` | Dataset 2 — P&L by service line, above-the-line rows |
| `cogs_by_category` | Dataset 2 — one value per COGS category, period total |
| `billable_hours` | Dataset 3 — hours export, rolled up |

**Company-wide, one value:**

| Field | Source |
|---|---|
| `nonbillable_hours` | Dataset 3 — hours export, all ops NB codes |
| `overhead_by_category` | Dataset 1 — P&L by month, period total |
| `labor_burden_rate` | Dataset 1 — payroll taxes + benefits + comp ÷ total wages |

**Nonbillable hours are NOT collected by service line.** Splitting them would require a parallel `NB-[SL]` time code for every service line code, doubling the code list and making field time entry materially messier. Almost no company does this. A driver that cannot be reliably fed is not a driver, however well it explains the underlying economics — so the pool is the correct structure, not a compromise.

Treat nonbillable as **its own service line with no revenue** when handling hours. The company nonbillable rate is derived from the pool and applied as the default across every service line; §7.1 covers reallocation when a service-line-specific rate is asserted.

Plus a period label recorded once.

### 6.3 `current_state`
Per service line.

| Field | Type | Notes |
|---|---|---|
| `field_headcount` | Current count | Point-in-time, trivially available |
| `annual_hours_per_head` | Assumption | Default 2,000. Owned and stated, not derived |

> **Decision needed:** whether `annual_hours_per_head` is per service line or one company-wide value. Per service line is correct if season lengths or overtime patterns genuinely differ; otherwise a single value prevents accidental drift.

### 6.4 `assumption`
The assumption register. Baseline + assumptions = the plan, so **these are the only things in Layer 1 that are not facts** — which makes them the only things a client can dispute. They ship with the baseline plan and are accepted explicitly.

| Field | Notes |
|---|---|
| `assumption_id` | |
| `description` | Plain language |
| `value` | |
| `scope` | Company, or a specific service line |
| `owner` | Who is accountable for it holding |
| `basis` | Why this value — client statement or prior-year pattern. See below on industry norms |

**On industry norms as a basis.** The baseline never borrows an industry figure for something the company already does (§1.1) — their own actuals are the only valid source there. The narrow exception is where **no in-house baseline exists at all**: a service line the company is adding in the plan year has no history to derive from, and an industry norm is a defensible starting point because the alternative is no number.

When used, it is recorded as such, owned, and replaced by actuals as soon as the line has a period of history. An industry norm standing in for a rate the company *could* have derived is a benchmark in disguise.

Typical Layer 1 set, and it should stay short:

- Annual hours per head (default 2,000)
- General inflation rate (default 5%)
- Current rates persist — RPMH, nonbillable %, and cost rates hold at historical levels
- Any service-line nonbillable % asserted against the company pool (§7.1) — each one forces a residual onto the other lines, so each is a real claim requiring a basis
- Current headcount is retained through the year

That last pair is worth stating out loud rather than leaving implicit. "We assume you keep the crew you have and perform at the level you performed" is an assumption, and clients often want to argue with it — which is a productive argument to have at kickoff rather than in month four.

### 6.5 `category`
The reporting roll-up. Roughly 18 summary accounts: 1 revenue, 5 COGS, 10 overhead, 1 other income, 1 other expense.

| Field | Notes |
|---|---|
| `category_id` | |
| `name` | |
| `section` | REV / COGS / OH / OTH-INC / OTH-EXP |

### 6.6 `plan_line`
The buildable unit. A terminal category has one; a category needing deeper treatment has several (Payroll [Field] → Wages + Labor Burden).

| Field | Notes |
|---|---|
| `line_id` | |
| `category_id` | |
| `name` | |
| `scope` | `service_line` or `company` (R7) |
| `driver_type` | `primary`, `derived`, or `inflation` |
| `driver_ref` | For `primary`: a `driver_id`. For `derived`: another `line_id`. Blank for `inflation` |
| `basis` | e.g. "% of revenue", "rate per hour", "% of dollars" |
| `is_kpi` | Whether this appears on a scorecard |

Rules:
- Depth capped at two levels. A `derived` line may not reference another `derived` line.
- A `service_line`-scoped line may not derive from a `company`-scoped line.
- A `derived` reference resolves **at the scope of the referencing line** — service-line to service-line resolves *within the same service line* (Materials [Install] = % of Revenue [Install], not of total revenue).

### 6.7 `driver`
Two kinds.

**System drivers** — calculated on the volume build, referenced by plan lines: `BILLABLE_HOURS`, `TOTAL_HOURS`, `REVENUE`. Service-line scoped.

**Company drivers** — entered: inflation rate, plus any count a bucket has earned (vehicles, facilities, equipment units). Company scoped.

Most overhead never gets a company driver. It lands in the inflation bin, and the count is requested only once the bucket clears the materiality test (R10) — which is why no counts appear in the required dataset list.

| Field | Notes |
|---|---|
| `driver_id` | |
| `name`, `unit` | |
| `scope` | `service_line` or `company` |
| `baseline` | Current count, requested ad hoc when the bucket earns a driver. Calculated for system drivers |
| `distribution` | `flat`, `seasonal`, or `event` — how the annual figure spreads (§10) |

### 6.8 `rate`
Resolves the many-to-many between plan lines and service lines. **The rate is a property of the line × service line intersection, not of the line.** Materials isn't 30% — Materials-at-Install is 30% and Materials-at-Maintenance is 10%.

| Field | Notes |
|---|---|
| `line_id` | Service-line-scoped lines only |
| `service_line_id` | |
| `baseline` | **Derived from actuals.** COGS rates come from dataset 2: `cogs_by_category(line, service_line) ÷ revenue(service_line)` for %-of-revenue lines. Wage rate comes from the current employee roster (§3.3) |
| `plan` | Derived — baseline + initiative impacts (R4) |

Revenue lines are excluded — revenue is produced by the volume build, not by a rate.

**These rates are facts, not assumptions.** Because dataset 2 reports the P&L *by service line*, Materials-at-Install and Materials-at-Maintenance are both directly derivable. Nonbillable hours are the exception — they arrive as a single company pool and require the allocation in §7.1. No other rate does.

### 6.9 `initiative`
The only mechanism by which a plan value differs from baseline.

| Field | Notes |
|---|---|
| `initiative_id` | |
| `target_type` | `driver`, `rate`, or `volume_input` |
| `target_ref` | The `driver_id`, `line_id`, or volume field affected |
| `service_line_id` | Where applicable |
| `impact` | The delta applied to baseline |
| `owner` | A person |
| `function` | Leadership / Finance / Sales / Ops / HR |
| `description` | Specific enough to act on — "forego X conference, ~$10K" not "reduce overhead" |
| `logic` | Why this impact is achievable — the *how* |
| `completion_requirement` | Definition of done. Distinct from the date: "foreman onboarded and running a route" is a requirement; "by Q3" is a date |
| `target_date` | |
| `effective_period` | When impact begins — a mid-year hire delivers partial-year hours |

---

## 7. Derivations from history

### 7.1 Nonbillable rate and its allocation

**Basis, fixed everywhere:** `nonbillable_rate = nonbillable_hours / total_hours`, where `total_hours = billable_hours + nonbillable_hours`. Never NB ÷ billable. The plan build consumes it as `billable = total × (1 − NB%)`, so a mixed basis silently corrupts the hours chain.

**Company rate:**
```
company_total_hours = Σ billable_hours(all service lines) + company_nonbillable_hours
company_NB%         = company_nonbillable_hours / company_total_hours
```

**Default:** every service line inherits `company_NB%`. With no assumptions entered, the build is complete and reconciles by construction.

**Reallocation when a service line rate is asserted.** A service-line NB% assumption is a claim about how the historical pool was *actually* distributed. The pool is a fact, so the assumption is **zero-sum** — asserting one line's rate forces the residual onto the others.

```
for each service line i with an asserted NB%:
    total_i = billable_i / (1 − NB%_i)
    NB_i    = total_i − billable_i

residual_pool = company_nonbillable_hours − Σ NB_i

for each remaining service line j:
    NB_j    = residual_pool × (billable_j / Σ billable(remaining lines))
    total_j = billable_j + NB_j
    NB%_j   = NB_j / total_j
```

**Worked example.** Install billable 4,500; Maintenance billable 4,500; company nonbillable 2,250.

Company NB% = 2,250 ÷ 11,250 = **20%**. Assumption entered: Install NB% = 10%.

| | Billable | NB | Total | NB % |
|---|---|---|---|---|
| Install | 4,500 | 500 | 5,000 | 10.0% |
| Maintenance | 4,500 | 1,750 | 6,250 | **28.0%** |
| **Company** | 9,000 | 2,250 | 11,250 | 20.0% |

Install: 4,500 ÷ (1 − 10%) = 5,000 total, so 500 nonbillable. Residual 1,750 falls to Maintenance, giving 1,750 ÷ 6,250 = 28%.

Hours reconcile and the pool is conserved. That conservation is the point: **every derivative in the plan stays anchored to a fact the company actually produced.**

### 7.2 Assumption vs. initiative — same number, different mechanics

This distinction decides what happens to the *other* service lines, and it is easy to get wrong.

| | **Assumption** | **Initiative** |
|---|---|---|
| Claim | Install *was already* running at 10% | Install *will be changed* to 10% |
| Pool | Conserved — the 2,250 is fact | Reduced — fewer nonbillable hours overall |
| Install baseline | 10% | 20% (company default) |
| Maintenance | Forced to 28% | **Unaffected at 20%** |
| Requires owner | No | Yes — plus logic, completion requirement, date |

An assumption redistributes history. An initiative changes the future. Recording a planned improvement as an assumption both overstates Maintenance's nonbillable rate and hides the improvement from the initiative register, where its owner and its measurement live.

### 7.3 Revenue per man hour

```
RPMH = revenue / billable_hours
```

Per service line, from historical facts only. Never entered.

### 7.4 Direction of the hours calculation

Note that the chain runs opposite ways in the two contexts, which is correct:

- **Historical:** billable hours are known; NB% is derived or asserted; total is derived.
- **Plan:** total hours are known (`headcount × hrs/head`); NB% is planned; billable is derived.

This is why reducing nonbillable rate in the plan *increases billable hours* rather than reducing total hours — the crew works the same hours, more of them billable.

---

## 8. The Baseline Plan

**This is a complete plan.** It requires no initiatives, and shipping it with an empty initiative register is a valid, finished deliverable.

Per service line:

```
baseline_total_hours    = field_headcount × annual_hours_per_head
baseline_billable_hours = baseline_total_hours × (1 − nonbillable_rate_i)
baseline_revenue        = baseline_billable_hours × RPMH_i
```

where `nonbillable_rate_i` is the service line's rate after §7.1 allocation — the company default unless an assumption asserted otherwise.

Report `baseline_revenue − historical_revenue` as the **annualization effect** (R3).

Layer 1 output is the full P&L: baseline revenue and COGS per service line (§9), company overhead, and net profit — accompanied by the assumption register (§6.4). Together these say: *this is your year if nothing changes, given these assumptions.*

**Worked example.** Install: historical revenue $1M, billable 5,000 hrs, nonbillable 1,250 hrs, current headcount 4, hrs/head 2,000.

| | |
|---|---|
| RPMH | $1,000,000 ÷ 5,000 = **$200** |
| Nonbillable rate | 1,250 ÷ 6,250 = **20%** |
| Baseline total hours | 4 × 2,000 = **8,000** |
| Baseline billable hours | 8,000 × 0.80 = **6,400** |
| Baseline revenue | 6,400 × $200 = **$1,280,000** |
| Annualization effect | $1,280,000 − $1,000,000 = **+$280,000** |

---

## 9. Cost and overhead build

**COGS** — per service line, per plan line, by `driver_type`:

| Type | Calculation |
|---|---|
| `primary` | `driver value (this service line) × plan rate` |
| `derived` | `referenced line's value (same service line) × plan rate` |
| `inflation` | `prior year actual × (1 + inflation rate)` |

Wages key off `TOTAL_HOURS`, not billable — nonbillable hours are paid.

**Overhead** — company scope, no service-line dimension. Most lines land in the inflation bin by default. A line earns its own driver only if it would be worth watching as a KPI.

**Roll-up:**
```
Revenue (sum of service lines)
− COGS (sum of service lines)
= Gross Profit
− Overhead
+ Other income − Other expense
= Net Profit
```

Net profit is the arbiter. Every initiative is ultimately justified by its effect on it.

---

## 10. Distribution to periods

The plan is built annually, then distributed. This is a separate step and it is where the seasonal shape enters.

| `distribution` | Behavior |
|---|---|
| `flat` | Even across periods |
| `seasonal` | Follows the service line's seasonal curve |
| `event` | Lands on a specified date (equipment purchase, a hire) |

The seasonal curve is weekly field hours by service line, following historical volume and billable-split patterns.

**Year-one caveat:** deriving that curve needs weekly historical hours by service line, which many clients won't have. In that case the curve is *constructed* from monthly totals plus known operational structure (season start and end, working weeks, crew schedules, holiday weeks) and labeled an assumption with an owner. Year one's actual capture produces a real curve for year two.

Initiatives carry `effective_period`, so a March hire contributes roughly 10/12 of annual hours rather than a full year.

---

## 11. Output structure — the round trip

The raw exports in §3 do more than supply inputs. **They define the structure the finished budget must land in**, because they are what the company can readily pull for actuals once the year is running.

If the budget lives in a shape that doesn't match how their actuals come out, budget-vs-actual requires manual manipulation every month. Which means it won't happen — and the plan quietly becomes a document nobody opens after February.

### 11.1 The deliverable

**A QBO-importable budget: account × month, for the fiscal year, by class where service-line detail is wanted.**

The company then pulls budget vs. actual natively, in the system they already use, without the advisor in the loop and without a separate reporting tool.

### 11.2 What this requires of the build

**Monthly grain is mandatory.** The distribution step (§10) is not an optional refinement — an annual figure cannot be imported. Every plan line produces twelve values.

**Where the COA was restructured (§11.3), there is no reverse mapping.** The standard categories exist as real QBO accounts, so the monthly budget pushes directly to the accounts the actuals already land in. This is the intended path, and the reason restructuring is worth requiring.

**Where it was not**, the registry has to run backward: a category's monthly budget redistributes across the client accounts that rolled into it.

```
account_budget(a, month) = category_budget(c, month)
                           × historical_share(a within c)
```

Pro-rata by each account's historical share of its category — their own actuals decide the split, consistent with R2. Accounts with no historical activity receive nothing unless an initiative targets them.

This path carries two hazards the restructured path does not. A one-off can distort a share (a single equipment purchase making one account 80% of its category), and **the same registry version must serve both directions** — if intake and output disagree, budget and actuals land in different buckets and every variance all year is fictional.

**Service-line budgets require classes.** Where the client tags transactions by class at entry, the above-the-line budget can carry the service-line dimension into QBO. Where they don't, the service-line plan remains an advisor-side artifact and only the company-level budget round-trips. This is the same tagging decision that determines whether dataset 2 arrives clean (§3.1), now with a second consequence attached.

### 11.3 COA restructuring — sequence and handoff

Restructuring is required for a direct budget push. It is **downstream of the mapping**, because the mapping is what defines the target structure.

**Sequence**

1. Pull raw exports (§3)
2. Normalize and map to standard categories (§4, §5)
3. Build and ship the baseline plan (§8)
4. **COA restructure** — mechanical, delegable, runs in parallel
5. Push the monthly budget

For a baseline-only engagement that is the whole sequence, and step 4 is the only thing gating step 5.

Where initiatives are being agreed (§15), they slot between steps 4 and 5 and the restructure runs in parallel with them — the plan pushed at step 5 is then the vetted one rather than the baseline. Either way the restructure has the full engagement window, and the budget can be pushed again later if the plan changes.

**The instruction set is an output of the build.** By the end of step 2 the mapping already names every parent account to create and every existing account to reparent. The build emits it as a task list:

```
For each standard category:
  1. Create summary account — name, number, account type, detail type
For each existing account:
  2. Set parent account = its mapped summary account
```

Mechanical, fully specified, and delegable — no judgment is exercised while executing it, because every decision was made during mapping.

**Never merge.** Reparenting preserves detail and history follows the account. Merging in QBO is irreversible and destroys the detail permanently. Consolidation is achieved with sub-accounts under a common parent, never by merging.

### 11.4 Future direction — not in scope

Extending the deliverable to generate weekly ops scorecards from a raw hours export dropped in by the company. Noted as a direction, deliberately excluded from this specification.

---

## 12. Build workflow

The full sequence, from raw exports to a budget in the accounting system.

**1 — Extract**
Pull the five source datasets (§3). Record the historical period once and use it consistently; the hours export period must match the P&L period exactly.

**2 — Normalize accounts**
Apply string normalization to account names, run the resolution order (§4.3), and resolve the manual queue above the materiality cutoff (§4.5) using the driver question (§4.4). Set `scope` and `generalizable` on every manual resolution.

**3 — Resolve service line grain**
Map ops service lines to financial service lines and compute operational and financial grain (§5.3). Record configuration variance (§5.5).

**4 — Tie out**
Run the revenue and gross profit ties (§3.4) before anything downstream. A failed tie is a data problem to resolve with the client, not a variance to allocate away.

**5 — Derive baseline rates**
RPMH, nonbillable rate and its allocation across service lines, COGS rates (§7).

**6 — Build the baseline plan**
Volume and revenue (§8), then cost and overhead (§9). Run validation (§13).

**7 — Distribute to periods**
Apply the distribution method per driver (§10). Every plan line produces twelve monthly values.

**8 — Emit deliverables**
Baseline plan, assumption register, annualization effect, findings, COA restructure instruction set, and the importable monthly budget (§14).

**9 — COA restructure**
Hand off the instruction set (§11.3). Mechanical, delegable, and runs in parallel with everything after step 8.

**10 — Push the budget**
Once the restructure is complete, import the monthly budget. The client then runs budget vs. actual natively.

Steps 1 and 4 through 8 should be automated end to end. **Steps 2 and 3 carry the manual queue** and are the honest measure of whether a build is repeatable by someone other than its designer — track operator time on them per client.

---

## 13. Validation

Run before a plan is considered buildable.

**Structural**
- Every plan line maps to a valid category; every category has at least one plan line
- `line_id` unique
- Every `primary` line references an existing driver; every `derived` line references an existing line
- No cycles; no derived-on-derived; no service-line line deriving from a company line
- `inflation` lines carry no `driver_ref`

**Data**
- Historicals present for every service line (revenue, billable hours)
- Company nonbillable hours present
- Current headcount present for every service line
- Hours-per-head assumption stated

**Nonbillable allocation (§7.1)**
- `residual_pool ≥ 0` — asserted service-line rates cannot consume more nonbillable hours than the company pool contains
- If every service line carries an asserted rate, the implied NB hours must equal the company pool exactly; the system is over-specified otherwise
- Allocated hours reconcile: `Σ NB_i = company_nonbillable_hours`
- Every asserted service-line NB% has a basis recorded, and is classified as assumption or initiative (§7.2)

**Assumptions**
- Every Layer 1 assumption is stated, valued, and owned

**Initiative integrity** *(largely automatic under R4, but worth asserting)*
- **An empty initiative register is valid.** Layer 1 alone is a complete plan; zero initiatives is not a deficiency
- Every initiative has an owner, a completion requirement, a target date, and a valid `target_ref`
- Every initiative's impact is traceable to a specific original budget line
- Initiative impacts are **realizable** — the cost actually releases, or the capacity actually exists

**Confidence**
- Revenue-to-hours correlation by service line. High correlation → tighter bands. Low correlation → wider bands plus a stated caveat, raised with the client before kickoff. This is a confidence qualifier, not a gate.

---

## 14. Outputs

**Layer 1 — shippable on its own:**

1. **Baseline plan** — annual P&L by service line and company, from current state
2. **Assumption register** — the short list of non-facts the plan rests on, each owned
3. **Annualization effect** — baseline vs historical revenue, with cause

**Layer 2 — added as initiatives are agreed:**

4. **Plan P&L** — baseline plus initiatives, distributed to periods
5. **Initiative register** — the full delta between current and desired state, each with logic, owner, completion requirement, and date
**Deliverable format (§11):**

6. **COA restructure instruction set** — parent accounts to create and existing accounts to reparent, derived from the mapping (§11.3). Delegable as written
7. **QBO-importable budget** — account × month, by class where available

**Both layers:**

8. **Driver/KPI list** — plan drivers restated as measurable benchmarks with baselines
9. **Findings** — service-line grain gap, correlation caveats, material accounts defaulted to the inflation bin

---

## 15. Beyond the baseline — Initiatives

*Out of scope for the four steps in §0, and included so the data model reads whole. The baseline plan is complete and shippable without any of this (R4a).*

Initiatives exist to close the gap between **current state** (Layer 1) and **desired state**. Anything a company wants above what its current machine produces — more top line, better margin, higher throughput — arrives here, or it does not arrive at all.

Plan values are computed, not entered:

```
plan_value(target) = baseline_value(target) + Σ initiative.impact
                     where initiative.target_ref = target
```

Applied to every plannable quantity: headcount, hours per head, nonbillable rate, RPMH, every rate, every company driver.

Consequences, all of which come free from the structure:

- An orphan delta is impossible. A plan number cannot differ from baseline without an initiative behind it.
- Every change traces to a named owner and a target date.
- Deleting an initiative reverts the plan automatically.
- Scenario analysis is initiative toggling, not re-entry.
- The initiative list *is* the difference between current reality and the plan — which is exactly what a leadership conversation needs.

Then:

```
plan_total_hours    = plan_headcount × plan_hours_per_head
plan_billable_hours = plan_total_hours × (1 − plan_nonbillable_rate)
plan_revenue        = plan_billable_hours × plan_RPMH
```

**Headcount is lumpy and should be reported as such.** At $200 RPMH and 1,600 billable hours per head, one head is $320K. A client asking for +$220K cannot get there with fractional hiring — the honest answers are one head with an offsetting adjustment elsewhere, a partial-year start, or closing the gap through rate and efficiency initiatives instead.

---

## 16. Open items

- `annual_hours_per_head`: per service line or company-wide (§6.3)
- Materiality threshold for what earns its own driver bucket vs. the inflation bin
- Whether initiative impacts are entered as absolute deltas or as target values with the delta computed
- Band-setting method for KPI benchmarks (out of scope here)
- Whether the QBO budget is pushed via API or delivered as an import file

---

*v1.0 — 3 September 2026*
