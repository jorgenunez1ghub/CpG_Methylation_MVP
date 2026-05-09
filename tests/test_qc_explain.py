from io import BytesIO

from cpg_methylation_mvp.core import analyze_methylation, explain_qc_summary, process_methylation_upload


def _explain_from_payload(payload: bytes, source_name: str = "test.csv", **kwargs: object) -> dict[str, list[str]]:
    processed = process_methylation_upload(BytesIO(payload), source_name=source_name, **kwargs)
    summary = analyze_methylation(processed.normalized_df)
    return explain_qc_summary(summary=summary, report=processed.report)


def test_qc_explain_clean_upload() -> None:
    explanation = _explain_from_payload(b"cpg_id,beta\ncg1,0.2\ncg2,0.8\n")
    assert any("Retained rows: 2" in item for item in explanation["observed_data"])
    assert any("do not establish a biological or clinical conclusion" in item for item in explanation["limitations"])


def test_qc_explain_missing_beta_and_dropped_rows() -> None:
    explanation = _explain_from_payload(b"cpg_id,beta\ncg1,0.2\ncg2,\n")
    assert any("Dropped rows" in item for item in explanation["observed_data"])
    assert any("preprocessing" in item.lower() for item in explanation["possible_meaning"])


def test_qc_explain_out_of_range_metrics() -> None:
    processed = process_methylation_upload(BytesIO(b"cpg_id,beta\ncg1,0.2\n"), source_name="test.csv")
    explanation = explain_qc_summary(
        summary={
            "row_count": 1.0,
            "unique_cpg": 1.0,
            "missing_beta_pct": 0.0,
            "out_of_range_beta_count": 1.0,
            "beta_min": 0.2,
            "beta_median": 0.2,
            "beta_max": 0.2,
        },
        report=processed.report,
    )
    assert any("Out-of-range beta values" in item for item in explanation["possible_meaning"])


def test_qc_explain_duplicate_preserve_policy() -> None:
    explanation = _explain_from_payload(b"cpg_id,beta\ncg1,0.2\ncg1,0.8\n")
    assert any("Duplicate CpG groups retained" in item for item in explanation["observed_data"])
    assert any("duplicate-handling policy" in item.lower() for item in explanation["next_steps"])


def test_qc_explain_duplicate_aggregation_policy() -> None:
    explanation = _explain_from_payload(
        b"cpg_id,beta,chrom\ncg1,0.2,chr1\ncg1,0.8,chr1\n",
        duplicate_policy="aggregate_mean_when_metadata_match",
    )
    assert any("aggregation was applied" in item.lower() for item in explanation["observed_data"])


def test_qc_explain_parse_warning() -> None:
    explanation = _explain_from_payload(
        b"cpg_id\tbeta\ncg1\t0.2\n",
        source_name="warning.csv",
    )
    assert any("Parse warnings recorded" in item for item in explanation["observed_data"])
