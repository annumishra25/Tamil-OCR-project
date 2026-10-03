"""
Stage 8 Evaluation Matrix & Benchmarking Engine
Stage 8 Model Domain Adaptation

Evaluates Baseline vs Fine-Tuned OCR across:
1. Synthetic Validation (35 samples)
2. Synthetic Test (35 samples)
3. Real CICT Gold-Standard External Test (23 verified lines)
with and without manuscript preprocessing.
"""

import sys
import os
import time
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import torch
from torch.utils.data import DataLoader
from PIL import Image

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
sys.path.append(str(PROJECT_ROOT))

from src.ocr.processor import TamilOCRProcessor
from src.ocr.dataset import TamilLineDataset, collate_tamil_lines
from src.ocr.model_loader import load_tamil_crnn_model
from src.evaluation.metrics import calculate_cer, calculate_wer, normalize_tamil_text
from src.preprocessing.pipeline import PreprocessingPipeline

METRICS_DIR = PROJECT_ROOT / "results" / "metrics"
PREDICTIONS_DIR = PROJECT_ROOT / "results" / "predictions"
CHECKPOINTS_DIR = PROJECT_ROOT / "models" / "checkpoints" / "stage8"


class Stage8Evaluator:
    def __init__(
        self,
        checkpoint_path: Optional[Path] = None,
        device: Optional[torch.device] = None
    ):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = checkpoint_path
        self.model, self.processor, _ = load_tamil_crnn_model(checkpoint_path=self.checkpoint_path, device=self.device)
        self.model.eval()
        self.pipeline_engine = PreprocessingPipeline()

        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)

    def evaluate_dataset(
        self,
        jsonl_path: Path,
        dataset_name: str,
        apply_preprocessing: bool = False,
        preprocessing_pipeline: str = "pipeline_c_illum_clahe"
    ) -> Dict[str, Any]:
        """
        Runs evaluation on a specified JSONL split.
        """
        if not jsonl_path.exists():
            raise FileNotFoundError(f"Split file not found: {jsonl_path}")

        records = []
        with open(jsonl_path, mode='r', encoding='utf-8') as f:
            for l in f:
                if l.strip():
                    records.append(json.loads(l.strip()))

        predictions = []
        latencies = []
        t_start_total = time.time()

        for rec in records:
            img_rel = rec.get("image_path")
            img_path = PROJECT_ROOT / img_rel if not os.path.isabs(img_rel) else Path(img_rel)

            if not img_path.exists():
                continue

            img_pil = Image.open(img_path).convert("RGB")
            
            # Apply preprocessing if requested
            if apply_preprocessing:
                img_np = np.array(img_pil)
                prep_np, _ = self.pipeline_engine.run_pipeline(img_np, pipeline_key=preprocessing_pipeline)
                img_pil = Image.fromarray(prep_np)

            # Process tensor
            t_sample_start = time.time()
            tensor = self.processor.process_image(img_pil).unsqueeze(0).to(self.device)

            with torch.no_grad():
                if self.device.type == "cuda":
                    with torch.amp.autocast('cuda', dtype=torch.float16):
                        log_probs = self.model(tensor)
                else:
                    log_probs = self.model(tensor)

                decoded = self.model.decode_predictions(log_probs, self.processor)[0]

            latency_ms = (time.time() - t_sample_start) * 1000.0
            latencies.append(latency_ms)

            gt_text = rec.get("normalized_transcription") or rec.get("transcription", "")
            pred_text = decoded["transcription"]

            cer = calculate_cer(gt_text, pred_text)
            wer = calculate_wer(gt_text, pred_text)
            exact = (gt_text == pred_text)

            predictions.append({
                "sample_id": rec.get("sample_id"),
                "dataset": dataset_name,
                "ground_truth": gt_text,
                "prediction": pred_text,
                "cer": round(cer, 4),
                "wer": round(wer, 4),
                "exact_match": exact,
                "confidence": decoded["confidence"],
                "latency_ms": round(latency_ms, 2),
                "image_path": str(img_rel)
            })

        total_time = time.time() - t_start_total
        mean_cer = float(np.mean([p["cer"] for p in predictions])) if predictions else 1.0
        mean_wer = float(np.mean([p["wer"] for p in predictions])) if predictions else 1.0
        exact_pct = (sum(1 for p in predictions if p["exact_match"]) / len(predictions) * 100.0) if predictions else 0.0
        mean_lat = float(np.mean(latencies)) if latencies else 0.0

        return {
            "dataset_name": dataset_name,
            "sample_count": len(predictions),
            "mean_cer": round(mean_cer, 4),
            "mean_wer": round(mean_wer, 4),
            "exact_match_pct": round(exact_pct, 2),
            "mean_latency_ms": round(mean_lat, 2),
            "total_inference_sec": round(total_time, 2),
            "preprocessing": preprocessing_pipeline if apply_preprocessing else "None (Raw)",
            "predictions": predictions
        }


