"""
Benchmark Image Quality Metrics Across Ingested Palm-Leaf Corpora
Stage 4 Quality Profiling
"""

import sys
import os
import csv
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
sys.path.append(str(PROJECT_ROOT))

from src.preprocessing.quality_analysis import analyze_image_quality

METRICS_DIR = PROJECT_ROOT / "results" / "metrics"
OUTPUT_CSV = METRICS_DIR / "image_quality.csv"

def run_quality_benchmark():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Collect sample manuscript images from each ingested dataset
    images_to_test = []
    
    # 1. CICT GT-133
    cict_img = PROJECT_ROOT / "data" / "raw" / "cict" / "CICT-PLM-GT-133.jpg"
    if cict_img.exists():
        images_to_test.append(("CICT_Tirukkural", "Raw_Capture", cict_img))

    # 2. THPLMD Staging Images
    staging_thplmd = PROJECT_ROOT / "data" / "processed" / "staging" / "thplmd"
    if staging_thplmd.exists():
        for root, dirs, files in os.walk(staging_thplmd):
            for f in files:
                if f.lower().endswith((".jpg", ".png")) and not f.lower().endswith(".zip"):
                    fpath = Path(root) / f
                    rel_p = fpath.relative_to(staging_thplmd).as_posix()
                    ds_name = "THPLMD"
                    if "naladiyar" in rel_p.lower():
                        ds_name = "THPLMD_Naladiyar"
                    elif "thirikadugam" in rel_p.lower():
                        ds_name = "THPLMD_Thirikadugam"
                    elif "tholkappiyam" in rel_p.lower():
                        ds_name = "THPLMD_Tholkappiyam"
                    
                    sub_type = "Binarized" if "binarized" in rel_p.lower() else "Original"
                    images_to_test.append((ds_name, sub_type, fpath))

    # 3. CICT Extracted Line Crops (Sample 5 lines)
    lines_dir = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines"
    if lines_dir.exists():
        for f in sorted(os.listdir(lines_dir))[:5]:
            if f.endswith(".png"):
                images_to_test.append(("CICT_Line_Crop", "Line_Crop", lines_dir / f))

    print(f"Profiling Image Quality across {len(images_to_test)} manuscript files...")
    
    results = []
    for ds_name, sub_type, fpath in images_to_test:
        try:
            q = analyze_image_quality(str(fpath))
            q["dataset"] = ds_name
            q["image_type"] = sub_type
            q["relative_path"] = fpath.relative_to(PROJECT_ROOT).as_posix()
            results.append(q)
            print(f"[{ds_name:20s}] {q['filename']:25s} | Dim: {q['width']}x{q['height']} | Brightness: {q['mean_brightness']:5.1f} | Contrast: {q['contrast_std']:4.1f} | Noise: {q['estimated_noise_sigma']:4.1f} | Skew: {q['estimated_skew_deg']:+5.1f} deg")
        except Exception as e:
            print(f"Error profiling {fpath}: {e}")

    if results:
        # Reorder columns with metadata first
        fieldnames = ["dataset", "image_type", "filename", "relative_path", "width", "height", "aspect_ratio",
                      "mean_brightness", "contrast_std", "dynamic_range", "laplacian_blur_var",
                      "tenengrad_sharpness", "estimated_noise_sigma", "illumination_variance",
                      "illumination_gradient", "otsu_threshold", "fg_bg_separability",
                      "edge_density", "estimated_skew_deg"]
        
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        print(f"\nGenerated Image Quality Report: {OUTPUT_CSV} ({len(results)} profiled images)")

    return results

if __name__ == "__main__":
    run_quality_benchmark()
