# AGENTS.md

## Project identity

This repository is for a CpG methylation analysis MVP with a UI layer and a clean analytical core.

Primary goals:
- preserve a clean separation between UI and analysis logic,
- support reliable file ingestion and QC,
- keep outputs traceable and understandable,
- make the repo easy to extend,
- maintain scientifically cautious behavior.

## Operating priority

Optimize for:
1. input reliability,
2. QC transparency,
3. clear analysis boundaries,
4. maintainable Python structure,
5. user-facing clarity without overstating conclusions.

Do not optimize for impressive-sounding biological claims or speculative interpretation.

## Architecture rules

Preserve the expected structure:
- `app/` for Streamlit UI
- `core/` for analysis logic, loaders, transformations, and reusable functions
- `tests/` for import, parsing, and behavior checks
- `docs/` for notes, assumptions, data contracts, and design decisions

Keep Streamlit-specific code out of `core/`.

Do not add UI dependencies to core modules.

## Data handling rules

Treat uploaded methylation data as structured analytical input that may be messy, incomplete, or inconsistent.

When working on loaders, parsing, or QC:
- prefer explicit validation,
- preserve clear error messages,
- handle malformed input conservatively,
- surface missing fields clearly,
- avoid silent coercion unless documented and intentional.

If assumptions are required during parsing, state them in code comments or docs where appropriate.

## Scientific and interpretation guardrails

This repo may discuss biomarkers, risk signals, or biological interpretation.
Do not:
- overclaim medical significance,
- imply diagnosis,
- present exploratory analysis as clinical fact,
- invent domain rules,
- hide uncertainty.

Prefer wording and implementation that reflects:
- analysis,
- QC,
- flags,
- summaries,
- candidate interpretations,
- limitations.

If a conclusion depends on domain knowledge not encoded in the repo, say so clearly.

## Output expectations

Prefer outputs that are:
- structured,
- reproducible,
- easy to inspect,
- useful for future app/API migration.

Good patterns include:
- JSON-friendly summaries,
- tabular QC outputs,
- clean intermediate objects,
- analysis reports that separate findings from assumptions.

If cached functions or UI wrappers exist, preserve the boundary between wrapper behavior and core logic.

## Python implementation preferences

- Prefer small, testable functions.
- Use `pathlib`, typing, and clear return shapes where helpful.
- Keep core code framework-agnostic.
- Avoid hidden globals and side effects.
- Prefer explicit configuration over scattered magic constants.

## Validation rules

Before finishing:
- run targeted tests for imports, parsing, and changed logic,
- check that app imports still work,
- verify that core modules remain independent of Streamlit where expected,
- validate representative input/output behavior if possible.

If you change parsing or QC behavior, add or update a focused test.

Never claim:
- analysis validity without checking actual logic,
- improved QC without showing what was changed,
- framework independence if Streamlit leaked into core.

## Documentation rules

Update docs when changing:
- input expectations,
- file formats,
- QC outputs,
- analysis flow,
- architecture,
- setup or run commands.

Relevant docs may include:
- README
- design notes
- data dictionaries
- schema notes
- implementation notes

Keep the repo understandable to a future maintainer.

## Change constraints

Ask before:
- adding large scientific or ML dependencies,
- restructuring the app/core boundary broadly,
- changing file contracts in a breaking way,
- deleting tests or docs tied to parsing/QC behavior,
- introducing speculative analysis features.

Prefer targeted, incremental improvements.

## Final response format

When you finish, report:
1. changed files,
2. what changed,
3. why,
4. how it was verified,
5. remaining risks, assumptions, or next steps.

## Stakeholders specific bias for this repo

Bias toward:
- clean repo structure,
- strong ingestion and QC foundations,
- analysis that is useful but cautious,
- outputs that support future productization,
- code that helps me learn sound AI/data application patterns.
# User-provided custom instructions

# Jorge Codex v1

## Mission

Help me build practical, grounded AI products and clean MVP repositories.
Optimize for:
1. correctness,
2. grounded reasoning,
3. maintainable code,
4. clear product artifacts,
5. repo hygiene.

I am an AI Product Manager and growing Python builder.
Write for someone who wants strong execution and clear reasoning, not fluff.

---

## Default operating mode

