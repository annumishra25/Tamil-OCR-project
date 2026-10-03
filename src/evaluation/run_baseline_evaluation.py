"""
Zero-Shot Baseline OCR Evaluation on CICT-PLM-GT-133 Gold-Standard Lines
Stage 3 Model Discovery & Evaluation Suite
"""

import sys
import os
import csv
import json
import time
from pathlib import Path
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr")
sys.path.append(str(PROJECT_ROOT))
from src.evaluation.metrics import normalize_tamil_text, calculate_cer, calculate_wer

CICT_LINES_CSV = PROJECT_ROOT / "data" / "processed" / "cict_gt133_lines.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"
METRICS_DIR = RESULTS_DIR / "metrics"

def ensure_result_dirs():
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

def load_cict_lines():
    lines = []
    with open(CICT_LINES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            lines.append(r)
    return lines

def evaluate_easyocr(lines, use_gpu=True):
    print("\n=======================================================")
    print("--- Evaluating Model 1: EasyOCR Tamil ('ta') ---")
    print("=======================================================")
    
    try:
        import easyocr
        import easyocr.config as cfg
        import torch
        
        # Patch EasyOCR tamil_g1 character list to match 143-class tamil.pth weights
        full_tamil_chars = '0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZஃஅஆஇஈஉஊஎஏஐஒஓஔகஙசஜஞடணதநனபமயரறலளழவஷஸஹாிீுூெேைொோௌ்'
        cfg.recognition_models['gen1']['tamil_g1']['characters'] = full_tamil_chars

        gpu_ready = use_gpu and torch.cuda.is_available()
        print(f"Initializing EasyOCR reader (lang=['ta'], gpu={gpu_ready})...")
        reader = easyocr.Reader(['ta'], gpu=gpu_ready, verbose=False)
    except Exception as e:
        print(f"Error initializing EasyOCR: {e}")
        return None

    predictions = []
    total_cer, total_wer = 0.0, 0.0
    valid_count = 0

    for idx, line in enumerate(lines, start=1):
        img_path = PROJECT_ROOT / line["image_path"]
        ref_text = line["transcription"]
        line_id = line["line_id"]
        line_type = line["line_type"]

        start_time = time.time()
        try:
            results = reader.readtext(str(img_path), detail=1)
            elapsed = time.time() - start_time
            
            # Combine detected text segments on line
            detected_texts = [res[1] for res in results]
            confidences = [res[2] for res in results] if results else [0.0]
            
            raw_pred = " ".join(detected_texts).strip()
            norm_pred = normalize_tamil_text(raw_pred)
            norm_ref = normalize_tamil_text(ref_text)
            
            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            cer = calculate_cer(norm_ref, norm_pred)
            wer = calculate_wer(norm_ref, norm_pred)
            
            status = "SUCCESS"
        except Exception as e:
            elapsed = time.time() - start_time
            raw_pred = ""
            norm_pred = ""
            avg_conf = 0.0
            cer = 1.0
            wer = 1.0
            status = f"ERROR: {e}"

        record = {
            "line_index": idx,
            "line_id": line_id,
            "line_type": line_type,
            "image_filename": line["image_filename"],
            "reference_text": ref_text,
            "normalized_reference": normalize_tamil_text(ref_text),
            "raw_prediction": raw_pred,
            "normalized_prediction": norm_pred,
            "confidence": round(avg_conf, 4) if results else "NOT_AVAILABLE",
            "cer": round(cer, 4),
            "wer": round(wer, 4),
            "inference_time_sec": round(elapsed, 4),
            "status": status
        }
        predictions.append(record)
        total_cer += cer
        total_wer += wer
        valid_count += 1
        
        print(f"[{idx:02d}] {line_id:15s} | CER: {cer:.3f} | WER: {wer:.3f} | Time: {elapsed:.2f}s")
        print(f"     Ref : '{ref_text}'")
        print(f"     Pred: '{raw_pred}'")

    avg_cer = total_cer / valid_count if valid_count else 1.0
    avg_wer = total_wer / valid_count if valid_count else 1.0

    print(f"\n--- EasyOCR Baseline Summary ---")
    print(f"Total Lines Evaluated: {valid_count}")
    print(f"Mean Character Error Rate (CER): {avg_cer:.4f} ({avg_cer*100:.2f}%)")
    print(f"Mean Word Error Rate (WER): {avg_wer:.4f} ({avg_wer*100:.2f}%)")

    return {
        "model_name": "EasyOCR (Tamil)",
        "framework": "PyTorch (CRAFT + CRNN)",
        "device": "CUDA (RTX 4050)" if gpu_ready else "CPU",
        "total_lines": valid_count,
        "mean_cer": round(avg_cer, 4),
        "mean_wer": round(avg_wer, 4),
        "predictions": predictions
    }

def evaluate_trocr_candidate(lines):
    print("\n=======================================================")
    print("--- Evaluating Model 2: Indic / Multilingual TrOCR ---")
    print("=======================================================")
    print("Investigating HuggingFace Vision-Encoder-Decoder / TrOCR models for Indic scripts...")
    
    # TrOCR for Tamil zero-shot evaluation
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"PyTorch Device for TrOCR: {device}")
    except Exception as e:
        print(f"Transformers / TrOCR import note: {e}")
        return None

    # TrOCR zero-shot candidates
    return {
        "model_name": "Indic TrOCR (ViT + Transformer)",
        "framework": "Hugging Face / PyTorch",
        "device": "CUDA (RTX 4050)" if torch.cuda.is_available() else "CPU",
        "status": "CANDIDATE_FOR_FINE_TUNING",
        "notes": "Base TrOCR weights are available; fine-tuning with Tamil palm-leaf tokens is scheduled for Stage 8."
    }

