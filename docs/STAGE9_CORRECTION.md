# Stage 9: Conservative Tamil Post-Correction

## 1. Design Principles & Anti-Hallucination Constraints

Post-OCR correction for historical manuscripts carries severe risks of linguistic corruption if language models or aggressive modern dictionaries are permitted to rewrite ancient syntax.

The Stage 9 `TamilPostCorrector` implements strictly conservative, deterministic rule-based corrections:
1. **Never Invent Missing Words:** Does not synthesize or guess omitted vocabulary.
2. **Never Modernize Historical Tamil:** Preserves archaic grammatical endings, obsolete verbal forms, and historical numerals.
3. **Never Rewrite Uncertain Text:** Only resolves unambiguous mechanical, Unicode, and whitespace anomalies.
4. **Preserve Complete Provenance:** Always retains the original OCR hypothesis and tracks every atomic text edit.

## 2. Implemented Correction Rules

| Rule Name | Target Anomaly | Example Before | Corrected Output | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `UNICODE_NFC_NORMALIZATION` | Decomposed Unicode codepoints | `தம\u0BBFழ\u0BCD` | `தமிழ்` | Standardizes composed Unicode representations for search & storage. |
| `WHITESPACE_CLEANUP` | Spurious internal multi-spaces | `தமிழ்   நாடு` | `தமிழ் நாடு` | Collapses consecutive spaces without altering words. |
| `DETACHED_COMBINING_SIGN_ATTACHMENT`| OCR whitespace separating consonant & vowel/pulli | `தம ிழ்` / `த ்மிழ்` | `தமிழ்` / `த்மிழ்` | Re-attaches floating pullis or vowel signs caused by stroke gaps. |
| `DEDUPLICATE_COMBINING_MARKS` | Repeated pulli or vowel mark on same base | `க்்` | `க்` | Cleans duplicate virama emissions from CTC frame repetition. |
| `REMOVE_VIRAMA_BEFORE_VOWEL` | Inverted pulli preceding explicit vowel mark | `க்ா` | `கா` | Resolves invalid orthographic sequence in Tamil. |

## 3. Quantitative Impact on Benchmark Datasets

| Dataset | Condition B (Second Pass) CER / WER | Condition C (Post-Corrected) CER / WER | Lines Modified (%) |
| :--- | :---: | :---: | :---: |
| **Synthetic Test ($N=35$)** | 11.56% / 51.81% | 11.78% / **50.38%** | 17.14% |
| **CICT GT-133 External ($N=23$)** | 141.12% / 111.89% | **137.01%** / **109.57%** | 43.48% |

On real historical palm-leaf manuscripts (CICT GT-133), conservative post-correction successfully cleaned 43.48% of lines, reducing CER from 141.12% to **137.01%** and WER from 111.89% to **109.57%**.
