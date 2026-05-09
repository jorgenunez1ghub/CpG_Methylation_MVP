# Demo Readiness Checklist (Release 0.1)

- [ ] Local install succeeds: `pip install -e ".[dev]"`
- [ ] Verification gate passes: `make verify`
- [ ] App launches: `streamlit run app/main.py`
- [ ] Sample upload succeeds (`data/sample/*`)
- [ ] Processing report reviewed (run ID, checksum, parse strategy, duplicate policy)
- [ ] QC explanation reviewed (observed data, meaning, limitations, next steps)
- [ ] Structured interpretation reviewed (coverage, summary, limitations)
- [ ] Downloads verified (normalized CSV, processing report JSON/CSV, interpretation JSON, duplicate/audit artifacts if present)
- [ ] No secrets / no private health data committed
- [ ] Hosted/manual smoke check completed (see `docs/demo/hosted_smoke_check.md` when available)
