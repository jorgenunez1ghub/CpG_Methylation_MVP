# PR #21 Review: Test Dependency Install Gap (April 7, 2026)

## PR under review
PR #21 is currently open and stale (about one month old).

A reviewer comment on the PR states: **"INstall test dependencies before running pytest"**.

## Assessment
That comment is valid and should be preserved as an explicit workflow/repo instruction.

Why this matters:
- running `pytest` without test dependencies can fail in clean environments,
- stale PRs often fail CI due to environment drift,
- making test dependency installation explicit improves repeatability for both contributors and CI.

## Actions applied in this branch
1. Updated GitHub Actions test workflow to install the package with dev extras before running tests (`pip install -e ".[dev]"`).
2. Updated README test instructions so local test runs mirror CI expectations.

## Recommendation for PR #21 triage
If PR #21 does **not** contain unique functional changes beyond this dependency-install guidance, close it as **superseded** after merging these targeted updates.

If PR #21 contains additional unique code changes, salvage those hunks into a focused follow-up PR and then close #21.
