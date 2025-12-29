# Model Use

## Current MVP (No LLM)
This MVP is **rule-based** and uses:
- Streamlit (UI)
- Pandas (CSV parsing, cleaning, aggregation)

It does **not** call an LLM or external model API. Outputs are derived from:
- user-provided CSV data
- threshold and summary statistics

## Safety & Intended Use
- Educational demo only; not medical advice.
- The app does not diagnose, treat, or recommend medical interventions.
- Users are encouraged to consult qualified clinicians for interpretation.

## If an LLM is added later (planned safeguards)
If future versions introduce an LLM for narrative summaries or question generation:
- Constrained templates (structured output)
- “Unknown/insufficient data” handling
- No clinical claims or prescriptive supplement guidance
- Clear citations/traceability where possible
- Evaluation set + regression checks for reliability
- Privacy-first handling (avoid storing user uploads; minimize logging)