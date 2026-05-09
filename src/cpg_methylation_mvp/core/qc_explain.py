"""Deterministic explanation helpers for QC summary outputs."""

from __future__ import annotations

from .ingest import ProcessingReport


def explain_qc_summary(summary: dict[str, float], report: ProcessingReport) -> dict[str, list[str]]:
    """Return cautious, deterministic explanation text for QC outputs."""
    observed_data: list[str] = [
        f"Retained rows: {report.retained_row_count:,}.",
        f"Unique CpG IDs: {int(summary.get('unique_cpg', 0)):,}.",
        f"Missing beta values among retained rows: {summary.get('missing_beta_pct', 0.0):.2f}%.",
        f"Out-of-range beta values among retained rows: {int(summary.get('out_of_range_beta_count', 0)):,}.",
    ]

    if report.duplicate_cpg_id_groups > 0:
        observed_data.append(
            f"Duplicate CpG groups retained: {report.duplicate_cpg_id_groups:,} (extra rows: {report.duplicate_cpg_id_extra_rows:,})."
        )
    if report.aggregation_applied:
        observed_data.append(
            "Duplicate aggregation was applied under the selected policy "
            f"({report.aggregated_duplicate_cpg_id_groups:,} group(s) from {report.aggregated_duplicate_input_rows:,} row(s))."
        )
    else:
        observed_data.append("Duplicate aggregation was not applied in this run.")

    if report.dropped_row_count > 0:
        observed_data.append(f"Dropped rows during required-field checks: {report.dropped_row_count:,}.")
    if report.parse_warnings:
        observed_data.append(f"Parse warnings recorded: {', '.join(report.parse_warnings)}.")

    possible_meaning = [
        "This summary reflects technical data quality and preprocessing behavior for this upload.",
    ]
    if summary.get("missing_beta_pct", 0.0) > 0:
        possible_meaning.append(
            "Missing beta values can indicate incomplete source data or preprocessing gaps that should be reviewed before interpretation."
        )
    if summary.get("out_of_range_beta_count", 0.0) > 0:
        possible_meaning.append(
            "Out-of-range beta values suggest scale or parsing issues that should be corrected at the source before downstream analysis."
        )
    if report.duplicate_cpg_id_groups > 0:
        possible_meaning.append(
            "Duplicate CpG rows can reflect repeated measurements or merged inputs and should be handled with an explicit duplicate policy."
        )
    if report.parse_warnings:
        possible_meaning.append(
            "Parse warnings indicate file-format conditions that may affect trust in row-level results."
        )

    limitations = [
        "These QC signals do not establish a biological or clinical conclusion.",
        "This is an educational workflow and not medical advice.",
    ]

    next_steps = [
        "Review the source file and preprocessing method before using this output for downstream analysis.",
        "Resolve missing or out-of-range beta values in the source pipeline when present.",
    ]
    if report.duplicate_cpg_id_groups > 0 and not report.aggregation_applied:
        next_steps.append("Choose and document a duplicate-handling policy before interpreting duplicated markers.")
    if report.parse_warnings:
        next_steps.append("Address parse warnings by re-exporting the file with a single consistent delimiter and UTF-8 encoding.")

    return {
        "observed_data": observed_data,
        "possible_meaning": possible_meaning,
        "limitations": limitations,
        "next_steps": next_steps,
    }
