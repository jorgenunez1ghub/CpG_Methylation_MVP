import json

import pandas as pd

from app.main import _normalized_csv_bytes, _processing_report_csv_bytes, _processing_report_json
from cpg_methylation_mvp.core import ProcessingReport


def test_processing_report_download_serializers() -> None:
    report = ProcessingReport(
        source_file="sample.csv",
        uploaded_at="2026-04-08T12:00:00+00:00",
        parse_strategy="extension_delimiter",
        delimiter_used=",",
        recovered_from_extension_mismatch=False,
        input_row_count=3,
        retained_row_count=2,
        dropped_row_count=1,
        dropped_rows_by_reason={
            "missing_cpg_id": 0,
            "missing_beta": 1,
            "missing_cpg_id_and_beta": 0,
        },
        duplicate_cpg_id_groups=1,
        duplicate_cpg_id_extra_rows=1,
    )

    report_json = _processing_report_json(report)
    report_csv = _processing_report_csv_bytes(report).decode("utf-8")
    normalized_csv = _normalized_csv_bytes(pd.DataFrame({"cpg_id": ["cg1"], "beta": [0.2]})).decode("utf-8")

    assert json.loads(report_json)["source_file"] == "sample.csv"
    assert "dropped_rows_missing_beta" in report_csv
    assert "cpg_id,beta" in normalized_csv
