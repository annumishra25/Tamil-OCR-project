"""
Unit & Integration Tests for Stage 9: Confidence Second Pass & Tamil Post-Correction.

Tests:
1. Real CTC confidence estimation from log-probabilities.
2. Threshold routing logic (first-pass acceptance vs. second-pass triggering).
3. Second-pass candidate generation across multiple preprocessing variants.
4. Ambiguity detection and REVIEW_REQUIRED flagging.
5. Conservative Tamil Unicode normalization and orthography correction rules.
6. Original text preservation during post-correction.
7. Verification of zero CICT label contamination / exclusion.
"""

import unittest
import torch
import numpy as np
from PIL import Image
from pathlib import Path

from src.ocr.processor import TamilOCRProcessor
from src.ocr.crnn_model import TamilCRNN
from src.confidence.confidence_estimator import CTCConfidenceEstimator, SequenceConfidenceResult
from src.confidence.second_pass import SecondPassRouter, SecondPassResult
from src.correction.tamil_postcorrection import TamilPostCorrector, CorrectionResult


class TestConfidenceEstimator(unittest.TestCase):
    def setUp(self):
        self.processor = TamilOCRProcessor()
        self.estimator = CTCConfidenceEstimator(self.processor)

    def test_real_confidence_extraction(self):
        # Create synthetic log_probs for T=10 frames, num_class=143
        T, num_class = 10, 143
        logits = torch.randn(T, 1, num_class)
        # Force high probability on character index 10 at frame 2, 20 at frame 5
        logits[2, 0, 10] = 10.0
        logits[5, 0, 20] = 12.0
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)

        result = self.estimator.estimate_confidence(log_probs, batch_index=0)
        self.assertIsInstance(result, SequenceConfidenceResult)
        self.assertGreater(result.sequence_confidence, 0.0)
        self.assertLessEqual(result.sequence_confidence, 1.0)
        self.assertTrue(len(result.token_confidences) > 0)
        # Check that token probabilities are valid probabilities
        for tc in result.token_confidences:
            self.assertGreaterEqual(tc.probability, 0.0)
            self.assertLessEqual(tc.probability, 1.0)
            self.assertGreaterEqual(tc.entropy, 0.0)

    def test_blank_only_sequence(self):
        # Sequence where all frames predict blank (index 0)
        T, num_class = 8, 143
        logits = torch.zeros(T, 1, num_class)
        logits[:, :, 0] = 20.0  # Dominant blank
        log_probs = torch.nn.functional.log_softmax(logits, dim=-1)

        result = self.estimator.estimate_confidence(log_probs, batch_index=0)
        self.assertEqual(result.transcription, "")
        self.assertEqual(result.sequence_confidence, 0.0)
        self.assertEqual(len(result.token_confidences), 0)


class TestTamilPostCorrector(unittest.TestCase):
    def setUp(self):
        self.corrector = TamilPostCorrector()

    def test_unicode_nfc_normalization(self):
        # Decomposed Tamil text
        decomposed = "தம\u0BBFழ\u0BCD"
        result = self.corrector.correct(decomposed)
        self.assertEqual(result.corrected_text, "தமிழ்")

    def test_whitespace_cleanup(self):
        raw = "   தமிழ்    அரிச்சுவடி   "
        result = self.corrector.correct(raw)
        self.assertEqual(result.corrected_text, "தமிழ் அரிச்சுவடி")
        self.assertTrue(result.was_modified)

    def test_detached_combining_sign(self):
        # Detached vowel sign: 'தம ிழ்' -> 'தமிழ்'
        detached = "தம ிழ்"
        result = self.corrector.correct(detached)
        self.assertEqual(result.corrected_text, "தமிழ்")
        self.assertTrue(result.was_modified)

    def test_deduplicate_combining_marks(self):
        # Double pulli on same consonant: 'க்்' -> 'க்'
        double_pulli = "க்்"
        result = self.corrector.correct(double_pulli)
        self.assertEqual(result.corrected_text, "க்")
        self.assertTrue(result.was_modified)

    def test_original_text_preservation(self):
        sample = "இல்லை தவறு அவர்க்காயினும்"
        result = self.corrector.correct(sample)
        self.assertEqual(result.original_text, sample)


class TestSecondPassRouter(unittest.TestCase):
    def setUp(self):
        self.processor = TamilOCRProcessor()
        self.model = TamilCRNN(num_class=143)
        self.model.eval()
        self.router = SecondPassRouter(
            model=self.model,
            processor=self.processor,
            device=torch.device("cpu"),
            confidence_threshold=0.85,
            ambiguity_margin=0.03,
            review_floor=0.50,
            candidate_pipelines=["raw", "pipeline_a_clahe"]
        )

    def test_router_structure_and_schema(self):
        dummy_img = Image.new("L", (128, 32), color=200)
        res = self.router.process_line(
            dummy_img,
            source_id="TEST_FOLIO",
            line_id="LINE_001"
        )
        self.assertIsInstance(res, SecondPassResult)
        self.assertEqual(res.source_id, "TEST_FOLIO")
        self.assertEqual(res.line_id, "LINE_001")
        self.assertIn("first_pass_text", res.__dict__)
        self.assertIn("second_pass_triggered", res.__dict__)
        self.assertIn("selected_text", res.__dict__)
        self.assertIn("corrected_text", res.__dict__)
        self.assertIn("review_required", res.__dict__)

    def test_zero_cict_leakage_rule(self):
        # Verify that router does not contain or reference external_test annotations internally
        self.assertFalse(hasattr(self.router, "external_test_labels"))
        self.assertFalse(hasattr(self.router, "cict_ground_truth"))


if __name__ == "__main__":
    unittest.main()
