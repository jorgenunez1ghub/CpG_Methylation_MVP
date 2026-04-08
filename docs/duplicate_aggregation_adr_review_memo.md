# Duplicate Aggregation ADR Review Memo

Follow-up note:
- The memo's recommended numeric-precision and disclosure-field edits have been applied to `docs/duplicate_aggregation_adr.md`.
- The ADR is now in a ready-for-approval-review state; this memo remains the review record behind those edits.

## Scope reviewed
This memo reviews `docs/duplicate_aggregation_adr.md` and makes recommendations on the four open decision points that should be resolved before any duplicate-aggregation code is implemented.

Review date: 2026-04-08

## Executive recommendation
Approve the ADR direction.

The current ADR is already aligned with the repo’s operating priorities:
- input reliability,
- QC transparency,
- maintainable app/core separation,
- scientifically cautious behavior.

My recommendation is to keep the overall direction and approve the revised ADR if stakeholders accept the explicit policy and disclosure contract.

## Decision summary

| Decision point | Recommendation | Approval posture |
|---|---|---|
| Policy name | Keep `aggregate_mean_when_metadata_match` | Approve as written |
| Beta collapse rule | Use arithmetic mean for v1 and do not round stored output values | Approve with one clarification |
| Conflict handling | Keep fail-fast on metadata conflicts for v1 | Approve as written |
| Audit/report disclosure | Expand the minimum report field set beyond the current draft | Approve with modification |

## 1. Policy name

### Recommendation
Keep the proposed public policy value:

- `aggregate_mean_when_metadata_match`

### Why
- It matches the style of the current public literals:
  - `preserve_rows_and_warn`
  - `reject_duplicates`
- It is explicit about both the aggregation math and the safety condition.
- It avoids ambiguous names like `aggregate_duplicates` or `safe_aggregate`, which hide the actual rule.
- The string is long, but length is acceptable in a public API if the meaning is clear.

### Practical note
The internal/public policy value and the user-facing label do not need to match.

Recommended future UI label:
- `Aggregate duplicates (mean beta, matching metadata only)`

This keeps the API explicit and the UI readable.

## 2. Beta collapse rule

### Recommendation
Approve arithmetic mean as the v1 aggregation rule for this explicit mode.

### Why
- It is deterministic and easy to verify in tests and audit artifacts.
- It stays within the existing `[0, 1]` beta range once inputs are already validated.
- It is easier to explain than more complex summary rules.
- It fits the MVP’s trust-first posture better than introducing weighting, winsorization, or domain-specific heuristics.

### Required clarification before approval
Add one sentence to the ADR stating:
- aggregated beta values are stored at full numeric precision in core outputs,
- rounding is display-only in the UI or report presentation layer.

This avoids accidental data-loss behavior sneaking into the core logic.

### Why not recommend median for v1
- Median is plausible, but it is not obviously more correct for this repo’s current use case.
- Introducing robustness-oriented aggregation language risks sounding more scientifically authoritative than the repo currently supports.
- Mean is simpler to audit because the audit artifact can show `beta_min`, `beta_max`, and `beta_mean` directly.

## 3. Conflict handling

### Recommendation
Approve fail-fast behavior for metadata conflicts in v1.

### Why
- It preserves one consistent output meaning per run.
- It avoids a mixed artifact where some duplicate groups are aggregated and others are only partially resolved.
- It aligns with the repo’s preference for conservative handling over silent coercion.
- It keeps the first implementation smaller, easier to test, and easier to explain.

### Recommendation against partial quarantine for v1
Do not allow:
- aggregate safe groups,
- quarantine unsafe groups,
- still return a partially aggregated main output.

That design is reasonable later, but it adds:
- mixed output semantics,
- more report fields,
- more UI explanation burden,
- more regression surface.

### Practical fallback
The current preserve-and-review path already exists. That means fail-fast aggregation does not strand the user; it just directs them back to the safer review workflow.

## 4. Audit and processing-report disclosure

### Recommendation
Approve the audit-artifact concept, but strengthen the minimum processing-report contract before ADR approval.

### What is good in the draft
The draft already gets the core principle right:
- keep the main analytical dataframe simple,
- preserve aggregation provenance in a separate audit artifact,
- disclose aggregation explicitly in the processing report.

### What should be added to the ADR
The report field recommendations should be tightened so implementation does not guess later.

Recommended minimum report fields:
- existing `duplicate_policy`
- `aggregation_applied`
- `pre_duplicate_policy_row_count`
- `aggregated_duplicate_cpg_id_groups`
- `aggregated_duplicate_input_rows`
- `aggregation_output_row_count`
- `aggregation_blocked_conflict_groups`

### Why these fields matter
- `aggregation_applied` distinguishes “aggregation policy selected” from “duplicates actually aggregated.”
- `pre_duplicate_policy_row_count` preserves visibility into how many valid rows existed before collapse.
- `aggregated_duplicate_cpg_id_groups` shows how many duplicate groups were actually collapsed.
- `aggregated_duplicate_input_rows` shows how many retained rows fed into aggregation.
- `aggregation_output_row_count` makes the final one-row-per-`cpg_id` result explicit.
- `aggregation_blocked_conflict_groups` preserves transparency when aggregation is requested but not safely executable.

### Recommended audit artifact fields
Keep the ADR’s draft fields and add one more:
- `cpg_id`
- `source_row_count`
- `beta_min`
- `beta_max`
- `beta_mean`
- carried metadata values for `chrom`, `pos`, `gene`, `pval`
- `source_file`
- `uploaded_at`
- `aggregation_rule`

The extra `aggregation_rule` field makes exported audit files self-describing if the repo later adds more than one aggregation mode.

### Naming recommendation
Use a clearly distinct artifact name when aggregation is introduced, for example:
- `<source>_aggregated_normalized.csv`
- `<source>_aggregation_audit.csv`

This is better than overloading the current artifact names and forcing the report alone to carry all disclosure weight.

## Recommended ADR edits before approval
These edits were recommended by this memo and have now been applied to `docs/duplicate_aggregation_adr.md`:

1. Keep the policy name unchanged.
2. Add a clarification that aggregated beta values are not rounded in core outputs.
3. Keep fail-fast conflict handling unchanged.
4. Replace the current “recommended additive processing-report fields” list with the stronger minimum set listed in this memo.
5. Add `aggregation_rule` to the audit artifact minimum fields.

## Approval recommendation
Recommended disposition:

**Approve.**

That means:
- no change to the core direction,
- no change to the proposed policy name,
- no change to fail-fast conflict handling,
- the numeric-precision clarification is now in the ADR,
- the report/audit disclosure contract is now tightened in the ADR.

## What I would do next after approval
Once the ADR is approved, the first implementation PR should be narrowly scoped to:
- extend `DuplicatePolicy`,
- add focused duplicate-fixture tests,
- implement aggregation in core only,
- add audit artifact export,
- bump `report_version`,
- update the app selector/help text and docs together.
