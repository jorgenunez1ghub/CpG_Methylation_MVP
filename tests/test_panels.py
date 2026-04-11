from pathlib import Path

import pandas as pd

from cpg_methylation_mvp.core.panels import evaluate_panel, load_panel, panel_report_table


def test_load_panel_reads_demo_panel() -> None:
    panel_df = load_panel(Path("data/panels/core_demo_panel.csv"))

    assert list(panel_df.columns) == [
        "panel_id",
        "cpg_id",
        "marker_label",
        "expected_direction",
        "notes",
    ]
    assert len(panel_df) == 5
    assert panel_df["panel_id"].nunique() == 1


def test_evaluate_panel_returns_expected_structure() -> None:
    normalized_df = pd.DataFrame(
        {
            "cpg_id": ["cg00000029", "cg00000108", "cg99999999"],
            "beta": [0.82, 0.14, 0.55],
        }
    )
    panel_df = load_panel(Path("data/panels/core_demo_panel.csv"))

    result = evaluate_panel(normalized_df=normalized_df, panel_df=panel_df)

    assert result["panel_id"] == "core_demo"
    assert result["panel_marker_count"] == 5
    assert result["markers_found"] == 2
    assert result["markers_missing"] == 3
    assert result["coverage_pct"] == 40.0
    assert result["coverage_status"] == "partial"
    assert result["observed_markers"] == [
        {"cpg_id": "cg00000029", "marker_label": "Marker 1", "beta": 0.82},
        {"cpg_id": "cg00000108", "marker_label": "Marker 2", "beta": 0.14},
    ]
    assert result["missing_markers"] == [
        {"cpg_id": "cg00000109", "marker_label": "Marker 3"},
        {"cpg_id": "cg00000165", "marker_label": "Marker 4"},
        {"cpg_id": "cg00000236", "marker_label": "Marker 5"},
    ]
    assert result["limitations"] == [
        "This report is based only on panel coverage and observed beta values.",
        "No clinical interpretation is made.",
        "Missing CpGs reduce interpretability.",
    ]


def test_panel_report_table_flattens_observed_and_missing_rows() -> None:
    result = {
        "panel_id": "core_demo",
        "observed_markers": [{"cpg_id": "cg1", "marker_label": "Marker 1", "beta": 0.2}],
        "missing_markers": [{"cpg_id": "cg2", "marker_label": "Marker 2"}],
    }

    report_df = panel_report_table(result)

    assert list(report_df.columns) == ["panel_id", "cpg_id", "marker_label", "beta", "is_observed"]
    assert len(report_df) == 2
    assert report_df.iloc[0].to_dict() == {
        "panel_id": "core_demo",
        "cpg_id": "cg1",
        "marker_label": "Marker 1",
        "beta": 0.2,
        "is_observed": True,
    }
    assert report_df.iloc[1]["cpg_id"] == "cg2"
    assert bool(report_df.iloc[1]["is_observed"]) is False
