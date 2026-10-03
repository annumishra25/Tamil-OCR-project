"""
Unit Tests for Stage 6 Training-Pair Formulation, Dataset Integration & Leakage-Safe Splits
"""

import unittest
import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")

from src.data.normalization import normalize_tamil_unicode, compare_transcription_normalization, validate_tamil_script
from src.data.cict_loader import CICTDatasetLoader
from src.data.thplmd_loader import THPLMDDatasetLoader
from src.data.palmleaf_tamil_loader import PalmleafTamilLoader
from src.data.splits import SplitManager
from src.data.duplicate_detector import DuplicateDetector, compute_sha256


class TestDataPipeline(unittest.TestCase):

    def test_tamil_unicode_normalization(self):
        # Raw text with multiple spaces and zero-width characters
        raw = "இல்லைத்\u200B   தவற்   வாக்காயினு   மூடுதல்"
        norm = normalize_tamil_unicode(raw)
        self.assertEqual(norm, "இல்லைத் தவற் வாக்காயினு மூடுதல்")
        self.assertNotIn("\u200B", norm)

        # Comparison report
        comp = compare_transcription_normalization(raw)
        self.assertTrue(comp["is_changed"])
        self.assertEqual(comp["normalized"], norm)

    def test_tamil_script_validation(self):
        tamil_text = "ஊடலுவகை ௧௩௨௧"
        val = validate_tamil_script(tamil_text)
        self.assertGreater(val["tamil_pct"], 80.0)
        self.assertTrue(val["contains_numerals"])

    def test_cict_loader(self):
        loader = CICTDatasetLoader()
        records = loader.load_records()
        self.assertEqual(len(records), 23)
        self.assertTrue(all(r["label_status"] == "VERIFIED_GROUND_TRUTH" for r in records))
        self.assertTrue(all(r["source_group_id"] == "CICT_GT133_FOLIO_87" for r in records))
        self.assertTrue(all(r["split"] == "external_test" for r in records))

    def test_thplmd_loader(self):
        loader = THPLMDDatasetLoader()
        folios = loader.load_folios()
        self.assertEqual(len(folios), 158)
        self.assertTrue(all(r["label_status"] == "UNLABELED" for r in folios))
        self.assertTrue(all(r["transcription"] == "NOT_AVAILABLE" for r in folios))

    def test_palmleaf_tamil_loader(self):
        loader = PalmleafTamilLoader()
        summary = loader.inspect_archive()
        if summary.get("is_present"):
            self.assertEqual(summary["total_images"], 7100)
            self.assertEqual(summary["classes_count"], 71)
            records = loader.generate_character_records(limit=10)
            self.assertEqual(len(records), 10)
            self.assertEqual(records[0]["data_level"], "CHARACTER_LEVEL")

    def test_split_manager_no_leakage(self):
        mgr = SplitManager()
        clean_splits = {
            "train": [{"sample_id": "S1", "source_group_id": "FOLIO_A"}],
            "val": [{"sample_id": "S2", "source_group_id": "FOLIO_B"}],
            "test": [{"sample_id": "S3", "source_group_id": "FOLIO_C"}]
        }
        is_valid, violations = mgr.validate_no_leakage(clean_splits)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_split_manager_detects_leakage(self):
        mgr = SplitManager()
        leaky_splits = {
            "train": [
                {"sample_id": "S1_RAW", "source_group_id": "FOLIO_A"},
                {"sample_id": "S2_BIN", "source_group_id": "FOLIO_B"}
            ],
            "test": [
                {"sample_id": "S1_BIN", "source_group_id": "FOLIO_A"}  # LEAKAGE of FOLIO_A!
            ]
        }
        is_valid, violations = mgr.validate_no_leakage(leaky_splits)
        self.assertFalse(is_valid)
        self.assertEqual(len(violations), 1)
        self.assertIn("FOLIO_A", violations[0])

        # Ensure export_jsonl_splits raises ValueError on leakage
        with self.assertRaises(ValueError):
            mgr.export_jsonl_splits(leaky_splits)

    def test_duplicate_detector(self):
        detector = DuplicateDetector()
        rows, summary = detector.scan_images()
        self.assertGreater(summary["total_scanned_images"], 0)
        self.assertIn("unique_sha256_hashes", summary)


if __name__ == "__main__":
    unittest.main()
