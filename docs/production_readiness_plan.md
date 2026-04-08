# Production Readiness Plan

This document packages the next implementation pass by impact and separation of concerns.

## Phase 1 — Ingestion Trust Contract
- Keep duplicate handling explicit: preserve-and-warn or reject.
- Treat aggregation as deferred until a scientific rule is approved.
- Keep parse warnings first-class in the processing report.
- Preserve run-level traceability with report version, run ID, and input checksum.

## Phase 2 — Parse Hardening
- Maintain conservative delimiter recovery for mislabeled `.csv`/`.tsv` files.
- Warn on UTF-8 BOM removal and mixed-delimiter content.
- Fail clearly on malformed quotes or broken delimiter structure.
- Revisit chunked parsing only if file-size expectations exceed the current upload ceiling.

## Phase 3 — Artifact and Audit Readiness
- Keep normalized CSV + processing report JSON/CSV downloads available from the UI.
- Preserve processing-report compatibility when adding new fields; bump `report_version` intentionally.
- If durable storage is introduced later, define retention, naming, and access-control policy first.

## Phase 4 — Deployment Guardrails
- Keep the Streamlit upload ceiling aligned with the core ingest limit.
- Run deployed smoke checks for upload, report generation, duplicate warnings, and downloads.
- Preserve explicit privacy language: session-scoped workflow, no durable storage configured, educational use only.

## Phase 5 — Follow-on Work
- If needed, separate future work into:
  - `core-parsing-hardening`
  - `duplicate-policy-expansion`
  - `deployment-and-observability`
- Add a true browser-driven smoke test only if deployment automation justifies the dependency cost.
- Add aggregation only after the duplicate-policy decision is expanded into a scientific/data-contract ADR.
