# OCR / HTR Model Evaluation & Candidate Selection (Stage 3)

## 1. Executive Summary & Comparison Matrix

| Model Candidate | Architecture | Tamil Support | Line OCR Support | Pretrained Weights | Fine-Tunable via PyTorch | Confidence Output | 6 GB VRAM Suitability | License | Evaluation Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EasyOCR (Tamil)** | CRAFT (Detector) + CRNN / ResNet (Recognizer) | Yes (`ta`) | Yes (Line crops) | Yes (Automatic via PyTorch Hub) | Yes (PyTorch custom training) | Yes (Softmax probabilities) | **Excellent** (~1.2 GB inference) | Apache 2.0 | **Evaluated Zero-Shot** |
| **Indic TrOCR** | Vision Transformer (ViT) + Transformer Decoder | Yes (Indic) | Yes (Line crops) | Yes (Hugging Face Hub) | Yes (PyTorch fp16 / LoRA / Full) | Yes (Token-level Softmax Entropy) | **Good** (~3.8 GB with mixed precision) | Apache 2.0 / MIT | **Selected for Stage 8 Fine-Tuning** |
| **Tesseract OCR (Tamil)**| CNN + LSTM + CTC | Yes (`tam`, `tam_fast`) | Yes (Line & Page) | Yes (Traineddata) | Moderate (Complex Tesstrain pipeline) | Word-level only | **Excellent** (CPU-based) | Apache 2.0 | **Investigated** (External Binary) |
| **PaddleOCR (Tamil)** | DBNet + SVTR / CRNN | Limited / Multi | Yes (Line crops) | Yes | Moderate (PaddlePaddle framework) | Yes | **Good** | Apache 2.0 | **Investigated** |

---

## 2. Detailed Technical Profiles of Evaluated Candidates

### A. EasyOCR (Tamil) — Baseline Inference Benchmark
* **Architecture:** CRAFT text detector paired with ResNet feature extractor, BiLSTM sequence encoder, and CTC decoder.
* **Tamil Compatibility:** Native support via language code `['ta']`.
* **Hardware Footprint:** Minimal VRAM consumption (~1.2 GB during GPU inference), runs with near-instant inference per line on the RTX 4050.
* **Confidence Metric:** Exposes genuine per-token / per-box softmax probabilities.
* **Role in Pipeline:** Serves as the primary fast zero-shot baseline and comparison anchor.

### B. Indic TrOCR (Vision Transformer + Auto-regressive Transformer) — Fine-Tuning Backbone
* **Architecture:** Vision Transformer (ViT) encoder coupled with a language transformer decoder (e.g. `google/trocr` or Indic-adapted variants).
* **Line-Level Sequence Modeling:** Specifically designed for end-to-end line image transcription without requiring individual character segmentation.
* **6 GB VRAM Feasibility:**
  * Base model parameter count: ~220M – ~380M parameters.
  * Mixed precision (`torch.cuda.amp.autocast(dtype=torch.float16)`) and gradient accumulation allows training with batch sizes of 4 to 8 on 6 GB VRAM without out-of-memory errors.
* **Confidence Extraction:** Token-level predictive entropy and beam search log-likelihoods enable genuine, mathematically sound second-pass routing.
* **Role in Pipeline:** Selected as the primary deep architecture for **Stage 8 (Domain Adaptation & Fine-Tuning)**.

### C. Tesseract OCR (Tamil)
* **Architecture:** 1D-LSTM recurrent neural network with CTC decoding.
* **Deployment Characteristics:** Highly standardized C++ binary with `pytesseract` Python wrapper.
* **Limitation for Palm-Leaf Research:** Fine-tuning (`tesstrain`) requires generating synthetic TIFF/box files in a rigid non-PyTorch build system, making custom distortion-aware loss functions and dynamic confidence routing difficult to integrate.

---

## 3. Measurable Technical Selection Decision

### Selected Baseline Model for Next Stages:
**Primary Fine-Tuning Backbone: `Indic TrOCR` / `Vision-Encoder-Decoder (PyTorch)`**
**Fast Baseline & Preprocessing Benchmark: `EasyOCR (Tamil)`**

### Explicit Reasons for Selection:
1. **End-to-End PyTorch Ecosystem:** Both models operate directly in native PyTorch with full CUDA 12.4 acceleration on the RTX 4050.
2. **Line-Level Suitability:** Directly ingest rectangular manuscript line crops (e.g. `2140 × 37` px) without requiring fragile character pre-segmentation.
3. **Genuine Confidence Signal:** Directly yield token-level probability distributions essential for **Stage 9 (Confidence-Based Second-Pass OCR)**.
4. **Permissive Open-Source Licensing:** Both released under Apache 2.0, permitting research adaptation and distribution.
