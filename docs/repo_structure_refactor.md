# MVP Structure Refactor Notes

## Summary
- Kept Streamlit UI under `app/` with a single entrypoint at `app/main.py`.
- Moved parsing and schema transformation helpers to `core/io.py` and `core/transform.py`.
- Left validation and analysis in `core/validate.py` and `core/analyze.py`.
- Added smoke coverage for transform logic in `tests/test_transform.py`.

## Verification
- Run `pytest -q`.
- Run `streamlit run app/main.py` and upload `data/sample/methylation_sample.csv`.