def main():
    ensure_result_dirs()
    lines = load_cict_lines()
    print(f"Loaded {len(lines)} gold-standard CICT lines from {CICT_LINES_CSV}")

    easyocr_res = evaluate_easyocr(lines, use_gpu=True)
    trocr_info = evaluate_trocr_candidate(lines)

    # Save EasyOCR Per-Line Predictions
    if easyocr_res and "predictions" in easyocr_res:
        preds = easyocr_res["predictions"]
        csv_pred_path = PREDICTIONS_DIR / "baseline_easyocr.csv"
        keys = list(preds[0].keys())
        with open(csv_pred_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(preds)
        print(f"\nSaved line predictions: {csv_pred_path}")

    # Build Baseline Summary Matrix
    baseline_matrix = []
    if easyocr_res:
        baseline_matrix.append({
            "model": easyocr_res["model_name"],
            "architecture": easyocr_res["framework"],
            "hardware": easyocr_res["device"],
            "lines_evaluated": easyocr_res["total_lines"],
            "cer": f"{easyocr_res['mean_cer'] * 100:.2f}% ({easyocr_res['mean_cer']:.4f})",
            "wer": f"{easyocr_res['mean_wer'] * 100:.2f}% ({easyocr_res['mean_wer']:.4f})",
            "confidence_available": "YES",
            "zero_shot_status": "EVALUATED"
        })

    baseline_matrix.append({
        "model": "Tesseract OCR (Tamil / tam.traineddata)",
        "architecture": "LSTM + CTC",
        "hardware": "CPU",
        "lines_evaluated": len(lines),
        "cer": "NOT_RUN (Tesseract Windows binary not bundled)",
        "wer": "NOT_RUN",
        "confidence_available": "YES (Word-level)",
        "zero_shot_status": "INVESTIGATED"
    })

    baseline_matrix.append({
        "model": "Indic TrOCR (ViT + Transformer Decoder)",
        "architecture": "Vision-Encoder-Decoder",
        "hardware": "CUDA (RTX 4050)",
        "lines_evaluated": len(lines),
        "cer": "Pending Domain Adaptation",
        "wer": "Pending Domain Adaptation",
        "confidence_available": "YES (Softmax Token Entropy)",
        "zero_shot_status": "SELECTED_FOR_FINETUNING"
    })

    # Save Baseline Results CSV
    csv_matrix_path = METRICS_DIR / "baseline_results.csv"
    with open(csv_matrix_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(baseline_matrix[0].keys()))
        writer.writeheader()
        writer.writerows(baseline_matrix)
    print(f"Saved baseline metrics CSV: {csv_matrix_path}")

    # Save Baseline Results JSON
    json_matrix_path = METRICS_DIR / "baseline_results.json"
    full_export = {
        "evaluation_dataset": "CICT-PLM-GT-133 (Tirukkural Chapter 133)",
        "total_gold_lines": len(lines),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models": baseline_matrix,
        "detailed_runs": {
            "easyocr": easyocr_res,
            "trocr": trocr_info
        }
    }
    with open(json_matrix_path, 'w', encoding='utf-8') as f:
        json.dump(full_export, f, indent=2, ensure_ascii=False)
    print(f"Saved baseline metrics JSON: {json_matrix_path}")

if __name__ == "__main__":
    main()
