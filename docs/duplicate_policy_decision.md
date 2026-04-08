# Duplicate CpG Policy Decision

## Status
Accepted for the current production-hardening phase.

## Decision
The app supports two explicit duplicate `cpg_id` policies:

1. `preserve_rows_and_warn`
   - keep all duplicate rows in the retained dataframe
   - surface duplicate counts in the processing report
   - surface metadata-conflict counts when duplicate groups disagree on optional columns

2. `reject_duplicates`
   - fail ingestion if any duplicate `cpg_id` is present

## Why this decision
- Preserving rows is the safest default for QC review because it avoids silent data loss.
- Rejecting duplicates is appropriate for downstream workflows that require one row per `cpg_id`.
- Aggregation is intentionally deferred because it would introduce a scientific policy that is not yet encoded or validated in the repo.

## Aggregation is out of scope for now
If aggregation is introduced later, it must define:
- how `beta` values are combined,
- how conflicting metadata (`chrom`, `pos`, `gene`, `pval`) are reconciled,
- whether provenance stays row-level or group-level,
- how aggregation is disclosed in the processing report and downloadable artifacts.

## Current implementation implications
- Duplicate counts are tracked in the processing report.
- Duplicate metadata conflicts are tracked separately to show when aggregation would be unsafe.
- Preserved duplicates are exposed through a duplicate-review artifact so repeated rows can be inspected without inventing an aggregation rule.
- UI copy must continue to describe duplicate handling as a user-selected policy, not an inferred scientific truth.

## Next safe step before aggregation
The revised ADR is now ready for approval review in `docs/duplicate_aggregation_adr.md`.

Any future aggregation change should begin by approving that ADR before code is opened.

The ADR must answer:
- which workflow actually requires one-row-per-`cpg_id` output,
- which `beta` aggregation candidates were considered and why one was approved,
- how conflicting metadata is reconciled or when aggregation must still fail,
- how row-level provenance is preserved or disclosed after aggregation,
- how aggregated output is labeled in the UI, downloads, and processing report.

The minimum delivery package should include:
- an ADR in `docs/` with explicit decision status,
- a small duplicate-fixture matrix covering aligned duplicates, divergent beta duplicates, metadata conflicts, and partial-metadata duplicates,
- focused tests proving aggregation is opt-in and never silent,
- a report-compatibility note stating whether the processing report schema/version must change.
