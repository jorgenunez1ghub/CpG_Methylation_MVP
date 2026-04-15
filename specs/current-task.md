# Current Task Spec

## Goal
Add a lightweight agent-workflow operating layer that helps future work start with clear context and end with deterministic verification.

## Context
The repo already has strong project-state, next-step, workflow, schema, validation, and release docs. The missing practical pieces were:
- a single local verification command,
- a concise root-level program wrapper,
- a durable context pack for future agent sessions,
- a decision log for repo-operating choices.

Remote GitHub state checked on 2026-04-14:
- local `main` matched `origin/main`,
- no open PRs,
- no open issues.

## Constraints
- Preserve existing app behavior and public core API.
- Do not add biomedical, ML, RAG, or lint/typecheck dependencies in this pass.
- Keep Streamlit-specific logic out of core modules.
- Keep artifacts short enough to be useful as handoff context.

## Done When
- `Makefile` provides `make verify`.
- `program.md` explains the repo operating model.
- `docs/context/context-pack.md` captures the minimal handoff context.
- `docs/context/decision-log.md` records the operating decision.
- README and daily dev docs point to the verification command.
- `make verify` passes locally.

## Next Spec Update
Replace this file at the start of the next implementation session with the next small task from `NEXT_STEPS.md`.
