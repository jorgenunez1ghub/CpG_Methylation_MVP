# Duplicate Aggregation ADR

## Status
Approved by stakeholders on 2026-04-08. Implemented in the current codebase.

Companion review memo:
- `docs/duplicate_aggregation_adr_review_memo.md`

Stakeholder brief:
- `docs/duplicate_aggregation_stakeholder_brief.md`

## Date
2026-04-08

## Decision scope
This ADR defines the approved duplicate-aggregation contract for the CpG methylation MVP.

The current codebase implements that contract as an explicit, opt-in duplicate policy.

## Context
- The ingestion pipeline supports three explicit duplicate `cpg_id` policies:
  - `preserve_rows_and_warn`
  - `reject_duplicates`
  - `aggregate_mean_when_metadata_match`
- The app exposes a duplicate-review artifact so repeated rows and metadata conflicts remain inspectable.
- The app also exposes an aggregation-audit artifact when duplicate rows are collapsed under the approved rule.
- Some downstream workflows require one retained row per `cpg_id`.
- The repo is an educational MVP and should prefer inspectability, reversibility, and conservative failure behavior over silent data repair.

## Problem
If the repo adds duplicate aggregation, it needs a rule for:
- how duplicate `beta` values are collapsed,
- how optional metadata is reconciled,
- how provenance remains inspectable,
- how the UI and report disclose that rows were aggregated,
- what happens when duplicate groups are not safe to aggregate.

## Approved decision
Duplicate aggregation ships as a third explicit duplicate policy:

- `aggregate_mean_when_metadata_match`

This policy is opt-in only. The default remains `preserve_rows_and_warn`.

## Proposed aggregation contract

### 1. Aggregation happens after current validation
- Run existing parsing, normalization, required-field filtering, and beta validation first.
- Apply aggregation only to retained rows.
- Non-duplicate rows pass through unchanged.

### 2. Grouping key
- Group only by canonical `cpg_id`.
- Do not aggregate across files, sessions, or external reference data.

### 3. Beta aggregation math
- Aggregate duplicate-group `beta` values with the arithmetic mean.
- Store aggregated `beta` values at full numeric precision in core outputs; any rounding is display-only in UI or report presentation layers.

Rationale:
- it is deterministic and easy to inspect,
- it preserves the same `[0, 1]` scale already validated by the pipeline,
- it is simple enough for an MVP report and audit artifact,
- it should be described as a workflow simplification, not a scientifically superior biological rule.

### 4. Metadata reconciliation
Apply the following rule independently to each optional canonical metadata column:
- `chrom`
- `pos`
- `gene`
- `pval`

For each column in a duplicate group:
- if all values are empty/null after normalization, keep the aggregated value empty,
- if there is exactly one distinct non-empty value, carry that value forward,
- if there is more than one distinct non-empty value, the group is conflicting and is not safe to aggregate.

This allows partial metadata fill-in when non-empty values agree, while still rejecting conflicting annotations.

### 5. Failure behavior
- Aggregation must not silently mix aggregated and non-aggregated duplicate groups in the same output on the first implementation pass.
- If the user selects aggregation and any duplicate group has conflicting metadata, ingestion should fail with a clear error.
- The error should report how many duplicate groups were blocked and direct the user to re-run with `preserve_rows_and_warn` for manual review.

This keeps the first implementation simple and avoids mixed semantics in one output artifact.

### 6. Provenance and audit requirements
The aggregated normalized dataframe should remain analytically simple:
- canonical columns,
- existing ingestion provenance columns (`source_file`, `uploaded_at`).

Row-level aggregation provenance should be preserved outside the main dataframe through a dedicated audit artifact.

The audit artifact should include, at minimum:
- `cpg_id`
- `source_row_count`
- `beta_min`
- `beta_max`
- `beta_mean`
- carried metadata values for `chrom`, `pos`, `gene`, `pval`
- `source_file`
- `uploaded_at`
- `aggregation_rule`

The existing duplicate-review artifact should remain available for preserve-and-review workflows and should not be removed if aggregation is added later.

