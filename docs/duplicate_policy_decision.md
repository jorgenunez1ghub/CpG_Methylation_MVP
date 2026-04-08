# Duplicate CpG Policy Decision

## Status
Accepted and implemented in the current codebase.

## Decision
The app supports three explicit duplicate `cpg_id` policies:

1. `preserve_rows_and_warn`
   - keep all duplicate rows in the retained dataframe
   - surface duplicate counts in the processing report
   - surface metadata-conflict counts when duplicate groups disagree on optional columns

2. `reject_duplicates`
   - fail ingestion if any duplicate `cpg_id` is present

3. `aggregate_mean_when_metadata_match`
   - aggregate duplicate groups by arithmetic mean on `beta`
   - carry forward optional metadata only when non-empty values agree
   - fail ingestion when duplicate groups contain conflicting optional metadata
   - emit a separate aggregation-audit artifact for provenance review

## Why this decision
- Preserving rows is the safest default for QC review because it avoids silent data loss.
- Rejecting duplicates is appropriate for downstream workflows that require one row per `cpg_id`.
- Explicit aggregation is appropriate for downstream workflows that require one row per `cpg_id`, but only when the rule and disclosure contract are approved and inspectable.

## Aggregation contract
The implemented aggregation path defines:
- how `beta` values are combined,
- how conflicting metadata (`chrom`, `pos`, `gene`, `pval`) are reconciled,
- how row-level provenance is preserved through an audit artifact,
- how aggregation is disclosed in the processing report and downloadable artifacts.

## Current implementation implications
- Duplicate counts are tracked in the processing report.
- Duplicate metadata conflicts are tracked separately to show when aggregation would be unsafe.
- Preserved duplicates are exposed through a duplicate-review artifact so repeated rows can be inspected without inventing an aggregation rule.
- Aggregated duplicates are exposed through a separate aggregation-audit artifact rather than silently replacing provenance.
- UI copy must continue to describe duplicate handling as a user-selected policy, not an inferred scientific truth.

## Current implementation reference
The approved implementation contract lives in `docs/duplicate_aggregation_adr.md`.

Any future change to aggregation behavior should revise that ADR rather than modifying aggregation rules ad hoc in code.
