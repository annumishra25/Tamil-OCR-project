"""
Evaluate Preprocessing Pipeline Variations on CICT-PLM-GT-133 Lines
Stage 4 Preprocessing Benchmarking
"""

import sys
import os
import csv
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

from src.evaluation.metrics import normalize_tamil_text, calculate_cer, calculate_wer
from src.preprocessing.pipeline import PreprocessingPipeline, DEFAULT_PIPELINES

CICT_LINES_CSV = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
OUTPUT_CSV = METRICS_DIR / "preprocessing_results.csv"

def load_cict_lines():
    lines = []
    with open(CICT_LINES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            lines.append(r)
    return lines

def evaluate_preprocessing_pipelines():
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    lines = load_cict_lines()
    print(f"Loaded {len(lines)} gold-standard lines for preprocessing benchmarking.")

    # Initialize EasyOCR Reader
    try:
        import easyocr
        import easyocr.config as cfg
        import torch
        
        # Patch EasyOCR tamil_g1 character list to match 143-class tamil.pth weights
        full_tamil_chars = '0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZஃஅஆஇஈஉஊஎஏஐஒஓஔகஙசஜஞடணதநனபமயரறலளழவஷஸஹாிீுூெேைொோௌ்'
        cfg.recognition_models['gen1']['tamil_g1']['characters'] = full_tamil_chars

        gpu_ready = torch.cuda.is_available()
        print(f"Initializing EasyOCR Reader (gpu={gpu_ready})...")
        reader = easyocr.Reader(['ta'], gpu=gpu_ready, verbose=False)
    except Exception as e:
        print(f"Error initializing OCR engine: {e}")
        return None

    pipeline_engine = PreprocessingPipeline()
    pipelines_to_test = [
        ("raw", "Raw Unprocessed"),
        ("grayscale", "Standard Grayscale"),
        ("pipeline_a_clahe", "Pipeline A (CLAHE)"),
        ("pipeline_b_denoise_clahe", "Pipeline B (Bilateral + CLAHE)"),
        ("pipeline_c_illum_clahe", "Pipeline C (Illumination Norm + CLAHE)"),
        ("pipeline_d_sauvola_deskew", "Pipeline D (Sauvola + Deskew)"),
        ("pipeline_e_master_adaptive", "Pipeline E (Master Adaptive)")
    ]

    all_results = []
    pipeline_summaries = []

    for p_key, p_name in pipelines_to_test:
        print(f"\n--- Testing Preprocessing: {p_name} ({p_key}) ---")
        total_cer, total_wer, total_time = 0.0, 0.0, 0.0
        line_count = 0

        for line in lines:
            img_path = PROJECT_ROOT / line["image_path"]
            ref_text = line["transcription"]
            line_id = line["line_id"]
            
            orig_bgr = cv2.imread(str(img_path))
            t0 = time.time()
            if p_key == "raw":
                processed_img = orig_bgr
            else:
                processed_img, _ = pipeline_engine.run_pipeline(orig_bgr, p_key)

            # OCR Inference
            try:
                ocr_res = reader.readtext(processed_img, detail=1)
                t_elapsed = time.time() - t0
                pred_texts = [r[1] for r in ocr_res]
                raw_pred = " ".join(pred_texts).strip()
            except Exception as e:
                t_elapsed = time.time() - t0
                raw_pred = ""

            norm_pred = normalize_tamil_text(raw_pred)
            norm_ref = normalize_tamil_text(ref_text)
            cer = calculate_cer(norm_ref, norm_pred)
            wer = calculate_wer(norm_ref, norm_pred)

            record = {
                "line_id": line_id,
                "pipeline_key": p_key,
                "pipeline_name": p_name,
                "reference_text": ref_text,
                "normalized_reference": norm_ref,
                "raw_prediction": raw_pred,
                "normalized_prediction": norm_pred,
                "cer": round(cer, 4),
                "wer": round(wer, 4),
                "processing_time_sec": round(t_elapsed, 4)
            }
            all_results.append(record)
            total_cer += cer
            total_wer += wer
            total_time += t_elapsed
            line_count += 1

        mean_cer = total_cer / line_count if line_count else 1.0
        mean_wer = total_wer / line_count if line_count else 1.0
        mean_time = total_time / line_count if line_count else 0.0

        summary = {
            "pipeline_key": p_key,
            "pipeline_name": p_name,
            "lines_evaluated": line_count,
            "mean_cer": round(mean_cer, 4),
            "mean_wer": round(mean_wer, 4),
            "mean_time_sec": round(mean_time, 4)
        }
        pipeline_summaries.append(summary)
        print(f"  Summary -> Mean CER: {mean_cer*100:.2f}% | Mean WER: {mean_wer*100:.2f}% | Mean Time: {mean_time:.3f}s")

    # Save detailed per-line results
    if all_results:
        keys = list(all_results[0].keys())
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\nGenerated Preprocessing Comparison Results: {OUTPUT_CSV}")

    # Save summary JSON
    summary_json_path = METRICS_DIR / "preprocessing_summary.json"
    with open(summary_json_path, 'w', encoding='utf-8') as f:
        json.dump({"pipelines": pipeline_summaries}, f, indent=2, ensure_ascii=False)
    print(f"Generated Preprocessing Summary JSON: {summary_json_path}")

    return pipeline_summaries

if __name__ == "__main__":
    evaluate_preprocessing_pipelines()
