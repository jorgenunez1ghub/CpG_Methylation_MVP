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
- The context package remains experimental until a real evidence source and citation contract are defined.
