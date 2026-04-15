from __future__ import annotations

import json
from pathlib import Path

import pytest

from cpg_methylation_mvp.core import IngestError, load_panel, process_methylation_upload, structured_interpretation

_FIXTURE_DIR = Path("tests/fixtures/workflow_01")
_PANEL_PATH = Path("data/panels/core_demo_panel.csv")


def _process_fixture(filename: str):
    fixture_path = _FIXTURE_DIR / filename
    with fixture_path.open("rb") as handle:
        return process_methylation_upload(handle, source_name=fixture_path.name)


def test_workflow_01_happy_path_matches_expected_summary() -> None:
    processed = _process_fixture("happy_path.csv")
    panel_df = load_panel(_PANEL_PATH)
    interpretation = structured_interpretation(normalized_df=processed.normalized_df, panel_df=panel_df)

    expected = json.loads((_FIXTURE_DIR / "expected_happy_summary.json").read_text(encoding="utf-8"))

    assert interpretation["workflow_id"] == expected["workflow_id"]
    assert interpretation["panel_id"] == expected["panel_id"]
    assert interpretation["status"] == expected["status"]
    assert interpretation["observed_data"] == expected["observed_data"]
    assert interpretation["interpretation"]["markers_aligned"] == expected["interpretation"]["markers_aligned"]
    assert interpretation["interpretation"]["markers_uncertain"] == expected["interpretation"]["markers_uncertain"]


def test_workflow_01_malformed_input_fails_with_readable_error() -> None:
    fixture_path = _FIXTURE_DIR / "malformed_missing_beta.csv"
    with fixture_path.open("rb") as handle:
        with pytest.raises(IngestError) as exc:
            process_methylation_upload(handle, source_name=fixture_path.name)
    assert "Missing required column" in str(exc.value)


def test_workflow_01_unsupported_input_fails_with_readable_error() -> None:
    fixture_path = _FIXTURE_DIR / "unsupported_input.txt"
    with fixture_path.open("rb") as handle:
        with pytest.raises(IngestError) as exc:
            process_methylation_upload(handle, source_name=fixture_path.name)
    assert any(
        message in str(exc.value)
        for message in (
            "Missing required column",
            "uploaded file is empty",
        )
    )


def test_workflow_01_interpretation_edge_case_marks_uncertain_signal() -> None:
    processed = _process_fixture("interpretation_edge_intermediate.csv")
    panel_df = load_panel(_PANEL_PATH)
    interpretation = structured_interpretation(normalized_df=processed.normalized_df, panel_df=panel_df)

    assert interpretation["status"] == "complete"
    assert interpretation["interpretation"]["markers_uncertain"] == 1
    marker = interpretation["interpretation"]["marker_interpretations"][0]
    assert marker["observed_state"] == "intermediate"
    assert marker["agreement"] == "uncertain"
