# CpG_Methylation_MVP

A lightweight **Streamlit** MVP that turns a methylation-related CSV into a readable screening summary:
**upload → preview → validate → flag high methylation rows → export results**.

> **Disclaimer:** Educational demo only. Not medical advice. This tool does not diagnose, treat, or prevent disease. Consult a qualified clinician for medical interpretation.

---

## What this MVP does
- Upload a CSV containing methylation-related values
- Preview and validate the dataset
- Map columns (handles real-world header differences)
- Flag rows above a configurable “high methylation” threshold
- Generate simple summary rollups (top genes by mean methylation)
- Export:
  - flagged rows as CSV
  - a basic report as Markdown

---

## Expected CSV format
Minimum expected fields (column names can be mapped in the UI):
- `Gene`
- `Methylation_Level` (numeric 0.0–1.0)

---

## Run locally
1) Install dependencies:
```bash
pip install -r requirements.txt