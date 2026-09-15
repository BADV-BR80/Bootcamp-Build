# Plan Line Definitions — DRAFT v0.1

*Status: **draft for review.** Not yet approved. Derived from `reference/PL_Summary_Accounts.xlsx` (client-supplied category list) and `baseline-plan-build-spec.md` §6.5, §6.6, §6.7, §6.8, §9, §10.*

*Companion to the build spec. This file is the canonical `plan_line` and `category` configuration for the build; the spec defines the rules, this defines the wiring.*

---

## 1. Purpose

`baseline-plan-build-spec.md` §6.5 defines the `category` entity (the ~18-row reporting roll-up) and §6.6 defines the `plan_line` entity (the buildable unit), but neither list was populated. This file populates both.

The category list is taken **verbatim** from the client-supplied summary account sheet. It reconciles to §6.5 exactly:

| Section | Count | Spec §6.5 expects |
|---|---|---|
| REV | 1 | 1 |
| COGS | 5 | 5 |
| OH | 10 | 10 |
| OTH-INC | 1 | 1 |
| OTH-EXP | 1 | 1 |
| **Total** | **18** | **~18** |

Two categories split into more than one plan line, giving **20 plan lines from 18 categories**.

---

## 2. Driver types

Spec §6.6 defines three `driver_type` values. This draft proposes **two additions**, both flagged for approval in §5 below.

| `driver_type` | In spec? | Calculation | `driver_ref` |
|---|---|---|---|
| `volume` | **PROPOSED** | Output of the §8 volume build. Never a rate, never entered (R1) | — |
| `primary` | Yes §6.6 | `driver value (this scope) × rate` | a `driver_id` |
| `derived` | Yes §6.6 | `referenced line's value (same scope) × rate` | a `line_id` |
| `inflation` | Yes §6.6 | `prior year actual × (1 + inflation_rate)` | — |
| `carryforward` | **PROPOSED** | `TTM average`, held flat — no inflation applied | — |

System drivers referenced below are the §6.7 set: `TOTAL_HOURS`, `BILLABLE_HOURS`, `REVENUE` (all service-line scoped), plus company-scoped `REVENUE_CO` and the company driver `OH_HEADCOUNT`.

---

## 3. The plan lines

`scope` follows R7: above the line is per service line, below the line is company-wide.
`distribution` follows §10 and is **new** — it is not in the client sheet but is required for step 7 of §12.

### Revenue

| line_id | Category | Plan line | Scope | Driver type | Driver ref | Basis | KPI | Distribution |
|---|---|---|---|---|---|---|---|---|
| R-01 | Sales Revenue | Sales Revenue | service_line | `volume` | — | `billable_hours × RPMH` (R1, §8) | Yes | seasonal |

*Revenue has no rate (§6.8) and no input cell (R1). Contra-revenue accounts — discounts, refunds, credits — map to this category and net against it.*

### COGS — all service-line scoped

| line_id | Category | Plan line | Scope | Driver type | Driver ref | Basis | KPI | Distribution |
|---|---|---|---|---|---|---|---|---|
| C-01 | Labor [Field] | Field Wages | service_line | `primary` | `TOTAL_HOURS` | avg field wage rate, $/hr | Yes | seasonal |
| C-02 | Labor [Field] | Field Labor Burden | service_line | `derived` | C-01 | % of field wages | Yes | seasonal |
| C-03 | Materials [Field] | Materials | service_line | `primary` | `REVENUE` | % of revenue (this service line) | Yes | seasonal |
| C-04 | Equipment + Vehicles [Field] | Rental Equipment | service_line | `primary` | `REVENUE` | % of revenue (this service line) | No | seasonal |
| C-05 | Subcontractors [Field] | Subcontractors | service_line | `primary` | `REVENUE` | % of revenue (this service line) | No | seasonal |
| C-06 | Other COGS [Field] | Other COGS | service_line | `primary` | `REVENUE` | % of revenue (this service line) | No | seasonal |

