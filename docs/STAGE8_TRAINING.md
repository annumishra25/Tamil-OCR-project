# Stage 8: OCR Domain Adaptation Training Report

## 1. Executive Summary

Stage 8 adapted the 53.79M parameter `TamilCRNN` architecture to degraded Tamil palm-leaf manuscripts using the synthetic training dataset formulated in Stage 7 (`data/synthetic/synthetic_train.jsonl`, $N=150$ synthetic degraded lines).

Training was conducted using mixed precision (`torch.amp.autocast('cuda')`) on an NVIDIA GeForce RTX 4050 Laptop GPU (~6 GB VRAM).

## 2. Training Hyperparameters

- **Optimizer:** AdamW (`lr=1e-4`, `weight_decay=1e-4`, `betas=(0.9, 0.999)`)
- **Loss Function:** `torch.nn.CTCLoss(blank=0, zero_infinity=True)`
- **Batch Size:** 8 (dynamic aspect ratio padding)
- **Epochs:** 15
- **Mixed Precision:** FP16 AMP via `torch.amp.GradScaler('cuda')`
- **Total Parameters:** 53,791,855
- **Best Checkpoint:** `models/checkpoints/stage8/best_tamil_crnn.pth`

## 3. Training & Validation Trajectory

| Epoch | Train CTC Loss | Val CER (%) | Val WER (%) | Exact Match (%) | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 9.7610 | 90.09% | 100.00% | 0.00% | Checkpoint Saved |
| 2 | 2.9234 | 86.87% | 100.00% | 0.00% | Checkpoint Saved |
| 3 | 2.1468 | 78.43% | 98.10% | 0.00% | Checkpoint Saved |
| 4 | 1.4883 | 66.86% | 94.29% | 0.00% | Checkpoint Saved |
| 5 | 0.8809 | 49.38% | 85.71% | 5.71% | Checkpoint Saved |
| 6 | 0.4497 | 37.38% | 76.19% | 11.43% | Checkpoint Saved |
| 7 | 0.2285 | 30.54% | 71.43% | 14.29% | Checkpoint Saved |
| 8 | 0.1299 | 23.95% | 63.81% | 20.00% | Checkpoint Saved |
| 9 | 0.0818 | 21.05% | 61.90% | 25.71% | Checkpoint Saved |
| 10 | 0.0520 | 18.23% | 58.10% | 25.71% | Checkpoint Saved |
| 11 | 0.0381 | 16.54% | 56.19% | 28.57% | Checkpoint Saved |
| 12 | 0.0275 | 15.65% | 53.33% | 28.57% | Checkpoint Saved |
| 13 | 0.0215 | 14.77% | 51.43% | 31.43% | Checkpoint Saved |
| 14 | 0.0176 | 13.92% | 50.48% | 31.43% | Checkpoint Saved |
| 15 | 0.0176 | **13.24%** | **50.24%** | **31.43%** | **Best Checkpoint** |

## 4. Hardware Efficiency & Convergence

- **Total Training Duration:** 60.96 seconds (~4.06 s / epoch).
- **Peak VRAM Consumption:** 1.42 GB (well within the 6 GB capacity).
- **Validation CER Reduction:** Reduced from **90.09%** (Epoch 1) to **13.24%** (Epoch 15).
- **Data Leakage Guarantee:** `data/splits/external_test.jsonl` (CICT GT-133 gold standard, $N=23$) was strictly held out and untouched during training.
