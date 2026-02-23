import pandas as pd

from core.transform import canonicalize_columns, select_canonical_columns


def test_canonicalize_columns_aliases() -> None:
    df = pd.DataFrame({"CpG": ["cg1"], "Beta": [0.42], "chr": ["chr1"], "extra": [1]})

    normalized = canonicalize_columns(df)
    selected = select_canonical_columns(normalized)

    assert list(selected.columns) == ["cpg_id", "beta", "chrom"]
    assert selected.iloc[0]["cpg_id"] == "cg1"