**On C-01 / C-02.** The client sheet gives Labor [Field] as `[Field_Headcount] × [Annual_Hours] × [Avg_Burdened_Rate]`. `field_headcount × annual_hours_per_head` **is** `TOTAL_HOURS` (§8), so this is the same arithmetic, factored into wage and burden. Splitting is what §6.6 uses as its canonical example, and it is worth doing for three reasons: labor burden rate is derived from a different source than the wage rate (§3.3 roster vs. §6.2 dataset 1); burden % is a KPI in its own right; and benefits changes are a common initiative target that needs a `target_ref` to land on.

`TOTAL_HOURS` and not `BILLABLE_HOURS` is correct and matches §9 — nonbillable hours are paid.

### Overhead — all company scoped

| line_id | Category | Plan line | Scope | Driver type | Driver ref | Basis | KPI | Distribution |
|---|---|---|---|---|---|---|---|---|
| O-01 | Administration | Administration | company | `inflation` | — | prior yr × (1 + i) | No | flat |
| O-02 | Business Development | Business Development | company | `inflation` | — | prior yr × (1 + i) | No | flat |
| O-03 | Facilities | Facilities | company | `inflation` | — | prior yr × (1 + i) | No | flat |
| O-04 | Finance | Finance | company | `primary` | `REVENUE_CO` | % of company revenue | No | seasonal |
| O-05 | Labor [OH] | Overhead Wages | company | `primary` | `OH_HEADCOUNT` | avg annual OH salary, from current roster | Yes | flat |
| O-06 | Labor [OH] | Overhead Labor Burden | company | `derived` | O-05 | % of OH wages | No | flat |
| O-07 | Professional Services | Professional Services | company | `inflation` | — | prior yr × (1 + i) | No | flat |
| O-08 | Sales + Marketing | Sales + Marketing | company | `primary` | `REVENUE_CO` | % of company revenue | Yes | flat |
| O-09 | Business Taxes | Business Taxes | company | `primary` | `REVENUE_CO` | % of company revenue | No | flat |
| O-10 | Vehicle + Equipment [OH] | Vehicle + Equipment | company | `primary` | `REVENUE_CO` | % of company revenue | No | seasonal |
| O-11 | Other Operating Expenses | Other Operating Expenses | company | `inflation` | — | prior yr × (1 + i) | No | flat |

**On O-05 / O-06.** The client sheet gives Labor [OH] as "pulled from employee list provided" — a source, not a driver. Modeled here as a company driver (`OH_HEADCOUNT`) × average annual salary from the current roster, plus a derived burden line. This keeps it consistent with R2 (current cost structure) and gives an overhead hire somewhere to land as an initiative (`target_type` = `driver`).

**O-04, O-08, O-09 and O-10 are carried as specified in the client sheet, but all four are flagged in §5.**

### Other income / other expense

| line_id | Category | Plan line | Scope | Driver type | Driver ref | Basis | KPI | Distribution |
|---|---|---|---|---|---|---|---|---|
| X-01 | Other Income | Other Income | company | `carryforward` | — | TTM average, no inflation | No | flat |
| X-02 | Other Expense | Other Expense | company | `carryforward` | — | TTM average, no inflation | No | flat |

---

## 4. Computed rows — not plan lines

These appear on the client sheet and in the output P&L but carry no `line_id`, no driver, and no rate. They are arithmetic on the lines above (§9 roll-up).

`Total COGS` · `Gross Profit` · `GP %` · `Total Overhead` · `Net Op. Profit` · `NOP %` · `Net Profit` · `NP %`

---

## 5. Open decisions

Ranked by how much they move the number. Items 1–4 are changes to the client-supplied drivers; 5–6 are structural approvals.

### 5.1 The annualization effect inflates every %-of-revenue overhead line

