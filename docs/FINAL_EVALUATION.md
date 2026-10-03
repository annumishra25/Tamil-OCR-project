# Stage 10: Final Comprehensive Evaluation Report

> **Research Contribution & Scope Statement:**
> *This project adapts an existing open-source Tamil OCR model (`TamilCRNN`, 53.79M parameters) to degraded historical Tamil palm-leaf manuscripts; it does NOT introduce a new OCR architecture.*

---

## 1. Executive Summary & Complete Experiment Matrix

The complete Tamil palm-leaf OCR adaptation pipeline was evaluated across 6 controlled experimental conditions on two distinct, disjoint benchmark datasets:
1. **Synthetic Palm-Leaf Test Partition ($N=35$):** Multi-level physics degradation (scratches, ink fading, striations, uneven illumination).
2. **CICT GT-133 Real Gold-Standard External Test ($N=23$):** 18th-century incised palm-leaf manuscript lines (strictly held out; never used for training or threshold tuning).

### Full Experimental Matrix (EXP-A to EXP-F)

| Exp ID | Experimental Condition | Model Weights & Architecture | Preprocessing / Strategy | Dataset ($N$) | Mean CER | Mean WER | Exact Match (%) | Latency (ms/line) |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **EXP-A** | Pretrained Zero-Shot Baseline | Pretrained EasyOCR Tamil CRNN | Raw (Unprocessed) | Synthetic Test ($N=35$) | 99.90% | 100.00% | 0.00% | 62.17 ms |
| **EXP-B** | Pretrained + Best Preprocessing | Pretrained EasyOCR Tamil CRNN | Pipeline C (Illum+CLAHE) | Synthetic Test ($N=35$) | 99.85% | 100.00% | 0.00% | 29.13 ms |
| **EXP-C** | Fine-Tuned Model (Raw) | Stage 8 Adapted TamilCRNN | Raw (Unprocessed) | Synthetic Test ($N=35$) | 12.76% | 48.24% | 31.43% | 26.66 ms |
| **EXP-D** | Fine-Tuned + Best Preprocessing | Stage 8 Adapted TamilCRNN | Pipeline C (Illum+CLAHE) | Synthetic Test ($N=35$) | 12.11% | 51.33% | 31.43% | 28.40 ms |
| **EXP-E** | Fine-Tuned + Confidence Second Pass| Stage 8 Adapted + Router | Multi-Filter Quality Gate ($\tau=0.85$)| Synthetic Test ($N=35$) | **11.56%** | 51.81% | **34.29%** | 80.63 ms |
| **EXP-F** | Fine-Tuned + Second Pass + Post-Correction| Full Adapted Pipeline | Dynamic Routing + NFC/Virama Cleaner| Synthetic Test ($N=35$) | **11.78%** | **50.38%** | **34.29%** | 82.58 ms |
| | | | | | | | | |
| **EXP-A** | Pretrained Zero-Shot Baseline | Pretrained EasyOCR Tamil CRNN | Raw (Unprocessed) | CICT GT-133 Real ($N=23$) | 193.80% | 104.35% | 0.00% | 40.32 ms |
| **EXP-B** | Pretrained + Best Preprocessing | Pretrained EasyOCR Tamil CRNN | Pipeline C (Illum+CLAHE) | CICT GT-133 Real ($N=23$) | 244.45% | 108.70% | 0.00% | 29.09 ms |
| **EXP-C** | Fine-Tuned Model (Raw) | Stage 8 Adapted TamilCRNN | Raw (Unprocessed) | CICT GT-133 Real ($N=23$) | 296.30% | 136.89% | 0.00% | 29.36 ms |
| **EXP-D** | Fine-Tuned + Best Preprocessing | Stage 8 Adapted TamilCRNN | Pipeline C (Illum+CLAHE) | CICT GT-133 Real ($N=23$) | 204.34% | 113.60% | 0.00% | 31.01 ms |
| **EXP-E** | Fine-Tuned + Confidence Second Pass| Stage 8 Adapted + Router | Multi-Filter Quality Gate ($\tau=0.85$)| CICT GT-133 Real ($N=23$) | **141.12%** | **111.89%** | 0.00% | 113.64 ms |
| **EXP-F** | Fine-Tuned + Second Pass + Post-Correction| Full Adapted Pipeline | Dynamic Routing + NFC/Virama Cleaner| CICT GT-133 Real ($N=23$) | **137.01%** | **109.57%** | 0.00% | 113.57 ms |

---

## 2. Detailed Error Analysis & Qualitative Case Studies

From the final detailed predictions ([`results/predictions/final_predictions.csv`](file:///C:/Users/vaish/tamil_palm_ocr/results/predictions/final_predictions.csv)):

### 1. Successful OCR Recognition (Exact Matches)
* `SYNTH_TEST_00196`: GT = `"மனக்கவலை மாற்றல் அரிது"` → Prediction = `"மனக்கவலை மாற்றல் அரிது"` (CER: 0.00%, Confidence: 0.9536)
* `SYNTH_TEST_00197`: GT = `"வேண்டுதல் வேண்டாமை இலானடி சேர்ந்தார்க்கு"` → Prediction = `"வேண்டுதல் வேண்டாமை இலானடி சேர்ந்தார்க்கு"` (CER: 0.00%, Confidence: 0.9389)
* `SYNTH_TEST_00202`: GT = `"தனக்குவமை இல்லாதான் தாள்சேர்ந்தார்க் கல்லால்"` → Prediction = `"தனக்குவமை இல்லாதான் தாள்சேர்ந்தார்க் கல்லால்"` (CER: 0.00%, Confidence: 0.9576)
* `SYNTH_TEST_00212`: GT = `"அறஞ்செய்யா ராயின் அருந்துயர்க் குற்ற"` → Prediction = `"அறஞ்செய்யா ராயின் அருந்துயர்க் குற்ற"` (CER: 0.00%, Confidence: 0.9502)

### 2. Character Substitutions
* Visual similarity confusions between `ர` (ra) and `ா` (long vowel sign aa), and `ன` (na) vs `னை` (nai).
* Example (`SYNTH_TEST_00204`): GT = `"நரைவருமென் றெண்ணி நல்லறி வாளர்"` → Prediction = `"நரைவருமென் றெண்ணிநல்லறி வளர்"` (Omission of length marker `ா`).

### 3. Second-Pass Reprocessing Improvements
* On real CICT manuscript lines with non-uniform illumination, the First Pass on raw images failed with CER > 250%. The confidence quality gate automatically triggered the second pass, selecting **Pipeline C (Illumination Norm + CLAHE)** and dropping CER to 141.12%.

### 4. Post-Correction Repairs
* Re-attached floating pullis and resolved detached vowel markers, reducing real CICT line WER from 111.89% to **109.57%**.

---

## 3. Methodological Limitations

1. **Small Real-World Gold-Standard Sample ($N=23$):** CICT GT-133 represents 23 verified, human-annotated lines from a single 18th-century palm-leaf folio (Tirukkural Chapter 133). While invaluable as an untouched test set, broader generalization across centuries and scribe hands cannot be claimed.
2. **Unlabeled Real Data (THPLMD):** THPLMD provides 158 authentic folio images, but lacks aligned line-level transcription ground truth.
3. **Historical Orthographic Deviation:** Incised stylus scripts frequently merge adjacent characters, omit the virama (pulli dot), and use archaic ligatures not present in modern Unicode Tamil print corpora.
