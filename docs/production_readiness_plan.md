# Production Readiness Plan

This document packages the next implementation pass by impact and separation of concerns.

## Phase 1 — Ingestion Trust Contract
- Keep duplicate handling explicit: preserve-and-warn, reject, or approved opt-in aggregation.
- Keep aggregation conservative: arithmetic mean only when optional metadata agree, with fail-fast conflicts and explicit audit/report disclosure.
- Keep parse warnings first-class in the processing report.
- Preserve run-level traceability with report version, run ID, and input checksum.

## Phase 2 — Parse Hardening
- Maintain conservative delimiter recovery for mislabeled `.csv`/`.tsv` files.
- Warn on UTF-8 BOM removal and mixed-delimiter content.
- Fail clearly on malformed quotes or mixed-delimiter row-structure breaks.
- Revisit chunked parsing only if file-size expectations exceed the current upload ceiling.

## Phase 3 — Artifact and Audit Readiness
- Keep normalized CSV + processing report JSON/CSV downloads available from the UI.
- Preserve processing-report compatibility when adding new fields; bump `report_version` intentionally.
- If durable storage is introduced later, define retention, naming, and access-control policy first.

## Phase 4 — Deployment Guardrails
- Keep the Streamlit upload ceiling aligned with the core ingest limit.
- Keep local Streamlit smoke automation in place as a pre-deploy gate.
- Run deployed smoke checks for upload, report generation, duplicate warnings, and downloads.
- Preserve explicit privacy language: session-scoped workflow, no durable storage configured, educational use only.

## Phase 5 — Follow-on Work
- If needed, separate future work into:
  - `core-parsing-hardening`
  - `duplicate-policy-expansion`
  - `deployment-and-observability`
- Add a true hosted browser-driven smoke test only if deployment automation justifies the dependency cost.
- Revisit aggregation only through ADR revision if the policy needs to expand beyond the implemented v1 contract.

## Concrete Solution Paths

### 1. Duplicate aggregation
- The first implementation is now in place from the approved contract in `docs/duplicate_aggregation_adr.md`.
- Keep the implemented mode opt-in behind the explicit `aggregate_mean_when_metadata_match` policy value rather than changing the default.
- Preserve the duplicate-review artifact for preserve-and-review workflows even though aggregation is now available.
- Any future aggregation changes should update tests, downloads, and processing-report disclosure together because retained-row semantics are now versioned behavior.

### 2. Hosted smoke automation
- Choose a single browser-automation stack deliberately instead of mixing tools in the repo.
- Keep the current local Streamlit smoke test as the fast gate, then add deployed-URL smoke coverage as a separate workflow.
- Limit the first deployed smoke scope to core trust checks: page load, upload success, duplicate warning visibility, and artifact download presence.
- Start the deployed smoke workflow as non-blocking until selectors, hosting URL, and artifact behavior are stable enough to gate releases.

### 3. Mixed-delimiter recovery
- Do not broaden silent parser coercion.
- If recovery work is prioritized, add an explicit pre-normalization workflow that separates clearly parseable rows from quarantined rows.
- Surface quarantined-row counts and reasons in user-facing output so partial recovery remains inspectable.
- Only add second-pass salvage for quarantined rows if the recovery rule is documented, tested, and reversible.
