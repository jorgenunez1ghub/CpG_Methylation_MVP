# Release 0.1 Plan — Hosted Demo (Level 1)

**Date:** 2026-04-07  
**Program increment:** Release 0.1  
**Target:** Hosted demo deployment for sample/sanitized inputs only  
**Out of scope for this release:** PHI-grade production deployment, persistent multi-user workflows, advanced biological interpretation

---

## 1) Release decision memo (Milestone 0 output)

### Decision
Proceed with **Level 1** as the immediate deployment target: a hosted demo that supports only sample/sanitized uploads.

### Why this target is correct now
- The current repo is strongest on upload → validate → normalize → QC workflow reliability.
- Architecture boundaries (Streamlit app layer vs framework-agnostic core) are already present and worth preserving.
- Existing docs explicitly frame the project as MVP/prototype and non-production for health-data handling.

### Non-goals (explicit)
- No claim of clinical readiness.
- No claim of PHI-compliant operations.
- No positioning as a secure external health-data product.

### Scope guardrails
- Demo-safe files only (synthetic/sanitized).
- Trust and transparency over breadth of feature set.
- No speculative biomarker or medical claims in app outputs.

---

## 2) Milestones 0–5 with Definition of Done (DoD)

## Milestone 0 — Program Re-baseline
**Dates:** 2026-04-08 to 2026-04-09  
**Goal:** lock target and governance model

### Deliverables
- Release target statement (Level 1 hosted demo).
- Scope freeze for Release 0.1.
- Must-have vs nice-to-have split.
- Initial risk register entries aligned to deployment scope.

### Definition of Done
- Team-approved statement: "Release 0.1 is a hosted demo for sanitized/sample files only."
- Single hosting path selected.
- Single accountable owner assigned per workstream (app/core, tests/CI, docs, deploy ops).

---

## Milestone 1 — Demo-Stable Foundation
**Dates:** 2026-04-10 to 2026-04-16  
**Goal:** make contract and runtime behavior legible

### Deliverables
- `SCHEMA.md` (canonical schema and required/optional fields).
- `DATA_DICTIONARY.md` (column semantics and examples).
- `validation_rules.md` (hard-fail vs warning behavior).
- README alignment with actual supported file contract and demo scope.
- `app/main.py` runtime-safe orchestration pattern for import/launch behavior.
- Explicit Python version support statement.

### Definition of Done
- A new contributor can determine valid input without reading core code.
- App startup/import behavior is documented and repeatable.
- CI remains green and app runs locally end-to-end on sample data.

---

## Milestone 2 — Quality + Contract Hardening
**Dates:** 2026-04-17 to 2026-04-23  
**Goal:** reduce ingestion/validation ambiguity and regression risk

### Deliverables
- Tests for:
  - missing required columns,
  - non-numeric beta values,
  - out-of-range beta values,
  - empty upload,
  - delimiter ambiguity,
  - duplicate CpG policy behavior,
  - known-file contract test.
- Explicit duplicate `cpg_id` behavior documented.
- Explicit metadata-column preservation/drop policy documented.
- Sample dataset documentation strengthened.

### Definition of Done
- File contract is tested, not just smoke-tested.
- Expected behavior for duplicate and metadata edge cases is explicit.
- Push/PR CI passes without manual exceptions.

---

## Milestone 3 — Deployment Packaging
**Dates:** 2026-04-24 to 2026-04-30  
**Goal:** repeatable deploy process and reproducible artifacts

### Deliverables
- Deployment manifest/config for selected host.
- Runtime/config documentation (`.streamlit` and env expectations).
- Smoke script/runbook.
- Export support:
  - normalized CSV,
  - QC summary JSON,
  - provenance block (filename, timestamp, delimiter, row counts).
- Basic structured logging for processing traceability.

### Definition of Done
- Fresh clone to hosted deploy is documented and reproducible.
- Artifacts are inspectable with clear provenance.
- Smoke checks pass on target hosting environment.

---

## Milestone 4 — Trust, UX, and Release Controls
**Dates:** 2026-05-01 to 2026-05-07  
**Goal:** external-demo safety and usability readiness

### Deliverables
- Plain-language interpretation helper next to QC metrics.
- Clear educational/non-medical disclaimer in-app.
- Session/no-persistence behavior documented.
- Release checklist, rollback checklist, lightweight incident runbook.
- UAT script (8–10 representative scenarios).