### 7. UI and processing-report disclosure
The implemented aggregation mode must be disclosed explicitly.

Minimum disclosure requirements:
- the duplicate-policy selector label should state that aggregation is explicit and conditional on metadata agreement,
- UI help text should say that aggregation is not the default and is not a clinical or biological interpretation rule,
- downloadable artifact names should distinguish aggregated output from preserve/warn output,
- the processing report should record that aggregation was requested and applied.

Minimum additive processing-report fields:
- existing `duplicate_policy`
- `aggregation_applied`
- `pre_duplicate_policy_row_count`
- `aggregated_duplicate_cpg_id_groups`
- `aggregated_duplicate_input_rows`
- `aggregation_output_row_count`
- `aggregation_blocked_conflict_groups`

Because these fields change report semantics, `report_version` should be bumped intentionally when they are introduced.

## Options considered

### Option A — Keep preserve/reject only
Pros:
- safest current behavior,
- no new scientific assumption.

Cons:
- does not satisfy workflows that require one row per `cpg_id`.

Decision:
- keep as current production behavior, but insufficient as the only long-term option.

### Option B — Aggregate by arithmetic mean when metadata match
Pros:
- explicit and deterministic,
- easier to explain than more complex statistical choices,
- supports one-row-per-`cpg_id` output without silent metadata coercion.

Cons:
- still introduces a workflow policy that must be disclosed clearly,
- may be too simplistic for some scientific contexts.

Decision:
- approved and implemented for the first aggregation pass.

### Option C — Aggregate while coercing metadata conflicts
Examples:
- keep the first metadata value,
- choose the most common metadata value,
- take the minimum `pval`.

Pros:
- maximizes the number of aggregatable groups.

Cons:
- hides disagreement,
- introduces arbitrary reconciliation rules,
- weakens trust and inspectability.

Decision:
- rejected.

### Option D — Partially aggregate safe groups and quarantine the rest
Pros:
- preserves some automated recovery.

Cons:
- produces mixed output semantics,
- complicates UI, reporting, and audit behavior,
- is harder to review than a fail-fast first version.

Decision:
- defer until a later phase, if needed.

## Duplicate fixture matrix for implementation

| Case | Example | Expected result under proposed policy |
|---|---|---|
| Exact duplicate metadata, different beta | same `chrom/pos/gene/pval`, beta `0.20` and `0.80` | aggregate to one row with beta `0.50` |
| Partial metadata, agreeing non-empty values | one row has `chrom=chr1`, one row has blank `chrom` | aggregate and carry `chr1` |
| All optional metadata missing | duplicate rows only contain `cpg_id` and `beta` | aggregate and keep optional metadata blank |
| Conflicting `chrom` | `chr1` vs `chr2` | fail aggregation |
| Conflicting `gene` | `TP53` vs `MDM2` | fail aggregation |
| Conflicting `pval` | `0.01` vs `0.20` | fail aggregation |
| Single non-duplicate row | one row only | pass through unchanged |

## Public API and documentation impact
This implementation updates together:
- `DuplicatePolicy` public type
- app duplicate-policy selector copy
- processing report schema/version notes
- `README.md`
- `docs/validation_rules.md`
- `docs/SCHEMA.md`
- `docs/DATA_DICTIONARY.md`
- tests covering aggregation eligibility, conflicts, audit output, and disclosure

## Non-goals
- No biological interpretation of why duplicates exist.
- No cross-file deduplication.
- No imputation of missing beta values.
- No automatic repair of conflicting metadata.
- No silent fallback from failed aggregation into preserve mode.

## Approval record
Stakeholder approval recorded on 2026-04-08 for:
- the duplicate-policy name `aggregate_mean_when_metadata_match`,
- arithmetic mean as the v1 workflow aggregation rule,
- fail-fast behavior on conflicting metadata,
- the documented audit artifact and processing-report disclosure contract.

Stakeholder approval authorized this implementation contract. The current codebase now carries the focused core changes, tests, report-version update, and UI/report disclosure required by this ADR.
