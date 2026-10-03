"""
Empirical Line Segmentation Benchmarking & Automatic THPLMD Processing
Stage 5 Segmentation Pipeline
"""

import sys
import os
import csv
import json
import numpy as np
import cv2
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
sys.path.append(str(PROJECT_ROOT))

from src.segmentation.line_segmenter import PalmLeafLineSegmenter

CICT_IMG_PATH = PROJECT_ROOT / "data" / "raw" / "cict" / "CICT-PLM-GT-133.jpg"
CICT_LINES_CSV = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
VISUALIZATIONS_DIR = PROJECT_ROOT / "results" / "visualizations"
METRICS_DIR = PROJECT_ROOT / "results" / "metrics"

def compute_box_iou(boxA, boxB):
    # box = [x, y, w, h] -> [x1, y1, x2, y2]
    xA1, yA1, xA2, yA2 = boxA[0], boxA[1], boxA[0] + boxA[2], boxA[1] + boxA[3]
    xB1, yB1, xB2, yB2 = boxB[0], boxB[1], boxB[0] + boxB[2], boxB[1] + boxB[3]

    inter_x1 = max(xA1, xB1)
    inter_y1 = max(yA1, yB1)
    inter_x2 = min(xA2, xB2)
    inter_y2 = min(yA2, yB2)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    boxA_area = boxA[2] * boxA[3]
    boxB_area = boxB[2] * boxB[3]

    union_area = boxA_area + boxB_area - inter_area
    if union_area == 0:
        return 0.0
    return inter_area / union_area

