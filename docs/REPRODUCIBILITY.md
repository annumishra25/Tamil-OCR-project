# Reproducibility Guide & Execution Runbook

This guide documents the exact end-to-end execution steps to reproduce all dataset formulation, synthetic generation, model fine-tuning, second-pass evaluation, and final benchmarking.

---

## 1. Environment & Hardware Specifications

- **OS:** Windows 10 / 11 64-bit
- **Python:** 3.11.9
- **GPU Accelerator:** NVIDIA GeForce RTX 4050 Laptop GPU (~6 GB VRAM)
- **PyTorch:** `2.6.0+cu124` (CUDA 12.4 active)
- **Random Seeds:** Deterministic random seeds fixed (`seed=42`) across data splitters and synthetic engines.

---

## 2. Step-by-Step Reproduction Workflow

### Step 1: Environment Setup
```powershell
.\.venv\Scripts\Activate.ps1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

### Step 2: Ingestion & Verified Split Formulation (Stage 2 & 6)
```powershell
python src/data/ingest_datasets.py
python src/data/build_safe_splits.py
```

### Step 3: Synthetic Palm-Leaf Degradation Generation (Stage 7)
```powershell
python src/augmentation/generate_synthetic_corpus.py
```

### Step 4: Model Domain Adaptation Fine-Tuning (Stage 8)
```powershell
python src/ocr/train.py --config configs/ocr/stage8_train.yaml
```

### Step 5: Confidence Second Pass & Post-Correction Evaluation (Stage 9)
```powershell
python src/confidence/run_stage9_evaluation.py
```

### Step 6: Final 6-Way Benchmark (Stage 10)
```powershell
python src/evaluation/run_final_evaluation.py
```

### Step 7: Run Complete Test Suite
```powershell
python -m unittest discover -s tests
```

### Step 8: Launch API Server and Interactive Frontend
```powershell
# Start FastAPI backend:
python -m uvicorn src.api.server:app --port 8000

# Start Frontend (in separate terminal):
cd app/frontend
npm.cmd run dev
```
Open `http://localhost:5173/` in your browser.
