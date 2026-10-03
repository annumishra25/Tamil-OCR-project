"""
Preprocessing Visualization & Multi-Stage Preview Generator
Stage 4 Visualization Tool
"""

import sys
import os
import argparse
import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
sys.path.append(str(PROJECT_ROOT))

from src.preprocessing.filters import (
    to_grayscale,
    denoise_bilateral,
    enhance_contrast_clahe,
    correct_illumination,
    threshold_sauvola,
    threshold_otsu,
    deskew_image,
    morphological_cleanup
)
from src.preprocessing.pipeline import PreprocessingPipeline

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
VISUALIZATIONS_DIR = PROJECT_ROOT / "results" / "visualizations"

def ensure_output_directories():
    (PROCESSED_DIR / "grayscale").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "denoised").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "contrast").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "threshold").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "deskewed").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "illumination").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "combined").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "previews").mkdir(parents=True, exist_ok=True)
    VISUALIZATIONS_DIR.mkdir(parents=True, exist_ok=True)

def generate_preprocessing_variants(image_path: str, save_individual: bool = True) -> dict:
    """
    Generate and save all core preprocessing filter variants for a manuscript image.
    """
    ensure_output_directories()
    path_obj = Path(image_path)
    stem = path_obj.stem
    
    img_bgr = cv2.imread(str(path_obj))
    if img_bgr is None:
        raise ValueError(f"Could not load image from {image_path}")

    # 1. Grayscale
    gray = to_grayscale(img_bgr)
    
    # 2. Illumination Corrected
    illum = correct_illumination(gray)
    
    # 3. Bilateral Denoised
    denoised = denoise_bilateral(gray)
    
    # 4. CLAHE Enhanced
    clahe = enhance_contrast_clahe(gray, clip_limit=2.5)
    
    # 5. Sauvola Adaptive Threshold
    sauvola = threshold_sauvola(clahe, window_size=25, k=0.2)
    sauvola_clean = morphological_cleanup(sauvola)
    
    # 6. Otsu Threshold
    otsu = threshold_otsu(gray)
    
    # 7. Deskewed
    deskewed, angle = deskew_image(gray)
    
    # 8. Master Adaptive Pipeline
    pipeline_engine = PreprocessingPipeline()
    master, meta = pipeline_engine.run_pipeline(img_bgr, "pipeline_e_master_adaptive")

    variants = {
        "1_Original": img_bgr,
        "2_Grayscale": gray,
        "3_Illumination_Corrected": illum,
        "4_Bilateral_Denoised": denoised,
        "5_CLAHE_Contrast": clahe,
        "6_Sauvola_Binarized": sauvola_clean,
        "7_Otsu_Binarized": otsu,
        "8_Master_Adaptive": master
    }

    if save_individual:
        cv2.imwrite(str(PROCESSED_DIR / "grayscale" / f"{stem}_grayscale.png"), gray)
        cv2.imwrite(str(PROCESSED_DIR / "illumination" / f"{stem}_illum_norm.png"), illum)
        cv2.imwrite(str(PROCESSED_DIR / "denoised" / f"{stem}_denoised.png"), denoised)
        cv2.imwrite(str(PROCESSED_DIR / "contrast" / f"{stem}_clahe.png"), clahe)
        cv2.imwrite(str(PROCESSED_DIR / "threshold" / f"{stem}_sauvola.png"), sauvola_clean)
        cv2.imwrite(str(PROCESSED_DIR / "threshold" / f"{stem}_otsu.png"), otsu)
        cv2.imwrite(str(PROCESSED_DIR / "deskewed" / f"{stem}_deskewed.png"), deskewed)
        cv2.imwrite(str(PROCESSED_DIR / "combined" / f"{stem}_master_adaptive.png"), master)

    # Build side-by-side comparison grid
    grid_path = VISUALIZATIONS_DIR / f"{stem}_preprocessing_comparison.png"
    create_comparison_grid(variants, grid_path, stem)
    print(f"Generated comparison grid: {grid_path}")

    return variants

def create_comparison_grid(variants: dict, output_path: Path, title: str):
    """Stack variants into a labeled visual grid."""
    panels = []
    # Standardize preview width
    target_w = 1200
    
    for label, img in variants.items():
        if len(img.shape) == 2:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
        h, w = img_rgb.shape[:2]
        scale = target_w / w
        target_h = max(30, int(h * scale))
        resized = cv2.resize(img_rgb, (target_w, target_h), interpolation=cv2.INTER_AREA)
        
        # Add label banner
        banner_h = 28
        banner = np.zeros((banner_h, target_w, 3), dtype=np.uint8)
        banner[:] = (26, 22, 19) # Laboratory dark background
        
        cv2.putText(
            banner,
            label.replace("_", " "),
            (15, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (212, 175, 55), # Gold accent
            1,
            cv2.LINE_AA
        )
        stacked = np.vstack([banner, resized])
        panels.append(stacked)
        
    final_grid = np.vstack(panels)
    # Save final grid
    cv2.imwrite(str(output_path), cv2.cvtColor(final_grid, cv2.COLOR_RGB2BGR))

def main():
    parser = argparse.ArgumentParser(description="Generate Preprocessing Comparison Grid for Palm-Leaf Manuscripts")
    parser.add_argument("image", nargs="?", default="data/raw/cict/CICT-PLM-GT-133.jpg", help="Path to manuscript image")
    args = parser.parse_args()

    img_p = Path(args.image)
    if not img_p.is_absolute():
        img_p = PROJECT_ROOT / img_p

    print(f"Generating preprocessing suite for: {img_p}")
    generate_preprocessing_variants(str(img_p))

if __name__ == "__main__":
    main()
