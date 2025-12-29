# CpG_Methylation_MVP — One-Pager (FAC-P/PM Evidence)

## Problem
People receive DNA methylation-related datasets (often CSV exports) that are difficult to interpret without technical tooling. The data is usually “messy” (inconsistent headers, non-numeric values, missing fields), and users need a quick way to validate inputs, view summary patterns, and flag outliers for follow-up.

## Target Users
- **Primary:** Non-technical users who have methylation-related CSV outputs and want a structured, readable summary.
- **Secondary:** Wellness practitioners / coaches (non-clinical) who want a fast “screening view” and questions to raise with a clinician.
- **Tertiary:** Product/PM stakeholders evaluating feasibility of an “upload → insight” workflow for health-data decision support.

## Solution (MVP)
A lightweight **Streamlit** web app that:
1) Accepts a user-uploaded CSV  
2) Displays a preview + schema checks  
3) Allows column mapping (to handle real-world file formats)  
4) Flags “high methylation” rows above a user-set threshold  
5) Produces an exportable CSV and a simple report

## MVP Scope (In Scope)
- CSV upload and parsing
- Data cleaning (coerce non-numeric methylation values)
- Column mapping (Gene + methylation fields)
- Threshold-based flagging + sortable results
- Simple aggregate summary (mean/median, top genes)
- Exports: flagged rows CSV + markdown report
- Basic disclaimers and safe framing (educational, not medical advice)

## Out of Scope (Not Included)
- Medical diagnosis, treatment recommendations, or clinical interpretation
- Storing user datasets (MVP operates on the uploaded file in-session)
- User accounts, authentication, or longitudinal tracking
- Integration with external EHR/health systems
- Model fine-tuning or advanced genomic interpretation logic

## Success Criteria (MVP)
- **Functional:** App successfully processes a valid CSV and produces flagged results + exports
- **Usability:** A non-technical user can complete the workflow in < 2 minutes
- **Reliability:** Handles common issues (wrong columns, missing values, non-numeric entries) with helpful messages
- **Safety:** Clear disclaimer + no claims of medical guidance; encourages professional consultation
- **Demo Readiness:** A 90-second demo can show end-to-end value (upload → insights → export)

## Next Iteration Ideas
- Add multiple “rulesets” (e.g., thresholds by gene group)
- Add data schema templates for common vendor formats
- Add evaluation harness + test dataset library
- Add optional local-only persistence (explicit user opt-in)