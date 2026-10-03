"""
Stage 9 Comprehensive Evaluation Engine
Benchmarks 3 Conditions across Synthetic Validation, Synthetic Test, and CICT External Test:
- Condition A: Stage 8 First-Pass Model (Raw)
- Condition B: Confidence-Triggered Second Pass Reprocessing
- Condition C: Second Pass + Conservative Tamil Post-Correction

Strictly preserves zero data leakage (CICT external test is never used for tuning).
"""

import sys
import os
import json
import csv
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import yaml
import numpy as np
import torch
from PIL import Image

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
sys.path.append(str(PROJECT_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from src.ocr.crnn_model import TamilCRNN
from src.ocr.processor import TamilOCRProcessor
from src.ocr.model_loader import load_tamil_crnn_model
from src.confidence.second_pass import SecondPassRouter, SecondPassResult
from src.evaluation.metrics import calculate_cer, calculate_wer


def load_yaml_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dataset_samples(jsonl_path: Path) -> List[Dict[str, Any]]:
    samples = []
    if not jsonl_path.exists():
        print(f"Warning: Dataset not found at {jsonl_path}")
        return samples
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))
    return samples


def evaluate_dataset_across_conditions(
    router: SecondPassRouter,
    samples: List[Dict[str, Any]],
    dataset_label: str
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Evaluates dataset across Condition A (First Pass), Condition B (Second Pass), Condition C (Post-Corrected).
    """
    detailed_rows = []

    cer_a_list, wer_a_list, exact_a_list = [], [], []
    cer_b_list, wer_b_list, exact_b_list = [], [], []
    cer_c_list, wer_c_list, exact_c_list = [], [], []

    reprocessed_count = 0
    improved_count = 0
    worsened_count = 0
    review_required_count = 0
    correction_count = 0
    latencies_ms = []

    for idx, item in enumerate(samples):
        # Resolve image path
        img_rel = item.get("image_path") or item.get("line_image_path") or item.get("processed_path")
        img_full = PROJECT_ROOT / img_rel if not Path(img_rel).is_absolute() else Path(img_rel)

        source_id = item.get("source_id") or item.get("source_folio_id", f"SAMPLE_{idx:04d}")
        line_id = item.get("line_id", f"LINE_{idx:03d}")
        gt_text = item.get("transcription") or item.get("ground_truth_text", "")

        t0 = time.perf_counter()
        res: SecondPassResult = router.process_line(
            img_input=img_full,
            source_id=source_id,
            line_id=line_id
        )
        t1 = time.perf_counter()
        lat_ms = (t1 - t0) * 1000.0
        latencies_ms.append(lat_ms)

        # Condition A: First pass text
        text_a = res.first_pass_text
        cer_a = calculate_cer(gt_text, text_a)
        wer_a = calculate_wer(gt_text, text_a)
        exact_a = (text_a == gt_text)
        cer_a_list.append(cer_a)
        wer_a_list.append(wer_a)
        exact_a_list.append(exact_a)

        # Condition B: Second pass selected text
        text_b = res.selected_text
        cer_b = calculate_cer(gt_text, text_b)
        wer_b = calculate_wer(gt_text, text_b)
        exact_b = (text_b == gt_text)
        cer_b_list.append(cer_b)
        wer_b_list.append(wer_b)
        exact_b_list.append(exact_b)

        # Condition C: Post-corrected text
        text_c = res.corrected_text
        cer_c = calculate_cer(gt_text, text_c)
        wer_c = calculate_wer(gt_text, text_c)
        exact_c = (text_c == gt_text)
        cer_c_list.append(cer_c)
        wer_c_list.append(wer_c)
        exact_c_list.append(exact_c)

        if res.second_pass_triggered:
            reprocessed_count += 1

        if cer_b < cer_a:
            improved_count += 1
        elif cer_b > cer_a:
            worsened_count += 1

        if res.review_required:
            review_required_count += 1

        if len(res.correction_changes) > 0:
            correction_count += 1

        detailed_rows.append({
            "dataset": dataset_label,
            "source_id": source_id,
            "line_id": line_id,
            "ground_truth": gt_text,
            "first_pass_text": text_a,
            "first_pass_confidence": res.first_pass_confidence,
            "cer_condition_a": round(cer_a, 4),
            "wer_condition_a": round(wer_a, 4),
            "second_pass_triggered": res.second_pass_triggered,
            "candidate_preprocessing": " | ".join(res.candidate_preprocessing),
            "candidate_texts": " | ".join(res.candidate_texts),
            "candidate_confidences": " | ".join([f"{c:.4f}" for c in res.candidate_confidences]),
            "selected_text": text_b,
            "selection_reason": res.selection_reason,
            "cer_condition_b": round(cer_b, 4),
            "wer_condition_b": round(wer_b, 4),
            "corrected_text": text_c,
            "correction_changes": json.dumps(res.correction_changes, ensure_ascii=False),
            "cer_condition_c": round(cer_c, 4),
            "wer_condition_c": round(wer_c, 4),
            "review_required": res.review_required,
            "latency_ms": round(lat_ms, 2),
            "image_path": str(img_rel)
        })

    N = max(1, len(samples))
    summary = {
        "dataset_name": dataset_label,
        "sample_count": len(samples),
        # Condition A
        "cond_a_cer": round(float(np.mean(cer_a_list)), 4) if cer_a_list else 0.0,
        "cond_a_wer": round(float(np.mean(wer_a_list)), 4) if wer_a_list else 0.0,
        "cond_a_exact_pct": round(float(np.mean(exact_a_list)) * 100.0, 2) if exact_a_list else 0.0,
        # Condition B
        "cond_b_cer": round(float(np.mean(cer_b_list)), 4) if cer_b_list else 0.0,
        "cond_b_wer": round(float(np.mean(wer_b_list)), 4) if wer_b_list else 0.0,
        "cond_b_exact_pct": round(float(np.mean(exact_b_list)) * 100.0, 2) if exact_b_list else 0.0,
        # Condition C
        "cond_c_cer": round(float(np.mean(cer_c_list)), 4) if cer_c_list else 0.0,
        "cond_c_wer": round(float(np.mean(wer_c_list)), 4) if wer_c_list else 0.0,
        "cond_c_exact_pct": round(float(np.mean(exact_c_list)) * 100.0, 2) if exact_c_list else 0.0,
        # Flow statistics
        "reprocessed_count": reprocessed_count,
        "reprocessed_pct": round((reprocessed_count / N) * 100.0, 2),
        "improved_count": improved_count,
        "improved_pct": round((improved_count / N) * 100.0, 2),
        "worsened_count": worsened_count,
        "worsened_pct": round((worsened_count / N) * 100.0, 2),
        "review_required_count": review_required_count,
        "review_required_pct": round((review_required_count / N) * 100.0, 2),
        "correction_count": correction_count,
        "correction_pct": round((correction_count / N) * 100.0, 2),
        "mean_latency_ms": round(float(np.mean(latencies_ms)), 2) if latencies_ms else 0.0
    }

    return summary, detailed_rows


def run_stage9_benchmark():
    config_path = PROJECT_ROOT / "configs" / "stage9.yaml"
    cfg = load_yaml_config(config_path)

    metrics_dir = PROJECT_ROOT / cfg["evaluation"]["output_dirs"]["metrics"]
    preds_dir = PROJECT_ROOT / cfg["evaluation"]["output_dirs"]["predictions"]
    metrics_dir.mkdir(parents=True, exist_ok=True)
    preds_dir.mkdir(parents=True, exist_ok=True)

    ckpt_path = PROJECT_ROOT / cfg["model"]["checkpoint_path"]
    if not ckpt_path.exists():
        ckpt_path = PROJECT_ROOT / cfg["model"]["pretrained_fallback"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading Stage 8 OCR Model from: {ckpt_path} on {device}...")
    model, processor, device = load_tamil_crnn_model(
        checkpoint_path=ckpt_path,
        device=device,
        vocab_size=cfg["model"]["num_class"]
    )

    router = SecondPassRouter(
        model=model,
        processor=processor,
        device=device,
        confidence_threshold=cfg["confidence"]["configured_threshold"],
        ambiguity_margin=cfg["confidence"]["ambiguity_margin"],
        review_floor=cfg["confidence"]["review_floor"],
        default_pipeline=cfg["reprocessing"]["default_pipeline"],
        candidate_pipelines=cfg["reprocessing"]["candidate_pipelines"]
    )

    datasets_to_eval = [
        ("Synthetic Validation (N=35)", PROJECT_ROOT / cfg["evaluation"]["datasets"]["synthetic_val"]),
        ("Synthetic Test (N=35)", PROJECT_ROOT / cfg["evaluation"]["datasets"]["synthetic_test"]),
        ("CICT GT-133 Real External Test (N=23)", PROJECT_ROOT / cfg["evaluation"]["datasets"]["external_test_cict"])
    ]

    all_summaries = []
    all_predictions = []

    print("\n" + "=" * 70)
    print("--- Running Stage 9 Second Pass & Post-Correction Benchmark ---")
    print("=" * 70)

    for label, path in datasets_to_eval:
        print(f"\n[Evaluating: {label}] (Path: {path})...")
        samples = load_dataset_samples(path)
        if not samples:
            print(f"Skipping empty or missing dataset: {path}")
            continue

        summary, pred_rows = evaluate_dataset_across_conditions(router, samples, label)
        all_summaries.append(summary)
        all_predictions.extend(pred_rows)

        print(f"  Condition A (First Pass):        CER = {summary['cond_a_cer']*100:.2f}%, WER = {summary['cond_a_wer']*100:.2f}%, Exact = {summary['cond_a_exact_pct']:.1f}%")
        print(f"  Condition B (Second Pass):       CER = {summary['cond_b_cer']*100:.2f}%, WER = {summary['cond_b_wer']*100:.2f}%, Exact = {summary['cond_b_exact_pct']:.1f}%")
        print(f"  Condition C (Post-Corrected):    CER = {summary['cond_c_cer']*100:.2f}%, WER = {summary['cond_c_wer']*100:.2f}%, Exact = {summary['cond_c_exact_pct']:.1f}%")
        print(f"  Flow: Reprocessed = {summary['reprocessed_pct']}%, Improved = {summary['improved_pct']}%, Worsened = {summary['worsened_pct']}%, Review = {summary['review_required_pct']}%")

    # Save summary matrix CSV and JSON
    matrix_csv_path = metrics_dir / "stage9_evaluation_matrix.csv"
    matrix_json_path = metrics_dir / "stage9_evaluation_matrix.json"

    if all_summaries:
        keys = all_summaries[0].keys()
        with open(matrix_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_summaries)

        with open(matrix_json_path, "w", encoding="utf-8") as f:
            json.dump(all_summaries, f, indent=2, ensure_ascii=False)

        print(f"\nSaved Stage 9 Summary Matrix: {matrix_csv_path}")

    # Save detailed predictions CSV and JSON
    preds_csv_path = preds_dir / "stage9_predictions.csv"
    preds_json_path = preds_dir / "stage9_predictions.json"

    if all_predictions:
        p_keys = all_predictions[0].keys()
        with open(preds_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=p_keys)
            writer.writeheader()
            writer.writerows(all_predictions)

        with open(preds_json_path, "w", encoding="utf-8") as f:
            json.dump(all_predictions, f, indent=2, ensure_ascii=False)

        print(f"Saved Stage 9 Predictions: {preds_csv_path}")


if __name__ == "__main__":
    run_stage9_benchmark()
