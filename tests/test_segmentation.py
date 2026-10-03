"""
Unit and Integration Tests for Palm-Leaf Line Segmentation
Stage 5 Test Suite
"""

import unittest
import numpy as np
import cv2
import tempfile
from pathlib import Path

from src.segmentation.line_segmenter import PalmLeafLineSegmenter
from src.segmentation.evaluate_segmentation import compute_box_iou

class TestPalmLeafSegmentation(unittest.TestCase):

    def setUp(self):
        # Create a synthetic multi-line manuscript image (height=200, width=600)
        self.img = np.full((200, 600, 3), 180, dtype=np.uint8)
        
        # Draw 4 horizontal text lines
        line_y_centers = [35, 75, 115, 155]
        for y in line_y_centers:
            cv2.putText(self.img, "TAMIL SCRIPT LINE TEST", (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)
            
        self.temp_path = Path(tempfile.gettempdir()) / f"test_seg_img_{np.random.randint(1000, 9999)}.png"
        cv2.imwrite(str(self.temp_path), self.img)

    def tearDown(self):
        import os
        if self.temp_path.exists():
            try:
                os.remove(str(self.temp_path))
            except Exception:
                pass

    def test_compute_box_iou_perfect_match(self):
        box1 = [10, 10, 100, 40]
        box2 = [10, 10, 100, 40]
        iou = compute_box_iou(box1, box2)
        self.assertAlmostEqual(iou, 1.0, places=4)

    def test_compute_box_iou_disjoint(self):
        box1 = [0, 0, 50, 50]
        box2 = [100, 100, 50, 50]
        iou = compute_box_iou(box1, box2)
        self.assertEqual(iou, 0.0)

    def test_compute_box_iou_partial(self):
        box1 = [0, 0, 100, 50]
        box2 = [50, 0, 100, 50]
        iou = compute_box_iou(box1, box2)
        # Intersection = 50 * 50 = 2500, Union = 5000 + 5000 - 2500 = 7500 -> 2500 / 7500 = 0.333
        self.assertAlmostEqual(iou, 1/3, places=3)

    def test_segment_horizontal_projection(self):
        segmenter = PalmLeafLineSegmenter(expected_line_height=35, min_line_height=15)
        lines, prep = segmenter.segment_horizontal_projection(self.img, prep_variant="clahe")
        self.assertGreaterEqual(len(lines), 3)
        self.assertLessEqual(len(lines), 6)
        for ln in lines:
            self.assertIn("reading_order", ln)
            self.assertIn("bbox", ln)
            self.assertGreater(ln["bbox"]["w"], 0)
            self.assertGreater(ln["bbox"]["h"], 0)

    def test_crop_lines(self):
        segmenter = PalmLeafLineSegmenter()
        lines, _ = segmenter.segment_horizontal_projection(self.img)
        temp_crop_dir = Path(tempfile.gettempdir()) / f"test_crops_{np.random.randint(1000, 9999)}"
        crops = segmenter.crop_lines(self.img, lines, temp_crop_dir, prefix="test_line")
        
        self.assertEqual(len(crops), len(lines))
        for c in crops:
            crop_file = Path(c["crop_path"])
            if crop_file.exists():
                self.assertGreater(crop_file.stat().st_size, 0)
                crop_file.unlink()
        if temp_crop_dir.exists():
            temp_crop_dir.rmdir()

    def test_draw_segmentation_overlay(self):
        segmenter = PalmLeafLineSegmenter()
        lines, _ = segmenter.segment_horizontal_projection(self.img)
        overlay_out = Path(tempfile.gettempdir()) / f"test_overlay_{np.random.randint(1000, 9999)}.png"
        segmenter.draw_segmentation_overlay(self.img, lines, overlay_out)
        self.assertTrue(overlay_out.exists())
        self.assertGreater(overlay_out.stat().st_size, 0)
        overlay_out.unlink()

if __name__ == "__main__":
    unittest.main()
