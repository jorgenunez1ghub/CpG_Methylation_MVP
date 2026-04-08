# NEXT_STEPS.md

## Purpose
This file is the active execution list for **CpG_Methylation_MVP**.  
Pair it with `PROJECT_STATE.md` to keep work intentional, the repo clean, and the demo reproducible.

---

## Release planning artifact
- See `docs/release_0_1_demo_plan_2026-04-07.md` for the scoped Level 1 hosted-demo release plan, gates, risk register, and program DoD.

---

## Next Milestone: Demo-Stable Foundation
**Definition of Done (DoD):**
- Fresh clone → `pip install -e .` → `streamlit run app/main.py` works
- Uploading `data/sample/*` runs end-to-end with expected outputs
- Canonical schema and validation rules are documented
- No secrets / private uploads are tracked by Git
- Basic tests cover ingestion and validation edge cases
- Repo structure is predictable and “portfolio ready”

---

## 0) Immediate Safety + Sync (Do this first)
### 0.1 Snapshot local work (if any)
- Create a rescue branch before cleanup if local is messy:
  - `rescue/cpg-pre-cleanup-YYYY-MM-DD`

### 0.2 Verify remote + branch state
- Confirm you are on the intended branch (`main` or feature branch)
- `git fetch origin` then inspect:
  - local ahead/behind
  - uncommitted changes
  - untracked files

### 0.3 Enforce repo hygiene
- Ensure `.gitignore` excludes:
  - `.env`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`
  - `uploads/`, `outputs/`, `data/raw/`
  - `.streamlit/secrets.toml`
- If any sensitive/local-only files are currently tracked:
  - remove from tracking via `git rm --cached ...`

**Exit condition:** `git status` is clean OR changes are committed on a rescue/feature branch.

---

## 1) Data Contract (Make the MVP legible)
### 1.1 Create and fill these docs
- `SCHEMA.md`  
  - canonical columns (v1)
  - required vs optional fields
  - allowed types and ranges
- `DATA_DICTIONARY.md`  
  - each column definition (meaning + units if relevant)
  - example values
- `validation_rules.md`  
  - exact validation checks
  - error messages and handling
  - what is warning vs hard failure

### 1.2 Add/confirm safe sample input
- `data/sample/methylation_sample.csv` (or similar)
- Document it in README:
  - file origin (synthetic / sanitized)
  - what it covers (required cols, optional cols, edge cases)

**Exit condition:** A new reader can understand what “valid input” means without reading code.

---

## 2) App UX Hardening (Minimum viable product polish)
### 2.1 Tighten upload error handling
- Ensure errors are:
  - specific (“missing column X”)
  - actionable (“expected columns: …”)
  - non-technical when possible (for demo)

### 2.2 Normalize output stability
- Confirm canonical output always includes:
  - `cpg_id`
  - `beta`
  - preserves optional metadata if present (explicitly defined)

### 2.3 QC view improvements (low effort, high value)
- Add a small “What this means” text block near QC metrics:
  - what missing beta implies
  - what out-of-range implies
  - what beta distribution shows

**Exit condition:** Demo feels intentional, not like raw developer output.

---

## 3) Tests (Fast, targeted coverage)
### 3.1 Add smoke tests for ingestion
Create tests that cover:
- happy path (valid sample)
- missing required columns
- non-numeric beta values
- out-of-range beta values (<0 or >1)
- empty file
- delimiter ambiguity (comma vs tab)
- duplicate CpG IDs handling (warn/allow/aggregate — choose behavior)

### 3.2 Add one “contract test”
- Given a known input file:
  - output schema matches canonical spec
  - QC metrics match expected values (within tolerance)

**Exit condition:** `pytest -q` passes locally and prevents regressions.

---

## 4) Repo Structure + Docs (Portfolio readiness)
### 4.1 Confirm structure
Target structure (not strict, but consistent):

- `app/` UI orchestration only
- `src/` core logic only
- `tests/` fast tests
- `docs/` architecture + decisions
- `data/sample/` safe samples only

### 4.2 Add or refresh docs
- `docs/architecture.md` (1 page)
  - flow diagram: upload → parse → validate → normalize → qc → render
- `docs/decisions/` (optional)
  - a short decision log entry for canonical schema v1

### 4.3 Update README
- Ensure README is aligned with reality:
  - exact run instructions
  - what sample file to use
  - what “canonical” means

**Exit condition:** Repo reads like a product, not a scratchpad.

---

## 5) Next Feature Track (After foundation is stable)
Pick **one** (avoid parallel complexity):

### Track A — QC Explanation Layer (best “next demo”)
- Add an explanation panel that:
  - interprets QC metrics in plain language
  - suggests next actions (“check file format”, “verify preprocessing”, etc.)
- Keep explanations deterministic (no LLM required yet)

### Track B — RAG-Ready Evidence Layer (future AI add-on)
- Add a `docs/context_pack/` describing:
  - what evidence sources will be retrieved
  - how results will be cited
  - what the model is allowed to claim (guardrails)
- Keep OpenAI keys optional (placeholders already exist)

### Track C — Export + Session Provenance
- Add “Export normalized CSV” + “Export QC summary JSON”
- Add a simple provenance block:
  - filename
  - timestamp
  - detected delimiter
  - row counts before/after normalization

---

## Operating Rules (Non-Negotiables)
- **No secrets committed** (ever)
- **No real user health uploads committed**
- `main` stays demoable
- Use feature branches for changes beyond tiny edits
- End each work session with:
  - committed changes
  - pushed branch
  - `git status` clean

---

## Suggested Branch Plan (Near Term)
- `feature/cpg-repo-hygiene`
- `feature/cpg-schema-docs`
- `feature/cpg-tests-ingestion`
- `feature/cpg-qc-explanations`
- `feature/cpg-duplicate-adr`
- `feature/cpg-hosted-smoke-automation`
- `feature/cpg-delimiter-quarantine`

---

## Daily “Re-entry” Checklist (2 minutes)
1. `git status`
2. `git fetch origin`
3. `git branch -vv`
4. Open `PROJECT_STATE.md` + this file
5. Pick **one** step and ship it to a clean commit

---

## Current Top 3 Next Actions
1. **Approve the revised duplicate aggregation ADR**
   Deliverables: approval decision on `docs/duplicate_aggregation_adr.md` and explicit sign-off on the policy/report disclosure contract.
2. **Add a deliberate hosted smoke automation track**
   Deliverables: one chosen browser stack, one deployed smoke workflow, and a non-blocking first CI pass over the hosted URL.
3. **Design mixed-delimiter quarantine recovery**
   Deliverables: explicit pre-normalization/quarantine workflow, user-visible quarantine counts, and tests that prove recovery is not silent.

(These are the highest-value follow-on steps now that ingestion hardening, duplicate review, and local Streamlit smoke coverage are in place.)
