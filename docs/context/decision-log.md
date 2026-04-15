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
- Any future addition of lint, type checks, hosted smoke tests, or evals should be wired into `make verify` only when the underlying tool is configured and documented.
