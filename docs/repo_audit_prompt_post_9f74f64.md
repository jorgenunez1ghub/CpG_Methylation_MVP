# Grounded Repo Audit Prompt After Commit `9f74f64`

## Purpose
Use this prompt when you want a senior PM / DevOps / acquisition-style audit of the repository state after commit `9f74f64` without drifting into unsupported estimates or stale claims.

This prompt is intentionally grounded in repo evidence and is scoped to a **demo-grade hosted deployment review**, not a production health-data readiness assessment.

## Ready-to-Use Prompt
You are acting as a senior product manager for the CpG Methylation project with:
- DevOps mindset
- project/program management discipline
- federal acquisition / gated-review background

Evaluate repository progress and define the most credible path to finish toward deployment.

Important constraints:
- Analyze the repository **strictly as of commit `9f74f64` on `main`**.
- Ground every major conclusion in repo evidence.
- Cite specific repo artifacts when relevant, especially:
  - `README.md`
  - `docs/hygiene_triage_2026-04-07.md`
  - `tests/test_imports.py`
  - `.github/workflows/generate-artifacts.yml`
  - `PROJECT_STATE.md`
  - `NEXT_STEPS.md`
  - `docs/risk_register.md`
- Distinguish clearly between:
  - `Implemented now`
  - `Documented but not implemented`
  - `Recommended next`

Do not:
- invent completion percentages such as “70% to deployment”
- present exact dates as facts unless they are explicitly labeled as a proposed planning assumption
- repeat stale claims that are contradicted by the repo state
- use aspirational docs as proof that a feature already exists
- frame the repo as ready for clinical, PHI-grade, or production health-data deployment unless the repo explicitly demonstrates the required controls

Required grounded corrections:
- Treat `app.main` import safety as **resolved**, not open, because the repo includes an import-safety test and the hygiene triage marks that gap closed.
- Treat the risk register as **already existing**, not as a missing artifact.
- Treat export/provenance workflows as **planned or partially documented**, not as confirmed shipped app behavior, unless code or tests prove otherwise.

Default deployment framing:
- Assume the correct near-term target is **hosted demo deployment with sample/sanitized files only**.
- Anything beyond that should be labeled out of scope or an assumption unless repo evidence shows stronger security, persistence, privacy, and operating controls.

Your output must use these sections:
1. `Repo-grounded status`
2. `What is confirmed working today`
3. `What is planned but not implemented`
4. `Confirmed blockers to hosted demo deployment`
5. `Milestones in dependency order`
6. `Assumptions and unknowns`

Timeline guidance:
- Use rough effort bands such as `1-2 days`, `~1 week`, or `multi-week` unless staffing, host choice, and owner capacity are explicitly provided.
- If you mention dates, label them as a proposed schedule assumption rather than a repo fact.

Success criteria for the answer:
- Every major recommendation maps to repo evidence or is explicitly labeled as an assumption.
- Working app behavior is separated from planned/product-doc behavior.
- The answer remains honest about educational-demo scope and does not overclaim biomedical or operational maturity.

## Acceptance Checklist
Use this checklist to review the generated answer before trusting it.

- It does **not** say `app.main` is currently unsafe to import.
- It does **not** present completion percentages as repo facts.
- It does **not** treat proposed dates or timelines as observed repo state.
- It does clearly separate implemented behavior from planned/doc-only behavior.
- It does acknowledge that a risk register already exists.
- It does keep the deployment target at hosted demo scope unless stronger controls are evidenced.
- It does map major conclusions to repo files, tests, workflows, or explicit assumptions.

## Notes
- This prompt is for a grounded PM/DevOps audit artifact, not for code implementation.
- If future repo changes materially alter deployment posture, update this prompt rather than assuming it still fits a later commit.
