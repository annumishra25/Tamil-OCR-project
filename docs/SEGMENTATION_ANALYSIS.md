# Stage 5: Tamil Palm-Leaf Manuscript Layout & Segmentation Analysis

**Project:** Distortion-Aware Tamil Palm-Leaf Manuscript OCR / HTR System  
**Date:** October 2026  
**Status:** Completed Analysis  

---

## 1. Manuscript Geometry & Physical Layout Overview

Palm-leaf manuscripts (*Olaipuvadi* / ஓலைச்சுவடி) possess unique physical and geometric properties distinct from modern printed or paper documents:

| Collection | Typical Resolution | Aspect Ratio | Bands / Lines | Character Height | Inter-Line Spacing |
|---|---|---|---|---|---|
| **CICT-PLM-GT-133 (Tirukkural)** | 2762 × 459 px | 6.01 : 1 | 10 lines (23 regions) | ~25–38 px | ~3–6 px (very dense) |
| **THPLMD Naladiyar** | 3996 × 600 px | 6.66 : 1 | 12–16 lines | ~20–32 px | ~2–5 px |
| **THPLMD Thirikadugam** | 3996 × 600 px | 6.66 : 1 | 14–18 lines | ~18–28 px | ~2–4 px |
| **THPLMD Tholkappiyam** | 3996 × 600 px | 6.66 : 1 | 10–14 lines | ~24–36 px | ~3–6 px |

---

## 2. Detailed Layout Observations by Collection

### A. CICT GT-133 (Tirukkural Chapter 133)
* **Writing Zones:**
  1. **Marginal Title & Folio Number (Left Margin):** Contains Tamil numeral page notation and chapter heading (*ஊடலுவகை*).
  2. **Central Main Body Couplets:** 10 primary lines corresponding to Kural verses 1321 to 1330.
  3. **Right Marginal Indexing:** Tamil traditional numerals denoting couplet indices (௧ to ௰).
* **Text Continuity:** Each line corresponds to one full poetic line of a Kural couplet. Characters are inscribed without inter-word white space (scriptio continua).
* **Physical Degradation:** Darkened borders, horizontal leaf striations, fibrous grain running parallel to text lines, ink fading on right quadrant.

### B. THPLMD Naladiyar (53 Folios)
* **Layout Structure:**
  * Highly dense horizontal text bands (12 to 16 lines per leaf).
  * Continuous script across almost the entire width of the leaf (margins < 5% of leaf width).
  * Binding cord holes (*kadi-thulai*) located at approximately 1/4 and 3/4 widths of the leaf, occasionally interrupting text strokes.
* **Line Orientation:** Near-horizontal (within ±1.2° skew), but minor local sagging or curvature along the drying grain.
* **Damage Regions:** Darkened leaf edges, surface flaking, oil staining, and longitudinal cracks along leaf veins.

### C. THPLMD Thirikadugam (24 Folios)
* **Layout Structure:**
  * Very compact line height (18–28 px) with minimal baseline separation.
  * Ascenders (e.g., combining vowel signs ி, ீ, கொம்புகள் ெ, ே) frequently touch or overlap descenders (ு, ூ, ள) from the preceding line.
* **Damage Regions:** Spot insect damage, uneven binarization contrast, faint incised strokes requiring illumination correction before segmentation.

### D. THPLMD Tholkappiyam (81 Folios)
* **Layout Structure:**
  * Pre-binarized collection with high contrast.
  * 10 to 14 text bands with clear stroke geometry.
  * Thinner character widths and consistent margin spacing on left and right borders (~50–80 px).

---

## 3. Segmentation Challenges in Palm-Leaf Manuscripts

1. **Sub-5-Pixel Inter-Line Gaps:**
   * Unlike printed paper documents with generous line spacing, palm leaves maximized scarce surface area, packing 10–18 lines into 450–600 pixels of vertical height.
   * Standard 2D morphological dilation quickly merges adjacent lines into a single inseparable blob.
2. **Ascender/Descender Touching Stems:**
   * Vowel diacritics (*pulli* dots, *kombu*, *kaal*, *kombu-suzhi*) bridge across line boundaries.
3. **Leaf Texture & Fiber Noise:**
   * Natural horizontal leaf fibers produce spurious false peaks in raw projection profiles.
   * Preprocessing with Gaussian smoothing + CLAHE is required before projection profile computation.
4. **Distinction of Line Types:**
   * Main text body lines must be distinguished from marginal titles, chapter headers, and Tamil numerical indices.

---

## 4. Reading Order Determination Strategy

1. **Top-to-Bottom Primary Scan:**
   * Text bands sorted strictly by vertical coordinate ($Y_{\text{min}}$ / centroid $Y$).
2. **Marginal Zone Partitioning:**
   * Coordinates with $X_{\text{max}} < 0.15 \times W$ categorized as Left Marginal Text (Folio numbers, section headers).
   * Coordinates with $X_{\text{min}} > 0.85 \times W$ categorized as Right Marginal Indices.
   * Coordinates spanning $[0.10 \times W, 0.90 \times W]$ categorized as Main Body Text.
3. **Ambiguity Flagging:**
   * Folios with overlapping bounding boxes or irregular horizontal bands are flagged with `manual_review_required = TRUE`.
