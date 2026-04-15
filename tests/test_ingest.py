import unittest
from io import BytesIO

from cpg_methylation_mvp.core.ingest import (
    DEFAULT_MAX_UPLOAD_BYTES,
    PROCESSING_REPORT_VERSION,
    IngestError,
    duplicate_review_table,
    load_methylation_file,
    process_methylation_upload,
)


class TestIngest(unittest.TestCase):
    def test_delimiter_handling_tsv(self) -> None:
        tsv_payload = (
            "cpg_id\tbeta\tchrom\n"
            "cg000001\t0.25\tchr1\n"
            "cg000002\t0.90\tchr2\n"
        ).encode("utf-8")

        df = load_methylation_file(BytesIO(tsv_payload), source_name="sample.tsv")

        self.assertEqual(len(df), 2)
        self.assertIn("cpg_id", df.columns)
        self.assertIn("beta", df.columns)

    def test_delimiter_sniffing_for_txt(self) -> None:
        txt_payload = (
            "cpg_id\tbeta\n"
            "cg000001\t0.25\n"
            "cg000002\t0.90\n"
        ).encode("utf-8")

        df = load_methylation_file(BytesIO(txt_payload), source_name="sample.txt")

        self.assertEqual(len(df), 2)
        self.assertIn("cpg_id", df.columns)
        self.assertIn("beta", df.columns)

    def test_missing_required_column(self) -> None:
        csv_payload = "cpg_id,chrom\ncg000001,chr1\n".encode("utf-8")

        with self.assertRaises(IngestError) as context:
            load_methylation_file(BytesIO(csv_payload), source_name="missing_beta.csv")

        self.assertIn("Missing required column", str(context.exception))

    def test_non_numeric_beta(self) -> None:
        csv_payload = "cpg_id,beta\ncg000001,abc\n".encode("utf-8")

        with self.assertRaises(IngestError) as context:
            load_methylation_file(BytesIO(csv_payload), source_name="bad_beta.csv")

        self.assertIn("non-numeric beta", str(context.exception))

    def test_out_of_range_beta(self) -> None:
        csv_payload = "cpg_id,beta\ncg000001,1.2\n".encode("utf-8")

        with self.assertRaises(IngestError) as context:
            load_methylation_file(BytesIO(csv_payload), source_name="out_of_range.csv")

        self.assertIn("outside [0, 1]", str(context.exception))

    def test_empty_file_raises_error(self) -> None:
        with self.assertRaises(IngestError) as context:
            load_methylation_file(BytesIO(b""), source_name="empty.csv")

        self.assertIn("uploaded file is empty", str(context.exception).lower())

    def test_duplicate_cpg_ids_are_preserved_and_reported(self) -> None:
        csv_payload = (
            "cpg_id,beta,chrom\n"
            "cg000001,0.2,chr1\n"
            "cg000001,0.8,chr1\n"
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(csv_payload), source_name="duplicates.csv")
        df = processed.normalized_df

        self.assertEqual(len(df), 2)
        self.assertEqual(df["cpg_id"].nunique(), 1)
        self.assertEqual(processed.report.duplicate_cpg_id_groups, 1)
        self.assertEqual(processed.report.duplicate_cpg_id_extra_rows, 1)
        self.assertEqual(processed.report.duplicate_metadata_conflict_groups, 0)
        self.assertEqual(processed.report.duplicate_policy, "preserve_rows_and_warn")

    def test_duplicate_metadata_conflicts_are_reported(self) -> None:
        csv_payload = (
            "cpg_id,beta,chrom\n"
            "cg000001,0.2,chr1\n"
            "cg000001,0.8,chr2\n"
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(csv_payload), source_name="duplicates_conflict.csv")

        self.assertEqual(processed.report.duplicate_cpg_id_groups, 1)
        self.assertEqual(processed.report.duplicate_metadata_conflict_groups, 1)

    def test_duplicate_review_table_surfaces_conflict_columns(self) -> None:
        csv_payload = (
            "cpg_id,beta,chrom,gene\n"
            "cg000001,0.2,chr1,GENE1\n"
            "cg000001,0.8,chr2,GENE1\n"
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(csv_payload), source_name="duplicates_conflict.csv")
        review_df = duplicate_review_table(processed.normalized_df)

        self.assertEqual(len(review_df), 2)
        self.assertTrue(review_df["duplicate_group_has_metadata_conflict"].all())
        self.assertEqual(set(review_df["duplicate_group_conflict_columns"]), {"chrom"})
        self.assertEqual(set(review_df["duplicate_group_row_count"]), {2})
        self.assertEqual(set(review_df["duplicate_group_extra_rows"]), {1})
        self.assertEqual(set(review_df["duplicate_group_beta_min"]), {0.2})
        self.assertEqual(set(review_df["duplicate_group_beta_max"]), {0.8})

    def test_duplicate_cpg_ids_can_be_rejected_explicitly(self) -> None:
        csv_payload = (
            "cpg_id,beta\n"
            "cg000001,0.2\n"
            "cg000001,0.8\n"
        ).encode("utf-8")

        with self.assertRaises(IngestError) as context:
            process_methylation_upload(
                BytesIO(csv_payload),
                source_name="duplicates.csv",
                duplicate_policy="reject_duplicates",
            )

        self.assertIn("requires unique cpg_id values", str(context.exception))

    def test_duplicate_cpg_ids_can_be_aggregated_when_metadata_match(self) -> None:
        csv_payload = (
            "cpg_id,beta,chrom,gene\n"
            "cg000001,0.2,chr1,\n"
            "cg000001,0.8,,GENE1\n"
        ).encode("utf-8")

        processed = process_methylation_upload(
            BytesIO(csv_payload),
            source_name="aggregate_duplicates.csv",
            duplicate_policy="aggregate_mean_when_metadata_match",
        )

        self.assertEqual(len(processed.normalized_df), 1)
        aggregated_row = processed.normalized_df.iloc[0]
        self.assertEqual(aggregated_row["cpg_id"], "cg000001")
        self.assertAlmostEqual(float(aggregated_row["beta"]), 0.5)
        self.assertEqual(aggregated_row["chrom"], "chr1")
        self.assertEqual(aggregated_row["gene"], "GENE1")
        self.assertEqual(processed.report.duplicate_policy, "aggregate_mean_when_metadata_match")
        self.assertTrue(processed.report.aggregation_applied)
        self.assertEqual(processed.report.pre_duplicate_policy_row_count, 2)
        self.assertEqual(processed.report.aggregated_duplicate_cpg_id_groups, 1)
        self.assertEqual(processed.report.aggregated_duplicate_input_rows, 2)
        self.assertEqual(processed.report.aggregation_output_row_count, 1)
        self.assertEqual(processed.report.aggregation_blocked_conflict_groups, 0)
        self.assertIsNotNone(processed.aggregation_audit_df)
        assert processed.aggregation_audit_df is not None
        self.assertEqual(len(processed.aggregation_audit_df), 1)
        audit_row = processed.aggregation_audit_df.iloc[0]
        self.assertEqual(audit_row["aggregation_rule"], "aggregate_mean_when_metadata_match")
        self.assertEqual(int(audit_row["source_row_count"]), 2)
        self.assertAlmostEqual(float(audit_row["beta_mean"]), 0.5)
        self.assertEqual(audit_row["source_file"], "aggregate_duplicates.csv")

    def test_aggregate_policy_fails_on_metadata_conflicts(self) -> None:
        csv_payload = (
            "cpg_id,beta,chrom\n"
            "cg000001,0.2,chr1\n"
            "cg000001,0.8,chr2\n"
        ).encode("utf-8")

        with self.assertRaises(IngestError) as context:
            process_methylation_upload(
                BytesIO(csv_payload),
                source_name="aggregate_conflict.csv",
                duplicate_policy="aggregate_mean_when_metadata_match",
            )

        self.assertIn("cannot aggregate 1 duplicated cpg_id group", str(context.exception).lower())
        self.assertIn("preserve_rows_and_warn", str(context.exception))

    def test_aggregate_policy_is_noop_when_no_duplicate_groups_exist(self) -> None:
        csv_payload = (
            "cpg_id,beta,chrom\n"
            "cg000001,0.2,chr1\n"
            "cg000002,0.8,chr2\n"
        ).encode("utf-8")

        processed = process_methylation_upload(
            BytesIO(csv_payload),
            source_name="unique_rows.csv",
            duplicate_policy="aggregate_mean_when_metadata_match",
        )

        self.assertEqual(len(processed.normalized_df), 2)
        self.assertFalse(processed.report.aggregation_applied)
        self.assertEqual(processed.report.aggregated_duplicate_cpg_id_groups, 0)
        self.assertEqual(processed.report.aggregated_duplicate_input_rows, 0)
        self.assertEqual(processed.report.aggregation_output_row_count, 2)
        self.assertIsNone(processed.aggregation_audit_df)

    def test_whitespace_only_cpg_ids_are_dropped_and_reported(self) -> None:
        csv_payload = (
            "cpg_id,beta\n"
            "   ,0.4\n"
            "cg000001,0.2\n"
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(csv_payload), source_name="blank_cpg.csv")

        self.assertEqual(len(processed.normalized_df), 1)
        self.assertEqual(processed.normalized_df.iloc[0]["cpg_id"], "cg000001")
        self.assertEqual(processed.report.dropped_row_count, 1)
        self.assertEqual(processed.report.dropped_rows_by_reason["missing_cpg_id"], 1)

    def test_all_invalid_rows_raise_clear_error(self) -> None:
        csv_payload = "cpg_id,beta\n   ,   \n".encode("utf-8")

        with self.assertRaises(IngestError) as context:
            process_methylation_upload(BytesIO(csv_payload), source_name="all_invalid.csv")

        self.assertIn("No valid rows remain", str(context.exception))
        self.assertNotIn("empty", str(context.exception).lower())

    def test_unrecognized_columns_do_not_report_empty_file(self) -> None:
        csv_payload = "foo,bar\n1,2\n".encode("utf-8")

        with self.assertRaises(IngestError) as context:
            load_methylation_file(BytesIO(csv_payload), source_name="wrong_cols.csv")

        self.assertIn("Missing required column", str(context.exception))
        self.assertNotIn("empty", str(context.exception).lower())

    def test_mislabeled_extension_is_recovered_from_content(self) -> None:
        tab_payload = "cpg_id\tbeta\ncg000001\t0.2\n".encode("utf-8")

        processed = process_methylation_upload(BytesIO(tab_payload), source_name="mislabeled.csv")

        self.assertEqual(len(processed.normalized_df), 1)
        self.assertEqual(processed.normalized_df.iloc[0]["cpg_id"], "cg000001")
        self.assertEqual(processed.report.parse_strategy, "recovered_from_mislabeled_extension")
        self.assertTrue(processed.report.recovered_from_extension_mismatch)
        self.assertIn("recovered_from_mislabeled_extension", processed.report.parse_warnings)

    def test_utf8_bom_is_removed_and_reported(self) -> None:
        bom_payload = b"\xef\xbb\xbfcpg_id,beta\ncg000001,0.2\n"

        processed = process_methylation_upload(BytesIO(bom_payload), source_name="bom.csv")

        self.assertEqual(processed.normalized_df.iloc[0]["cpg_id"], "cg000001")
        self.assertIn("removed_utf8_bom", processed.report.parse_warnings)

    def test_mixed_delimiters_with_inconsistent_row_width_raise_clear_error(self) -> None:
        mixed_payload = (
            "cpg_id,beta\n"
            "cg000001,0.2\n"
            "cg000002\t0.3\n"
        ).encode("utf-8")

        with self.assertRaises(IngestError) as context:
            process_methylation_upload(BytesIO(mixed_payload), source_name="mixed.csv")

        self.assertIn("single delimiter", str(context.exception).lower())

    def test_mixed_delimiter_warning_remains_nonfatal_for_quoted_text(self) -> None:
        mixed_payload = (
            'cpg_id,beta,note\n'
            'cg000001,0.2,"contains\ttab"\n'
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(mixed_payload), source_name="quoted_tabs.csv")

        self.assertEqual(processed.report.retained_row_count, 1)
        self.assertIn("mixed_delimiters_detected", processed.report.parse_warnings)
        self.assertNotIn("mixed_delimiters_inconsistent_structure", processed.report.parse_warnings)

    def test_malformed_quotes_raise_clear_error(self) -> None:
        bad_payload = b'cpg_id,beta\n"cg000001,0.2\n'

        with self.assertRaises(IngestError) as context:
            process_methylation_upload(BytesIO(bad_payload), source_name="bad_quotes.csv")

        self.assertIn("malformed quotes", str(context.exception).lower())

    def test_upload_limit_is_enforced(self) -> None:
        oversized_payload = b"a" * (DEFAULT_MAX_UPLOAD_BYTES + 1)

        with self.assertRaises(IngestError) as context:
            process_methylation_upload(BytesIO(oversized_payload), source_name="oversized.csv")

        self.assertIn("25 MB limit", str(context.exception))

    def test_processing_report_exposes_row_accounting_and_provenance(self) -> None:
        csv_payload = (
            "cpg_id,beta\n"
            "cg000001,0.2\n"
            "cg000001,0.7\n"
            "cg000002,\n"
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(csv_payload), source_name="sample_upload.csv")

        self.assertEqual(processed.report.report_version, PROCESSING_REPORT_VERSION)
        self.assertTrue(processed.report.run_id)
        self.assertEqual(processed.report.source_file, "sample_upload.csv")
        self.assertEqual(len(processed.report.input_sha256), 64)
        self.assertEqual(processed.report.parse_strategy, "extension_delimiter")
        self.assertEqual(processed.report.input_row_count, 3)
        self.assertEqual(processed.report.retained_row_count, 2)
        self.assertEqual(processed.report.dropped_row_count, 1)
        self.assertEqual(processed.report.dropped_rows_by_reason["missing_beta"], 1)
        self.assertEqual(processed.report.duplicate_cpg_id_groups, 1)
        self.assertEqual(processed.report.duplicate_cpg_id_extra_rows, 1)
        self.assertFalse(processed.report.aggregation_applied)
        self.assertEqual(processed.report.pre_duplicate_policy_row_count, 2)
        self.assertEqual(processed.report.aggregated_duplicate_cpg_id_groups, 0)
        self.assertEqual(processed.report.aggregated_duplicate_input_rows, 0)
        self.assertEqual(processed.report.aggregation_output_row_count, 2)
        self.assertEqual(processed.report.parse_warnings, ())
        self.assertTrue((processed.normalized_df["source_file"] == "sample_upload.csv").all())
        self.assertTrue(processed.normalized_df["uploaded_at"].notna().all())


if __name__ == "__main__":
    unittest.main()
