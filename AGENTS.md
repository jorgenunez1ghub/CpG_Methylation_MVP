# AGENTS.md
## Architecture rules
- app/ is Streamlit UI only (widgets, session_state, rendering).
- core/ contains all business logic (io/validate/transform/analyze/ingest/config).
- core/ MUST NOT import streamlit.
- app/ MUST NOT implement data processing beyond calling core functions.

## Commands
- Install (editable): pip install -e .
- Run app: streamlit run app/main.py
- Tests: pytest -q

## Expectations for changes
- Keep PRs small and focused.
- No network calls in tests.
- No secrets committed; use .env + .env.example.
