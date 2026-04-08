# Duplicate Aggregation ADR — Stakeholder Review Brief

Decision outcome:
- Approved by stakeholders on 2026-04-08.

## Purpose
This brief translates `docs/duplicate_aggregation_adr.md` into a stakeholder decision view.

It is written for PM, product, and demo-governance stakeholders who needed a clear approval record and implementation boundary for duplicate aggregation.

## Executive summary
**Recommendation: approve the ADR.**

Reason:
- it solves a real workflow gap for users who need one row per `cpg_id`,
- it keeps aggregation explicit and opt-in rather than changing current default behavior,
- it preserves the repo’s trust posture by failing on unsafe metadata conflicts,
- it requires audit and disclosure artifacts so aggregation does not become silent data rewriting.

This approval authorized a controlled implementation plan. It did **not** mean that aggregation was scientifically validated beyond the defined workflow rule or appropriate for clinical interpretation.

## Approved stakeholder decision scope
Stakeholders approved four things:

1. A new explicit duplicate policy may be added later:
   - `aggregate_mean_when_metadata_match`
2. Duplicate `beta` values in that mode may be collapsed by arithmetic mean.
3. Duplicate groups with conflicting metadata should fail rather than being silently coerced.
4. Aggregation must be disclosed through report fields, artifact naming, and an audit export.

## Why this ADR is reasonable

### 1. It addresses a legitimate product need
Today the repo supports:
- preserve duplicates and warn, or
- reject duplicates.

That is safe, but it does not support workflows that need one-row-per-`cpg_id` output for downstream analysis or simplified exports.

### 2. It does not weaken current trust defaults
The current default remains:
- `preserve_rows_and_warn`

That matters because the repo is explicitly trust-first and educational. The ADR does not convert aggregation into the default path.

### 3. It makes the rule understandable
The proposed rule is simple:
- if metadata agrees, aggregate by mean,
- if metadata conflicts, stop and tell the user.

This is easier to explain and defend than more complex or silent reconciliation rules.

### 4. It preserves inspectability
The ADR requires:
- processing-report disclosure,
- distinct aggregated artifact naming,
- a separate audit artifact,
- continued duplicate-review support for non-aggregation workflows.

That keeps the output reviewable by users and maintainers.

## Risk evaluation

### Controlled risks
These risks are meaningfully reduced by the ADR design:

- **Silent data loss risk**
  Mitigated by opt-in mode, explicit disclosure, and audit output.

- **Metadata corruption risk**
  Mitigated by fail-fast behavior when duplicate groups disagree.

- **Overclaim / scientific overreach risk**
  Mitigated by positioning aggregation as a workflow simplification, not a biological truth.

- **Maintenance risk**
  Mitigated by scoping the first implementation narrowly and requiring report-version updates.

### Residual risks
These still remain even if the ADR is approved:

- arithmetic mean may not be the right scientific rule for every downstream use case,
- some users may still misread aggregation as “cleaning” rather than an explicit transformation,
- future feature requests may push toward more aggressive conflict resolution.

These are acceptable for the MVP only if the repo continues to keep:
- the current safe default,
- explicit language,
- no clinical framing,
- fail-fast conflict behavior.

## Recommendation on the four decision points

### 1. Policy name
**Recommendation: approve.**

Why:
- explicit,
- matches current naming style,
- clear enough for API use,
- user-facing UI can still use a friendlier label.

### 2. Beta aggregation rule
**Recommendation: approve arithmetic mean for v1.**

Why:
- deterministic,
- easy to test,
- easy to explain,
- lower risk than introducing more advanced scientific heuristics in an MVP.

Important condition:
- stored values should keep full numeric precision in core outputs.

### 3. Conflict behavior
**Recommendation: approve fail-fast.**

Why:
- safer than silently choosing one metadata value,
- avoids mixed semantics in one output,
- fits the repo’s conservative handling standard.

### 4. Disclosure and audit requirements
**Recommendation: approve.**

Why:
- this is the main safeguard that keeps aggregation transparent,
- it preserves provenance for later review,
- it reduces the risk that stakeholders or users over-trust transformed output.

## What stakeholders are not approving
Approving this ADR does **not** approve:
- immediate production release of aggregation,
- clinical or biomedical interpretation claims,
- automatic repair of conflicting metadata,
- cross-file deduplication,
- silent fallback behavior,
- broader parsing or data-repair changes.

## Implementation impact after approval
Approval justified one focused implementation PR with this shape:
- extend duplicate policy enum/type,
- implement aggregation in core,
- add duplicate-fixture tests,
- add audit artifact export,
- add report fields and bump `report_version`,
- update UI help text and docs together.

This is a moderate, bounded change. It is not a repo-wide rewrite.

## Recorded stakeholder decision
**The ADR was approved and has now been implemented under that controlled scope.**

Suggested approval statement:

> We approve the duplicate aggregation ADR as an explicit, opt-in workflow rule. Approval is limited to the documented mean-when-metadata-match contract, fail-fast conflict handling, and required audit/report disclosure. This approval does not change the current default duplicate behavior or imply clinical interpretation validity.
