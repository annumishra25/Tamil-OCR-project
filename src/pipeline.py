"""
End-to-End Tamil Palm-Leaf Manuscript Digitization Pipeline
Stage 10: Final System Integration

Pipeline Workflow:
PALM-LEAF FOLIO IMAGE
       ↓
IMAGE QUALITY ANALYSIS (Sharpness, Contrast, Illumination Uniformity)
       ↓
ADAPTIVE PREPROCESSING (Illumination Norm + CLAHE)
       ↓
LINE SEGMENTATION (Horizontal Projection Profile)
       ↓
TamilCRNN RECOGNITION (Adapted 53.79M Param Model)
       ↓
CTC CONFIDENCE ESTIMATION & QUALITY GATING
       ↓
SECOND-PASS REPROCESSING (Across multi-filter candidate bank if confidence < threshold)
       ↓
TAMIL POST-CORRECTION (Conservative Unicode NFC & Combining Mark Attachment)
       ↓
DIGITAL TAMIL TEXT EXPORT (TXT, JSON, CSV)
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union
import numpy as np
import cv2
import torch
from PIL import Image

PROJECT_ROOT = Path(r"C:\Users\vaish\tamil_palm_ocr").resolve()
sys.path.append(str(PROJECT_ROOT))

from src.preprocessing.quality_analysis import analyze_image_quality
from src.preprocessing.pipeline import PreprocessingPipeline
from src.segmentation.line_segmenter import PalmLeafLineSegmenter
from src.ocr.crnn_model import TamilCRNN
from src.ocr.processor import TamilOCRProcessor
from src.ocr.model_loader import load_tamil_crnn_model
from src.confidence.second_pass import SecondPassRouter, SecondPassResult
from src.correction.tamil_postcorrection import TamilPostCorrector


class EndToEndPalmLeafPipeline:
    def __init__(
        self,
        checkpoint_path: Optional[Path] = None,
        confidence_threshold: float = 0.85,
        device: Optional[torch.device] = None
    ):
        self.device = device or (torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        
        ckpt = checkpoint_path or (PROJECT_ROOT / "models" / "checkpoints" / "stage8" / "best_tamil_crnn.pth")
        if not ckpt.exists():
            ckpt = PROJECT_ROOT / "models" / "pretrained" / "tamil_pretrained.pth"

        print(f"Initializing End-to-End Pipeline with model: {ckpt} on {self.device}...")
        self.model, self.processor, self.device = load_tamil_crnn_model(
            checkpoint_path=ckpt,
            device=self.device,
            vocab_size=143
        )

        self.segmenter = PalmLeafLineSegmenter()
        self.preprocessor = PreprocessingPipeline()
        self.router = SecondPassRouter(
            model=self.model,
            processor=self.processor,
            device=self.device,
            confidence_threshold=confidence_threshold,
            ambiguity_margin=0.025,
            review_floor=0.50,
            default_pipeline="raw",
            candidate_pipelines=["raw", "pipeline_a_clahe", "pipeline_c_illum_clahe", "pipeline_d_sauvola_deskew"]
        )
        self.post_corrector = TamilPostCorrector()

    def process_folio(
        self,
        img_input: Union[str, Path, np.ndarray, Image.Image],
        folio_id: str = "FOLIO_001"
    ) -> Dict[str, Any]:
        """
        Executes full 8-step digitization pipeline on a palm-leaf folio.
        """
        start_time = time.time()

        # Normalize input to numpy array and PIL Image
        if isinstance(img_input, (str, Path)):
            img_path = Path(img_input)
            img_np = cv2.imread(str(img_path))
            if img_np is None:
                raise ValueError(f"Could not load image: {img_path}")
            img_pil = Image.open(str(img_path))
        elif isinstance(img_input, Image.Image):
            img_pil = img_input
            img_np = cv2.cvtColor(np.array(img_input), cv2.COLOR_RGB2BGR)
        elif isinstance(img_input, np.ndarray):
            img_np = img_input
            img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
        else:
            raise TypeError("img_input must be a file path, PIL Image, or numpy array")

        # Step 1: Image Quality Analysis
        quality_metrics = analyze_image_quality(img_np)

        # Step 2: Line Segmentation
        line_boxes, overlay_np = self.segmenter.segment_horizontal_projection(img_np, prep_variant="illum_clahe")
        
        # If no lines found (e.g. single-line crop was passed), fallback to entire image as 1 line
        if not line_boxes:
            h, w = img_np.shape[:2]
            line_boxes = [{
                "line_idx": 1,
                "bbox": [0, 0, w, h],
                "confidence": 1.0,
                "polygon": [[0, 0], [w, 0], [w, h], [0, h]]
            }]

        # Step 3 to 6: Line Cropping, OCR, Second-Pass, and Post-Correction
        processed_lines = []
        full_text_lines = []
        review_count = 0

        h_full, w_full = img_np.shape[:2]

        for box_info in line_boxes:
            l_idx = box_info["line_idx"]
            x, y, w, h = box_info["bbox"]

            # Safe crop bounds
            x0 = max(0, x)
            y0 = max(0, y)
            x1 = min(w_full, x + w)
            y1 = min(h_full, y + h)

            line_crop_np = img_np[y0:y1, x0:x1]
            if line_crop_np.size == 0:
                continue

            line_crop_pil = Image.fromarray(cv2.cvtColor(line_crop_np, cv2.COLOR_BGR2RGB))
            line_id = f"{folio_id}_L{l_idx:02d}"

            # Run confidence-triggered OCR router
            res: SecondPassResult = self.router.process_line(
                img_input=line_crop_pil,
                source_id=folio_id,
                line_id=line_id
            )

            if res.review_required:
                review_count += 1

            line_dict = {
                "line_idx": l_idx,
                "line_id": line_id,
                "bbox": [x, y, w, h],
                "first_pass_text": res.first_pass_text,
                "first_pass_confidence": round(res.first_pass_confidence, 4),
                "second_pass_triggered": res.second_pass_triggered,
                "candidate_preprocessing": res.candidate_preprocessing,
                "candidate_texts": res.candidate_texts,
                "candidate_confidences": [round(c, 4) for c in res.candidate_confidences],
                "selected_text": res.selected_text,
                "selection_reason": res.selection_reason,
                "corrected_text": res.corrected_text,
                "correction_changes": res.correction_changes,
                "review_required": res.review_required
            }
            processed_lines.append(line_dict)
            if res.corrected_text.strip():
                full_text_lines.append(res.corrected_text.strip())

        total_time_sec = round(time.time() - start_time, 3)
        final_transcription = "\n".join(full_text_lines)

        return {
            "folio_id": folio_id,
            "image_dimensions": {"width": w_full, "height": h_full},
            "quality_analysis": quality_metrics,
            "segmented_lines_count": len(processed_lines),
            "lines": processed_lines,
            "final_transcription": final_transcription,
            "review_required_count": review_count,
            "total_processing_time_sec": total_time_sec,
            "status": "COMPLETED"
        }
