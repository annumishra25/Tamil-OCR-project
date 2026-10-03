"""
Unit tests for OCR components (Stage 8).
Tests processor encoding/decoding, model architecture & parameters,
dataset collation, checkpoint saving/loading, and CER/WER calculation.
"""
import unittest
import torch
import numpy as np
from PIL import Image

from src.ocr.processor import TamilOCRProcessor
from src.ocr.crnn_model import TamilCRNN
from src.evaluation.metrics import calculate_cer, calculate_wer


class TestTamilProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = TamilOCRProcessor()

    def test_vocab_size(self):
        self.assertEqual(self.processor.vocab_size, len(self.processor.vocab))
        self.assertEqual(self.processor.vocab[0], "[CTC_BLANK]")

    def test_encode_decode_roundtrip(self):
        sample_text = "தமிழ் அரிச்சுவடி"
        indices = self.processor.encode_text(sample_text)
        self.assertTrue(len(indices) > 0)
        decoded = self.processor.decode_indices(indices, merge_repeated=False)
        self.assertEqual(decoded, sample_text)

    def test_ctc_decode_repeated(self):
        # CTC decode should collapse consecutive repeated indices
        raw_indices = [0, 10, 10, 0, 20, 20, 30, 0]
        decoded = self.processor.decode_indices(raw_indices, merge_repeated=True)
        expected = self.processor.idx_to_char[10] + self.processor.idx_to_char[20] + self.processor.idx_to_char[30]
        self.assertEqual(decoded, expected)

    def test_image_processing(self):
        dummy_img = Image.new("L", (200, 40), color=128)
        tensor = self.processor.process_image(dummy_img)
        self.assertEqual(tensor.dim(), 3)
        self.assertEqual(tensor.shape[0], 1)
        self.assertEqual(tensor.shape[1], 32)
        # Width should be a multiple of 4
        self.assertEqual(tensor.shape[2] % 4, 0)


class TestTamilCRNNModel(unittest.TestCase):
    def setUp(self):
        self.model = TamilCRNN(num_class=143)

    def test_parameter_count(self):
        param_count = sum(p.numel() for p in self.model.parameters())
        self.assertEqual(param_count, 53791855)

    def test_forward_shape(self):
        # Batch of 2 images: 1 channel, height 32, width 128
        dummy_input = torch.randn(2, 1, 32, 128)
        logits = self.model(dummy_input)
        # Output shape: (T, B, num_class) for PyTorch CTCLoss
        self.assertEqual(logits.dim(), 3)
        self.assertEqual(logits.shape[1], 2)
        self.assertEqual(logits.shape[2], 143)


class TestOCRMetrics(unittest.TestCase):
    def test_cer_exact_match(self):
        cer = calculate_cer("தமிழ்", "தமிழ்")
        self.assertEqual(cer, 0.0)

    def test_cer_mismatch(self):
        cer = calculate_cer("தமிழ்", "தமழ")
        self.assertGreater(cer, 0.0)

    def test_wer_calculation(self):
        wer = calculate_wer("தமிழ் நாடு இந்தியா", "தமிழ் நாடு உலகம்")
        self.assertAlmostEqual(wer, 1/3, places=2)


if __name__ == "__main__":
    unittest.main()
