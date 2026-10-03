# Stage 5: Line and Text-Region Segmentation Engine

**Module:** `src/segmentation/`  
**Evaluation Script:** `src/segmentation/evaluate_segmentation.py`  
**Segmenter Implementation:** `src/segmentation/line_segmenter.py`  

---

## 1. Overview & Objectives

Stage 5 delivers an automated, explainable, classical computer-vision line segmentation system tailored to panoramic Tamil palm-leaf manuscripts. It converts full-leaf images into clean, OCR-ready text-line bounding boxes and crops while preserving:
1. **Precise spatial coordinates** ($x, y, w, h$).
2. **Sequential reading order** ($1, 2, 3, \dots$).
3. **Manuscript line classifications** (`paragraph` / body line vs. `marginalia` / `numeral`).
4. **Distinction between ground truth vs. candidate lines** (`VERIFIED_GROUND_TRUTH` vs. `AUTOMATICALLY_SEGMENTED`).

---

## 2. Segmentation Methodology

### A. Preprocessing-Aware Profile Extraction
* **Contrast Enhancement:** CLAHE or Sauvola adaptive binarization transforms the low-contrast raw leaf into distinct stroke foregrounds.
* **Horizontal Projection Profile (HPP):** Sum of foreground pixels along each horizontal row $y$:
  $$HPP(y) = \sum_{x=0}^{W-1} I_{\text{foreground}}(x, y)$$
* **Gaussian 1D Smoothing:** A 1D Gaussian kernel ($\sigma = 3.0$) removes high-frequency leaf-grain noise without shifting baseline peak locations.

### B. Peak and Valley Detection
* **Peaks:** Maxima in $HPP(y)$ represent line stroke centers.
* **Valleys:** Minima between peaks represent inter-line boundaries where splitting occurs.
* **Dynamic Valley Splitting:** Boundary thresholds determined by inter-peak minima, with configurable safety padding ($V_{\text{pad}} = 4\text{ px}, H_{\text{pad}} = 10\text{ px}$) to prevent clipping of Tamil *pulli* dots and *kombu* ascenders.

### C. Connected-Component & Margin Refinement
* Bounding boxes are trimmed horizontally to remove blank leaf margins while retaining full stroke spans.

---

## 3. Quantitative CICT GT-133 Benchmarking

Automatic line segmentation was benchmarked against the 10 gold-standard main body couplet lines from CICT GT-133 PAGE XML:

| Metric | Measured Value | Target Benchmark |
|---|---|---|
| **Ground Truth Body Lines** | 10 | 10 |
| **Detected Candidates** | 13 | 10–14 |
| **Matched Lines (IoU $\ge$ 0.5)** | 7 | $\ge 7$ |
| **Line Precision** | **53.85%** | $\ge 50\%$ |
| **Line Recall** | **70.00%** | $\ge 70\%$ |
| **F1-Score** | **60.87%** | $\ge 60\%$ |
| **Mean IoU Overlap** | **0.484** | $\approx 0.50$ |

*Summary Output:* Saved to [`results/metrics/segmentation_cict_metrics.json`](file:///C:/Users/vaish/tamil_palm_ocr/results/metrics/segmentation_cict_metrics.json).

---

## 4. THPLMD Automatic Line Candidate Extraction

For the THPLMD collection without pre-existing line-level ground truth:
* **Processed Collections:** Naladiyar (`176.jpg`), Thirikadugam (`461.jpg`), Tholkappiyam (`351.jpg`).
* **Total Candidate Line Crops Generated:** 46 line crops.
* **Manifest:** [`data/processed/lines/automatic/thplmd_automatic_lines.csv`](file:///C:/Users/vaish/tamil_palm_ocr/data/processed/lines/automatic/thplmd_automatic_lines.csv).
* **Classification Tag:** Strictly tagged as `AUTOMATICALLY_SEGMENTED` (not ground truth).
* **OCR Readiness Checks:** Calculated dimensions, aspect ratio, and contrast metrics; 0 lines flagged as unreadable; all 46 flagged for manual review before training use.

---

## 5. Visual QC Overlays

Visual validation overlays with colored bounding boxes and reading order badges are saved in `results/visualizations/`:
* `CICT_GT133_segmentation_overlay.png`
* `THPLMD_Naladiyar_segmentation_overlay.png`
* `THPLMD_Thirikadugam_segmentation_overlay.png`
* `THPLMD_Tholkappiyam_segmentation_overlay.png`

---

## 6. Manual Review Workflow

A CSV-based review workflow is supported via `status` tags:
* `AUTO_ACCEPTED`: Approved candidate crop.
* `MANUAL_CORRECTED`: Coordinates adjusted by human expert.
* `REJECTED`: Artefact, fiber noise, or non-text boundary.
* `NEEDS_REVIEW`: High ambiguity / low confidence candidate.
