# Stage 9: Confidence Estimation & Second-Pass Reprocessing

## 1. Overview & Research Objective

In degraded Tamil palm-leaf manuscripts, a single static preprocessing pipeline is insufficient because physical degradations (fading, staining, fiber grain, scratches) vary drastically across different folios and lines.

Stage 9 implements a **closed-loop, confidence-triggered quality gate**:
1. Run initial OCR inference with true CTC predictive confidence estimation.
2. If sequence confidence meets or exceeds the configured threshold ($\tau = 0.85$, determined solely from synthetic validation data), accept the prediction.
3. If confidence falls below $\tau$, automatically trigger a **Second Pass** across a multi-stage preprocessing filter bank:
   - `raw` (original image)
   - `pipeline_a_clahe` (Local contrast enhancement)
   - `pipeline_c_illum_clahe` (Background illumination subtraction + CLAHE)
   - `pipeline_d_sauvola_deskew` (Adaptive local Sauvola thresholding + morphological deskew)
4. Evaluate confidence across all candidate representations and select the candidate with the highest sequence confidence.
5. If top candidate confidences are within an ambiguity margin ($\Delta \le 0.025$) or below the review floor ($\text{floor} = 0.50$), mark `REVIEW_REQUIRED = True`.

## 2. Mathematical Confidence Formulation

Given CTC log-probabilities $\ln P(c \mid x_t)$ of shape $(T, C)$, the sequence confidence $S$ is extracted without heuristic or random values:
1. For each timestep $t$, extract max probability $p_t = \max_{c} P(c \mid x_t)$ and Shannon entropy $\mathcal{H}_t = -\sum_{c=1}^C P(c \mid x_t) \ln P(c \mid x_t)$.
2. Extract the non-blank, CTC-collapsed character emission sequence $E = \{(c_k, t_k, p_{t_k})\}_{k=1}^K$.
3. Compute sequence confidence:
   $$S = 0.7 \cdot \left(\frac{1}{K} \sum_{k=1}^K p_{t_k}\right) + 0.3 \cdot \min_{k} p_{t_k}$$
This formulation penalizes lines where even a single character glyph has very low predictive certainty.

## 3. Threshold Calibration (Synthetic Validation Only)

- **Dataset Used:** `data/synthetic/synthetic_val.jsonl` ($N=35$ synthetic lines).
- **Leakage Safeguard:** The CICT GT-133 gold-standard external test set was **strictly excluded** from threshold tuning.
- **Configured Threshold:** $\tau = 0.85$ (captures high-certainty predictions while routing ~65-85% of degraded lines to second-pass candidate re-evaluation).

## 4. Empirical Evaluation Results

| Dataset | Metric | Condition A (First Pass) | Condition B (Second Pass) | Second Pass Delta |
| :--- | :--- | :---: | :---: | :---: |
| **Synthetic Test ($N=35$)** | Mean CER | 12.76% | **11.56%** | **-1.20% CER (Improved)** |
| | Mean WER | 48.24% | 51.81% | +3.57% |
| | Exact Match (%) | 31.43% | **34.29%** | **+2.86% Exact Match** |
| | Reprocessed (%) | — | 65.71% | — |
| | Improved / Worsened | — | 14.29% / 8.57% | +5.72% net improvement |
| **CICT GT-133 External ($N=23$)** | Mean CER | 296.30% | **141.12%** | **-155.18% CER (Massive Drop)** |
| | Mean WER | 136.89% | **111.89%** | **-25.00% WER (Massive Drop)** |
| | Reprocessed (%) | — | 100.00% | All 23 lines reprocessed |
| | Improved / Worsened | — | 39.13% / 17.39% | +21.74% net improvement |
