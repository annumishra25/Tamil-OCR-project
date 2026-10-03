// API Service Layer for Tamil Palm-Leaf Manuscript Digitization Laboratory
// Interfaces cleanly separate Mock Adapters (current) from future Live PyTorch Backend

export const SYSTEM_STATUS = {
  gpu: {
    name: 'NVIDIA GeForce RTX 4050 Laptop GPU',
    vram: '6,141 MiB (~6 GB)',
    cudaAvailable: true,
    cudaVersion: '12.4'
  },
  pipeline: {
    status: 'Stage 9 Confidence Second Pass & Post-Correction Completed',
    ocrModel: 'TamilCRNN + SecondPassRouter + TamilPostCorrector',
    activeStage: 'Stage 9: Confidence Second Pass + Post-Correction (Complete)'
  }
};

// High-fidelity sample manuscript based on CICT-PLM-GT-133 (Tirukkural Ch 133)
export const SAMPLE_MANUSCRIPTS = [
  {
    id: 'CICT-PLM-GT-133',
    title: 'Tirukkural Chapter 133 (ஊடலுவகை)',
    work: 'Tirukkural (திருக்குறள்)',
    author: 'Thiruvalluvar (திருவள்ளுவர்)',
    folioNumber: '87 (Recto)',
    linesCount: 10,
    totalAnnotations: 23,
    kuralRange: '1321 - 1330',
    dimensions: { width: 2762, height: 459 },
    sourceInstitution: 'Central Institute of Classical Tamil (CICT)',
    license: 'CC BY 4.0',
    isDemo: true,
    lines: [
      {
        id: 'L1',
        kural: 1321,
        numeral: '௧',
        rawOcr: 'இல்லைத் தவற் வாக்காயினு மூடுதல் வல்லது வாளிக்கு மா று',
        correctedText: 'இல்லை தவறு அவர்க்காயினும் ஊடுதல் வல்லது அவர் அளிக்கு மாறு',
        confidence: 0.91,
        status: 'HIGH_CONFIDENCE',
        secondPassApplied: false,
        bbox: { x: 359, y: 30, w: 2140, h: 37 }
      },
      {
        id: 'L2',
        kural: 1322,
        numeral: '௨',
        rawOcr: 'ஊடலிற் றோன்று ஞ்சிறுதுனி நல்லளி வாடினும் பாடு பெறு ம',
        correctedText: 'ஊடலின் தோன்றும் சிறுதுனி நல்லளி வாடினும் பாடு பெறும்',
        confidence: 0.88,
        status: 'HIGH_CONFIDENCE',
        secondPassApplied: false,
        bbox: { x: 359, y: 71, w: 2140, h: 37 }
      },
      {
        id: 'L3',
        kural: 1323,
        numeral: '௩',
        rawOcr: 'புலத்தலிற் பத்தேணுடுண்டோ நிலத்தொடு நீரியைந் தன்னூர்க த் து',
        correctedText: 'புலத்தலின் புத்தேள்நாடு உண்டோ நிலத்தொடு நீர் இயைந்தன்னார் அகத்து',
        confidence: 0.64,
        status: 'LOW_CONFIDENCE',
        secondPassApplied: true,
        secondPassOcr: 'புலத்தலிற் புத்தேணாடூண்டோ நிலத்தொடு நீரியைந் தன்னூர்க த் து',
        bbox: { x: 359, y: 112, w: 2140, h: 37 }
      },
      {
        id: 'L4',
        kural: 1324,
        numeral: '௪',
        rawOcr: 'புல்லிவிடாப் புல்வி யுடடோன்றுமெனனுள்ளமுடைக்கும் படை',
        correctedText: 'புல்லி விடாஅப் புலவியுள் தோன்றும் என் உள்ளம் உடைக்கும் படை',
        confidence: 0.82,
        status: 'ACCEPTABLE',
        secondPassApplied: false,
        bbox: { x: 359, y: 153, w: 2140, h: 37 }
      },
      {
        id: 'L5',
        kural: 1325,
        numeral: '௫',
        rawOcr: 'தவரிலநாயினுந்தா  மவீழவரா மென்றேள் கறலி னுங் கொன்றுடைத் து',
        correctedText: 'தவறிலர் ஆயினும் தாம் வீழ்வார் மென்தோள் அகறலின் ஆங்கொன்று உடைத்து',
        confidence: 0.58,
        status: 'LOW_CONFIDENCE',
        secondPassApplied: true,
        secondPassOcr: 'தவரிலராயினுந்தா  மவீழவரா மென்றேள் அகறலி னுங் கொன்றுடைத் து',
        bbox: { x: 359, y: 194, w: 2140, h: 37 }
      },
      {
        id: 'L6',
        kural: 1326,
        numeral: '௬',
        rawOcr: 'உணலிசநுமுண்டதற்லினிது காமம் புணாதலினூட லிநி து',
        correctedText: 'உணலினும் உண்டது அறல் இனிது காமம் புணர்தலின் ஊடல் இனிது',
        confidence: 0.79,
        status: 'ACCEPTABLE',
        secondPassApplied: false,
        bbox: { x: 359, y: 235, w: 2140, h: 37 }
      },
      {
        id: 'L7',
        kural: 1327,
        numeral: '௭',
        rawOcr: 'உளடலிற் றேற்றுவ ரவென்றார்  துமநநுங் கூடலிற் காணப்படு ம்',
        correctedText: 'ஊடலில் தோற்றவர் வென்றார் அது மன்னும் கூடலில் காணப் படும்',
        confidence: 0.75,
        status: 'ACCEPTABLE',
        secondPassApplied: false,
        bbox: { x: 359, y: 276, w: 2140, h: 37 }
      },
      {
        id: 'L8',
        kural: 1328,
        numeral: '௮',
        rawOcr: 'உளடிப் பெருகுவுங் தொல்லொநு துல்வியாப்பக்  கடலிற றேனறிய      ஷப் பு',
        correctedText: 'ஊடிப் பெறுகுவம் கொல்லோ நுதல்வியப்பக் கூடலில் தோன்றிய உப்பு',
        confidence: 0.49,
        status: 'LOW_CONFIDENCE',
        secondPassApplied: true,
        secondPassOcr: 'ஊடிப் பெறுகுவம் கொல்லோ நுதல்வியப்பக் கூடலில் தோன்றிய உப்பு',
        bbox: { x: 359, y: 317, w: 2140, h: 37 }
      },
      {
        id: 'L9',
        kural: 1329,
        numeral: '௯',
        rawOcr: 'உளடுக மந்நொ வொளியிழை யாமிரப்ப நீடுகு மன்னோ விர ர்',
        correctedText: 'ஊடுக மன்னோ ஒளியிழை யாம் இரப்ப நீடுக மன்னோ இரா',
        confidence: 0.85,
        status: 'HIGH_CONFIDENCE',
        secondPassApplied: false,
        bbox: { x: 359, y: 358, w: 2140, h: 37 }
      },
      {
        id: 'L10',
        kural: 1330,
        numeral: '௰',
        rawOcr: 'உளடுதுல காமத்திற் கின் பமதற் கின்பங் கூடிமுயங்கப்  பெறி ன்',
        correctedText: 'ஊடுதல் காமத்திற்கு இன்பம் அதற்கு இன்பம் கூடி முயங்கப் பெறின்',
        confidence: 0.94,
        status: 'HIGH_CONFIDENCE',
        secondPassApplied: false,
        bbox: { x: 359, y: 399, w: 2140, h: 37 }
      }
    ]
  }
];

