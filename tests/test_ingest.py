from io import BytesIO
import unittest

from cpg_methylation_mvp.core.ingest import IngestError, load_methylation_file, process_methylation_upload


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
            "cpg_id,beta\n"
            "cg000001,0.2\n"
            "cg000001,0.8\n"
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(csv_payload), source_name="duplicates.csv")
        df = processed.normalized_df

        self.assertEqual(len(df), 2)
        self.assertEqual(df["cpg_id"].nunique(), 1)
        self.assertEqual(processed.report.duplicate_cpg_id_groups, 1)
        self.assertEqual(processed.report.duplicate_cpg_id_extra_rows, 1)
        self.assertEqual(processed.report.duplicate_policy, "preserve_rows_and_warn")

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

    def test_processing_report_exposes_row_accounting_and_provenance(self) -> None:
        csv_payload = (
            "cpg_id,beta\n"
            "cg000001,0.2\n"
            "cg000001,0.7\n"
            "cg000002,\n"
        ).encode("utf-8")

        processed = process_methylation_upload(BytesIO(csv_payload), source_name="sample_upload.csv")

        self.assertEqual(processed.report.source_file, "sample_upload.csv")
        self.assertEqual(processed.report.parse_strategy, "extension_delimiter")
        self.assertEqual(processed.report.input_row_count, 3)
        self.assertEqual(processed.report.retained_row_count, 2)
        self.assertEqual(processed.report.dropped_row_count, 1)
        self.assertEqual(processed.report.dropped_rows_by_reason["missing_beta"], 1)
        self.assertEqual(processed.report.duplicate_cpg_id_groups, 1)
        self.assertEqual(processed.report.duplicate_cpg_id_extra_rows, 1)
        self.assertTrue((processed.normalized_df["source_file"] == "sample_upload.csv").all())
        self.assertTrue(processed.normalized_df["uploaded_at"].notna().all())


if __name__ == "__main__":
    unittest.main()
