# Workflow 01 release/readiness checklist

## Contract alignment
- [ ] README explicitly describes only Workflow 01 support.
- [ ] `docs/workflows/mvp_workflow_01.md` matches app and core behavior.
- [ ] Unsupported behaviors are documented as fail-closed.

## Verification
- [ ] Happy-path fixture passes (`tests/fixtures/workflow_01/happy_path.csv`).
- [ ] Malformed input fixture fails with readable error.
- [ ] Unsupported input fixture fails with readable error.
- [ ] Interpretation edge fixture yields explicit uncertainty.
- [ ] Streamlit smoke tests pass with interpretation UI section and download artifact.

## Observability and triage
- [ ] Ingestion step success/failure log lines are present in app runtime logs.
- [ ] Parse/validation failures are distinguishable from interpretation coverage limitations.
- [ ] Known limitations remain visible in UI and exported interpretation JSON.

## Demo readiness
- [ ] Local run path is reproducible (`streamlit run app/main.py`).
- [ ] Output artifacts download successfully (normalized CSV, processing report, interpretation JSON).
- [ ] Team one-paragraph support statement is consistent with Workflow 01 scope.