### Definition of Done
- Stakeholder can run demo without developer narration.
- Failure states are understandable and bounded.
- Language avoids medical overclaim and diagnostic framing.

---

## Milestone 5 — Hosted Demo Go-Live
**Dates:** 2026-05-08 to 2026-05-14  
**Goal:** live, accessible demo release

### Deliverables
- Hosted deployment completed.
- Smoke test evidence recorded.
- Demo screenshots + walkthrough notes.
- Known-issues list captured.
- Release tag created (`v0.1-demo` or equivalent).

### Definition of Done
- External stakeholder can access and run sample upload workflow.
- Normalization and QC views behave as documented.
- Export path works for demo artifacts.
- Secrets/private data are absent from repo and host config.

---

## 3) Critical path (must not slip)

1. Lock release scope (Level 1 only).  
2. Lock schema + validation contract.  
3. Expand ingestion/contract tests for edge cases.  
4. Package deployment path with runbook/smoke checks.  
5. Add release and rollback controls.  
6. Launch with honest demo-grade framing.

If any of steps 1–3 are skipped, trust in analysis outcomes is weak. If steps 4–5 are skipped, deployment repeatability is weak.

---

## 4) Governance model and gate criteria

## Gate A — Scope Readiness
- Release target, user profile, and non-goals approved.
- Demo-safe data policy approved.

## Gate B — Technical Readiness
- Schema contract docs complete.
- Contract and edge-case tests passing.
- App/core separation preserved.

## Gate C — Operational Readiness
- Deployment manifest present.
- Smoke and rollback runbooks validated once.
- Logging/provenance minimum in place.

## Gate D — Trust Readiness
- Disclaimer and no-overclaim language reviewed.
- QC limitations explained clearly.
- Artifact outputs include provenance context.

## Gate E — Go-Live Approval
- Hosted environment validated.
- Known issues acknowledged.
- Release tag + release notes completed.

---

## 5) Risk register (Release 0.1 view)

| ID | Risk | Likelihood | Impact | Control / Mitigation | Trigger to escalate | Owner |
|---|---|---:|---:|---|---|---|
| R1 | Scope creep into production-grade claims | Medium | High | Scope freeze + release statement + gate checks | New feature requests imply PHI/security promises | PM |
| R2 | Input contract ambiguity causes user errors | High | High | Schema/data dictionary/validation docs + UI contract hints | Repeated support questions on valid format | App/Core |
| R3 | Hidden ingestion behavior reduces trust | Medium | High | Before/after row accounting + dropped-row reasons + tests | QC results inconsistent with user expectation | Core |
| R4 | Deployment drift (works locally, not hosted) | Medium | High | Deployment manifest + smoke script + runbook | Failed smoke test after config change | DevOps |
| R5 | Over-interpretation of output as medical advice | Medium | High | In-app disclaimer + language review + UAT script | Stakeholder confusion about diagnostic meaning | PM/UX |
| R6 | Sensitive data accidentally uploaded in demo | Medium | High | Demo-safe policy + warnings + no persistence + hygiene checks | User attempts real identifiable uploads | PM/Ops |
| R7 | Regression in ingestion edge cases | Medium | Medium | Contract tests + CI gating | PR merges with broken edge-case handling | Core |
| R8 | Insufficient rollback readiness | Low | High | Rollback checklist + prior version tag + ownership | Post-release defect with no quick recovery | DevOps |

---

## 6) Release 0.1 Definition of Done (program-level)

Release 0.1 is done when all conditions below are true:

1. Hosted demo is reachable by external stakeholders.
2. Upload → validate → normalize → QC flow works on sample/sanitized inputs.
3. Input contract is documented (`SCHEMA.md`, `DATA_DICTIONARY.md`, `validation_rules.md`).
4. CI includes contract-focused ingestion tests for common malformed inputs.
5. Deployment + smoke + rollback steps are documented and executable.
6. Output framing is educational and non-diagnostic, with visible limitations.
7. Repo and deployment configuration contain no secrets or private upload artifacts.

---

## 7) Evidence package checklist (for gate reviews)

- Gate A: release decision memo + scope/non-goal list.
- Gate B: schema contract docs + test run logs + architecture checks.
- Gate C: deployment manifest + smoke evidence + rollback drill notes.
- Gate D: UI disclaimer screenshots + UAT outcomes + wording review.
- Gate E: live URL, release tag, known issues, post-go-live monitoring notes.

This checklist is designed to keep Release 0.1 auditable, bounded, and demo-credible without overstating production readiness.