def benchmark_cict_segmentation():
    print("\n=======================================================")
    print("--- 1. Evaluating Line Segmentation on CICT GT-133 ---")
    print("=======================================================")

    # Load Ground Truth lines
    gt_lines = []
    with open(CICT_LINES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            gt_lines.append(r)
            
    # Filter to main body lines (which are continuous horizontal bands)
    body_gt = [g for g in gt_lines if g["line_type"] == "paragraph"]
    print(f"Loaded {len(gt_lines)} total CICT GT lines ({len(body_gt)} main body couplet lines).")

    segmenter = PalmLeafLineSegmenter(min_line_height=15, max_line_height=50, horizontal_padding=10, vertical_padding=4)
    auto_lines, prep_img = segmenter.segment_horizontal_projection(CICT_IMG_PATH, prep_variant="clahe")
    print(f"Automatic Segmentation detected: {len(auto_lines)} line bands.")

    # Match detected lines with ground truth body lines (IoU threshold >= 0.5)
    matches = 0
    ious = []
    
    for gt in body_gt:
        gt_box = [int(gt["bbox_x"]), int(gt["bbox_y"]), int(gt["bbox_width"]), int(gt["bbox_height"])]
        best_iou = 0.0
        best_match = None
        for auto in auto_lines:
            abox = [auto["bbox"]["x"], auto["bbox"]["y"], auto["bbox"]["w"], auto["bbox"]["h"]]
            iou = compute_box_iou(gt_box, abox)
            if iou > best_iou:
                best_iou = iou
                best_match = auto
                
        ious.append(best_iou)
        if best_iou >= 0.5:
            matches += 1
        print(f"GT Line {gt['line_id']:15s} (y={gt['bbox_y']}, h={gt['bbox_height']}) -> Best Auto Match IoU: {best_iou:.3f}")

    precision = matches / len(auto_lines) if auto_lines else 0.0
    recall = matches / len(body_gt) if body_gt else 0.0
    f1 = 2 * precision * recall / (precision + recall + 1e-6)
    mean_iou = float(np.mean(ious)) if ious else 0.0

    print(f"\n--- CICT Line Segmentation Quality Metrics ---")
    print(f"Ground Truth Body Lines: {len(body_gt)}")
    print(f"Detected Line Candidates: {len(auto_lines)}")
    print(f"Matched Lines (IoU >= 0.5): {matches}")
    print(f"Precision: {precision*100:.2f}% | Recall: {recall*100:.2f}% | F1: {f1*100:.2f}%")
    print(f"Mean IoU Overlap: {mean_iou:.3f}")

    # Generate Visual Overlay
    overlay_out = VISUALIZATIONS_DIR / "CICT_GT133_segmentation_overlay.png"
    segmenter.draw_segmentation_overlay(CICT_IMG_PATH, auto_lines, overlay_out, title="CICT GT-133 Auto Lines")

    # Save metrics JSON
    cict_seg_metrics = {
        "dataset": "CICT-PLM-GT-133",
        "ground_truth_body_lines": len(body_gt),
        "detected_lines": len(auto_lines),
        "matched_lines": matches,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "mean_iou": round(mean_iou, 4),
        "overlay_path": str(overlay_out.relative_to(PROJECT_ROOT).as_posix())
    }
    with open(METRICS_DIR / "segmentation_cict_metrics.json", 'w', encoding='utf-8') as f:
        json.dump(cict_seg_metrics, f, indent=2)

    return cict_seg_metrics

def process_thplmd_automatic_segmentation():
    print("\n=======================================================")
    print("--- 2. Processing Automatic Line Segmentation on THPLMD ---")
    print("=======================================================")

    staging_base = PROJECT_ROOT / "data" / "processed" / "staging" / "thplmd"
    auto_lines_dir = PROCESSED_DIR / "lines" / "automatic"
    auto_lines_dir.mkdir(parents=True, exist_ok=True)

    segmenter = PalmLeafLineSegmenter(min_line_height=18, max_line_height=65, horizontal_padding=10, vertical_padding=4)
    
    # Collect sample folios across collections
    folio_samples = [
        ("Naladiyar", staging_base / "naladiyar" / "Naladiyar" / "Naladiyar Original" / "176.jpg"),
        ("Thirikadugam", staging_base / "thirikadugam" / "THIRIKADUGAM" / "THIRIKADUGAM ORIGIANAL" / "461.jpg"),
        ("Tholkappiyam", staging_base / "tholkappiyam" / "THOLKAPPIYAM BINARIZED - (2)" / "351.jpg")
    ]

    all_thplmd_lines = []
    
    for coll_name, img_path in folio_samples:
        if not img_path.exists():
            print(f"Notice: {img_path} not found, searching staging...")
            continue
            
        print(f"\nSegmenting [{coll_name}] Folio: {img_path.name} ({img_path})...")
        lines, _ = segmenter.segment_horizontal_projection(img_path, prep_variant="clahe")
        
        # Crop lines to disk
        folio_crop_dir = auto_lines_dir / coll_name.lower() / img_path.stem
        crops = segmenter.crop_lines(img_path, lines, folio_crop_dir, prefix=f"{coll_name.lower()}_{img_path.stem}")
        
        for c in crops:
            c["collection"] = coll_name
            c["source_folio"] = img_path.name
            c["classification"] = "AUTOMATICALLY_SEGMENTED"
            all_thplmd_lines.append(c)
            
        print(f"  Extracted {len(crops)} line crops into {folio_crop_dir}")

        # Generate overlay
        overlay_path = VISUALIZATIONS_DIR / f"THPLMD_{coll_name}_segmentation_overlay.png"
        segmenter.draw_segmentation_overlay(img_path, lines, overlay_path, title=f"THPLMD {coll_name} Lines")

    # Save automatic line manifest CSV
    manifest_csv = auto_lines_dir / "thplmd_automatic_lines.csv"
    if all_thplmd_lines:
        fieldnames = ["collection", "source_folio", "reading_order", "line_id", "crop_filename",
                      "crop_path", "crop_width", "crop_height", "aspect_ratio", "status",
                      "segmentation_method", "classification", "manual_review_required"]
        with open(manifest_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(all_thplmd_lines)
        print(f"\nGenerated THPLMD Automatic Line Manifest: {manifest_csv} ({len(all_thplmd_lines)} line candidates)")

    return all_thplmd_lines

def main():
    cict_res = benchmark_cict_segmentation()
    thplmd_res = process_thplmd_automatic_segmentation()
    print("\nStage 5 Line & Text Region Segmentation Completed Successfully!")

if __name__ == "__main__":
    main()