export const PREPROCESSING_VARIANTS = [
  {
    id: 'original',
    name: 'Original Capture',
    description: 'Raw high-resolution photographic acquisition from palm-leaf folio with ambient lighting gradients.',
    badge: 'Raw'
  },
  {
    id: 'grayscale',
    name: 'Illumination Normalized Grayscale',
    description: 'Separates luminance channel and applies rolling background subtraction to balance palm-leaf fiber shading.',
    badge: 'Standard'
  },
  {
    id: 'clahe',
    name: 'CLAHE Contrast Stretching',
    description: 'Contrast Limited Adaptive Histogram Equalization to accentuate faded incisions in low-contrast zones.',
    badge: 'Enhanced'
  },
  {
    id: 'denoised',
    name: 'Bilateral Stroke-Preserving Denoising',
    description: 'Smooths natural leaf texture grain while preserving high-gradient inscribed incised character edges.',
    badge: 'Filtered'
  },
  {
    id: 'sauvola',
    name: 'Sauvola Adaptive Thresholding',
    description: 'Local variance-based binarization designed for degraded historical manuscripts with uneven ink/staining.',
    badge: 'Binarized'
  },
  {
    id: 'deskewed',
    name: 'Radon Transform Deskewing',
    description: 'Detects dominant text baseline orientation angle and corrects horizontal line tilt for accurate OCR slicing.',
    badge: 'Geometric'
  }
];

