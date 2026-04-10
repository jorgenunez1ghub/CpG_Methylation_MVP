import json

import pandas as pd

from app.main import (
    _aggregation_audit_csv_bytes,
    _duplicate_review_csv_bytes,
    _normalized_csv_bytes,
    _processing_report_csv_bytes,
    _processing_report_json,
)
from cpg_methylation_mvp.core import ProcessingReport


def test_processing_report_download_serializers() -> None:
    report = ProcessingReport(
        report_version="2.0",
        run_id="run-123",
        source_file="sample.csv",
        uploaded_at="2026-04-08T12:00:00+00:00",
        input_sha256="a" * 64,
        parse_strategy="extension_delimiter",
        delimiter_used=",",
        recovered_from_extension_mismatch=False,
        parse_warnings=("removed_utf8_bom",),
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
        duplicate_metadata_conflict_groups=0,
        aggregation_applied=True,
        pre_duplicate_policy_row_count=2,
        aggregated_duplicate_cpg_id_groups=1,
        aggregated_duplicate_input_rows=2,
        aggregation_output_row_count=1,
    )

    report_json = _processing_report_json(report)
    report_csv = _processing_report_csv_bytes(report).decode("utf-8")
    normalized_csv = _normalized_csv_bytes(pd.DataFrame({"cpg_id": ["cg1"], "beta": [0.2]})).decode("utf-8")
    duplicate_review_csv = _duplicate_review_csv_bytes(
        pd.DataFrame(
            {
                "cpg_id": ["cg1", "cg1"],
                "beta": [0.2, 0.8],
                "duplicate_group_row_count": [2, 2],
            }
        )
    ).decode("utf-8")
    aggregation_audit_csv = _aggregation_audit_csv_bytes(
        pd.DataFrame(
            {
                "cpg_id": ["cg1"],
                "source_row_count": [2],
                "beta_mean": [0.5],
                "aggregation_rule": ["aggregate_mean_when_metadata_match"],
            }
        )
    ).decode("utf-8")

    parsed_json = json.loads(report_json)
    assert parsed_json["source_file"] == "sample.csv"
    assert parsed_json["run_id"] == "run-123"
    assert "dropped_rows_missing_beta" in report_csv
    assert "aggregation_applied" in report_csv
    assert "parse_warnings" in report_csv
    assert "cpg_id,beta" in normalized_csv
    assert "duplicate_group_row_count" in duplicate_review_csv
    assert "aggregation_rule" in aggregation_audit_csv