def run_full_evaluation_matrix() -> List[Dict[str, Any]]:
    print("\n=======================================================")
    print("--- Stage 8: Running Full Experiment Evaluation Matrix ---")
    print("=======================================================")

    best_ckpt = CHECKPOINTS_DIR / "best_tamil_crnn.pth"
    synth_val = PROJECT_ROOT / "data" / "synthetic" / "synthetic_val.jsonl"
    synth_test = PROJECT_ROOT / "data" / "synthetic" / "synthetic_test.jsonl"
    cict_ext_test = PROJECT_ROOT / "data" / "splits" / "external_test.jsonl"

    matrix_results = []
    all_prediction_rows = []

    # Experiment A: Baseline Pretrained (Zero-Shot) on Synthetic Test
    print("\n[Exp A] Evaluating Pretrained Baseline (Zero-Shot) on Synthetic Test...")
    eval_baseline = Stage8Evaluator(checkpoint_path=None)
    res_a = eval_baseline.evaluate_dataset(synth_test, "Synthetic Test (35 Lines)", apply_preprocessing=False)
    res_a["experiment_id"] = "EXP-8A"
    res_a["model"] = "Pretrained Baseline (EasyOCR Tamil CRNN)"
    matrix_results.append(res_a)
    all_prediction_rows.extend(res_a["predictions"])

    # Experiment B: Baseline Pretrained on CICT Real Manuscript Gold Standard
    print("[Exp B] Evaluating Pretrained Baseline on CICT GT-133 External Test (23 Verified Lines)...")
    res_b = eval_baseline.evaluate_dataset(cict_ext_test, "CICT GT-133 Real External Test (N=23)", apply_preprocessing=False)
    res_b["experiment_id"] = "EXP-8B"
    res_b["model"] = "Pretrained Baseline (EasyOCR Tamil CRNN)"
    matrix_results.append(res_b)
    all_prediction_rows.extend(res_b["predictions"])

    # Experiment C: Fine-Tuned Model on Synthetic Test (Raw)
    if best_ckpt.exists():
        print(f"\n[Exp C] Evaluating Fine-Tuned Model ({best_ckpt.name}) on Synthetic Test...")
        eval_finetuned = Stage8Evaluator(checkpoint_path=best_ckpt)
        res_c = eval_finetuned.evaluate_dataset(synth_test, "Synthetic Test (35 Lines)", apply_preprocessing=False)
        res_c["experiment_id"] = "EXP-8C"
        res_c["model"] = "Fine-Tuned Tamil CRNN (Stage 8 Best Checkpoint)"
        matrix_results.append(res_c)
        all_prediction_rows.extend(res_c["predictions"])

        # Experiment D: Fine-Tuned Model on CICT Real Gold Standard
        print("[Exp D] Evaluating Fine-Tuned Model on CICT GT-133 Real External Test (N=23)...")
        res_d = eval_finetuned.evaluate_dataset(cict_ext_test, "CICT GT-133 Real External Test (N=23)", apply_preprocessing=False)
        res_d["experiment_id"] = "EXP-8D"
        res_d["model"] = "Fine-Tuned Tamil CRNN (Stage 8 Best Checkpoint)"
        matrix_results.append(res_d)
        all_prediction_rows.extend(res_d["predictions"])

        # Experiment E: Fine-Tuned Model + Preprocessing Pipeline C on CICT Real Gold Standard
        print("[Exp E] Evaluating Fine-Tuned Model + Preprocessing Pipeline C on CICT GT-133 (N=23)...")
        res_e = eval_finetuned.evaluate_dataset(cict_ext_test, "CICT GT-133 Real External Test (N=23)", apply_preprocessing=True, preprocessing_pipeline="pipeline_c_illum_clahe")
        res_e["experiment_id"] = "EXP-8E"
        res_e["model"] = "Fine-Tuned Tamil CRNN + Pipeline C (Illum Norm + CLAHE)"
        matrix_results.append(res_e)
        all_prediction_rows.extend(res_e["predictions"])

    # Save Summary Matrix CSV
    matrix_csv = METRICS_DIR / "stage8_evaluation_matrix.csv"
    fieldnames = [
        "experiment_id", "model", "dataset_name", "sample_count",
        "preprocessing", "mean_cer", "mean_wer", "exact_match_pct",
        "mean_latency_ms", "total_inference_sec"
    ]
    with open(matrix_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(matrix_results)

    # Save Summary Matrix JSON
    with open(METRICS_DIR / "stage8_evaluation_matrix.json", mode='w', encoding='utf-8') as f:
        json.dump(matrix_results, f, indent=2, ensure_ascii=False)

    # Save Predictions Log CSV
    pred_csv = PREDICTIONS_DIR / "stage8_predictions.csv"
    if all_prediction_rows:
        p_fieldnames = list(all_prediction_rows[0].keys())
        with open(pred_csv, mode='w', newline='', encoding='utf-8') as f:
            p_writer = csv.DictWriter(f, fieldnames=p_fieldnames)
            p_writer.writeheader()
            p_writer.writerows(all_prediction_rows)

    print(f"\nSaved Evaluation Matrix: {matrix_csv}")
    print(f"Saved Detailed Predictions: {pred_csv}")

    return matrix_results


if __name__ == "__main__":
    run_full_evaluation_matrix()