**This is the one that matters most.** Baseline revenue exceeds historical revenue by the annualization effect (R3) — the spec's own worked example in §8 is **+28%**. Every `primary`/`REVENUE_CO` overhead line grows by that same percentage automatically.

- For **Finance** (payment processing, bad debt) that is correct — those genuinely scale with revenue dollars.
- For **Business Taxes** (real estate, personal property) it is wrong. A property tax bill does not rise because the crew was fully staffed all year.
- For **Vehicle + Equipment [OH]** it is partly wrong. Fuel scales; registration, insurance and lease expense do not — and you cannot run 28% more revenue on the same trucks without buying trucks, which would be an initiative, not a baseline cost.

Net effect: baseline overhead is overstated and baseline net profit understated, by an amount proportional to the annualization effect.

**Recommendation:** split O-09 and O-10 into sub-accounts with separate drivers, or default both to `inflation` and revisit under R10.

### 5.2 Business Taxes contains corporate income tax

Two problems. Corporate income tax is a function of **pre-tax profit**, not revenue — so a %-of-revenue driver is wrong regardless of 5.1. And it sits in Overhead, above Net Operating Profit, which makes NOP not an operating measure.

**Recommendation:** move corporate income tax below NOP (either its own line or into Other Expense), leaving Business Taxes = property and personal property tax on `inflation`.

### 5.3 Vehicle + Equipment [OH] is the likeliest R10 driver candidate

Fuel, R&M, lease, registration, insurance, small tools — these are per-vehicle costs, and vehicle count is exactly the kind of metric an ops leader would put on a scorecard. Of all ten overhead categories, this is the one most likely to clear the §4.5 materiality test at all five clients.

**Recommendation:** split into `Fuel` (`primary`, `BILLABLE_HOURS` or `REVENUE_CO`) and `Vehicle Fixed` (`primary`, company driver `VEHICLE_COUNT`). Per §3, a vehicle count is requested ad hoc once the bucket earns a driver — this is that case.

### 5.4 Finance contains interest

Interest is a function of debt balance and rate, not revenue. If any of the five carry equipment notes or a line of credit, %-of-revenue misstates it in both directions over the year.

**Recommendation:** split into `Interest` (`carryforward`, or an amortization schedule if available) and `Finance Charges` (`primary`, `REVENUE_CO` — bad debt and processing fees).

### 5.5 Approve the two proposed driver types

`volume` (R-01) and `carryforward` (X-01, X-02) are additions to the §6.6 set of three. Both come from the client sheet: revenue is computed by the volume build, and "carryforward TTM average" is what the sheet specifies for the other income/expense rows.

`carryforward` is deliberately distinct from `inflation` — inflating a Gain on Sale by 5% has no meaning.

### 5.6 Approve the `distribution` column

Not on the client sheet. Required by §10 and §12 step 7 — an annual figure cannot be imported to QBO (§11.2), so every line needs a spread method. Defaults proposed above: seasonal for anything revenue- or hours-linked, flat for fixed overhead.

Two to check: **O-08 Sales + Marketing** is set to `flat` even though its driver is revenue, because marketing spend is typically front-loaded ahead of season rather than following it. **O-09 Business Taxes** may be better as `event` if property tax lands on known dates.

---

## 6. Smaller notes

- **Sales + Marketing contains uniforms**, which scale with headcount rather than revenue. Immaterial at most companies; noted rather than recommended for change.
- **Other Expense contains Dep./Amort** on carryforward. Depreciation follows an asset schedule, usually available from the tax preparer. Carryforward is a defensible baseline default under R2, but it will be wrong the moment a capex initiative exists. A known limitation, not a fix.
- **Business Development contains conferences**, which are dated events. `flat` is the default; `event` distribution is available if specific dates are known.
- **Labor burden rate** (C-02, O-06) is derived from dataset 1 per §6.2, which means it depends on account mapping being complete — payroll taxes, benefits and workers' comp must be identified first. It is a mapping-dependent output, not a direct extract, and cannot be computed at §12 step 1.
