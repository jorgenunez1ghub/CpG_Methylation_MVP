# PROJECT_STATE.md

## Project
CpG_Methylation_MVP

## Current Goal
Deliver a lightweight, credible Streamlit MVP for CpG methylation file upload, validation, normalization, and quick QC review.

The near-term objective is to make the repo:
- easy to run locally
- safe for demo use
- cleanly structured for future RAG / explanation features
- ready for portfolio presentation as an AI-health data workflow MVP

---

## Current Status
**Stage:** MVP foundation in place  
**Status:** Working prototype / cleanup and hardening phase  
**Primary Mode:** Local demo app with canonical parsing + QC  
**Default Branch:** `main`

### What exists now
- Streamlit app entrypoint at `app/main.py`
- `src/` package layout with `cpg_methylation_mvp.core`
- Core logic separated from Streamlit UI
- Upload flow for `.csv`, `.tsv`, `.txt`
- Parsing and normalization into canonical schema
- QC summary metrics and beta histogram
- Editable install via `pyproject.toml`
- `.env.example` present
- README with quickstart, architecture guardrails, and demo flow

### Current app promise
Upload methylation file → parse → validate → normalize → inspect QC summary.

---

## Product Intent
This repo is a **lightweight educational MVP**, not a clinical or production diagnostic tool.

### Intended use
- portfolio demo
- architecture learning repo
- context-engineering / RAG-ready health-data workflow foundation
- future customer onboarding + upload + interpretation experience prototype

### Non-goals right now
- medical diagnosis
- production-grade PHI handling
- advanced biological interpretation engine
- full multi-user deployment
- persistent database-backed workflows

---

## What Works
Based on repo structure and app code:

- Streamlit app bootstraps from `app/main.py`
- File uploader accepts supported text tabular formats
- Upload bytes are cached for rerun efficiency
- Parsed data is normalized into canonical schema
- QC summary is generated from normalized dataframe
- Histogram rendering is optimized for large-file-safe visualization
- Core logic is intended to remain framework-agnostic and separate from Streamlit
- Repo uses modern Python packaging with `pyproject.toml`

---

## Architecture Guardrails
These guardrails should remain true unless intentionally changed.

### Separation of concerns
- `app/` = Streamlit UI only
- `src/cpg_methylation_mvp/core/` = business logic only
- core modules must **not** import Streamlit
- UI copy/config belongs in `app/ui_config.py`

### Data handling
- uploaded files should be treated as local demo inputs unless a future secure architecture is added
- repo should store only safe sample data, schemas, and synthetic examples
- private or real health-related files should not be committed

### Product guardrail
- always preserve educational-demo disclaimer
- avoid language that implies diagnosis, treatment, or medical certainty

---

## Repo Health Assessment
### Strengths
- clean conceptual architecture for an MVP
- good separation between UI and core logic
- clear README framing
- packaging is already more mature than a one-file prototype
- caching choices show performance awareness

### Current risks / likely gaps
- repo may still be out of sync with local work
- data hygiene rules may not yet be fully enforced
- schema docs are not yet clearly visible as first-class repo assets
- tests may exist but likely need expansion
- no explicit `PROJECT_STATE.md` / `NEXT_STEPS.md` re-entry docs yet
- no explicit data dictionary / validation contract surfaced for external readers
- future AI/RAG placeholders exist in config, but not yet implemented

---

## Known Gaps
These are the most likely missing or incomplete layers for the next phase.

### Documentation gaps
- `DATA_DICTIONARY.md`
- `SCHEMA.md`
- `validation_rules.md`
- `NEXT_STEPS.md`
- explicit sample file documentation

### Engineering gaps
- stronger tests for parser edge cases
- more robust invalid-file handling
- clearer canonical schema contract
- branch and sync discipline between local and GitHub
- formal ignore rules for local-only uploads / outputs / secrets

### Product gaps
- biological interpretation layer not yet present
- no explanation UX for “what these QC results mean”
- no RAG context layer yet
- no audit or provenance view for uploaded files
- no saved session / export workflow

---

## Current Canonical Workflow
1. User opens Streamlit app
2. User uploads methylation file
3. File is parsed and normalized
4. Validation / QC metrics are computed
5. User sees normalized table and summary
6. User views beta distribution histogram

This is the current MVP spine and should remain stable while repo hygiene is improved.

---

## Current Priority
**Priority 1:** Repo hygiene and sync stability  
**Priority 2:** Data contract clarity  
**Priority 3:** Demo readiness  
**Priority 4:** Interpretation / RAG expansion

---

## Next 5 Practical Moves
### 1. Add data contract docs
Create:
- `SCHEMA.md`
- `DATA_DICTIONARY.md`
- `validation_rules.md`

### 2. Harden repo hygiene
Confirm `.gitignore` excludes:
- `.env`
- `.venv/`
- `__pycache__/`
- `uploads/`
- `outputs/`
- `data/raw/`
- notebook checkpoints
- generated reports

### 3. Add project re-entry docs
Create:
- `NEXT_STEPS.md`
- update this `PROJECT_STATE.md` weekly

### 4. Expand tests
Add tests for:
- missing required columns
- malformed delimiters
- non-numeric beta values
- out-of-range beta values
- empty uploads
- duplicate CpG rows
- optional metadata preservation

### 5. Prepare interpretation layer
Design the next module boundary for:
- QC explanation
- marker-level lookup or evidence mapping
- future retrieval layer
- user-facing “what should I look at next?” panel

---

## Recommended Branch Strategy
- `main` = stable, demoable
- `feature/...` = active work
- `fix/...` = small corrections
- `docs/...` = documentation-only changes
- `rescue/...` = temporary backup before cleanup

Suggested near-term branch names:
- `feature/cpg-repo-hygiene`
- `feature/cpg-schema-docs`
- `feature/cpg-qc-explanations`
- `fix/cpg-upload-validation`

---

## Definition of “Healthy MVP” for This Repo
This project is in a healthy state when:

- repo and local are in sync
- `main` runs cleanly from README quickstart
- sample input works end-to-end
- schema and validation rules are documented
- tests cover core ingestion edge cases
- no sensitive/local-only files are tracked
- README clearly explains scope and limitations
- next-step roadmap is visible to future-you

---

## Local-Only / Do Not Commit
Never commit:
- real personal health files
- client/user uploads
- `.env`
- secrets or API keys
- generated analysis outputs unless intentionally sanitized
- raw local experiment dumps

---

## Open Questions
- What exact canonical schema should be locked as version `v1`?
- Should duplicate CpG handling aggregate, warn, or preserve row-level input?
- What metadata columns should be preserved through normalization?
- What is the first interpretation feature: QC explanation, biomarker summaries, or evidence-backed retrieval?
- Will this remain a pure local demo, or evolve into a secure hosted workflow?

---

## Suggested Near-Term Milestone
### Milestone: “Demo-Stable Foundation”
To complete this milestone:
- repo is clean and synced
- schema docs exist
- sample file is documented
- tests cover ingestion basics
- README and project state reflect current architecture
- app demo is reproducible on a fresh local setup

Target outcome:
A polished, explainable, portfolio-ready MVP foundation that can later support RAG-based interpretation and richer health-data workflows.

---

## Last Review Notes
This repo already shows strong instincts:
- package-first structure
- UI/core separation
- caching awareness
- explicit guardrails in README
- future integration placeholders without overcommitting too early

The right next move is not to add more features immediately.  
The right next move is to **stabilize the foundation** so future interpretation, retrieval, and product layers sit on a clean base.
