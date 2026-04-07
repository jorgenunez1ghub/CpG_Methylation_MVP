# PR #27 Review: Preserve Alias Precedence with Multiple Aliases (April 7, 2026)

## PR under review
PR #27 is currently open and stale (about one month old).

A review note referenced commit `08280d7664` with the request to **"preserve alias precedence when multiple aliases are present"**.

## Assessment
This is a valid ingestion/normalization reliability concern.

Why this matters:
- alias collisions are realistic in messy analytical uploads,
- precedence should be deterministic and inspectable,
- ambiguous or duplicate canonical columns reduce QC transparency and can mask source-data intent.

## Actions applied in this branch
1. Updated canonical column mapping so alias resolution is deterministic and follows declared alias precedence.
2. Ensured exact alias matches win before case-insensitive fallback.
3. Added a focused regression test that verifies precedence behavior when both `beta` and `Beta` are present.

## Recommendation for PR #27 triage
If PR #27 contains no additional unique logic beyond alias-precedence preservation, close it as **superseded** after merging this branch.

If it contains additional unique changes, salvage those specific hunks into a focused follow-up PR.
