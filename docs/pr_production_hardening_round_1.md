# PR Summary

Production hardening pass for ingestion reliability, processing-report traceability, and deploy safeguards. This adds versioned processing reports with run IDs and checksums, conservative parse warnings and delimiter recovery, explicit duplicate-policy handling, downloadable report artifacts, and a deployment upload limit with updated operational docs.

# PR Description

## What changed
- hardened ingestion for UTF-8 BOMs, mixed-delimiter warnings, malformed-quote failures, and upload-size enforcement
- extended the processing report with `report_version`, `run_id`, `input_sha256`, parse warnings, and duplicate metadata conflict counts
- kept duplicate handling explicit with `preserve_rows_and_warn` and `reject_duplicates`
- added session download artifacts for normalized CSV plus processing report JSON/CSV
- configured a Streamlit upload ceiling and updated deploy/runbook/risk docs
- added regression tests for duplicate-policy behavior, parse warnings, size limits, and artifact serialization

## Why
- improves trust in messy real-world uploads
- makes QC and provenance easier to inspect and share
- reduces deployment ambiguity around upload size and session retention
- keeps scientific behavior conservative by deferring duplicate aggregation until rules are defined

## Verification
- `pytest -q`
- `python3 -m compileall app src tests`
