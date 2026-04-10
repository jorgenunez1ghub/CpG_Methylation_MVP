from io import BytesIO

from streamlit.testing.v1 import AppTest

from app.ui_config import APP_TITLE
from cpg_methylation_mvp.core import process_methylation_upload


def _download_labels(app_test: AppTest) -> list[str]:
    """Return download button labels from the rendered app tree."""
    return [element.proto.label for element in app_test.get("download_button")]


def test_streamlit_default_state_smoke() -> None:
    app_test = AppTest.from_file("app/main.py")

    app_test.run()

    assert app_test.title[0].value == APP_TITLE
    assert app_test.selectbox[0].label == "Duplicate CpG handling"
    assert app_test.selectbox[0].value == "Preserve rows and warn"
    assert "Aggregate duplicates (mean beta, matching metadata only)" in app_test.selectbox[0].options
    assert app_test.info[0].value == (
        "Upload a CSV/TSV file to view normalized data, processing report, and QC summary."
    )


def test_streamlit_processed_duplicate_state_smoke() -> None:
    duplicate_payload = (
        "cpg_id,beta,chrom\n"
        "cg000001,0.2,chr1\n"
        "cg000001,0.8,chr2\n"
    ).encode("utf-8")

    processed_upload = process_methylation_upload(BytesIO(duplicate_payload), source_name="duplicates.csv")
    app_test = AppTest.from_file("app/main.py")
    app_test.session_state["processed_upload"] = processed_upload

    app_test.run()

    assert [element.value for element in app_test.subheader] == [
        "Processing Report",
        "Duplicate Review",
        "Normalized Data (Canonical Schema)",
        "QC Summary (Retained Rows)",
    ]
    assert any("silent aggregation" in element.value.lower() for element in app_test.warning)
    assert any("unsafe without a defined scientific rule" in element.value.lower() for element in app_test.warning)
    assert _download_labels(app_test) == [
        "Download duplicate review CSV",
        "Download normalized CSV",
        "Download report JSON",
        "Download report CSV",
    ]


def test_streamlit_processed_aggregated_state_smoke() -> None:
    duplicate_payload = (
        "cpg_id,beta,chrom,gene\n"
        "cg000001,0.2,chr1,\n"
        "cg000001,0.8,,GENE1\n"
    ).encode("utf-8")

    processed_upload = process_methylation_upload(
        BytesIO(duplicate_payload),
        source_name="aggregate_duplicates.csv",
        duplicate_policy="aggregate_mean_when_metadata_match",
    )
    app_test = AppTest.from_file("app/main.py")
    app_test.session_state["processed_upload"] = processed_upload

    app_test.run()

    assert [element.value for element in app_test.subheader] == [
        "Processing Report",
        "Aggregation Audit",
        "Normalized Data (Canonical Schema)",
        "QC Summary (Retained Rows)",
    ]
    assert any("aggregated 1 duplicated cpg_id group" in element.value.lower() for element in app_test.info)
    assert _download_labels(app_test) == [
        "Download aggregation audit CSV",
        "Download normalized CSV",
        "Download report JSON",
        "Download report CSV",
    ]
