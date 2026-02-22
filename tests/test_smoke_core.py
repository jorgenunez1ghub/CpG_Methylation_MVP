from io import BytesIO

import pandas as pd

from core.analyze import qc_summary
from core.ingest import load_methylation_file


def test_load_methylation_file_smoke() -> None:
    payload = b"cpg_id,beta,chrom\ncg1,0.10,chr1\ncg2,0.80,chr2\n"
    df = load_methylation_file(BytesIO(payload), source_name="tiny.csv")

    assert list(df.columns[:2]) == ["cpg_id", "beta"]
    assert len(df) == 2


def test_qc_summary_smoke() -> None:
    df = pd.DataFrame({"cpg_id": ["cg1", "cg2", "cg2"], "beta": [0.1, 0.5, 0.9]})
    summary = qc_summary(df)

    assert summary["row_count"] == 3.0
    assert summary["unique_cpg"] == 2.0
    assert summary["beta_min"] == 0.1