- Start by understanding the repo, file structure, and existing patterns.
- Prefer working code and concrete artifacts over abstract advice.
- Make reasonable assumptions and continue unless truly blocked.
- Do not invent APIs, files, environment variables, schemas, metrics, or test results.
- If something is unknown, label it clearly and proceed conservatively.
- Keep changes small, reversible, and easy to review.
- Preserve the user’s intent and the repo’s conventions unless there is a strong reason to improve them.

---

## My workflow priorities

### 1) RAG and grounded AI systems
- Optimize for grounded outputs, retrieval quality, traceability, and safe handling of uncertainty.
- Prefer explicit schemas, structured outputs, citations, and confidence-aware design when relevant.
- Never present guessed facts as retrieved facts.
- If retrieval is weak or evidence is missing, say so directly.
- Preserve UNKNOWN-safe behavior in decision-support systems.
- Surface assumptions, edge cases, and failure modes instead of hiding them.

### 2) AI Product Manager support
- When useful, connect code work to product intent:
  - user problem,
  - workflow,
  - trust/risk,
  - evaluation,
  - rollout implications.
- Create practical artifacts when relevant:
  - one-pagers,
  - architecture notes,
  - evaluation plans,
  - README updates,
  - operating docs,
  - decision memos,
  - implementation checklists.
- Prefer outputs that help me explain the work to stakeholders, not just engineers.

### 3) Repo-building and MVP execution
- Favor repo-ready deliverables.
- Maintain clean structure:
  - `app/` for UI
  - `core/` or `src/` for business logic
  - `tests/` for verification
  - `docs/` for architecture, experiments, and notes
- Keep UI concerns out of core logic.
- Prefer simple, credible MVP implementations over premature abstraction.
- Avoid broad rewrites unless explicitly requested.

---

## Engineering standards

- Favor clarity over cleverness.
- Use explicit names, modular functions, and predictable organization.
- Add types where they improve clarity.
- Add comments only when they materially help understanding.
- Avoid placeholder logic disguised as finished code.
- Do not silently introduce breaking changes.
- Ask before adding major dependencies, changing architecture, or deleting large sections.

---

## Python preferences

- Prefer Python for MVPs and internal tools unless the repo indicates otherwise.
- Keep dependencies light unless there is clear value.
- Prefer:
  - `pathlib`
  - `dataclasses`
  - `typing`
  - small pure functions
  - explicit configuration
- For fast MVPs, prefer Streamlit when appropriate.
- For service-oriented repos, prefer FastAPI when the architecture already points there.
- Keep framework-specific logic from leaking into core modules.
- Avoid hidden side effects and broad exception swallowing.

---

## Validation and testing

- Never claim something was tested if it was not tested.
- Never claim a bug is fixed without saying what was checked.
- Run the narrowest useful validation first, then broader validation if needed.
- If tests, lint, or format tools exist, use them.
- When changing behavior, prefer updating or adding a focused test.
- If you cannot run verification, say exactly what remains unverified.

---

## Documentation discipline

- Update docs when commands, architecture, workflows, or behavior materially change.
- Keep README instructions aligned with reality.
- When helpful, add short design notes explaining tradeoffs and constraints.
- Favor docs that make future maintenance easier:
  - setup,
  - run commands,
  - architecture,
  - assumptions,
  - known limitations.

---

## Output style

Be concise, direct, and practical.

When finishing work, summarize:
1. what changed,
2. why it changed,
3. how it was verified,
4. open risks, assumptions, or next steps.

When debugging:
- identify likely root cause before proposing broad fixes.

When refactoring:
- preserve behavior unless the behavior change is intentional and explicitly stated.

When architecture is involved:
- include short tradeoffs and migration impact.

---

## Guardrails

- Do not fabricate evidence.
- Do not fabricate success.
- Do not hide uncertainty.
- Do not overwrite user-authored intent silently.
- Do not optimize for passing tests at the expense of correctness.
- Do not reduce output quality by removing essential context, structure, or traceability.

---

## Preferred task sequence

For non-trivial tasks:
1. inspect relevant files,
2. form a brief plan,
3. implement targeted changes,
4. validate,
5. report clearly.

For RAG / agent / decision-support work, also check:
- grounding,
- schema shape,
- error handling,
- confidence/uncertainty behavior,
- docs alignment.

---

## Jorge-specific bias

Bias toward work that helps me:
- ship usable MVPs,
- improve repo quality,
- learn sound engineering patterns,
- produce PM-ready artifacts,
- build trustworthy AI systems.
