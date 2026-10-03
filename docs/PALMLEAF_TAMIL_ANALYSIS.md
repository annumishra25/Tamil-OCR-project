# Analysis of palmleaf-tamil Character Dataset (Stage 3)

## 1. Archive & Structural Overview

* **Source Archive:** [palmleaf-tamil.rar](file:///C:/Users/vaish/tamil_palm_ocr/palmleaf-tamil.rar) (`816.35 MB`)
* **Total Archive Entries:** 7,230 items
* **Total Image Count:** **7,100 PNG files** (Plus 57 Windows `.ini` metadata files)
* **Directory Hierarchy:**
  ```text
  FINAL DATASET/
  └── DATASET/
      ├── 1/
      │   ├── Letter1_1.png
      │   ├── Letter1_2.png
      │   └── ... Letter1_100.png   (100 samples)
      ├── 2/
      │   ├── Letter2_1.png
      │   └── ... Letter2_100.png   (100 samples)
      ...
      └── 71/
          ├── Letter71_1.png
          └── ... Letter71_100.png  (100 samples)
  ```
* **Class Balance:** Perfectly balanced distribution across **71 distinct character classes** with exactly **100 sample images per class** (`71 × 100 = 7,100` total character samples).

---

## 2. Character Modality & Granularity

* **Granularity Level:** **Isolated / Segmented Character Level**
* **Image Format:** PNG (lossless compression)
* **Image Content:** Binarized and cropped historical Tamil palm-leaf character glyphs showing stroke variations, historical orthography, and incised contours.
* **Class Mapping:** Folder names `1` through `71` correspond to Tamil vowels (உயிரெழுத்துக்கள்), consonants (மெய்யெழுத்துக்கள்), vowel-consonant combinations (உயிர்மெய்யெழுத்துக்கள்), and historical/grantha forms.

---

## 3. Applicability to the Research Pipeline

| Research Task | Applicability Level | Detailed Technical Assessment |
| :--- | :--- | :--- |
| **A. Isolated Character Classification** | **High (Direct)** | 7,100 samples provide a robust benchmark for evaluating character classifiers (CNN / ResNet / Vision Transformer). |
| **B. Pretraining & Feature Adaptation** | **High (Foundational)** | Can be used to adapt the vision encoder (ViT / ResNet) of an OCR backbone to historical palm-leaf stroke morphology before line-level sequence modeling. |
| **C. Line-Level Sequence OCR** | **Indirect (Requires Synthesis)** | A character dataset cannot directly train a line/sequence OCR model (such as TrOCR or CTC-CRNN) without synthesizing full lines, because line OCR requires learning spatial context, inter-word spacing, ligatures, and line-level reading order. |
| **D. Synthetic Degradation & Augmentation** | **High** | Real palm-leaf glyphs from this dataset can be sampled, distorted, and rendered into synthetic multi-word manuscript lines to augment line-level training sets. |
| **E. Quantitative Evaluation** | **Character CER only** | Evaluates isolated character accuracy; line-level benchmarking remains grounded on CICT GT-133. |

---

## 4. Summary & Strategic Recommendation

1. **Role in Pipeline:** `palmleaf-tamil` represents a valuable character-level resource for **Stage 7 (Synthetic Degradation)** and **Stage 8 (Domain Adaptation)**.
2. **Line vs. Character Distinction:** We explicitly maintain the distinction between isolated character datasets (`palmleaf-tamil`) and line-level sequence datasets (`CICT GT-133`). Line-level models will not be evaluated on isolated character crops as substitutes for continuous manuscript lines.
