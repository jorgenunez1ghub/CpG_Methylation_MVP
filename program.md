# CpG Methylation MVP Program

## Purpose
Keep this repo focused on one trustworthy educational workflow: upload a CpG methylation file, validate and normalize it, inspect QC, evaluate curated demo-panel coverage, and return cautious structured interpretation.

This file is the operating wrapper for agent-assisted work. It does not replace the product docs; it points each work session to the minimum context needed to make a small, reviewable change.

## Product Boundary
- Educational demo only; not medical advice.
- Sample or sanitized inputs only.
- Streamlit stays in `app/`.
- Framework-agnostic ingestion, validation, transformation, panel, and analysis logic stays in `src/cpg_methylation_mvp/core/`.
- Future RAG or explanation work must preserve explicit uncertainty, citations, and non-clinical framing.

## Current Program Goal
Reach and preserve a demo-stable Release 0.1 foundation:
- valid sample upload runs end to end,
- canonical schema and validation behavior are documented and tested,
- outputs remain inspectable and reproducible,
- deployment and smoke checks are repeatable,
- repo hygiene supports GitHub review without hidden local state.

## Core Operating Loop
Use this four-field task spec before implementation:

```text
Goal:
Context:
Constraints:
Done when:
```

Then work in this order:
1. Read `PROJECT_STATE.md`, `NEXT_STEPS.md`, and `specs/current-task.md`.
2. Open only the files needed for the task plus `docs/context/context-pack.md`.
3. Make the smallest shippable change.
4. Run `make verify`.
5. Update docs, tests, or the decision log when behavior or workflow changes.

## Verification Gate
The default local gate is:

```bash
make verify
```

That command currently runs environment/import checks, Ruff linting, mypy type checking, and the pytest suite. Add evals or hosted smoke checks to `make verify` only after those tools are explicitly configured.

## Source Of Truth Map
- Product state: `PROJECT_STATE.md`
- Active next actions: `NEXT_STEPS.md`
- Current implementation task: `specs/current-task.md`
- Durable context pack: `docs/context/context-pack.md`
- Decision trail: `docs/context/decision-log.md`
- Workflow contract: `docs/workflows/mvp_workflow_01.md`
- Release plan: `docs/release_0_1_demo_plan_2026-04-07.md`
- Experimental context helpers: `src/cpg_methylation_mvp/context/`

## Change Guardrails
- Do not add speculative biomedical interpretation.
- Do not move business logic into Streamlit.
- Do not introduce large dependencies without an explicit decision.
- Do not reduce QC transparency for presentation polish.
- Keep every change rollback-friendly and test-backed when behavior changes.
