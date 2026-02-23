"""Fast smoke test for normalized analysis pipeline."""

from __future__ import annotations

import pandas as pd

from core import analyze_methylation


def test_analyze_methylation_summary_keys() -> None:
    df = pd.DataFrame(
        {
            "cpg_id": ["cg0001", "cg0002", "cg0003"],
            "beta": [0.10, 0.80, 0.50],
            "chrom": ["chr1", "chr2", "chr3"],
        }
    )

    summary = analyze_methylation(df)

    expected_keys = {
        "row_count",
        "unique_cpg",
        "missing_beta_pct",
        "out_of_range_beta_count",
        "beta_min",
        "beta_median",
        "beta_max",
    }
    assert expected_keys.issubset(summary.keys())
