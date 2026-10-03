"""
Tamil Palm-Leaf OCR Training & Domain Adaptation Pipeline
Stage 8 Model Domain Adaptation

Features:
- CTCLoss training with PyTorch AMP (Automatic Mixed Precision - fp16)
- Gradient accumulation and gradient clipping
- Validation evaluation loop tracking CER & WER
- Strict isolation: CICT external_test is NEVER touched during training
- Checkpoint persistence and metadata logging
"""

import sys
import os
import argparse
import time
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
sys.path.append(str(PROJECT_ROOT))

from src.ocr.processor import TamilOCRProcessor
from src.ocr.dataset import TamilLineDataset, collate_tamil_lines
from src.ocr.crnn_model import TamilCRNN
from src.ocr.model_loader import load_tamil_crnn_model
from src.evaluation.metrics import calculate_cer, calculate_wer


def train_one_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.CTCLoss,
    scaler: Optional[torch.cuda.amp.GradScaler],
    device: torch.device,
    grad_accum_steps: int = 1,
    grad_clip: float = 5.0
) -> float:
    model.train()
    total_loss = 0.0
    num_batches = 0
    optimizer.zero_grad()

    for step, batch in enumerate(dataloader):
        images = batch["images"].to(device)
        targets = batch["targets"].to(device)
        input_lengths = batch["input_lengths"].to(device)
        target_lengths = batch["target_lengths"].to(device)

        if len(targets) == 0:
            continue

        if scaler is not None and device.type == "cuda":
            with torch.amp.autocast('cuda', dtype=torch.float16):
                # Forward pass: log_probs shape (T, B, C)
                log_probs = model(images)
                loss = criterion(log_probs, targets, input_lengths, target_lengths)
                loss = loss / grad_accum_steps

            scaler.scale(loss).backward()

            if (step + 1) % grad_accum_steps == 0 or (step + 1) == len(dataloader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
        else:
            log_probs = model(images)
            loss = criterion(log_probs, targets, input_lengths, target_lengths)
            loss = loss / grad_accum_steps
            loss.backward()

            if (step + 1) % grad_accum_steps == 0 or (step + 1) == len(dataloader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                optimizer.step()
                optimizer.zero_grad()

        total_loss += loss.item() * grad_accum_steps
        num_batches += 1

    return total_loss / max(1, num_batches)


def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    processor: TamilOCRProcessor,
    device: torch.device
) -> Dict[str, Any]:
    model.eval()
    all_cers = []
    all_wers = []
    total_samples = 0
    predictions_log = []

    with torch.no_grad():
        for batch in dataloader:
            images = batch["images"].to(device)
            ground_truths = batch["texts"]
            sample_ids = batch["sample_ids"]

            if device.type == "cuda":
                with torch.amp.autocast('cuda', dtype=torch.float16):
                    log_probs = model(images)
            else:
                log_probs = model(images)

            decoded = model.decode_predictions(log_probs, processor)

            for i, dec in enumerate(decoded):
                gt = ground_truths[i]
                pred = dec["transcription"]
                cer = calculate_cer(gt, pred)
                wer = calculate_wer(gt, pred)
                all_cers.append(cer)
                all_wers.append(wer)
                total_samples += 1

                predictions_log.append({
                    "sample_id": sample_ids[i],
                    "ground_truth": gt,
                    "prediction": pred,
                    "cer": round(cer, 4),
                    "wer": round(wer, 4),
                    "confidence": dec["confidence"]
                })

    mean_cer = float(np.mean(all_cers)) if all_cers else 1.0
    mean_wer = float(np.mean(all_wers)) if all_wers else 1.0

    return {
        "mean_cer": round(mean_cer, 4),
        "mean_wer": round(mean_wer, 4),
        "total_samples": total_samples,
        "predictions": predictions_log
    }


def run_training(config_path: Path, is_smoke: bool = False) -> Dict[str, Any]:
    print("\n=======================================================")
    print(f"--- Stage 8: {'SMOKE TEST' if is_smoke else 'FINE-TUNING'} OCR MODEL ---")
    print("=======================================================")

    with open(config_path, mode='r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    seed = cfg.get("seed", 42)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    train_jsonl = PROJECT_ROOT / cfg["paths"]["train_jsonl"]
    val_jsonl = PROJECT_ROOT / cfg["paths"]["val_jsonl"]
    ckpt_dir = PROJECT_ROOT / cfg["paths"]["checkpoint_dir"]
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    max_train = cfg["training"].get("max_train_samples") if is_smoke else None
    max_val = cfg["training"].get("max_val_samples") if is_smoke else None

    # Load model and processor
    model, processor, device = load_tamil_crnn_model(vocab_size=cfg.get("vocab_size", 142))
    print(f"Using device: {device} ({torch.cuda.get_device_name(0) if device.type == 'cuda' else 'CPU'})")

    train_ds = TamilLineDataset(train_jsonl, processor=processor, max_samples=max_train)
    val_ds = TamilLineDataset(val_jsonl, processor=processor, max_samples=max_val)

    batch_size = cfg["training"].get("batch_size", 4)
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_tamil_lines,
        num_workers=0
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_tamil_lines,
        num_workers=0
    )

    print(f"Loaded {len(train_ds)} training samples and {len(val_ds)} validation samples.")

    epochs = cfg["training"].get("epochs", 2 if is_smoke else 15)
    lr = cfg["training"].get("learning_rate", 3e-4)
    grad_accum = cfg["training"].get("gradient_accumulation_steps", 1)
    fp16 = cfg["training"].get("fp16", True) and (device.type == "cuda")

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=cfg["training"].get("weight_decay", 1e-4))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    criterion = nn.CTCLoss(blank=0, zero_infinity=True)
    scaler = torch.amp.GradScaler('cuda') if fp16 else None

    best_val_cer = 999.0
    best_checkpoint_path = ckpt_dir / "best_tamil_crnn.pth"
    history = []
    t0 = time.time()

    for epoch in range(1, epochs + 1):
        t_epoch_start = time.time()
        train_loss = train_one_epoch(
            model=model,
            dataloader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            scaler=scaler,
            device=device,
            grad_accum_steps=grad_accum
        )
        scheduler.step()

        # Evaluate on validation partition
        val_metrics = evaluate_model(model, val_loader, processor, device)
        epoch_sec = time.time() - t_epoch_start

        epoch_record = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_cer": val_metrics["mean_cer"],
            "val_wer": val_metrics["mean_wer"],
            "lr": round(scheduler.get_last_lr()[0], 6),
            "epoch_seconds": round(epoch_sec, 2)
        }
        history.append(epoch_record)

        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val CER: {val_metrics['mean_cer']*100:.2f}% | "
            f"Val WER: {val_metrics['mean_wer']*100:.2f}% | "
            f"Time: {epoch_sec:.2f}s"
        )

        # Save best model
        if val_metrics["mean_cer"] < best_val_cer:
            best_val_cer = val_metrics["mean_cer"]
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_cer": best_val_cer,
                "val_wer": val_metrics["mean_wer"],
                "vocab_size": cfg.get("vocab_size", 142),
                "seed": seed,
                "config": cfg
            }, best_checkpoint_path)
            print(f"  -> Saved new best checkpoint: {best_checkpoint_path} (CER: {best_val_cer*100:.2f}%)")

    total_time = time.time() - t0
    print(f"\nTraining completed in {total_time:.2f}s. Best Validation CER: {best_val_cer*100:.2f}%")

    # Save training report
    exp_dir = PROJECT_ROOT / "experiments" / "finetuning"
    exp_dir.mkdir(parents=True, exist_ok=True)
    report_file = exp_dir / ("smoke_test_report.json" if is_smoke else "training_report.json")

    report_data = {
        "status": "COMPLETED",
        "is_smoke": is_smoke,
        "epochs": epochs,
        "best_val_cer": best_val_cer,
        "best_checkpoint_path": str(best_checkpoint_path.relative_to(PROJECT_ROOT).as_posix()),
        "total_training_seconds": round(total_time, 2),
        "history": history,
        "gpu_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    }

    with open(report_file, mode='w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

    return report_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/ocr/stage8_train.yaml")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    cfg_p = PROJECT_ROOT / ("configs/ocr/stage8_smoke.yaml" if args.smoke else args.config)
    run_training(cfg_p, is_smoke=args.smoke)