export const DATASETS_MANIFEST = [
  {
    id: 'cict-gt-133',
    name: 'CICT-PLM-GT-133 (Tirukkural Ch 133)',
    type: 'Palm-Leaf Manuscript Folio (2762 × 459 px)',
    imagesCount: 23,
    groundTruth: '23 Aligned Verified Lines (10 Body Couplets + 13 Marginalia)',
    tier: 'Level 3: Supervised Ground Truth',
    role: 'EXTERNAL_TEST (Gold-Standard Benchmark)',
    status: 'Verified & Sliced into data/processed/cict_gt133_lines/',
    format: 'JPEG + PAGE XML (2019-07-15) + JSON',
    license: 'CC BY 4.0 (CICT Chennai)'
  },
  {
    id: 'palmleaf-tamil',
    name: 'palmleaf-tamil Character Dataset',
    type: 'Isolated Character Glyphs (Lossless PNG)',
    imagesCount: 7100,
    groundTruth: '71 Character Classes (100 Samples / Class)',
    tier: 'Level 2: Character Morphology',
    role: 'CHARACTER_POOL (Encoder Pre-adaptation & Synthesis)',
    status: 'Indexed in palmleaf-tamil.rar (816.35 MB)',
    format: 'PNG (Lossless Binarized Crops)',
    license: 'Academic / Open-Access (Kaggle)'
  },
  {
    id: 'thplmd-naladiyar',
    name: 'THPLMD — Naladiyar Collection',
    type: 'Palm-Leaf Manuscript Folios (3996 × 600 px)',
    imagesCount: 53,
    groundTruth: 'Unlabeled (14 Automatic Line Candidates Sliced)',
    tier: 'Level 5: Unlabeled Real Folios',
    role: 'UNLABELED_POOL (Domain Statistics & Preprocessing)',
    status: 'Ingested in data/processed/staging/thplmd/naladiyar/',
    format: 'JPEG (29 Raw + 24 Binarized)',
    license: 'Academic Research Use'
  },
  {
    id: 'thplmd-thirikadugam',
    name: 'THPLMD — Thirikadugam Collection',
    type: 'Palm-Leaf Manuscript Folios (3996 × 600 px)',
    imagesCount: 24,
    groundTruth: 'Unlabeled (18 Automatic Line Candidates Sliced)',
    tier: 'Level 5: Unlabeled Real Folios',
    role: 'UNLABELED_POOL (Domain Statistics & Preprocessing)',
    status: 'Ingested in data/processed/staging/thplmd/thirikadugam/',
    format: 'JPEG (15 Raw + 9 Binarized)',
    license: 'Academic Research Use'
  },
  {
    id: 'thplmd-tholkappiyam',
    name: 'THPLMD — Tholkappiyam Binarized',
    type: 'Palm-Leaf Manuscript Folios (3996 × 600 px)',
    imagesCount: 81,
    groundTruth: 'Unlabeled (14 Automatic Line Candidates Sliced)',
    tier: 'Level 5: Unlabeled Real Folios',
    role: 'UNLABELED_POOL (Domain Statistics & Preprocessing)',
    status: 'Ingested in data/processed/staging/thplmd/tholkappiyam/',
    format: 'JPEG (81 Binarized)',
    license: 'Academic Research Use'
  },
  {
    id: 'iiit-tamil',
    name: 'IIIT Tamil Handwriting Dataset',
    type: 'Handwritten Tamil Words',
    imagesCount: 0,
    groundTruth: 'Unavailable Locally',
    tier: 'External / Awaiting',
    role: 'AWAITING_ACQUISITION',
    status: 'Offline (Host server-side error)',
    format: 'N/A',
    license: 'N/A'
  }
];

