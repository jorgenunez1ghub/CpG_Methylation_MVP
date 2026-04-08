# CpG_Methylation_MVP

Lightweight Streamlit MVP for CpG methylation upload, validation, normalization, and QC.

> **Disclaimer:** Educational demo only. Not medical advice.

## What it does
- Uploads CpG methylation files (`.csv`, `.tsv`, `.txt`) through a Streamlit UI.
- Validates schema and value quality (required columns, numeric beta values, range checks).
- Normalizes parsed input into a canonical table (`cpg_id`, `beta`, optional metadata columns).
- Shows a processing report with source provenance, input/retained/dropped row counts, and dropped-row reasons.
- Shows quick QC outputs for retained analytical rows (unique CpGs, beta statistics, simple chart).
- Uses Streamlit caching for file parsing and QC summary to reduce rerun work.
- Renders beta distribution as a compact histogram so large files remain responsive.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
streamlit run app/main.py
```

## Python version
- Requires Python `>=3.10` per `pyproject.toml`.
- Repo checks and app smoke runs have been exercised on Python 3.11 and 3.12.

## Config
Environment variables (see `.env.example`):
- `APP_PAGE_TITLE`: browser tab title.
- `APP_TITLE`: heading at top of app.
- `APP_LAYOUT`: Streamlit layout (`wide` or `centered`).
- `APP_CAPTION`: top disclaimer/caption text.
- `APP_DESCRIPTION`: intro markdown under title.
- `OPENAI_API_KEY`, `RAG_EMBEDDING_MODEL`: placeholders for future integrations.


## Python package layout
- Uses a `src/` layout with import path `cpg_methylation_mvp.*`.
- App imports public logic from `cpg_methylation_mvp.core`.
- Install editable from repo root with `pip install -e .`.

## Repo structure
- `app/`: Streamlit UI entrypoint and pages (UI orchestration only).
  - `app/main.py`: single entrypoint.
  - `app/pages/`: optional multipage views.
- `src/cpg_methylation_mvp/core/`: business logic modules.
  - `io.py`: file byte parsing and delimiter handling.
  - `transform.py`: canonical schema mapping and column selection.
  - `validate.py`: schema and value checks.
  - `analyze.py`: QC metric helpers.
- `tests/`: fast smoke tests for core functions.
- `docs/`: project notes and decision artifacts.
- `.env.example`: safe configuration template.


## Data contract docs
- `docs/SCHEMA.md`: canonical schema, required fields, aliases.
- `docs/DATA_DICTIONARY.md`: column-level definitions and examples.
- `docs/validation_rules.md`: validation checks and failure semantics.

## Deployment docs
- `deploy/render.yaml`: baseline manifest for Render deployment.
- `docs/deploy_runbook.md`: pre-deploy checks, runtime config, smoke checks, rollback.

## Architecture guardrails
- `app/` contains Streamlit UI only.
- `cpg_methylation_mvp.core` contains framework-agnostic business logic and **must not import Streamlit**.
- UI copy/config lives in `app/ui_config.py`, not in package core modules.

## Demo flow
1. Run `streamlit run app/main.py`.
2. Upload `data/sample/methylation_sample.csv`.
3. Confirm success message after parse/normalize.
4. Inspect the processing report for source filename, row accounting, and duplicate CpG warnings.
5. Inspect normalized table and retained-row QC metric cards.
6. Verify beta chart renders expected distribution.

## Run tests
```bash
pip install -e ".[dev]"
pytest -q
```

## Clean environment verification
Once package index access is available, rerun the full editable-install path:

```bash
pip install -e ".[dev]"
pytest -q
streamlit run app/main.py --server.headless true --server.address 127.0.0.1 --server.port 8765
```
