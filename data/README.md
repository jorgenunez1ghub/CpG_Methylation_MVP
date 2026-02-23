# Data directory policy

This folder is for **non-sensitive sample data only**.

## Allowed in git
- `data/sample/` files that are synthetic, de-identified, or public demo examples.
- Small reference fixtures used for local demos/tests.

## Not allowed in git
- `data/raw/` source uploads or any real user/patient data.
- `data/output/` generated analysis outputs, reports, or exports.
- Any file containing secrets, tokens, or credentials.

If you need to inspect raw or generated files locally, keep them under ignored paths (`data/raw/`, `data/output/`).
