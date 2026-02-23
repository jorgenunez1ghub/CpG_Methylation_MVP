from io import BytesIO

import pandas as pd

from cpg_methylation_mvp.core import (
    analyze_methylation,
    load_methylation_file,
    normalize_upload,
    validate_upload,
)


def test_load_methylation_file_smoke() -> None:
    payload = b"cpg_id,beta,chrom\ncg1,0.10,chr1\ncg2,0.80,chr2\n"
    df = load_methylation_file(BytesIO(payload), source_name="tiny.csv")

    assert list(df.columns[:2]) == ["cpg_id", "beta"]
    assert len(df) == 2


def test_validate_transform_analyze_smoke() -> None:
    raw = pd.DataFrame({"CpG": ["cg1", "cg2"], "Beta": [0.1, 0.9], "chr": ["chr1", "chr2"]})

    normalized = normalize_upload(raw)
    validated = validate_upload(normalized)
    summary = analyze_methylation(validated)

    assert list(normalized.columns) == ["cpg_id", "beta", "chrom"]
    assert summary["row_count"] == 2.0
    assert summary["unique_cpg"] == 2.0
