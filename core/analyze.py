"""Analysis helpers for normalized methylation data."""

from __future__ import annotations

import pandas as pd


def qc_summary(df: pd.DataFrame) -> dict[str, float]:
    """Return simple QC metrics for normalized methylation dataframe."""
    beta = df["beta"]
    return {
        "row_count": float(len(df)),
        "unique_cpg": float(df["cpg_id"].nunique()),
        "missing_beta_pct": float(beta.isna().mean() * 100),
        "out_of_range_beta_count": float(((beta < 0) | (beta > 1)).sum()),
        "beta_min": float(beta.min()),
        "beta_median": float(beta.median()),
        "beta_max": float(beta.max()),
    }
