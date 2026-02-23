"""Fast, in-memory pipeline smoke test without secrets or network calls."""

from __future__ import annotations

import pandas as pd

from core import analyze_methylation, normalize_upload, validate_upload


def test_validate_transform_analyze_pipeline_smoke() -> None:
    raw_df = pd.DataFrame(
        {
            "CpG": ["cg0001", "cg0002", "cg0003"],
            "Beta": [0.10, 0.35, 0.90],
            "chr": ["chr1", "chr2", "chr3"],
        }
    )

    normalized_df = normalize_upload(raw_df)
    validated_df = validate_upload(normalized_df)
    summary = analyze_methylation(validated_df)

    assert list(validated_df.columns) == ["cpg_id", "beta", "chrom"]
    assert summary["row_count"] == 3.0
    assert summary["unique_cpg"] == 3.0
    assert summary["out_of_range_beta_count"] == 0.0
