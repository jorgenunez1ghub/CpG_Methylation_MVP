# Deploy Runbook (MVP)

This runbook provides a minimal, repeatable deployment path for the Streamlit MVP.

## 1) Pre-deploy checks
From repo root:

```bash
pip install -e ".[dev]"
pytest -q
```

Expected: tests pass and no local import/runtime regressions.

Recommended focused UI gate before pushing a deploy:

```bash
pytest -q tests/test_streamlit_smoke.py
```

This covers the rendered Streamlit app state locally. Hosted browser automation is still out of scope for this MVP and the deployed smoke path below remains a manual check.

## 2) Manifest-based deployment (Render)
A baseline Render manifest is provided at `deploy/render.yaml`.

Key settings:
- build command: `pip install -e .`
- start command: `streamlit run app/main.py --server.address 0.0.0.0 --server.port $PORT`
- python version pin through environment variable
- Streamlit upload ceiling is configured in `.streamlit/config.toml` (`25 MB`)

## 3) Runtime configuration
Set app-facing environment variables as needed:
- `APP_PAGE_TITLE`
- `APP_TITLE`
- `APP_LAYOUT`
- `APP_CAPTION`
- `APP_DESCRIPTION`

Optional placeholders (future integrations only):
- `OPENAI_API_KEY`
- `RAG_EMBEDDING_MODEL`

## 4) Post-deploy smoke checks
- App loads and renders title/caption.
- Sample file upload (`data/sample/methylation_sample.csv`) succeeds.
- Processing report shows a run ID, input checksum, parser strategy, and row accounting.
- Duplicate handling selector is visible before upload.
- Duplicate-preserve mode surfaces warnings for duplicate sample fixtures as expected.
- QC metrics display non-empty values.
- Histogram renders.
- Normalized CSV download succeeds.
- Processing report JSON and CSV downloads succeed.

## 5) Rollback
If deployment fails or behavior regresses:
1. Roll back to previous successful Render deploy.
2. Re-run local checks with the exact branch commit.
3. Open a follow-up issue with failing input and observed traceback.

## 6) Operational cautions
- This repo is an educational demo and not medical advice.
- Do not upload or store sensitive/private real health data.
- No durable storage or retention workflow is configured for uploaded data or generated artifacts.
- Keep secrets out of Git (`.env`, `.streamlit/secrets.toml`).
