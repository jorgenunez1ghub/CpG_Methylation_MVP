# CpG_Methylation_MVP

A lightweight **Streamlit** MVP for methylation ingestion:
**upload → parse → validate → normalize → QC summary**.

> **Disclaimer:** Educational demo only. Not medical advice. This tool does not diagnose, treat, or prevent disease. Consult a qualified clinician for medical interpretation.

## What this MVP does
- Upload a methylation input file (`.csv` or `.tsv`)
- Auto-detect delimiter and parse tabular data
- Validate required fields and data quality (missing columns, non-numeric beta, range checks)
- Normalize into canonical columns for downstream analysis:
  - `cpg_id`, `beta`
  - optional: `chrom`, `pos`, `gene`, `pval`
  - metadata: `source_file`, `uploaded_at`
- Store normalized data in `st.session_state["normalized_df"]`
- Display quick QC metrics and beta distribution

## Upload format supported
- **Required columns:**
  - `cpg_id` (or alias like `CpG`, `probe_id`)
  - `beta` (or alias like `Beta`, `methylation_level`)
- **Optional columns:** `chrom`, `pos`, `gene`, `pval`
- **Rules:**
  - `beta` must be numeric and in `[0, 1]`
  - file must include a header row and at least one data row

A sample input is available at: `data/sample/methylation_sample.csv`.

## Run locally
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the app:
```bash
streamlit run app.py
```

## Run tests
```bash
python -m unittest discover -s tests -v
```
