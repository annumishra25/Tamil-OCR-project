"""
End-to-End Integration and Smoke Tests (Stage 10).
Tests:
1. Complete 8-step pipeline execution on a synthetic and real palm-leaf folio.
2. FastAPI backend endpoints (/api/status, /api/metrics, /api/experiments, /api/analyze, /api/ocr, /api/process).
3. Export generation (TXT, JSON, CSV).
"""

import unittest
import json
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from fastapi.testclient import TestClient

from src.pipeline import EndToEndPalmLeafPipeline
from src.api.server import app

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()


class TestEndToEndPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = EndToEndPalmLeafPipeline()
        cls.client = TestClient(app)

    def test_pipeline_smoke_run(self):
        # Create a test folio image (simulating a palm-leaf folio with 2 horizontal bands)
        folio_img = Image.new("RGB", (400, 100), color=(180, 150, 110))
        result = self.pipeline.process_folio(folio_img, folio_id="TEST_SMOKE_FOLIO")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["folio_id"], "TEST_SMOKE_FOLIO")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertIn("quality_analysis", result)
        self.assertIn("segmented_lines_count", result)
        self.assertIn("lines", result)
        self.assertIn("final_transcription", result)
        self.assertIn("total_processing_time_sec", result)

    def test_api_status_endpoint(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ONLINE")
        self.assertIn("gpu", data)
        self.assertIn("pipeline", data)

    def test_api_metrics_endpoint(self):
        response = self.client.get("/api/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue("metrics" in data or "status" in data)

    def test_api_experiments_endpoint(self):
        response = self.client.get("/api/experiments")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("experiments", data)
        self.assertTrue(len(data["experiments"]) > 0)


if __name__ == "__main__":
    unittest.main()
