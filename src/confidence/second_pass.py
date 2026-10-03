"""
Confidence-Triggered Second-Pass Reprocessing Engine
Stage 9: Confidence Second Pass + Tamil Post-Correction

Architecture:
1. First Pass: Runs default preprocessing + TamilCRNN OCR.
2. Confidence Evaluation: Real CTC sequence confidence extraction.
3. Quality Gating:
   - If confidence >= threshold: Accept first pass.
   - If confidence < threshold: Trigger Second Pass.
4. Candidate Generation: Re-processes image across multiple pre-processing filter banks:
   [Raw, Pipeline A (CLAHE), Pipeline C (Illumination Norm + CLAHE), Pipeline D (Sauvola Binarization)]
5. Selection & Ambiguity Checking:
   - Evaluates confidence across all candidates.
   - Selects highest confidence candidate.
   - If top candidate confidences are within ambiguity margin or below review floor, marks REVIEW_REQUIRED.
6. Post-Correction: Applies conservative Tamil orthographic cleaner.
7. Full Provenance: Returns complete candidate trace and selection reason.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import numpy as np
import torch
from PIL import Image

from src.ocr.crnn_model import TamilCRNN
from src.ocr.processor import TamilOCRProcessor
from src.preprocessing.pipeline import PreprocessingPipeline
from src.confidence.confidence_estimator import CTCConfidenceEstimator, SequenceConfidenceResult
from src.correction.tamil_postcorrection import TamilPostCorrector, CorrectionResult


@dataclass
class CandidateResult:
    pipeline_name: str
    transcription: str
    confidence: float
    token_confidences: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_name": self.pipeline_name,
            "transcription": self.transcription,
            "confidence": round(self.confidence, 4)
        }


@dataclass
class SecondPassResult:
    source_id: str
    line_id: str
    first_pass_text: str
    first_pass_confidence: float
    second_pass_triggered: bool
    candidate_preprocessing: List[str]
    candidate_texts: List[str]
    candidate_confidences: List[float]
    selected_text: str
    selection_reason: str
    corrected_text: str
    correction_changes: List[Dict[str, Any]]
    review_required: bool
    candidates: List[CandidateResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "line_id": self.line_id,
            "first_pass_text": self.first_pass_text,
            "first_pass_confidence": round(self.first_pass_confidence, 4),
            "second_pass_triggered": self.second_pass_triggered,
            "candidate_preprocessing": self.candidate_preprocessing,
            "candidate_texts": self.candidate_texts,
            "candidate_confidences": [round(c, 4) for c in self.candidate_confidences],
            "selected_text": self.selected_text,
            "selection_reason": self.selection_reason,
            "corrected_text": self.corrected_text,
            "correction_changes": self.correction_changes,
            "review_required": self.review_required,
            "candidates": [c.to_dict() for c in self.candidates]
        }


class SecondPassRouter:
    def __init__(
        self,
        model: TamilCRNN,
        processor: Optional[TamilOCRProcessor] = None,
        device: Optional[torch.device] = None,
        confidence_threshold: float = 0.85,
        ambiguity_margin: float = 0.025,
        review_floor: float = 0.50,
        default_pipeline: str = "raw",
        candidate_pipelines: Optional[List[str]] = None
    ):
        self.model = model
        self.processor = processor or TamilOCRProcessor()
        self.device = device or (torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        self.model.to(self.device)
        self.model.eval()

        self.confidence_threshold = confidence_threshold
        self.ambiguity_margin = ambiguity_margin
        self.review_floor = review_floor
        self.default_pipeline = default_pipeline
        self.candidate_pipelines = candidate_pipelines or [
            "raw",
            "pipeline_a_clahe",
            "pipeline_c_illum_clahe",
            "pipeline_d_sauvola_deskew"
        ]

        self.preprocessor = PreprocessingPipeline()
        self.confidence_estimator = CTCConfidenceEstimator(self.processor)
        self.post_corrector = TamilPostCorrector()

    def _infer_image_tensor(self, img_pil: Image.Image) -> SequenceConfidenceResult:
        """Runs single-image inference and extracts true CTC confidence."""
        tensor = self.processor.process_image(img_pil).unsqueeze(0).to(self.device)
        with torch.no_grad():
            log_probs = self.model(tensor)
        return self.confidence_estimator.estimate_confidence(log_probs, batch_index=0)

    def _run_preprocessing_pipeline(self, img_input: Union[Path, str, np.ndarray, Image.Image], pipeline_key: str) -> Image.Image:
        """Applies named preprocessing pipeline and returns PIL Image."""
        if isinstance(img_input, Image.Image):
            img_np = np.array(img_input)
        elif isinstance(img_input, (str, Path)):
            img_np = str(img_input)
        else:
            img_np = img_input

        if pipeline_key == "raw":
            if isinstance(img_input, Image.Image):
                return img_input
            elif isinstance(img_input, np.ndarray):
                return Image.fromarray(img_input)
            else:
                return Image.open(str(img_input))

        processed_np, _ = self.preprocessor.run_pipeline(img_np, pipeline_key=pipeline_key)
        return Image.fromarray(processed_np)

    def process_line(
        self,
        img_input: Union[Path, str, np.ndarray, Image.Image],
        source_id: str = "UNKNOWN_SOURCE",
        line_id: str = "LINE_001"
    ) -> SecondPassResult:
        """
        Executes full two-pass OCR pipeline on a single line crop.
        """
        # 1. First Pass Execution
        first_pass_img = self._run_preprocessing_pipeline(img_input, self.default_pipeline)
        first_pass_res = self._infer_image_tensor(first_pass_img)

        first_text = first_pass_res.transcription
        first_conf = first_pass_res.sequence_confidence

        candidate_results: List[CandidateResult] = [
            CandidateResult(
                pipeline_name=self.default_pipeline,
                transcription=first_text,
                confidence=first_conf,
                token_confidences=[tc.__dict__ for tc in first_pass_res.token_confidences]
            )
        ]

        # 2. Threshold Check
        if first_conf >= self.confidence_threshold:
            # High confidence -> Accept first pass directly
            second_pass_triggered = False
            selected_text = first_text
            selection_reason = "FIRST_PASS_CONFIDENCE_ABOVE_THRESHOLD"
            review_required = False
        else:
            # Low confidence -> Trigger Second Pass across candidate variants
            second_pass_triggered = True

            for pipe_name in self.candidate_pipelines:
                if pipe_name == self.default_pipeline:
                    continue  # Already computed in first pass

                try:
                    cand_img = self._run_preprocessing_pipeline(img_input, pipe_name)
                    cand_res = self._infer_image_tensor(cand_img)
                    candidate_results.append(CandidateResult(
                        pipeline_name=pipe_name,
                        transcription=cand_res.transcription,
                        confidence=cand_res.sequence_confidence,
                        token_confidences=[tc.__dict__ for tc in cand_res.token_confidences]
                    ))
                except Exception as e:
                    # In case of any filter exception, skip this candidate safely
                    pass

            # Sort candidates by confidence descending
            candidate_results.sort(key=lambda x: x.confidence, reverse=True)
            best_candidate = candidate_results[0]
            selected_text = best_candidate.transcription

            if best_candidate.pipeline_name == self.default_pipeline:
                selection_reason = "FIRST_PASS_RETAINED_AS_BEST_CANDIDATE"
            else:
                selection_reason = f"SECOND_PASS_SELECTED_{best_candidate.pipeline_name.upper()}"

            # Ambiguity Assessment:
            # Check if second best candidate is very close in confidence
            review_required = False
            if len(candidate_results) > 1:
                second_best = candidate_results[1]
                conf_diff = best_candidate.confidence - second_best.confidence
                if conf_diff < self.ambiguity_margin and best_candidate.confidence < self.confidence_threshold:
                    review_required = True
                    selection_reason += "_AMBIGUOUS_CANDIDATES"

            if best_candidate.confidence < self.review_floor:
                review_required = True
                selection_reason += "_LOW_CONFIDENCE_BELOW_FLOOR"

        # 3. Apply Conservative Tamil Post-Correction
        corr_res = self.post_corrector.correct(selected_text)
        corrected_text = corr_res.corrected_text
        correction_changes = [c.to_dict() for c in corr_res.changes]

        return SecondPassResult(
            source_id=source_id,
            line_id=line_id,
            first_pass_text=first_text,
            first_pass_confidence=first_conf,
            second_pass_triggered=second_pass_triggered,
            candidate_preprocessing=[c.pipeline_name for c in candidate_results],
            candidate_texts=[c.transcription for c in candidate_results],
            candidate_confidences=[c.confidence for c in candidate_results],
            selected_text=selected_text,
            selection_reason=selection_reason,
            corrected_text=corrected_text,
            correction_changes=correction_changes,
            review_required=review_required,
            candidates=candidate_results
        )
