# CpG_Methylation_MVP

Lightweight Streamlit MVP for CpG methylation upload, validation, normalization, and QC.

> **Disclaimer:** Educational demo only. Not medical advice.

## What it does
- Uploads CpG methylation files (`.csv`, `.tsv`, `.txt`) through a Streamlit UI.
- Validates schema and value quality (required columns, numeric beta values, range checks).
- Normalizes parsed input into a canonical table (`cpg_id`, `beta`, optional metadata columns).
- Shows quick QC outputs (row counts, unique CpGs, beta statistics, simple chart).
- Uses Streamlit caching for file parsing and QC summary to reduce rerun work.
- Renders beta distribution as a compact histogram so large files remain responsive.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/main.py
```

## Config
Environment variables (see `.env.example`):
- `APP_PAGE_TITLE`: browser tab title.
- `APP_TITLE`: heading at top of app.
- `APP_LAYOUT`: Streamlit layout (`wide` or `centered`).
- `APP_CAPTION`: top disclaimer/caption text.
- `APP_DESCRIPTION`: intro markdown under title.
- `OPENAI_API_KEY`, `RAG_EMBEDDING_MODEL`: placeholders for future integrations.

## Repo structure
- `app/`: Streamlit UI entrypoint and pages (UI orchestration only).
  - `app/main.py`: single entrypoint.
  - `app/pages/`: optional multipage views.
- `core/`: business logic modules.
  - `core/io.py`: file byte parsing and delimiter handling.
  - `core/transform.py`: canonical schema mapping and column selection.
  - `core/validate.py`: schema and value checks.
  - `core/analyze.py`: QC metric helpers.
- `tests/`: fast smoke tests for core functions.
- `docs/`: project notes and decision artifacts.
- `.env.example`: safe configuration template.


## Architecture guardrails
- `app/` contains Streamlit UI only.
- `core/` contains framework-agnostic business logic and **must not import Streamlit**.
- UI copy/config lives in `app/ui_config.py`, not in `core/`.

## Demo flow
1. Run `streamlit run app/main.py`.
2. Upload `data/sample/methylation_sample.csv`.
3. Confirm success message after parse/normalize.
4. Inspect normalized table and QC metric cards.
5. Verify beta chart renders expected distribution.

## Run tests
```bash
pytest -q
```
