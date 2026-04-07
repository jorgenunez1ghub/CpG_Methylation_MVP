# CpG Methylation MVP Workflow Evaluation (2026-04-07)

## Scope

This evaluation maps the current user workflow end to end:

1. Upload
2. Validation
3. Normalization
4. QC
5. Outputs

It identifies trust/risk gaps and prioritizes fixes by impact:

- **P0**: blockers to running/verifying
- **P1**: workflow trust/usability issues
- **P2**: polish and maintainability upgrades

---

## A) End-to-end flow map + trust/risk gaps

## 1) Upload (Streamlit UI + file ingest entry)

### Current behavior
- User uploads one file in UI (`csv`, `tsv`, `txt`).
- App reads bytes and sends them to cached ingestion.
- Success and error states are shown in UI.

### Trust/risk gaps
1. **File type trust is extension-driven and weak.**
   - Delimiter detection uses filename suffix first; unknown extension falls back to generic sniffing.
   - A mislabeled file can produce parsing surprises.
2. **No explicit upload contract shown in UI near uploader.**
   - Users do not see canonical required columns and accepted aliases at the decision point.
3. **No preserved sample of dropped/invalid rows for audit.**
   - Downstream, rows may be removed (NA in key fields), but user cannot inspect what got removed.

---

## 2) Validation (schema + beta constraints)

### Current behavior
- Validation checks:
  - non-empty dataframe,
  - required canonical columns (`cpg_id`, `beta`),
  - numeric beta,
  - beta in range [0,1].
- Validation error messages are explicit and user-facing.

### Trust/risk gaps
1. **No duplicate CpG policy.**
   - Duplicate `cpg_id` rows are allowed silently.
   - If duplicates represent repeated measures, this may be acceptable, but policy is not explicit.
2. **No explicit validation summary object.**
   - Validation is pass/fail via exceptions.
   - There is no structured report users can inspect for warnings, row-level issue counts, or policy decisions.
3. **Whitespace/empty-string edge cases around `cpg_id`.**
   - `cpg_id` is stripped, but no direct warning count for empty IDs post-strip.

---

## 3) Normalization (alias mapping + canonical subset)

### Current behavior
- Known aliases are mapped to canonical columns.
- Canonical subset is retained in fixed order.

### Trust/risk gaps
1. **Alias collisions are resolved implicitly.**
   - Preferred column selection is deterministic, but app does not disclose when multiple aliases existed and one was chosen.
2. **Dropped non-canonical columns are not surfaced.**
   - Potentially useful provenance columns disappear without an explicit “dropped columns” report.
3. **No schema conformance report artifact.**
   - Users can’t download a machine-readable normalization report for auditability.

---

## 4) QC (summary metrics)

### Current behavior
- QC metrics include row count, unique CpGs, missing beta %, out-of-range count, min/median/max beta.
- Histogram rendered from cleaned beta values.

### Trust/risk gaps
1. **QC computed after hard row-drop in ingestion.**
   - Ingestion drops rows missing `beta` or `cpg_id` before analysis.
   - Reported missingness is therefore anchored to post-drop data, which can understate input quality issues.
2. **No before/after row accounting in UI.**
   - User cannot see: input rows, invalid rows, dropped rows, retained rows.
3. **No QC warning thresholds surfaced.**
   - Metrics are shown, but no explicit status flags (e.g., high missingness warning) for trust signaling.

---

## 5) Outputs (table + metrics + chart)

### Current behavior
- User sees normalized dataframe preview, metrics, and histogram.
- No explicit output export from app screen.

### Trust/risk gaps
1. **No downloadable QC/processing report.**
   - Limits reproducibility and stakeholder sharing.
2. **No run metadata bundle.**
   - `uploaded_at` exists in frame, but no generated run summary artifact (input name, parser mode, column mapping decisions).
3. **No limitation banner near results.**
   - Repo-level caveat exists, but a local result-level disclaimer would improve safe interpretation.

---

## B) Prioritized fixes by impact

## P0 — Blockers to running/verifying

> Current status: **No immediate runtime/test blockers identified in local verification (`pytest -q` passes).**

Even with tests passing, these are P0 for practical verification integrity:

1. **Add an explicit processing report object returned by ingestion.**
   - Include: input row count, rows dropped by reason, retained row count, chosen column mappings, dropped columns.
   - Why P0: without this, verification of pipeline behavior on real user files is incomplete.
2. **Expose before/after counts in UI and tests.**
   - Add “Input rows / Retained rows / Dropped rows” to QC panel.
   - Why P0: trust in QC requires transparent denominators.
3. **Add fixture tests for malformed-but-parseable files.**
   - Cases: duplicated alias columns, blank `cpg_id` after strip, mixed delimiters, mislabeled extension.
   - Why P0: these are high-probability real upload cases and currently under-tested.

---

## P1 — Workflow trust/usability issues

1. **Show upload contract inline near uploader.**
   - Required canonical columns, alias examples, allowed delimiters, expected ranges.
2. **Introduce warning tiers in QC.**
   - Example: missing beta >5% warning, >20% high-risk warning.
3. **Provide downloadable artifacts.**
   - Normalized CSV and JSON QC report.
4. **Display normalization decisions.**
   - “Mapped `probe_id` -> `cpg_id`; dropped columns: [...].”
5. **Add duplicate CpG handling policy.**
   - At minimum: explicit warning count; optionally user-selectable dedupe strategy.

---

## P2 — Polish/maintainability upgrades

1. **Formalize a typed processing report dataclass in core.**
   - Keep Streamlit-free and JSON-friendly.
2. **Document data contract and QC semantics in docs.**
   - Clarify that missingness currently reflects post-drop frame unless changed.
3. **Add golden-file tests for representative input/output pairs.**
   - Helps prevent regression in alias mapping and validation behavior.
4. **Improve app state traceability.**
   - Track run IDs in session state for easier debugging and user support.
5. **Add small architecture note on caching boundaries.**
   - Preserve app/core separation as features expand.

---

## Implementation sequence recommendation

1. **Sprint 1 (P0)**
   - Add processing report object and wire to UI.
   - Add tests for row accounting + malformed input fixtures.
2. **Sprint 2 (P1)**
   - Add warnings, upload contract guidance, downloads.
3. **Sprint 3 (P2)**
   - Docs hardening, typed artifacts, regression fixtures.

---

## Suggested acceptance criteria

- Given malformed input rows, app shows dropped-row counts by reason.
- QC panel shows both input and retained denominators.
- User can download:
  1) normalized data, and
  2) QC + normalization report JSON.
- Tests cover duplicate/blank-ID/mislabeled-extension/mixed-delimiter cases.
- Core remains Streamlit-independent.
