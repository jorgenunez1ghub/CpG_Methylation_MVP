# CpG_Methylation_MVP

Lightweight Streamlit MVP for CpG methylation upload, validation, normalization, and QC.

> **Disclaimer:** Educational demo only. Not medical advice.

## What it does
- Uploads CpG methylation files (`.csv`, `.tsv`, `.txt`) through a Streamlit UI.
- Validates schema and value quality (required columns, numeric beta values, range checks).
- Normalizes parsed input into a canonical table (`cpg_id`, `beta`, optional metadata columns).
- Recovers conservatively from mislabeled `.csv`/`.tsv` delimiters when content parsing is clearly better than extension-based parsing.
- Flags parse warnings such as UTF-8 BOM removal or mixed-delimiter content in the processing report.
- Fails clearly when mixed delimiters create inconsistent row structure instead of partially ingesting malformed rows.
- Shows a versioned processing report with source provenance, run ID, input checksum, parser strategy, input/retained/dropped row counts, and dropped-row reasons.
- Lets the user choose duplicate CpG handling (`preserve rows and warn`, `reject duplicates`, or explicit mean aggregation when metadata matches) before ingestion.
- Provides a duplicate-review CSV when repeated `cpg_id` rows are retained, so follow-up review stays inspectable without silent aggregation.
- Provides an aggregation-audit CSV when duplicate rows are collapsed under the approved aggregation policy.
- Provides downloadable artifacts for normalized data and the processing report (JSON + CSV).
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
- `docs/duplicate_policy_decision.md`: current duplicate `cpg_id` policy and aggregation guardrails.
- `docs/duplicate_aggregation_adr.md`: approved and implemented opt-in aggregation contract for duplicate handling.
- `docs/duplicate_aggregation_adr_review_memo.md`: review memo backing the duplicate aggregation ADR recommendations.
- `docs/duplicate_aggregation_stakeholder_brief.md`: stakeholder-facing approval brief and recorded decision for the duplicate aggregation ADR.
- `docs/production_readiness_plan.md`: phased production-hardening plan.

## Deployment docs
- `deploy/render.yaml`: baseline manifest for Render deployment.
- `docs/deploy_runbook.md`: pre-deploy checks, runtime config, smoke checks, rollback.
- `tests/test_streamlit_smoke.py`: local automated Streamlit smoke coverage for the rendered app state.

## Architecture guardrails
- `app/` contains Streamlit UI only.
- `cpg_methylation_mvp.core` contains framework-agnostic business logic and **must not import Streamlit**.
- UI copy/config lives in `app/ui_config.py`, not in package core modules.

## Demo flow
1. Run `streamlit run app/main.py`.
2. Upload `data/sample/methylation_sample.csv`.
3. Choose the duplicate CpG policy appropriate for the workflow.
4. Confirm success message after parse/normalize.
5. Inspect the processing report for source filename, parser strategy, row accounting, parse warnings, and duplicate CpG warnings.
6. If duplicate `cpg_id` rows are present, inspect or download the duplicate-review CSV before any manual deduplication.
7. If duplicate aggregation was applied, inspect or download the aggregation-audit CSV to review collapsed groups.
8. Download the normalized CSV and processing report artifacts if needed.
9. Inspect normalized table and retained-row QC metric cards.
10. Verify beta chart renders expected distribution.

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
