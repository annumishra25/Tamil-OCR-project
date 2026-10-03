# Distortion-Aware Tamil Palm-Leaf Manuscript OCR / HTR System

## 1. Project Purpose & Scope

This research project focuses on the **distortion-aware, manuscript-specific adaptation of an existing open-source Tamil OCR/HTR model** to digitize degraded historical Tamil palm-leaf manuscripts.

> **Research Contribution:**
> The objective is *not* to invent a new OCR architecture from scratch. Instead, we adapt existing open-source Indic/Tamil OCR and HTR architectures (such as TrOCR-based or CTC-based systems) to the unique physical degradation of historical Tamil palm-leaf manuscripts through:
> 1. Multi-scale manuscript image quality assessment and adaptive preprocessing.
> 2. Leakage-safe dataset structuring (THPLMD, CICT ground-truth, IIIT Tamil).
> 3. Controlled synthetic physical degradation modeling (scratches, uneven illumination, fading, ink loss, palm-leaf fiber noise).
> 4. Domain adaptation and fine-tuning on consumer-grade hardware (~6 GB VRAM).
> 5. Confidence-based reliability checking with selective second-pass reprocessing.
> 6. Conservative Tamil post-OCR orthographic and Unicode correction.
> 7. Rigorous CER (Character Error Rate) and WER (Word Error Rate) benchmark evaluation.
> 8. A dedicated historical manuscript digitization prototype interface.

---

## 2. Hardware & Environment Requirements

* **Operating System:** Windows 10 / 11 (64-bit)
* **Python Runtime:** Python `3.11.9` (64-bit AMD64)
* **GPU Accelerator:** NVIDIA GeForce RTX 4050 Laptop GPU (or equivalent NVIDIA GPU with Compute Capability >= 8.0)
* **Dedicated VRAM:** 6,141 MiB (~6 GB)
* **System RAM:** 16 GB minimum
* **Driver Version:** NVIDIA Driver >= 550.x (Current: 592.82, CUDA 13.1 driver capability)

---

## 3. Environment Setup & Verification

### Step 1: Activate the Python Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install CUDA-Enabled PyTorch
PyTorch must be installed using the official CUDA 12.4 wheel index:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Step 3: Install Foundational Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Verify CUDA Acceleration
Run the diagnostic command:
```powershell
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"
```
Expected Output:
```text
PyTorch: 2.6.0+cu124 (or 2.x+cu124)
CUDA Available: True
Device: NVIDIA GeForce RTX 4050 Laptop GPU
```

---

## 4. Repository Structure

```text
tamil_palm_ocr/
├── app/                        # Interactive Digitization Laboratory
│   ├── frontend/               # Vite/Vanilla SPA prototype interface
│   │   ├── src/
│   │   │   ├── components/     # UI components (Viewer, Editor, Review, etc.)
│   │   │   ├── pages/          # 9 Stage screens (Dashboard, Upload, Analysis, etc.)
│   │   │   ├── services/       # Mock and real API service adapters
│   │   │   └── styles/         # Manuscript laboratory theme styles
│   │   └── package.json
│   └── backend/                # Future FastAPI/PyTorch inference server
├── data/
│   ├── raw/                    # Immutable source archives (CICT, THPLMD, IIIT)
│   ├── processed/              # Preprocessed stages (grayscale, thresholded, deskewed)
│   ├── annotations/            # Ground truth PAGE XML, line coords, transcriptions
│   ├── synthetic/              # Synthetic clean & degraded training samples
│   └── splits/                 # Leakage-safe folio/manuscript train/val/test splits
├── docs/                       # Research documentation & architecture specs
│   ├── ARCHITECTURE.md         # Pipeline design & technical interfaces
│   ├── DATASETS.md             # Dataset manifest, provenance & licensing
│   ├── FRONTEND.md             # UI design system & component hierarchy
│   └── DEVELOPMENT_STATUS.md   # Current milestone status tracker
├── experiments/                # Experiment configurations and run logs
├── models/
│   ├── pretrained/             # Downloaded baseline model weights
│   ├── checkpoints/            # Intermediate fine-tuning checkpoints
│   └── final/                  # Final adapted models
├── results/
│   ├── predictions/            # OCR predictions per experiment
│   ├── metrics/                # CER/WER benchmark results
│   └── visualizations/         # Error analysis & attention heatmaps
├── src/                        # Core Python ML / Processing Pipeline
│   ├── data/                   # Manifest builders, parsers, split managers
│   ├── preprocessing/          # Denoising, illumination norm, binarization
│   ├── segmentation/           # Text band and line bounding box extractors
│   ├── augmentation/           # Realistic palm-leaf degradation transforms
│   ├── ocr/                    # Baseline & fine-tuned OCR model wrappers
│   ├── confidence/             # Softmax/entropy reliability scoring & 2nd pass
│   ├── correction/             # Rule-based Tamil Unicode orthography cleaner
│   └── evaluation/             # CER / WER calculation engines
├── PROJECT_PLAN.md             # 10-Stage milestone roadmap
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview & quickstart
```

---

## 5. Development Status

| Stage | Milestone | Status | Description |
| :--- | :--- | :--- | :--- |
| **Stage 1** | **Environment & Hardware** | **COMPLETED** | PyTorch CUDA 12.4 enabled, RTX 4050 verified, dependencies defined |
| **Stage 1 (UI)** | **Frontend Laboratory** | **COMPLETED** | 9-Page manuscript digitization UI with mock service layer (localhost:5173) |
| **Stage 2** | **Dataset Ingestion & Manifest** | **COMPLETED** | 158 THPLMD folios ingested, unified JSON/CSV manifest generated |
| **Stage 2.5** | **CICT Image Fetch & Linking** | **COMPLETED** | IIIF image downloaded from Zenodo, 23 verified lines linked |
| **Stage 3** | **OCR Model Selection & Baseline** | **COMPLETED** | Candidate models evaluated, zero-shot baseline benchmarks established |
| **Stage 4** | **Adaptive Preprocessing** | **COMPLETED** | 7 preprocessing pipelines benchmarked (Pipeline C best WER: 115.45%) |
| **Stage 5** | **Line / Band Segmentation** | **COMPLETED** | Projection profile segmentation + 46 THPLMD candidate crops |
| **Stage 6** | **Training Pairs & Splits** | **COMPLETED** | 7,327 items in 5 tiers, zero-leakage split isolation verified |
| **Stage 7** | **Synthetic Degradation** | **COMPLETED** | 220 physical degradation samples generated from authentic classical Tamil |
| **Stage 8** | **Model Domain Adaptation** | **COMPLETED** | 53.79M TamilCRNN fine-tuned (Val CER: 13.24%, 31.4% Exact Match); evaluated |
| **Stage 9** | **Second-Pass & Post-Correction** | **COMPLETED** | Closed-loop confidence routing, multi-candidate selection, conservative Tamil cleaner |
| **Stage 10** | **Final Benchmarking & Integration**| **COMPLETED** | Full EXP-A to EXP-F evaluation, FastAPI backend, end-to-end integration & tests |

---

## 6. How to Run the Frontend Prototype

To run the interactive manuscript digitization UI:

```powershell
cd app/frontend
npm.cmd install
npm.cmd run dev
```
Then open `http://localhost:5173/` in your browser.
