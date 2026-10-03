# Tamil Palm-Leaf OCR — Model Selection Rationale (Stage 8)

## 1. Selected Base Architecture

- **Architecture:** ResNet-VGG Convolutional Feature Extractor + 2-layer Bidirectional LSTM Sequence Encoder + CTC Linear Projection Head (`TamilCRNN` / `EasyOCR Tamil recognizer`).
- **Total Parameters:** 53,791,855 (~53.79M parameters).
- **Target Platform & Efficiency:** NVIDIA GeForce RTX 4050 Laptop GPU (~6 GB VRAM) running CUDA 12.4 (`torch 2.6.0+cu124`).
- **Input Specification:** Grayscale line image normalized to `(1, 32, W)` where $W \le 800$.
- **Output Specification:** CTC Log-Softmax probability matrix of shape `(T, B, 143)` covering 142 Tamil characters, combining signs, pulli markers, numerals, and 1 CTC blank token (`[CTC_BLANK]`).

## 2. Why an Existing OCR Model Adaptation?

1. **Avoid Reinventing the Wheel:** Developing a custom vision-language transformer or novel optical character recognizer from scratch requires hundreds of thousands of aligned training pairs which are absent for ancient Tamil palm-leaf manuscripts.
2. **Transfer Learning from Modern Tamil:** The official pretrained weights (`tamil.pth`, 53.79M parameters) contain rich topological representations of Tamil glyph geometry, loops, pullis, and ligatures.
3. **Domain Gap Bridging:** By fine-tuning the pretrained weights on synthetic degraded palm-leaf lines (incorporating authentic leaf textures, scratches, fiber striations, fading, and historical orthography), the model bridges the extreme domain gap between clean print and damaged manuscripts.

## 3. Hardware & Memory Footprint

| Component | VRAM Footprint | Training Time (15 Epochs) | Single-Line Inference Latency |
| :--- | :--- | :--- | :--- |
| **TamilCRNN (FP16 AMP)** | ~1.42 GB | 60.96 seconds | 27.20 ms / line |

The memory footprint comfortably fits within the 6 GB VRAM budget of the RTX 4050 Laptop GPU with zero out-of-memory errors.
