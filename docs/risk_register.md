# Risk Register — CpG_Methylation_MVP (MVP)

| Risk | Likelihood | Impact | Mitigation / Controls | Status |
|---|---:|---:|---|---|
| **Privacy risk from uploading sensitive health data** | Medium | High | No user accounts; operate in-session; avoid logging raw data; document “do not upload PII”; if deployed, configure platform not to persist uploads; add clear privacy note in README/app | Open |
| **User interprets output as medical advice** | Medium | High | Prominent disclaimer: educational only; avoid prescriptive supplement/medical language; emphasize “consult clinician”; constrain output to “screening summary + questions” | Open |
| **Hallucinations / incorrect AI statements (if AI features added later)** | Medium | High | Keep MVP rule-based; if LLM added: use constrained templates, require citations, implement “I don’t know,” add eval set, human-in-the-loop review for release notes | Planned |
| **Wrong column names / inconsistent vendor formats** | High | Medium | Column mapping UI; schema guidance; sample CSV; robust errors and warnings; conservative delimiter recovery for mislabeled `.csv`/`.tsv` files | Mitigated |
| **Non-numeric / corrupted methylation values** | High | Medium | Coerce numeric values, drop invalid rows, show count of removed rows, stop if no valid rows remain | Mitigated |
| **Ambiguous delimiter / malformed file structure** | Medium | Medium | Parse warnings for BOM/mixed delimiters, explicit malformed-quote error, downloadable processing report for audit | Mitigated |
| **Threshold misuse produces misleading flags** | Medium | Medium | Threshold slider with default; explain threshold meaning; show summary stats; encourage consistent thresholds for comparisons | Mitigated |
| **Performance issues on large CSVs** | Low–Med | Medium | Upload limit (`25 MB`), limit displayed rows, use efficient Pandas ops; future: chunked read | Mitigated |
| **Reproducibility and environment drift** | Medium | Medium | `requirements.txt` + `runtime.txt`; documented run steps; pin versions if needed | Mitigated |
| **Security misconfig (public deployment exposure)** | Low–Med | High | Use platform defaults; avoid secrets in repo; document safe deployment steps; consider access controls if needed | Planned |
