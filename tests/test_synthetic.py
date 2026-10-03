"""
Unit Tests for Stage 7 Synthetic Palm-Leaf Degradation Engine
"""

import unittest
import numpy as np
from PIL import Image
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")

from src.augmentation.text_renderer import TamilTextRenderer
from src.augmentation.palmleaf_degradation import (
    apply_fibrous_background_texture,
    apply_uneven_illumination,
    apply_stroke_fading_erosion,
    apply_scratches_and_cracks,
    apply_speckles_and_blotches,
    apply_blur_and_noise,
    apply_geometric_distortions,
    apply_contrast_and_brightness,
    degrade_palmleaf_image
)
from src.augmentation.synthetic_generator import SyntheticDatasetGenerator


class TestSyntheticDegradationEngine(unittest.TestCase):

    def setUp(self):
        self.renderer = TamilTextRenderer()
        self.test_tamil_text = "அகர முதல எழுத்தெல்லாம் ஆதி"

    def test_font_discovery(self):
        fonts = self.renderer.fonts
        self.assertGreater(len(fonts), 0)
        self.assertTrue(any("nirmala" in f["font_name"].lower() or "latha" in f["font_name"].lower() for f in fonts))

    def test_clean_text_rendering(self):
        img, meta = self.renderer.render_line(self.test_tamil_text, font_size=28)
        self.assertIsInstance(img, Image.Image)
        self.assertGreater(img.width, 100)
        self.assertGreater(img.height, 25)
        self.assertEqual(meta["text"], self.test_tamil_text)

    def test_individual_degradation_operators(self):
        img, _ = self.renderer.render_line(self.test_tamil_text, font_size=24)
        img_np = np.array(img.convert("RGB"))
        rng = np.random.RandomState(42)

        # 1. Texture
        tex = apply_fibrous_background_texture(img_np, strength=0.3, rng=rng)
        self.assertEqual(tex.shape, img_np.shape)

        # 2. Illumination
        illum = apply_uneven_illumination(tex, strength=0.25, rng=rng)
        self.assertEqual(illum.shape, img_np.shape)

        # 3. Fading
        faded = apply_stroke_fading_erosion(illum, erosion_iters=1, prob=1.0, rng=rng)
        self.assertEqual(faded.shape, img_np.shape)

        # 4. Scratches
        scratched = apply_scratches_and_cracks(faded, count=4, rng=rng)
        self.assertEqual(scratched.shape, img_np.shape)

        # 5. Speckles
        speckled = apply_speckles_and_blotches(scratched, count=8, rng=rng)
        self.assertEqual(speckled.shape, img_np.shape)

        # 6. Blur & Noise
        noisy = apply_blur_and_noise(speckled, gaussian_sigma=0.8, noise_std=5.0, rng=rng)
        self.assertEqual(noisy.shape, img_np.shape)

        # 7. Geometric
        geom = apply_geometric_distortions(noisy, rotation_deg=0.5, rng=rng)
        self.assertEqual(geom.shape, img_np.shape)

        # 8. Contrast
        final = apply_contrast_and_brightness(geom, contrast=0.85, brightness=1.0)
        self.assertEqual(final.shape, img_np.shape)

    def test_deterministic_seed_reproducibility(self):
        img, _ = self.renderer.render_line(self.test_tamil_text, font_size=26)
        seed = 999
        
        deg1, params1 = degrade_palmleaf_image(img, preset="MEDIUM", seed=seed)
        deg2, params2 = degrade_palmleaf_image(img, preset="MEDIUM", seed=seed)

        arr1 = np.array(deg1)
        arr2 = np.array(deg2)
        
        # Exact pixel match for identical seed
        np.testing.assert_array_equal(arr1, arr2)
        self.assertEqual(params1, params2)

    def test_zero_leakage_corpus_partitioning(self):
        gen = SyntheticDatasetGenerator()
        lines = gen.load_clean_corpus()
        self.assertGreater(len(lines), 0)

        splits = gen.partition_corpus(lines, train_ratio=0.70, val_ratio=0.15)
        
        train_groups = set(item["source_group_id"] for item in splits["train"])
        val_groups = set(item["source_group_id"] for item in splits["val"])
        test_groups = set(item["source_group_id"] for item in splits["test"])

        # Invariant: ZERO intersection of source_group_ids across splits
        self.assertEqual(len(train_groups.intersection(val_groups)), 0, "Leakage between train and val!")
        self.assertEqual(len(train_groups.intersection(test_groups)), 0, "Leakage between train and test!")
        self.assertEqual(len(val_groups.intersection(test_groups)), 0, "Leakage between val and test!")

    def test_quality_audit(self):
        gen = SyntheticDatasetGenerator()
        # Normal image with text content
        normal_img, _ = self.renderer.render_line(self.test_tamil_text, font_size=28)
        audit = gen.audit_quality(normal_img)
        self.assertTrue(audit["passed"])

        # Problematic too small image
        tiny_img = Image.new("RGB", (20, 10), (200, 200, 200))
        audit_tiny = gen.audit_quality(tiny_img)
        self.assertFalse(audit_tiny["passed"])
        self.assertIn("TOO_SMALL", audit_tiny["flags"])


if __name__ == "__main__":
    unittest.main()
