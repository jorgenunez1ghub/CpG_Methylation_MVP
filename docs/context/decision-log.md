# Decision Log

## 2026-04-14 - Add Lightweight Agent Workflow Controls

### Decision
Adopt a small operating layer for future agent-assisted work:
- root `program.md`,
- `specs/current-task.md`,
- `docs/context/context-pack.md`,
- `docs/context/decision-log.md`,
- `make verify`.

### Why
The repo already has substantial product and workflow documentation. The useful next step from the agent-production workflow frame is not multi-agent orchestration; it is clearer task framing, compact context handoff, and deterministic verification.

### Scope
Included:
- local verification command,
- task-control docs,
- docs alignment for daily development and README usage.

Excluded for now:
- new lint/typecheck dependencies,
- multi-agent handoff schemas,
- biomedical/RAG feature work,
- changes to ingestion, validation, normalization, QC, or Streamlit behavior.

### Consequences
- Future work should start by updating `specs/current-task.md`.
- `make verify` is the default local gate.
- Future hosted smoke tests or evals should be wired into `make verify` only when the underlying tool is configured and documented.

## 2026-04-14 - Add Lint/Typecheck Gate And Package Context Helpers

### Decision
Add dev-only Ruff and mypy tooling, wire both into `make verify`, and move the experimental context helpers from top-level `src/context/` into `src/cpg_methylation_mvp/context/`.

### Why
The repo needed deterministic feedback beyond tests, and the context helpers were useful for future RAG/evidence workflows but ambiguous because they lived outside the installable package and imported a missing prompt module.

### Scope
Included:
- `ruff`, `mypy`, and `pandas-stubs` as dev dependencies,
- Ruff and mypy configuration in `pyproject.toml`,
- `make lint` and `make typecheck`,
- package-scoped context helpers with a cautious prompt builder,
- focused context-helper and architecture tests.

Excluded for now:
- wiring context helpers into the Streamlit app,
- adding embeddings, vector databases, OpenAI calls, or retrieval dependencies,
- expanding biomedical interpretation claims.

### Consequences
- `make verify` now fails on lint, typecheck, or test regressions.
- Future RAG work should import from `cpg_methylation_mvp.context`, not from a top-level `src/context` module.
- The context package remains local-only until an external evidence source decision is made.

## 2026-04-14 - Wire Local Evidence Context Without LLM Dependencies

### Decision
Define a local evidence contract, add a repo-doc evidence index, and render deterministic cited context in the Streamlit app.

### Why
The context package needed a concrete evidence source and citation/display contract before any embedding, vector-store, or LLM-backed interpretation work. A local repo-doc index is the smallest useful source because it grounds current workflow, schema, validation, duplicate, and data-policy guidance without adding scientific claims.

### Scope
Included:
- `docs/context/evidence_contract.md`,
- `data/evidence/workflow_01_context_chunks.json`,
- evidence contract validation helpers,
- deterministic Workflow 01 context builder,
- app rendering for cited local context,
- tests for evidence loading, context building, app table output, and invalid source rejection.

Excluded for now:
- external scientific literature sources,
- embeddings or vector storage,
- LLM calls,
- clinical evidence claims.

### Consequences
- The app now has a cited context section backed by local repo docs.
- Retrieved context remains repo-policy/workflow evidence, not biomedical evidence.
- Future external RAG work must extend the evidence contract before adding new sources.

## 2026-04-14 - Define External Scientific RAG Source Gate

### Decision
Add an external scientific RAG policy and machine-readable source rules without enabling external retrieval at runtime.

### Why
External scientific retrieval needs source quality, freshness, review, and citation rules before implementation. The repo should not add embeddings, vector storage, or LLM-backed interpretation until those rules are enforceable.

### Scope
Included:
- `docs/context/external_scientific_rag_policy.md`,
- `data/evidence/external_source_policy.json`,
- policy validation in `cpg_methylation_mvp.context`,
- tests proving the policy exists and runtime use remains disabled until approved.

Excluded for now:
- external source registry,
- external fetching,
- embeddings/vector database,
- LLM calls,
- clinical or marker actionability claims.

### Consequences
- Future scientific RAG work must create a reviewed source registry before enabling runtime use.
- `runtime_enabled` must remain `false` until an explicit implementation decision updates the policy and tests.
- Citations for external chunks must include locator, freshness, review, claim-scope, and limitation fields.
