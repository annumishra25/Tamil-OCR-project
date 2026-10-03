# Frontend Architecture & Manuscript Laboratory UI

## 1. Design Aesthetic & Visual Language

The frontend interface is crafted with a **Historical Manuscript Digitization Laboratory** aesthetic:
* **Color Palette:**
  * Backgrounds: Deep manuscript charcoal and rich palm-leaf obsidian (`#14110F`, `#1D1916`, `#26211D`)
  * Accents: Aged palm-leaf ochre (`#C29B38`), Temple Gold (`#E5B842`), Terra Cotta / Vermilion (`#A8422B`), Forest Jade (`#3B7A57`)
  * Surfaces & Borders: Weathered parchment translucent borders (`rgba(194, 155, 56, 0.2)`), subtle glassmorphism
  * Typography: `Cinzel` / `Outfit` for classical academic headers, `Noto Serif Tamil` & `Noto Sans Tamil` for accurate Tamil Unicode rendering.
* **Tone:** Scholarly, scientific, respectful of historical heritage, precise.

---

## 2. Page Hierarchy & Flow

```text
[Home / Dashboard]
       │
       ├──► [1. Upload Manuscript] ──► Drag-and-drop, dimension/size validator
       │
       ├──► [2. Manuscript Analysis Workspace] ──► Synchronized 3-pane viewer (Original / Preprocessed / Line OCR)
       │
       ├──► [3. Preprocessing Studio] ──► Visual 6-panel filter comparison
       │
       ├──► [4. OCR Results Inspector] ──► Line-by-line prediction, confidence badge, second-pass status
       │
       ├──► [5. Tamil Text Editor] ──► Dual-view (Raw OCR vs. Corrected Tamil) with copy/export
       │
       ├──► [6. Confidence Review] ──► Low-confidence routing verification workflow
       │
       ├──► [7. Datasets Catalog] ──► Real provenance, file counts & licensing status
       │
       └──► [8. Experiments & Metrics] ──► CER / WER benchmark matrix (clearly marked 'Not evaluated yet')
```

---

## 3. Component Hierarchy

```text
app/frontend/
├── index.html                   # HTML entry point with Google Fonts & Meta tags
├── package.json                 # Vite + React configuration
├── vite.config.js               # Dev server configuration
└── src/
    ├── main.jsx                 # Application bootstrapping
    ├── App.jsx                  # Main application container & navigation state
    ├── styles/
    │   └── theme.css            # Manuscript color tokens, typography, glassmorphism, scrollbars
    ├── services/
    │   └── api.js               # Typed Mock/Real API service layer
    ├── components/
    │   ├── Header.jsx           # Laboratory branding & navigation bar
    │   ├── StatusBanner.jsx     # Hardware (RTX 4050) & Pipeline status indicator
    │   ├── ImageViewer.jsx      # Zoomable / Pannable manuscript canvas
    │   ├── LineBoundingBox.jsx  # Interactive line polygon overlay
    │   └── Modal.jsx            # Notification & export dialogs
    └── pages/
        ├── DashboardPage.jsx    # Project overview, stats, recent manuscripts
        ├── UploadPage.jsx       # Drag & drop upload handler with sample loader
        ├── AnalysisPage.jsx     # 3-Pane interactive manuscript workspace
        ├── PreprocessingPage.jsx# 6-Filter comparison matrix
        ├── OcrResultsPage.jsx   # Line OCR inspector with confidence indicators
        ├── EditorPage.jsx       # Side-by-side Tamil text editor with export
        ├── ConfidenceReviewPage.jsx # 2-Pass low-confidence resolution flow
        ├── DatasetsPage.jsx     # Live dataset provenance dashboard
        └── ExperimentsPage.jsx  # Benchmark evaluation table (CER/WER)
```

---

## 4. Mock Service vs. Live Backend Adapter

The frontend uses `src/services/api.js` which exports asynchronous methods:
* `uploadManuscript(file)`
* `fetchPreprocessingVariants(manuscriptId)`
* `fetchLineSegmentation(manuscriptId)`
* `runOcrInference(manuscriptId, lineIds)`
* `runSecondPassOcr(manuscriptId, lineId)`
* `saveTamilCorrection(manuscriptId, lineId, text)`
* `fetchDatasetsManifest()`
* `fetchExperiments()`

All mock data returned is explicitly flagged with `isDemo: true` and status indicators `DEMO` to ensure no scientific confusion.
