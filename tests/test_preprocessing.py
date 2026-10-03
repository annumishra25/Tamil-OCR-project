"""
Comprehensive Unit and Integration Test Suite for Preprocessing Pipeline
Stage 4 Test Suite
"""

import unittest
import numpy as np
import cv2
import tempfile
from pathlib import Path

from src.preprocessing.filters import (
    to_grayscale,
    denoise_bilateral,
    denoise_nlm,
    enhance_contrast_linear,
    enhance_contrast_clahe,
    correct_illumination,
    threshold_sauvola,
    threshold_otsu,
    unsharp_mask,
    deskew_image,
    morphological_cleanup
)
from src.preprocessing.quality_analysis import analyze_image_quality
from src.preprocessing.pipeline import PreprocessingPipeline

class TestPreprocessingPipeline(unittest.TestCase):

    def setUp(self):
        # Create a synthetic 100x400 palm-leaf like image with gradient and text
        self.test_img = np.zeros((100, 400, 3), dtype=np.uint8)
        # Background gradient
        for y in range(100):
            self.test_img[y, :, :] = int(140 + (y / 100.0) * 60)
        # Add synthetic character incisions (dark lines)
        cv2.putText(self.test_img, "TAMIL OCR", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (40, 30, 20), 2)
        
        # Save to temp file for path-based tests
        self.temp_path = Path(tempfile.gettempdir()) / f"test_palm_sample_{np.random.randint(10000, 99999)}.png"
        cv2.imwrite(str(self.temp_path), self.test_img)

    def tearDown(self):
        import os
        if self.temp_path.exists():
            try:
                os.remove(str(self.temp_path))
            except Exception:
                pass

    def test_to_grayscale(self):
        gray = to_grayscale(self.test_img)
        self.assertEqual(len(gray.shape), 2)
        self.assertEqual(gray.shape, (100, 400))

    def test_denoise_bilateral(self):
        gray = to_grayscale(self.test_img)
        denoised = denoise_bilateral(gray)
        self.assertEqual(denoised.shape, (100, 400))
        self.assertEqual(denoised.dtype, np.uint8)

    def test_enhance_contrast_clahe(self):
        gray = to_grayscale(self.test_img)
        clahe = enhance_contrast_clahe(gray, clip_limit=2.0)
        self.assertEqual(clahe.shape, (100, 400))
        self.assertGreaterEqual(np.max(clahe), np.max(gray) - 5)

    def test_correct_illumination(self):
        gray = to_grayscale(self.test_img)
        illum = correct_illumination(gray, kernel_size=21)
        self.assertEqual(illum.shape, (100, 400))
        self.assertEqual(illum.dtype, np.uint8)

    def test_threshold_sauvola(self):
        gray = to_grayscale(self.test_img)
        binary = threshold_sauvola(gray, window_size=15, k=0.2)
        self.assertEqual(binary.shape, (100, 400))
        unique_vals = np.unique(binary)
        self.assertTrue(set(unique_vals).issubset({0, 255}))

    def test_threshold_otsu(self):
        gray = to_grayscale(self.test_img)
        binary = threshold_otsu(gray)
        self.assertEqual(binary.shape, (100, 400))
        unique_vals = np.unique(binary)
        self.assertTrue(set(unique_vals).issubset({0, 255}))

    def test_deskew_image(self):
        # Rotate image by 3 degrees
        h, w = self.test_img.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), 3.0, 1.0)
        rotated = cv2.warpAffine(self.test_img, M, (w, h))
        
        deskewed, angle = deskew_image(rotated)
        self.assertEqual(deskewed.shape, rotated.shape)
        self.assertIsInstance(angle, float)

    def test_morphological_cleanup(self):
        binary = np.full((100, 100), 255, dtype=np.uint8)
        # Add 1-pixel noise speckles
        binary[10, 10] = 0
        binary[50, 50] = 0
        # Add a larger connected block (character)
        binary[20:30, 20:30] = 0
        
        cleaned = morphological_cleanup(binary, min_component_area=15)
        # Speckles should be removed (set back to 255)
        self.assertEqual(cleaned[10, 10], 255)
        self.assertEqual(cleaned[50, 50], 255)
        # Large component preserved
        self.assertEqual(cleaned[25, 25], 0)

    def test_pipeline_execution(self):
        engine = PreprocessingPipeline()
        out_img, meta = engine.run_pipeline(self.test_img, "pipeline_e_master_adaptive")
        self.assertIsNotNone(out_img)
        self.assertEqual(meta["pipeline_key"], "pipeline_e_master_adaptive")
        self.assertIn("to_grayscale", meta["steps_executed"])
        self.assertGreater(meta["elapsed_seconds"], 0.0)

    def test_image_quality_analysis(self):
        q = analyze_image_quality(str(self.temp_path))
        self.assertEqual(q["width"], 400)
        self.assertEqual(q["height"], 100)
        self.assertGreater(q["mean_brightness"], 0)
        self.assertGreater(q["contrast_std"], 0)
        self.assertIn("laplacian_blur_var", q)
        self.assertIn("estimated_noise_sigma", q)

    def test_edge_case_small_image(self):
        small_img = np.zeros((10, 10, 3), dtype=np.uint8)
        engine = PreprocessingPipeline()
        out_img, meta = engine.run_pipeline(small_img, "pipeline_a_clahe")
        self.assertEqual(out_img.shape, (10, 10))

    def test_edge_case_grayscale_input(self):
        gray_input = np.full((50, 50), 128, dtype=np.uint8)
        gray_out = to_grayscale(gray_input)
        self.assertEqual(gray_out.shape, (50, 50))

if __name__ == "__main__":
    unittest.main()
