"""
Configurable Preprocessing Pipeline Engine & Adaptive Quality Selector
Stage 4 Pipeline Architecture
"""

import sys
import json
import time
import numpy as np
import cv2
from pathlib import Path
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
sys.path.append(str(PROJECT_ROOT))

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

# Predefined standard pipeline definitions
DEFAULT_PIPELINES = {
    "raw": {
        "name": "Raw Capture",
        "description": "Original unchanged photographic capture.",
        "steps": []
    },
    "grayscale": {
        "name": "Standard Grayscale",
        "description": "Single-channel luminance extraction.",
        "steps": ["to_grayscale"]
    },
    "pipeline_a_clahe": {
        "name": "Pipeline A (CLAHE Contrast Boost)",
        "description": "Grayscale conversion followed by local CLAHE contrast equalization.",
        "steps": ["to_grayscale", "enhance_contrast_clahe"]
    },
    "pipeline_b_denoise_clahe": {
        "name": "Pipeline B (Bilateral Denoise + CLAHE)",
        "description": "Stroke-preserving bilateral denoising to suppress palm fiber grain, followed by CLAHE.",
        "steps": ["to_grayscale", "denoise_bilateral", "enhance_contrast_clahe"]
    },
    "pipeline_c_illum_clahe": {
        "name": "Pipeline C (Illumination Norm + CLAHE)",
        "description": "Rolling background division to eliminate ambient shadows, followed by CLAHE.",
        "steps": ["to_grayscale", "correct_illumination", "enhance_contrast_clahe"]
    },
    "pipeline_d_sauvola_deskew": {
        "name": "Pipeline D (Sauvola Adaptive Binarization + Deskew)",
        "description": "Adaptive local thresholding followed by baseline deskewing and noise speckle cleanup.",
        "steps": ["to_grayscale", "threshold_sauvola", "morphological_cleanup", "deskew_image"]
    },
    "pipeline_e_master_adaptive": {
        "name": "Pipeline E (Master Distortion-Aware Adaptive Pipeline)",
        "description": "Multi-stage: Illumination correction, bilateral denoise, CLAHE, and Sauvola thresholding.",
        "steps": ["to_grayscale", "correct_illumination", "denoise_bilateral", "enhance_contrast_clahe", "threshold_sauvola", "morphological_cleanup"]
    }
}

class PreprocessingPipeline:
    def __init__(self, pipeline_config: dict = None):
        self.config = pipeline_config or DEFAULT_PIPELINES

    def apply_step(self, img: np.ndarray, step_name: str) -> np.ndarray:
        if step_name == "to_grayscale":
            return to_grayscale(img)
        elif step_name == "denoise_bilateral":
            return denoise_bilateral(img)
        elif step_name == "denoise_nlm":
            return denoise_nlm(img)
        elif step_name == "enhance_contrast_linear":
            return enhance_contrast_linear(img)
        elif step_name == "enhance_contrast_clahe":
            return enhance_contrast_clahe(img)
        elif step_name == "correct_illumination":
            return correct_illumination(img)
        elif step_name == "threshold_sauvola":
            return threshold_sauvola(img)
        elif step_name == "threshold_otsu":
            return threshold_otsu(img)
        elif step_name == "unsharp_mask":
            return unsharp_mask(img)
        elif step_name == "deskew_image":
            deskewed, _ = deskew_image(img)
            return deskewed
        elif step_name == "morphological_cleanup":
            return morphological_cleanup(img)
        else:
            raise ValueError(f"Unknown preprocessing step: {step_name}")

    def run_pipeline(self, img_input, pipeline_key: str = "pipeline_e_master_adaptive") -> tuple[np.ndarray, dict]:
        """
        Execute a named pipeline on an input image (either numpy array or path).
        Returns (processed_image, execution_metadata).
        """
        start_time = time.time()
        
        if isinstance(img_input, (str, Path)):
            img = cv2.imread(str(img_input))
            if img is None:
                raise ValueError(f"Could not load image from {img_input}")
        elif isinstance(img_input, np.ndarray):
            img = img_input.copy()
        else:
            raise TypeError("img_input must be a file path or numpy ndarray")

        if pipeline_key not in self.config:
            raise KeyError(f"Pipeline key '{pipeline_key}' not found in configuration.")

        pipeline_def = self.config[pipeline_key]
        current_img = img
        steps_executed = []

        for step in pipeline_def.get("steps", []):
            current_img = self.apply_step(current_img, step)
            steps_executed.append(step)

        elapsed_sec = time.time() - start_time

        meta = {
            "pipeline_key": pipeline_key,
            "pipeline_name": pipeline_def.get("name", pipeline_key),
            "steps_executed": steps_executed,
            "elapsed_seconds": round(elapsed_sec, 4),
            "output_shape": list(current_img.shape)
        }
        return current_img, meta

    def select_adaptive_pipeline(self, image_path: str) -> str:
        """
        Analyze image quality metrics and explainably select the most appropriate preprocessing pipeline.
        """
        q = analyze_image_quality(image_path)
        
        # Explainable heuristic rules based on physical palm-leaf distortions
        if q["illumination_variance"] > 35.0 or q["illumination_gradient"] > 120.0:
            # Severe ambient shadow or illumination gradient
            return "pipeline_c_illum_clahe"
        elif q["estimated_noise_sigma"] > 25.0:
            # Significant fibrous noise / texture grain
            return "pipeline_b_denoise_clahe"
        elif q["contrast_std"] < 30.0:
            # Low contrast faint incisions
            return "pipeline_a_clahe"
        elif q["fg_bg_separability"] > 0.65:
            # High foreground/background contrast suitable for Sauvola binarization
            return "pipeline_d_sauvola_deskew"
        else:
            return "pipeline_e_master_adaptive"
