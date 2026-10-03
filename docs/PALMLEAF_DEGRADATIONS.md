# Physical Degradation Patterns in Tamil Palm-Leaf Manuscripts (Stage 4)

## 1. Observed Physical Degradation Taxonomy

Based on direct empirical analysis of the **THPLMD** (Naladiyar, Thirikadugam, Tholkappiyam) and **CICT GT-133** manuscript collections:

```
+-----------------------------------------------------------------------------------------------+
|                       HISTORICAL TAMIL PALM-LEAF DEGRADATIONS                                |
+-----------------------------------------------------------------------------------------------+
    │
    ├── 1. Surface Texture & Substrate Degradations
    │   ├── Longitudinal leaf fiber ridges (parallel horizontal striations)
    │   ├── Natural leaf grain noise (estimated noise sigma: 3.0 - 7.5)
    │   └── Age-related substrate yellowing and darkening (mean brightness: 134 - 186 / 255)
    │
    ├── 2. Optical & Illumination Distortions
    │   ├── Non-uniform ambient lighting gradients across panoramic folios (gradient > 120)
    │   ├── Vignetting and shadow gradients near leaf extremities
    │   └── Low global contrast (standard deviation: 21.0 - 55.0)
    │
    ├── 3. Stroke & Scribal Degradations
    │   ├── Incised stylus fading (extremely faint glyph loops and disconnected ascenders)
    │   ├── Inconsistent soot/lampblack ink absorption into incisions
    │   ├── Absent inter-word spacing (continuous scriptio continua)
    │   └── Pulli (dot) erosion and historical orthographic variants (e.g. உளடல் for ஊடல்)
    │
    ├── 4. Structural & Mechanical Damage
    │   ├── String binding holes (perforation voids interrupting text flow)
    │   ├── Transverse micro-cracks and leaf brittleness crossing vertical character strokes
    │   └── Edge fraying, insect bores (wormholes), and physical chipped margins
    │
    └── 5. Binarization-Induced Artifacts
        ├── Stroke dropout under global thresholding (Otsu disconnects thin loops)
        └── Background noise amplification under aggressive local thresholding
```

---

## 2. Empirical Measurements from Quality Profiling (164 Images)

| Distortion Dimension | Measurement Range in THPLMD / CICT | Impact on OCR Recognition | Preprocessing Counter-Strategy |
| :--- | :--- | :--- | :--- |
| **Panoramic Aspect Ratio** | `6.0 : 1` to `6.66 : 1` (`3996 × 600` / `2762 × 459`) | Prevents standard square CNN inputs | Aspect-ratio preserving line slicing |
| **Substrate Brightness** | Mean intensity `134.8` – `246.7` (out of 255) | Global thresholding fails on dark folios | Rolling background illumination division |
| **Contrast Standard Dev** | `16.1` – `59.1` (Median: `37.2`) | Low contrast obscures faint incisions | CLAHE (Clip limit `2.0` – `2.5`) |
| **Fiber Noise ($\sigma$)** | `0.0` – `7.4` on line crops | False-positive character boundary detections | Bilateral filter ($d=9, \sigma_c=75, \sigma_s=75$) |
| **Baseline Skew** | `-1.8^\circ` to `+1.2^\circ` | Angled bounding boxes slice line caps | Hough / Radon deskewing |

---

## 3. Principles for Preprocessing without Information Loss

1. **The Anti-Destructive Rule:** Never apply aggressive global binarization (e.g. Otsu) as a sole hard gate. Thin Tamil character ligatures and pulli dots have similar gray levels to ambient leaf fibers; global binarization erases them completely.
2. **Multi-Scale Illumination Flattening:** Rolling morphological closing extracts the background envelope, enabling division-based normalization that removes shadows without thinning character strokes.
3. **Preservation of Raw Image Paths:** Preprocessing generates separate derived variants (`data/processed/`); raw inputs (`data/raw/`) remain immutable for second-pass fallback.
