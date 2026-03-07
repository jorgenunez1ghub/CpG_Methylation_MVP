from io import BytesIO
import unittest

from cpg_methylation_mvp.core.ingest import IngestError, load_methylation_file


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

    def test_utf8_bom_header_is_handled(self) -> None:
        csv_payload = "\ufeffcpg_id,beta\ncg000001,0.45\n".encode("utf-8")

        df = load_methylation_file(BytesIO(csv_payload), source_name="bom.csv")

        self.assertEqual(len(df), 1)
        self.assertIn("cpg_id", df.columns)
        self.assertAlmostEqual(float(df.loc[0, "beta"]), 0.45)


if __name__ == "__main__":
    unittest.main()
