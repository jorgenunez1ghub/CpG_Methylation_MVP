# Hygiene Triage Report — 2026-04-07

Scope completed for:
- install/run steps
- folder structure
- dependency clarity
- test command health
- docs freshness

## 1) Install / Run Steps

### Commands run
- `python --version`
- `pip --version`
- `pip install -e '.[dev]'`
- `timeout 20s streamlit run app/main.py --server.headless true --server.address 127.0.0.1 --server.port 8765`

### Findings
- Python and pip are available in the environment (`Python 3.12.12`, `pip 25.3`).
- Editable install currently fails in this environment because pip cannot reach package index/build dependencies (proxy `403 Forbidden`).
- Streamlit app startup succeeds in headless mode and serves locally (`http://127.0.0.1:8765`) before timeout stops it.

### Triage status
- **Warning (environmental):** install step could not be fully validated due to network/proxy restrictions.
- **Pass:** runtime app start command is healthy.

## 2) Folder Structure

### Commands run
- `rg --files`
- `find . -maxdepth 3 -type d | sort`

### Findings
- Expected high-level structure exists and is aligned with intended architecture:
  - `app/` for Streamlit UI
  - `src/cpg_methylation_mvp/core/` for core logic
  - `tests/` for verification
  - `docs/` for product/dev artifacts
  - `data/sample/` for sample input
- `app/pages/` directory exists (currently empty), which is acceptable for optional multipage extension.
- Additional `src/context/` modules exist and should remain documented as non-core helpers to avoid architecture ambiguity.

### Triage status
- **Pass:** structure is coherent for MVP and future extension.

## 3) Dependency Clarity

### Files inspected
- `pyproject.toml`
- `requirements.txt`
- `runtime.txt`
- `README.md`

### Findings
- Dependency declarations are mostly aligned:
  - runtime deps in `pyproject.toml`: `streamlit`, `pandas`, `tabulate`
  - `requirements.txt` includes those + `pytest`
  - dev extra in `pyproject.toml` includes `pytest`
- Runtime pin is coarse (`runtime.txt` uses `python-3.11`), while current environment run was on Python 3.12. This is not necessarily wrong, but cross-version test expectations should be explicit.

### Triage status
- **Pass with note:** dependencies are clear; version-compatibility expectations can be made explicit.

## 4) Test Command Health

### Commands run
- `PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python -c "import app.main; import cpg_methylation_mvp.core as core; print('imports_ok')"`

### Findings
- Test suite passes: `12 passed in 0.82s`.
- Importing `app.main` directly in bare Python raises `KeyError` for `st.session_state["normalized_df"]` because top-level script code executes outside Streamlit runtime context.
- Core package import remains fine.

### Triage status
- **Pass:** tests are healthy.
- **Risk noted:** `app.main` is not import-safe outside `streamlit run`; this can affect tooling or smoke-import checks.

## 5) Docs Freshness

### Files inspected
- `README.md`
- `PROJECT_STATE.md`
- `NEXT_STEPS.md`

### Findings
- README quickstart and architecture framing are generally aligned with repo reality.
- `PROJECT_STATE.md` had stale text saying `NEXT_STEPS.md` was not present; this has been corrected.

### Triage status
- **Pass with minor fix applied:** stale project-state statement updated.

## Hygiene actions applied in this triage

1. Expanded `.gitignore` to cover additional local/sensitive directories/files:
   - `uploads/`
   - `outputs/`
   - `.streamlit/secrets.toml`
2. Updated stale `PROJECT_STATE.md` line about `NEXT_STEPS.md` presence.

## Follow-up update — import safety closure

### Commands run
- `PYTHONPATH=src python3 -c "import app.main; import cpg_methylation_mvp.core as core; print('imports_ok')"`
- `PYTHONPATH=src pytest -q tests/test_imports.py`
- `PYTHONPATH=src pytest -q`
- Python-managed headless startup probe for `streamlit run app/main.py --server.headless true --server.address 127.0.0.1 --server.port 8765`

### Findings
- `app.main` no longer executes UI flow at import time; importing it in bare Python now succeeds and exposes an explicit `main()` entrypoint.
- A focused smoke test now guards that `import app.main` remains safe.
- Full test suite passes with the added import-safety check: `13 passed`.
- Headless Streamlit startup still succeeds after the entrypoint refactor.

### Follow-up status
- **Resolved:** `app.main` import-safety gap previously called out as a repo-hygiene P1 item.
- **Resolved:** README now states the supported Python floor (`>=3.10`) and notes that checks have been exercised on Python 3.11 and 3.12.
- **Still open (environmental):** editable-install verification remains partially blocked until package index/proxy access is restored.

## Recommended next actions (P1)

1. Once package registry access is restored, rerun full clean-environment verification:
   - `pip install -e '.[dev]'`
   - `pytest -q`
   - headless `streamlit run app/main.py` smoke check
2. Optionally add a tiny health script/Make target documenting two paths:
   - full install path (`pip install -e '.[dev]'`) for normal environments
   - local fallback test path (`PYTHONPATH=src pytest -q`) when packaging install is blocked.
