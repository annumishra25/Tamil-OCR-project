# Dataset Ingestion, Provenance & Ground-Truth Analysis (Stage 2)

## 1. Executive Summary & Inventory Table

| Dataset | Total Images | Level | Tamil Labels | Aligned Transcriptions | Original Images | Binarized Images | Training Modality Role | Evaluation Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **THPLMD — Naladiyar** | 53 | Folio / Page (`3996 × 600`) | No | None in archive | 29 | 24 | Target domain preprocessing & unsupervised adaptation | Unsupervised only |
| **THPLMD — Thirikadugam** | 24 | Folio / Page (`3996 × 600`) | No | None in archive | 15 | 9 | Target domain preprocessing & unsupervised adaptation | Unsupervised only |
| **THPLMD — Tholkappiyam** | 81 | Folio / Page (`3996 × 600`) | No | None in archive | 0 | 81 | Binarization & stroke morphology benchmarking | Unsupervised only |
| **CICT — Tirukkural GT-133**| 1 | Folio / Line (`2762 × 459`) | Yes | 10 Body Lines + 3 Marginalia + 10 Numerals (23 Total) | 1 | 0 | Supervised OCR fine-tuning & line evaluation | **Gold Benchmark** |
| **palmleaf-tamil** | 0 | Character / Word | Unknown | Unknown | 0 | 0 | Not present in workspace / Not downloaded | N/A |
| **IIIT Tamil Handwriting** | 0 | Word | Unknown | Unknown | 0 | 0 | Offline (Server-side download error on host) | N/A |

---

## 2. Dataset Classification & Categorization

Following the taxonomy in Section 9 of the Master Specification:

1. **`THPLMD_Naladiyar`**: `IMAGE_ONLY` (Contains 29 raw color/grayscale captures + 24 binarized captures).
2. **`THPLMD_Thirikadugam`**: `IMAGE_ONLY` (Contains 15 raw color captures + 9 binarized captures).
3. **`THPLMD_Tholkappiyam`**: `IMAGE_ONLY` (Contains 81 binarized captures).
4. **`CICT_Tirukkural` (`CICT-PLM-GT-133`)**: `IMAGE_AND_PAGE_XML` (1 full high-resolution manuscript image paired with complete PAGE XML 2019 schema and JSON metadata).
5. **`palmleaf-tamil`**: `UNRESOLVED` (Archive not present in current workspace).
6. **`iiit_tamil`**: `UNRESOLVED` (Host server offline; directory intentionally preserved empty).

---

## 3. Structural & Geometric Analysis

### A. THPLMD Collections (158 Total Folio Images)
* **Image Format:** JPEG (RGB, 8-bit per channel).
* **Dimensions:** Completely standardized at **`3996 × 600` pixels** across all 158 images (Aspect ratio `6.66 : 1`).
* **Content:** Panoramic palm-leaf manuscript folios showing horizontal lines of incised Tamil script, string holes, natural leaf grain, fading, and edge fractures.
* **Ground Truth Status:** **No text transcriptions are embedded within the archives.** These images cannot directly serve as supervised OCR training pairs without manual transcription or external label alignment.

### B. CICT Palm-Leaf Ground Truth (`CICT-PLM-GT-133`)
* **Image Resolution:** **`2762 × 459` pixels** (Downloaded directly from Zenodo IIIF concept DOI `10.5281/zenodo.21337086`).
* **Ground Truth Structure (PAGE XML & JSON):**
  * **Main Body (`region_body`):** 10 lines with exact polygon bounding coordinates, baselines, and complete Tamil Unicode text (Couplets K1321 to K1330).
  * **Left Margin (`region_left`):** 3 lines capturing chapter title cells (`ஊட`, `லுவகை`) and leaf numeral (`௮௰௭`).
  * **Right Margin (`region_right`):** 10 lines capturing Tamil numerals (`௧` through `௰`).
  * **Total Verified Line-Level Supervised Crops:** **23 Labeled Crops** (10 high-value full couplet lines).

---

## 4. Duplicate & Leakage Analysis

### Critical Leakage Finding: Original vs. Binarized Folio Overlap
Within the THPLMD archives, several folios exist in **both** raw photography and binarized versions under identical numeric stems:
* **Naladiyar:** 24 folios are shared between `Naladiyar Original/` and `Naladiyar Binarized/` (e.g., folios `126`, `127`, `128`, `130`, `131`, ...).
* **Thirikadugam:** 9 folios are shared between `THIRIKADUGAM ORIGIANAL/` and `THIRIKADUGAM BINARIZED/` (e.g., folios `461`, `464`, `465`, `467`, `468`, ...).
* **Embedded Archive:** `Naladiyar.zip` contained an embedded copy of `THIRIKADUGAM.zip` (26,344,206 bytes), which has been isolated during staging to prevent duplicate file counting.

> [!WARNING]
> **Zero-Leakage Partitioning Rule:**
> If a folio (e.g., Naladiyar folio `126`) is placed into a train split, its binarized counterpart (`126.jpg` in binarized folder) must **NEVER** be placed in the test or validation split. Splitting must strictly occur at the **Folio Stem Identifier level**.

---

## 5. Answers to Target Data Inventory Questions

### A. Character-Level Training Data
* **Count:** 0 isolated character images currently present locally.
* **Status:** `palmleaf-tamil.zip` was not present in the workspace. If character-level data is provided later, it will be used for character recognition pretraining and synthetic glyph degradation.

### B. Word-Level Training Data
* **Count:** 0 labeled word images currently present locally (IIIT Tamil dataset is offline).

### C. Line-Level Training Data
* **Count:** **23 labeled lines** from CICT GT-133 (10 body couplets, 3 marginalia, 10 numerals).
* **Ground Truth Source:** Aligned PAGE XML (`CICT-PLM-GT-133.xml`).

### D. Manuscript / Page-Level Data
* **Count:** **159 total folio images** (158 THPLMD + 1 CICT).
* **Transcribed Folios:** 1 (CICT GT-133).
* **Un-transcribed Folios:** 158 (THPLMD).

### E. CICT Ground Truth Usability
* **Usable Supervised Samples:** **1 Folio / 23 Line Crops** completely linked and validated.

### F. Synthetic Training Potential
* Clean Tamil Unicode text from Tirukkural, Naladiyar, and classical Tamil literature can be rendered using authentic Tamil fonts (`Noto Serif Tamil`, `Anek Tamil`) and subjected to physical palm-leaf degradation (texture blending, fibrous noise, scratches, fading, uneven lighting) to generate large-scale synthetic line training pairs.

---

## 6. Strategic Assessment for Next Stages

1. **Supervised Data Reality:** The project currently possesses **1 gold-standard ground-truth folio (23 line crops)** and **158 un-transcribed manuscript folios**.
2. **Role of Existing Data:**
   * **THPLMD (158 Folios):** Used for **Stage 4 (Adaptive Preprocessing)**, **Stage 5 (Line Segmentation)**, background noise extraction, and unsupervised domain adaptation.
   * **CICT GT-133 (23 Line Crops):** Used as the **Primary Real Ground-Truth Evaluation Benchmark** for zero-shot baseline and fine-tuned comparisons.
   * **Synthetic Physical Degradation (Stage 7):** Clean Tamil text paired with realistic palm-leaf noise modeling is essential to bridge the supervised training gap prior to fine-tuning.
3. **Is IIIT Tamil Data Critical?**
   * While IIIT Tamil would provide handwriting domain data, the synthetic palm-leaf degradation pipeline (Stage 7) + Indic TrOCR pretrained representations + CICT benchmark provides a fully self-contained, reproducible path forward.