export const EXPERIMENTS_MATRIX = [
  {
    id: 'exp-01',
    pipeline: 'Baseline OCR (Raw Image)',
    model: 'EasyOCR Tamil (Zero-Shot)',
    preprocessing: 'None (Raw Unprocessed)',
    cer: '96.23% (0.9623)',
    wer: '132.66% (1.3266)',
    status: 'Evaluated (Stage 3 & 4)'
  },
  {
    id: 'exp-02',
    pipeline: 'Standard Grayscale Conversion',
    model: 'EasyOCR Tamil (Zero-Shot)',
    preprocessing: 'Luminance Grayscale',
    cer: '95.30% (0.9530)',
    wer: '131.21% (1.3121)',
    status: 'Evaluated (Stage 4)'
  },
  {
    id: 'exp-03',
    pipeline: 'Pipeline A (CLAHE Contrast Boost)',
    model: 'EasyOCR Tamil (Zero-Shot)',
    preprocessing: 'CLAHE (Clip Limit 2.5)',
    cer: '96.19% (0.9619)',
    wer: '118.18% (1.1818)',
    status: 'Evaluated (Stage 4)'
  },
  {
    id: 'exp-04',
    pipeline: 'Pipeline C (Illumination Norm + CLAHE)',
    model: 'EasyOCR Tamil (Zero-Shot)',
    preprocessing: 'Morphological Bg Division + CLAHE',
    cer: '95.89% (0.9589)',
    wer: '115.45% (1.1545)',
    status: 'Evaluated (Best WER Stage 4)'
  },
  {
    id: 'exp-05',
    pipeline: 'Pipeline D (Sauvola Binarization + Deskew)',
    model: 'EasyOCR Tamil (Zero-Shot)',
    preprocessing: 'Sauvola Local Thresholding (w=25, k=0.2)',
    cer: '95.29% (0.9529)',
    wer: '141.83% (1.4183)',
    status: 'Evaluated (Best CER Stage 4)'
  },
  {
    id: 'exp-06',
    pipeline: 'EXP-8A: Baseline Zero-Shot on Synthetic Test (N=35)',
    model: 'EasyOCR Tamil CRNN (Zero-Shot)',
    preprocessing: 'None (Raw)',
    cer: '99.90% (0.9990)',
    wer: '100.00% (1.0000)',
    status: 'Evaluated (Stage 8 Benchmark)'
  },
  {
    id: 'exp-07',
    pipeline: 'EXP-8C: Fine-Tuned Model on Synthetic Test (N=35)',
    model: 'TamilCRNN (best_tamil_crnn.pth)',
    preprocessing: 'None (Raw)',
    cer: '12.76% (0.1276)',
    wer: '48.24% (0.4824)',
    status: 'Evaluated (Stage 8 Best Model: 31.4% Exact Match)'
  },
  {
    id: 'exp-08',
    pipeline: 'EXP-8E: Fine-Tuned Model + Preprocessing Pipeline C (N=23)',
    model: 'TamilCRNN (best_tamil_crnn.pth)',
    preprocessing: 'Pipeline C (Illum Norm + CLAHE)',
    cer: '191.48% (1.9148)',
    wer: '104.91% (1.0491)',
    status: 'Evaluated (Stage 8 Real CICT External Test)'
  },
  {
    id: 'exp-09',
    pipeline: 'EXP-9A: Stage 8 First-Pass Model on CICT External Test (N=23)',
    model: 'TamilCRNN (best_tamil_crnn.pth)',
    preprocessing: 'Raw (Unprocessed)',
    cer: '296.30% (2.9630)',
    wer: '136.89% (1.3689)',
    status: 'Evaluated (Stage 9 Condition A Baseline)'
  },
  {
    id: 'exp-10',
    pipeline: 'EXP-9B: Confidence Second-Pass Reprocessing on CICT (N=23)',
    model: 'TamilCRNN + Quality Gate (Threshold 0.85)',
    preprocessing: 'Dynamic Multi-Filter Routing (Raw/CLAHE/Illum/Sauvola)',
    cer: '141.12% (1.4112)',
    wer: '111.89% (1.1189)',
    status: 'Evaluated (Stage 9 Condition B: -155.18% CER Reduction)'
  },
  {
    id: 'exp-11',
    pipeline: 'EXP-9C: Second Pass + Conservative Tamil Post-Correction (N=23)',
    model: 'TamilCRNN + Router + TamilPostCorrector',
    preprocessing: 'Dynamic Multi-Filter Routing + NFC/Combining Rules',
    cer: '137.01% (1.3701)',
    wer: '109.57% (1.0957)',
    status: 'Evaluated (Stage 9 Condition C: Best Palm-Leaf Pipeline)'
  }
];

const BACKEND_BASE_URL = 'http://127.0.0.1:8000';

export const api = {
  async getSystemStatus() {
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/api/status`);
      if (res.ok) {
        const liveData = await res.json();
        return { ...SYSTEM_STATUS, ...liveData };
      }
    } catch (e) {
      // Live backend offline -> return verified system status
    }
    return Promise.resolve(SYSTEM_STATUS);
  },

  async getManuscript(id = 'CICT-PLM-GT-133') {
    const found = SAMPLE_MANUSCRIPTS.find(m => m.id === id) || SAMPLE_MANUSCRIPTS[0];
    return Promise.resolve(found);
  },

  async getDatasets() {
    return Promise.resolve(DATASETS_MANIFEST);
  },

  async getExperiments() {
    try {
      const res = await fetch(`${BACKEND_BASE_URL}/api/experiments`);
      if (res.ok) {
        const liveData = await res.json();
        if (liveData.experiments && liveData.experiments.length > 0) {
          return liveData.experiments;
        }
      }
    } catch (e) {
      // Fallback
    }
    return Promise.resolve(EXPERIMENTS_MATRIX);
  },

  async saveCorrection(manuscriptId, lineId, text) {
    console.log(`[Correction Saved] Manuscript: ${manuscriptId}, Line: ${lineId}, Text: ${text}`);
    return Promise.resolve({ success: true, timestamp: new Date().toISOString() });
  },

  async processFolioLive(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folio_id', file.name.split('.')[0] || 'UPLOADED_FOLIO');

    const res = await fetch(`${BACKEND_BASE_URL}/api/process`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) {
      throw new Error(`Pipeline processing failed with status: ${res.status}`);
    }
    return await res.json();
  }
};
